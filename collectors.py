import asyncio
import sys
import os
import re
from datetime import datetime
from playwright.async_api import async_playwright

# 解决 Playwright 和 Streamlit 在 Windows 上的事件循环冲突
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".playwright_profile")


def format_timestamp(ts):
    """把 Unix 时间戳转成标准日期字符串"""
    try:
        ts = int(ts)
        if ts <= 0:
            return None
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


async def fetch_douyin_data(short_url: str, headless: bool = True) -> dict:
    """接收分享文本，自动提取链接并抓取数据。"""

    # 1. 提取真实链接（解决用户直接复制整段分享文本的问题）
    match = re.search(r"https?://[^\s]+", short_url)
    if not match:
        return {"error": "没有在输入的内容中找到有效链接，请检查粘贴内容。"}
    short_url = match.group(0)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=headless,
            viewport={"width": 1440, "height": 900},
        )

        detail_data = {"body": None}

        async def on_response(response):
            if "/aweme/v1/web/aweme/detail/" in response.url:
                try:
                    detail_data["body"] = await response.json()
                except Exception:
                    pass

        context.on("response", on_response)

        page = await context.new_page()

        try:
            await page.goto(short_url, wait_until="domcontentloaded", timeout=60000)
            # 等待 10 秒，确保页面元素和接口数据加载完毕
            await page.wait_for_timeout(10000)

            if not detail_data["body"]:
                # 如果抓取失败，保存截图供排查
                await page.screenshot(path="debug_headless.png", full_page=True)
                html_content = await page.content()
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                await context.close()
                return {"error": f"未捕获到接口数据。当前页面URL: {page.url}。已保存截图供排查。"}

            aweme = detail_data["body"].get("aweme_detail", {}) or {}
            stats = aweme.get("statistics", {}) or {}
            author = aweme.get("author", {}) or {}
            desc = aweme.get("desc", "") or ""

            aweme_id = stats.get("aweme_id") or aweme.get("aweme_id") or ""
            create_ts = aweme.get("create_time") or stats.get("create_time") or 0

            result = {
                "platform": "douyin",
                "aweme_id": aweme_id,
                "author": author.get("nickname", "未知"),
                "title": desc[:30],
                "description": desc,
                "likes": stats.get("digg_count", None),
                "comments": stats.get("comment_count", None),
                "favorites": stats.get("collect_count", None),
                "shares": stats.get("share_count", None),
                "publish_time": format_timestamp(create_ts),
                "video_url": f"https://www.douyin.com/video/{aweme_id}" if aweme_id else short_url,
            }
            await context.close()
            return result

        except Exception as e:
            await context.close()
            return {"error": f"采集过程中发生错误: {str(e)}"}
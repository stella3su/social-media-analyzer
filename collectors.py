import asyncio
import sys
import os
import re
import json
from datetime import datetime
from playwright.async_api import async_playwright

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

DY_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".playwright_profile")
XHS_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".xhs_profile")


def format_timestamp(ts):
    try:
        ts = int(ts)
        if ts <= 0: return None
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None


def parse_xhs_num(num_str):
    if not num_str: return 0
    try:
        if "万" in str(num_str): return int(float(str(num_str).replace("万", "")) * 10000)
        return int(num_str)
    except:
        return 0


# ==================== 抖音逻辑不变 ====================
async def fetch_douyin_data(short_url: str, headless: bool = True) -> dict:
    match = re.search(r"https?://[^\s]+", short_url)
    if not match: return {"error": "没有在输入的内容中找到有效链接。"}
    short_url = match.group(0)
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=DY_PROFILE_DIR, headless=headless,
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        detail_data = {"body": None}

        async def on_response(response):
            if "/aweme/v1/web/aweme/detail/" in response.url:
                try:
                    detail_data["body"] = await response.json()
                except:
                    pass

        context.on("response", on_response)
        page = await context.new_page()
        try:
            await page.goto(short_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(15000)
            if not detail_data["body"]:
                await page.screenshot(path="douyin_debug.png", full_page=True)
                await context.close()
                return {"error": "未捕获到抖音接口数据，可能被风控拦截。"}
            aweme = detail_data["body"].get("aweme_detail", {}) or {}
            stats = aweme.get("statistics", {}) or {}
            author = aweme.get("author", {}) or {}
            desc = aweme.get("desc", "") or ""
            aweme_id = stats.get("aweme_id") or aweme.get("aweme_id") or ""
            create_ts = aweme.get("create_time") or stats.get("create_time") or 0
            result = {
                "platform": "douyin", "aweme_id": aweme_id,
                "author": author.get("nickname", "未知"), "title": desc[:30], "description": desc,
                "likes": stats.get("digg_count", 0), "comments": stats.get("comment_count", 0),
                "favorites": stats.get("collect_count", 0), "shares": stats.get("share_count", 0),
                "publish_time": format_timestamp(create_ts),
                "video_url": f"https://www.douyin.com/video/{aweme_id}" if aweme_id else short_url,
            }
            await context.close()
            return result
        except Exception as e:
            await context.close()
            return {"error": f"抖音采集错误: {str(e)}"}


# ==================== 小红书终极精准提取 ====================
async def fetch_xiaohongshu_data(short_url: str, headless: bool = True) -> dict:
    match = re.search(r"https?://[^\s]+", short_url)
    if not match: return {"error": "没有找到有效链接。"}
    target_url = match.group(0)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=XHS_PROFILE_DIR, headless=headless,
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(10000)

            # 直接去浏览器内存里拿小红书的 State 字典，这是最不可能出错的方法
            state_data = await page.evaluate("() => window.__INITIAL_STATE__ || null")

            if not state_data:
                await context.close()
                return {"error": "未能获取到页面初始数据，极可能被重定向到了首页。"}

            # 查找笔记数据
            note_map = state_data.get("note", {}).get("noteDetailMap", {})
            if not note_map:
                await context.close()
                return {"error": "页面里没有笔记详情数据，链接可能已过期或被强制重定向。"}

            # 提取数据
            note_info = list(note_map.values())[0].get("note", {})
            if not note_info:
                await context.close()
                return {"error": "数据字典为空。"}

            result = {
                "platform": "xiaohongshu",
                "aweme_id": "xhs_" + str(int(datetime.now().timestamp())),
                "author": note_info.get("user", {}).get("nickname", "未知"),
                "title": note_info.get("title", "") or note_info.get("desc", "")[:30],
                "description": note_info.get("desc", ""),
                "likes": parse_xhs_num(note_info.get("interactInfo", {}).get("likedCount", "0")),
                "comments": parse_xhs_num(note_info.get("interactInfo", {}).get("commentCount", "0")),
                "favorites": parse_xhs_num(note_info.get("interactInfo", {}).get("collectedCount", "0")),
                "shares": parse_xhs_num(note_info.get("interactInfo", {}).get("shareCount", "0")),
                "publish_time": "未知",
                "video_url": target_url,
            }
            await context.close()
            return result

        except Exception as e:
            await context.close()
            return {"error": f"小红书采集发生错误: {str(e)}"}
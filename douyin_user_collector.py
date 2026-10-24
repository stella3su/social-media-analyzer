from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import json
import csv

PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".playwright_profile")

# 换成你要采集的账号主页链接
USER_URL = "https://www.douyin.com/user/MS4wLjABAAAAhV40YlQOgJ3x4mO7jLPq5_6pu3NLsKhUwBLaSGQkz5ldPuPMkobGfv1ONZZEKTX-?from_tab_name=main"

# 滚动几次（每次触发一批新视频加载）
SCROLL_TIMES = 5


def format_timestamp(ts):
    try:
        ts = int(ts)
        if ts <= 0:
            return None
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def main():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1440, "height": 900},
        )

        # 存放所有捕获到的 post 接口响应
        captured_responses = []

        def on_response(response):
            if "/aweme/v1/web/aweme/post/" in response.url:
                try:
                    captured_responses.append(response.json())
                except Exception:
                    pass

        context.on("response", on_response)

        page = context.new_page()
        print("正在访问账号主页:", USER_URL)
        page.goto(USER_URL, wait_until="domcontentloaded", timeout=60000)

        print("\n" + "=" * 60)
        print("浏览器已打开。请确认视频列表已加载，然后回终端按回车开始自动滚动采集。")
        print("=" * 60)
        input("\n>>> 按回车继续...")

        # 自动滚动，触发更多视频加载
        for i in range(SCROLL_TIMES):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(2500)
            print(f"已滚动 {i+1}/{SCROLL_TIMES} 次")

        page.wait_for_timeout(3000)

        print(f"\n共捕获 {len(captured_responses)} 个 post 接口响应")

        # 从所有响应里提取视频，按 aweme_id 去重
        all_videos = {}
        for resp in captured_responses:
            for item in resp.get("aweme_list", []) or []:
                aweme_id = item.get("aweme_id")
                if aweme_id and aweme_id not in all_videos:
                    all_videos[aweme_id] = item

        print(f"去重后共获得 {len(all_videos)} 条视频")

        # 逐条提取结构化字段
        results = []
        for aweme_id, item in all_videos.items():
            stats = item.get("statistics", {}) or {}
            author = item.get("author", {}) or {}
            desc = item.get("desc", "") or ""
            create_ts = item.get("create_time", 0) or 0

            results.append({
                "platform": "douyin",
                "aweme_id": aweme_id,
                "author": author.get("nickname", ""),
                "title_summary": desc[:30],
                "description": desc,
                "likes": stats.get("digg_count", 0),
                "comments": stats.get("comment_count", 0),
                "favorites": stats.get("collect_count", 0),
                "shares": stats.get("share_count", 0),
                "publish_timestamp": create_ts,
                "publish_time": format_timestamp(create_ts),
                "video_url": f"https://www.douyin.com/video/{aweme_id}",
                "transcript": "",
            })

        # 按发布时间倒序排列
        results.sort(key=lambda x: x["publish_timestamp"], reverse=True)

        # 保存 JSON
        with open("douyin_user_notes.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("结构化数据已保存到 douyin_user_notes.json")

        # 保存 CSV（方便用表格打开核对）
        if results:
            with open("douyin_user_notes.csv", "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            print("CSV 数据已保存到 douyin_user_notes.csv")

        # 打印前 5 条做快速核对
        print("\n===== 前 5 条视频概览 =====")
        for r in results[:5]:
            print(f"[{r['publish_time']}] 点赞:{r['likes']} 收藏:{r['favorites']} | {r['title_summary']}")

        page.wait_for_timeout(3000)
        context.close()


if __name__ == "__main__":
    main()
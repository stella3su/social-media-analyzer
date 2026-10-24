from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import json

PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".playwright_profile")
SHORT_URL = "https://v.douyin.com/xBJyk_E6AVo/"


def format_timestamp(ts):
    """把 Unix 时间戳转成标准日期字符串；如果无效返回 None"""
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

        detail_data = {"body": None}

        def on_response(response):
            if "/aweme/v1/web/aweme/detail/" in response.url:
                try:
                    detail_data["body"] = response.json()
                except Exception:
                    pass

        context.on("response", on_response)

        page = context.new_page()
        print("正在访问短链:", SHORT_URL)
        page.goto(SHORT_URL, wait_until="domcontentloaded", timeout=60000)

        print("\n" + "=" * 60)
        print("浏览器已打开。请确认视频页面加载完毕，然后回终端按回车。")
        print("=" * 60)
        input("\n>>> 按回车继续...")

        page.wait_for_timeout(3000)

        if not detail_data["body"]:
            print("❌ 未捕获到 detail 接口响应，无法提取数据。")
            context.close()
            return

        # 1. 保留原始响应，不覆盖
        raw_path = "douyin_detail_raw.json"
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(detail_data["body"], f, ensure_ascii=False, indent=2)
        print(f"原始 detail 响应已保存到 {raw_path}")

        # 2. 从响应中提取字段（容错：所有取值都用 .get 带默认值）
        aweme = detail_data["body"].get("aweme_detail", {}) or {}
        stats = aweme.get("statistics", {}) or {}
        author = aweme.get("author", {}) or {}

        desc = aweme.get("desc", "") or ""

        # aweme_id 优先从 statistics 取，退化到 aweme_detail
        aweme_id = stats.get("aweme_id") or aweme.get("aweme_id") or ""

        # create_time 优先从 aweme_detail 取，退化到 statistics
        create_ts = aweme.get("create_time") or stats.get("create_time") or 0
        publish_time = format_timestamp(create_ts)

        # 拼标准视频 URL
        if aweme_id:
            video_url = f"https://www.douyin.com/video/{aweme_id}"
        else:
            video_url = SHORT_URL

        # 3. 组装最终结构化结果
        result = {
            "platform": "douyin",
            "aweme_id": aweme_id,
            "author": author.get("nickname", ""),
            "title_summary": desc[:30],           # 前30字摘要，不伪装成"真实标题"
            "description": desc,                  # 完整描述
            "likes": stats.get("digg_count", 0),
            "comments": stats.get("comment_count", 0),
            "favorites": stats.get("collect_count", 0),
            "shares": stats.get("share_count", 0),
            "publish_timestamp": create_ts,       # 保留原始 Unix 时间戳
            "publish_time": publish_time,         # 转换后的标准日期
            "video_url": video_url,
            "transcript": "",
        }

        # 4. 打印，方便人工核验
        print("\n===== 提取到的结构化数据 =====")
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # 5. 保存结果（不覆盖原始 raw 文件）
        out_path = "douyin_note.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结构化数据已保存到 {out_path}")

        # 6. 数据核验提示
        print("\n===== 请人工核验 =====")
        print(f"作者: {result['author']}")
        print(f"点赞: {result['likes']}（与页面显示对比）")
        print(f"评论: {result['comments']}")
        print(f"收藏: {result['favorites']}")
        print(f"分享: {result['shares']}")
        print(f"发布时间: {result['publish_time']}（原始戳: {result['publish_timestamp']}）")
        print(f"视频 URL: {result['video_url']}")

        page.wait_for_timeout(3000)
        context.close()


if __name__ == "__main__":
    main()
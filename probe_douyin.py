from playwright.sync_api import sync_playwright
import os
import json

PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".playwright_profile")
SHORT_URL = "https://v.douyin.com/xBJyk_E6AVo/"

def main():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1440, "height": 900},
        )

        # 用来存放我们关心的接口响应
        captured = []

        def on_response(response):
            url = response.url
            # 只关心包含 aweme 和 detail/social/count 的接口
            if "aweme" in url and any(k in url for k in ["detail", "social/count", "related"]):
                try:
                    body = response.json()
                    captured.append({"url": url, "body": body})
                except Exception:
                    # 不是 JSON 就跳过
                    pass

        context.on("response", on_response)

        page = context.new_page()
        print("正在访问短链:", SHORT_URL)
        page.goto(SHORT_URL, wait_until="domcontentloaded", timeout=60000)

        print("\n" + "=" * 60)
        print("浏览器已打开。请在窗口里确认视频页面加载完毕。")
        print("然后回到终端按【回车】继续。")
        print("=" * 60)
        input("\n>>> 按回车继续...")

        page.wait_for_timeout(3000)

        print(f"\n共捕获 {len(captured)} 个目标接口响应：\n")

        for i, item in enumerate(captured):
            url_short = item["url"].split("?")[0]
            print(f"===== [{i}] {url_short} =====")
            print(json.dumps(item["body"], ensure_ascii=False, indent=2)[:2000])
            print()

        # 把完整响应保存到文件，方便后续查看
        with open("douyin_probe_responses.json", "w", encoding="utf-8") as f:
            json.dump(captured, f, ensure_ascii=False, indent=2)
        print("完整响应已保存到 douyin_probe_responses.json")

        page.wait_for_timeout(5000)
        context.close()

if __name__ == "__main__":
    main()
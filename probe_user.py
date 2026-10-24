from playwright.sync_api import sync_playwright
import os
import json

PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".playwright_profile")

# 把这里换成你复制的账号主页链接
USER_URL = "https://www.douyin.com/user/MS4wLjABAAAAhV40YlQOgJ3x4mO7jLPq5_6pu3NLsKhUwBLaSGQkz5ldPuPMkobGfv1ONZZEKTX-?from_tab_name=main"

def main():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1440, "height": 900},
        )

        captured = []

        def on_response(response):
            url = response.url
            if "/aweme/v1/web/aweme/post/" in url:
                try:
                    captured.append({"url": url, "body": response.json()})
                except Exception:
                    pass

        context.on("response", on_response)

        page = context.new_page()
        print("正在访问账号主页:", USER_URL)
        page.goto(USER_URL, wait_until="domcontentloaded", timeout=60000)

        print("\n" + "=" * 60)
        print("浏览器已打开。请确认账号主页的视频列表加载完毕，然后回终端按回车。")
        print("=" * 60)
        input("\n>>> 按回车继续...")

        page.wait_for_timeout(3000)

        print(f"\n共捕获 {len(captured)} 个 post 接口响应")
        if captured:
            # 保存完整响应（方便调试）
            with open("douyin_user_raw.json", "w", encoding="utf-8") as f:
                json.dump(captured, f, ensure_ascii=False, indent=2)
            print("完整响应已保存到 douyin_user_raw.json")

            # 只打印视频数量，不发完整内容
            first = captured[0]["body"]
            aweme_list = first.get("aweme_list", [])
            print(f"第一个接口返回的视频数量: {len(aweme_list)}")
            if aweme_list:
                sample = aweme_list[0]
                print("\n第一个视频的字段名（只看键，不看值）:")
                print(list(sample.keys())[:30])
        else:
            print("❌ 未捕获到 post 接口响应，可能需要滚动页面触发加载。")

        page.wait_for_timeout(5000)
        context.close()

if __name__ == "__main__":
    main()
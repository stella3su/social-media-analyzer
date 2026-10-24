from playwright.sync_api import sync_playwright

def main():
    # 启动 Playwright 上下文
    with sync_playwright() as p:
        # 启动 Chromium，headless=False 表示显示浏览器窗口
        browser = p.chromium.launch(headless=False)
        # 新建一个页面
        page = browser.new_page()
        # 打开测试网址
        page.goto("https://example.com")
        # 获取网页标题
        title = page.title()
        print("网页标题:", title)
        # 截图保存到当前项目目录
        page.screenshot(path="test_playwright.png")
        print("截图已保存: test_playwright.png")
        # 关闭浏览器
        browser.close()

if __name__ == "__main__":
    main()
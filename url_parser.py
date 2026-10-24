import re
import json
import requests

# 1. 把从小红书复制出来的整段分享文本，原样粘到这里
share_text = """90 【求秋招公司推荐 - 老公你说句话呀 | 小红书 - 你的生活兴趣社区】 😆 90r0EkF32WKG6gL 😆 https://www.xiaohongshu.com/discovery/item/6abba13b0000000012035250?source=web share&xhsshare=pc_web&xsec_token=AB_bxMJFSCH58XK9S7MQqk-aQidHS7fF0H09PYmnKdCqw=&xsec_source=pc_share"""

# 2. 用正则表达式，自动从分享文本里提取出以 http 开头的链接
match = re.search(r"https?://[^\s]+", share_text)
if not match:
    print("没有从文本里找到链接，请检查你粘贴的内容。")
    exit()

url = match.group(0)
print("提取到的链接是:", url)
print("-" * 50)

# 3. 模拟浏览器请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

# 4. 发送请求
response = requests.get(url, headers=headers, timeout=10)
print("状态码:", response.status_code)
print("页面长度:", len(response.text))
html = response.text

# 5. 探测所有 __INITIAL 相关的 JS 变量名
print("\n===== 探测所有 __INITIAL 变量名 =====")
init_vars = re.findall(r"window\.__[A-Z_]+__", html)
for v in set(init_vars):
    print("找到:", v)

# 6. 常见的笔记字段是否出现在 HTML 里
print("\n===== 常见字段关键词探测 =====")
keywords = ["noteDetail", "interactInfo", "likedCount", "collectedCount",
            "noteId", "desc", "tagList", "xsec_token"]
for kw in keywords:
    print(f"'{kw}':", kw in html)

# 7. 找找有没有 <script> 标签里塞了 JSON
print("\n===== 是否有 JSON 型 script 标签 =====")
script_blocks = re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
print("找到 JSON script 数量:", len(script_blocks))
if script_blocks:
    print("第一个 JSON block 前300字:")
    print(script_blocks[0][:300])

# 8. 看看 HTML 里有没有登录/验证相关的提示
print("\n===== 是否返回了登录/验证页 =====")
login_hints = ["请登录", "登录后", "验证", "captcha", "slide", "扫码"]
for hint in login_hints:
    print(f"'{hint}':", hint in html)
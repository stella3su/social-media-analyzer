import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. 加载 .env 文件里的环境变量
load_dotenv()

# 2. 读取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

# 3. 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 4. 发送测试消息
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "请回复：大模型连接成功！"}
    ]
)

# 5. 打印返回结果
print(response.choices[0].message.content)
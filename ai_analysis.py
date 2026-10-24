import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# 1. 加载环境变量和初始化客户端
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 2. 读取清洗后的 CSV 文件
df = pd.read_csv("competitor_notes_cleaned.csv", encoding="gbk")

# 3. 取出第一条笔记的数据
first_note = df.iloc[0]
title = str(first_note["title"])
content = str(first_note["content"])

# 4. 构造提示词（Prompt）
# 注意：我们在提示词里必须明确告诉 AI 要输出 JSON，并且把需要的字段列清楚
prompt = f"""
你是一名资深的新媒体内容运营专家。
请分析以下这篇小红书竞品笔记，并严格按照 JSON 格式输出分析结果。
需要包含以下 8 个字段：
- topic_type: 选题类型（例如：经验分享、避坑指南、干货教程、职场吐槽等）
- title_structure: 标题结构（例如：数字型、痛点型、对比型、悬念型等）
- pain_points: 用户痛点（一句话）
- content_format: 内容形式（图文或视频，如果无法判断可填未知）
- target_audience: 目标人群（例如：应届生、转行小白、职场人）
- emotion: 情绪特点（例如：焦虑、共鸣、鼓励、好奇）
- keywords: 关键词（提取 3-5 个词，放在一个列表里）
- highlights: 内容亮点（一句话）

笔记标题：{title}
笔记正文：{content}

请直接输出 JSON 格式，不要有任何多余的废话和 Markdown 标记。
"""

# 5. 调用大模型，并强制要求返回 JSON 格式
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": prompt}
    ],
    response_format={"type": "json_object"} # 强制 AI 输出标准 JSON
)

# 6. 打印大模型返回的原始结果
print("===== 大模型返回的原始 JSON =====")
result_json = response.choices[0].message.content
print(result_json)

# 7. 用 Python 解析 JSON，看看能不能提取出来
print("\n===== 解析后的字段 =====")
data = json.loads(result_json)
for key, value in data.items():
    print(f"{key}: {value}")

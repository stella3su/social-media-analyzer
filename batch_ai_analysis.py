import os
import json
import time
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# 1. 加载环境变量和初始化客户端
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 2. 读取清洗后的 CSV
df = pd.read_csv("competitor_notes_cleaned.csv", encoding="gbk")

# 3. 准备一个空列表，用来装所有分析结果
results = []

# 4. 循环遍历每一行数据
for index, row in df.iterrows():
    note_id = row["note_id"]
    title = str(row["title"])
    content = str(row["content"])

    print(f"正在分析第 {note_id} 条笔记...")

    prompt = f"""
    你是一名资深的新媒体内容运营专家。
    请分析以下这篇小红书竞品笔记，并严格按照 JSON 格式输出分析结果。
    需要包含以下 8 个字段：
    - topic_type: 选题类型
    - title_structure: 标题结构
    - pain_points: 用户痛点
    - content_format: 内容形式
    - target_audience: 目标人群
    - emotion: 情绪特点
    - keywords: 关键词（列表）
    - highlights: 内容亮点

    笔记标题：{title}
    笔记正文：{content}

    请直接输出 JSON 格式，不要有任何多余的废话和 Markdown 标记。
    """

    try:
        # 调用大模型
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        # 解析返回的 JSON
        ai_data = json.loads(response.choices[0].message.content)

        # 把原始数据（标题、点赞等）和 AI 分析结果合并成一个字典
        merged_data = {
            "note_id": note_id,
            "title": title,
            "likes": row["likes"],
            "total_interaction": row["likes"] + row["collects"] + row["comments"] + row["shares"],
            "topic_type": ai_data.get("topic_type", ""),
            "title_structure": ai_data.get("title_structure", ""),
            "pain_points": ai_data.get("pain_points", ""),
            "target_audience": ai_data.get("target_audience", ""),
            "emotion": ai_data.get("emotion", ""),
            "keywords": ",".join(ai_data.get("keywords", [])),
            "highlights": ai_data.get("highlights", "")
        }
        results.append(merged_data)

    except Exception as e:
        # 如果某条笔记分析失败，不中断程序，而是记录错误
        print(f"第 {note_id} 条分析失败，原因：{e}")
        # 把失败的数据也记下来，但 AI 字段留空
        results.append({
            "note_id": note_id, "title": title, "likes": row["likes"],
            "total_interaction": 0, "topic_type": "分析失败",
            "title_structure": "", "pain_points": "", "target_audience": "",
            "emotion": "", "keywords": "", "highlights": ""
        })

    # 每次请求后暂停 1 秒，避免触发 API 频率限制
    time.sleep(1)

# 5. 把结果列表转换成 DataFrame，并保存为新的 CSV
result_df = pd.DataFrame(results)
result_df.to_csv("ai_analysis_result.csv", index=False, encoding="gbk")

print("\n===== 全部笔记分析完成！ =====")
print(f"共分析 {len(result_df)} 条笔记，结果已保存到 ai_analysis_result.csv")
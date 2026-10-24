import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量和初始化客户端
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 确保 API Key 存在
if not api_key:
    print("警告：未找到 DEEPSEEK_API_KEY，请检查 .env 文件！")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def analyze_content_with_ai(title: str, content: str) -> dict:
    """
    接收标题和正文，调用 DeepSeek 进行结构化分析，返回字典。
    """
    prompt = f"""
    你是一名资深的新媒体内容运营专家。
    请分析以下这篇新媒体竞品作品（可能是小红书或抖音），并严格按照 JSON 格式输出分析结果。
    需要包含以下 8 个字段：
    - topic_type: 选题类型（例如：经验分享、避坑指南、干货教程等）
    - title_structure: 标题结构（例如：数字型、痛点型、对比型等）
    - pain_points: 用户痛点
    - content_format: 内容形式（图文或视频）
    - target_audience: 目标人群
    - emotion: 情绪特点
    - keywords: 关键词（列表格式）
    - highlights: 内容亮点

    作品标题：{title}
    作品正文/描述：{content}

    请直接输出 JSON 格式，不要有任何多余的废话和 Markdown 标记。
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7  # 保持一定的稳定性
        )

        # 解析返回的 JSON
        ai_data = json.loads(response.choices[0].message.content)

        # 规范化一下 keywords，如果是列表就转成字符串，方便展示
        if isinstance(ai_data.get("keywords"), list):
            ai_data["keywords"] = ", ".join(ai_data["keywords"])

        return ai_data

    except Exception as e:
        # 失败时返回带有 error 字段的字典
        return {"error": f"AI 分析失败: {str(e)}"}


if __name__ == "__main__":
    # 测试代码
    print("开始测试 AI 分析模块...")
    test_title = "能绷住的可以确诊抑郁症了 #时代少年团 #母婴 #癫 #疯"
    test_desc = "能绷住的可以确诊抑郁症了 #时代少年团 #母婴 #癫 #疯"

    result = analyze_content_with_ai(test_title, test_desc)
    print("\n===== AI 分析结果 =====")
    print(json.dumps(result, ensure_ascii=False, indent=2))
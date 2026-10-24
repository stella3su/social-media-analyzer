import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 1. 读取数据
df = pd.read_csv("ai_analysis_result.csv", encoding="gbk")
df_success = df[df["topic_type"] != "分析失败"].copy()
print(f"共载入有效分析数据 {len(df_success)} 条")

# ================= 归一化：把细碎标签合并成大类 =================
def standardize_audience(text):
    text = str(text)
    if "零经验" in text or "转行" in text or "小白" in text:
        return "零经验/转行求职者"
    elif "应届" in text or "校招" in text:
        return "应届生/校招群体"
    elif "新手" in text or "新人" in text or "0基础" in text:
        return "新手运营"
    else:
        return "其他职场人"

def standardize_emotion(text):
    text = str(text)
    if "焦虑" in text:
        return "缓解焦虑"
    elif "实用" in text or "干货" in text:
        return "实用/干货导向"
    elif "鼓励" in text or "共鸣" in text or "共情" in text:
        return "鼓励/共鸣"
    elif "自信" in text or "励志" in text:
        return "励志/自信"
    else:
        return "其他情绪"

def standardize_topic(text):
    text = str(text)
    if "求职" in text or "面试" in text or "简历" in text:
        return "求职面试干货"
    elif "技能" in text or "教学" in text or "教程" in text:
        return "技能教学"
    elif "经验分享" in text or "干货" in text:
        return "经验分享"
    else:
        return "职场综合"

df_success["standard_audience"] = df_success["target_audience"].apply(standardize_audience)
df_success["standard_emotion"] = df_success["emotion"].apply(standardize_emotion)
df_success["standard_topic"] = df_success["topic_type"].apply(standardize_topic)
# ===============================================================

# 2. 聚合统计
print("\n===== 【归一化后】不同选题类型的平均互动量 =====")
topic_group = df_success.groupby("standard_topic")["total_interaction"].mean().sort_values(ascending=False)
print(topic_group)

print("\n===== 【归一化后】目标人群分布 =====")
audience_group = df_success["standard_audience"].value_counts()
print(audience_group)

print("\n===== 【归一化后】情绪特点频次 =====")
emotion_group = df_success["standard_emotion"].value_counts()
print(emotion_group)

# 3. 画图（优化了尺寸、旋转角度和字号，解决重叠问题）
plt.figure(figsize=(10, 6))  # 把画布加宽
topic_group.plot(kind="bar", width=0.5) # 柱子稍微细一点
plt.title("不同选题类型的平均互动量对比（归一化后）", fontsize=14)
plt.ylabel("平均总互动量", fontsize=12)
plt.xticks(rotation=0, fontsize=12) # 归一化后类别变少，水平放就行
plt.tight_layout()
plt.savefig("ai_topic_bar.png")
print("\n图表已保存为 ai_topic_bar.png")
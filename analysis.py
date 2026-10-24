import pandas as pd
import matplotlib.pyplot as plt

# 设置中文，防止图片中文乱码
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

# 读取csv
df = pd.read_csv("competitor_notes.csv")

print("===== 数据概览 =====")
print(df.head())
print("\n===== 基础统计（点赞、收藏、评论、分享） =====")
print(df[["likes", "collects", "comments", "shares"]].describe())

# 按内容形式分组统计：图文 vs 视频
group_data = df.groupby("content_type")[["likes", "collects"]].mean()
print("\n===== 图文/视频平均点赞收藏对比 =====")
print(group_data)

# 绘制柱状图：图文视频平均点赞收藏
group_data.plot(kind="bar", figsize=(8,5))
plt.title("图文/视频笔记平均点赞&收藏对比")
plt.ylabel("数量")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("stat_bar.png")
plt.show()
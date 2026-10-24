import pandas as pd
from collections import Counter
import matplotlib
# 新增：指定后端，解决PyCharm的backend_interagg报错
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Windows黑体，解决中文显示
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 读取CSV，指定gbk编码
df = pd.read_csv("competitor_notes.csv", encoding="gbk")

all_tags = []
# 遍历tags列拆分标签
for tag_str in df["tags"]:
    # 空值跳过，防止报错
    if pd.isna(tag_str):
        continue
    tag_list = tag_str.split(",")
    for tag in tag_list:
        all_tags.append(tag.strip())

# 统计标签词频
tag_count = Counter(all_tags)
print("===== 标签词频统计 =====")
for tag, cnt in tag_count.most_common():
    print(f"{tag} : {cnt}")

# 绘制TOP8高频标签柱状图
top_tags = dict(tag_count.most_common(8))
plt.figure(figsize=(9, 5))
plt.bar(top_tags.keys(), top_tags.values())
plt.title("笔记高频标签TOP8")
plt.ylabel("出现次数")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("tag_wordcount.png")
# 删掉 plt.show()，不再弹窗，图片直接保存到项目文件夹

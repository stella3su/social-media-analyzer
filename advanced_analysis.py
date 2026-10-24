import pandas as pd

# 1. 读取CSV，加encoding防止报错
df = pd.read_csv("competitor_notes.csv", encoding="gbk")

# 2. 一键修复标签逗号问题（把中文逗号替换成英文逗号）
df["tags"] = df["tags"].astype(str).str.replace("，", ",")

# 3. 自动清洗：把点赞、收藏、评论、分享列里的“脏数据”转成纯数字
num_cols = ["likes", "collects", "comments", "shares"]
for col in num_cols:
    # 先转成字符串，去掉里面可能混入的空格
    df[col] = df[col].astype(str).str.strip()
    # 把“1.2万”这种格式自动换算成 12000
    df[col] = df[col].str.replace("万", "0000", regex=False)
    # 强制转成数字。凡是转不了的（比如"1900/1/0"、"无"），一律变成 0
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# 4. 安全地计算总互动量
df["total_interaction"] = df["likes"] + df["collects"] + df["comments"] + df["shares"]

# 5. 按总互动量，从大到小排序
df = df.sort_values(by="total_interaction", ascending=False)

# 6. 提取前 30% 的数据（30条数据的前 30% 就是前 9 条）
top_n = int(len(df) * 0.3)
if top_n < 1: top_n = 1
top_notes = df.head(top_n)

# 7. 打印高互动笔记的核心信息
print(f"===== 高互动 Top {top_n} 笔记详情 =====")
for index, row in top_notes.iterrows():
    print(f"标题: {row['title']}")
    print(f"互动总量: {row['total_interaction']}")
    print(f"内容形式: {row['content_type']}")
    print(f"标签: {row['tags']}")
    print("-" * 30)

# 8. 存一份清洗过的新文件，给下一步 AI 分析用
df.to_csv("competitor_notes_cleaned.csv", index=False, encoding="gbk")
print("已生成清理后的文件: competitor_notes_cleaned.csv")
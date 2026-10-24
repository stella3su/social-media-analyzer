import pandas as pd
import os
import json
from datetime import datetime

# 统一的字段结构
COLUMNS = [
    "platform", "content_id", "content_type", "author",
    "title", "description", "likes", "comments",
    "favorites", "shares", "publish_time", "url"
]


def process_xhs():
    """处理小红书数据"""
    print("正在读取小红书数据...")
    df = pd.read_csv("competitor_notes.csv", encoding="gbk")

    # 映射字段
    unified = pd.DataFrame()
    unified["platform"] = ["xiaohongshu"] * len(df)
    unified["content_id"] = df["note_id"].astype(str)
    unified["content_type"] = df["content_type"]
    unified["author"] = "未知作者"  # 原来的 V1 数据没有作者字段
    unified["title"] = df["title"]
    unified["description"] = df["content"]
    unified["likes"] = pd.to_numeric(df["likes"], errors="coerce")
    unified["comments"] = pd.to_numeric(df["comments"], errors="coerce")
    unified["favorites"] = pd.to_numeric(df["collects"], errors="coerce")
    unified["shares"] = pd.to_numeric(df["shares"], errors="coerce")
    unified["publish_time"] = df["publish_time"]
    unified["url"] = "无"  # V1 数据没有链接

    return unified


def process_douyin():
    """处理抖音数据"""
    print("正在读取抖音数据...")
    df = pd.read_csv("douyin_user_notes.csv", encoding="utf-8-sig")

    # 映射字段
    unified = pd.DataFrame()
    unified["platform"] = ["douyin"] * len(df)
    unified["content_id"] = df["aweme_id"].astype(str)
    unified["content_type"] = "视频"  # 抖音默认都是视频
    unified["author"] = df["author"]
    unified["title"] = df["title_summary"]
    unified["description"] = df["description"]
    unified["likes"] = pd.to_numeric(df["likes"], errors="coerce")
    unified["comments"] = pd.to_numeric(df["comments"], errors="coerce")
    unified["favorites"] = pd.to_numeric(df["favorites"], errors="coerce")
    unified["shares"] = pd.to_numeric(df["shares"], errors="coerce")
    unified["publish_time"] = df["publish_time"]
    unified["url"] = df["video_url"]

    return unified


def main():
    # 1. 读取并映射两个平台
    df_xhs = process_xhs()
    df_dy = process_douyin()

    # 2. 合并
    print("正在合并数据...")
    merged = pd.concat([df_xhs, df_dy], ignore_index=True)

    # 3. 确保列顺序正确
    merged = merged[COLUMNS]

    # 4. 保存
    output_file = "unified_notes.csv"
    merged.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"\n✅ 合并完成！共 {len(merged)} 条数据。")
    print(f"📁 已保存至: {output_file}")

    # 打印前 5 行预览
    print("\n===== 合并后数据前 5 行预览 =====")
    print(merged[["platform", "content_id", "likes", "favorites", "publish_time"]].head())


if __name__ == "__main__":
    main()
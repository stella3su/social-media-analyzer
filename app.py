import streamlit as st
import asyncio
import plotly.graph_objects as go
import os
import subprocess
from dotenv import load_dotenv
from collectors import fetch_douyin_data, fetch_xiaohongshu_data
from analyzer import analyze_content_with_ai


@st.cache_resource
def install_playwright_browser():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except:
        pass


install_playwright_browser()
load_dotenv()

try:
    if "DEEPSEEK_API_KEY" in st.secrets:
        os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]
except:
    pass

# ================= 修改了这里的标题 =================
st.set_page_config(page_title="新媒体内容智能分析系统", page_icon="📊", layout="wide")
st.title("📊 新媒体内容智能分析系统")
st.markdown("粘贴链接，一键获取作品数据并生成 AI 深度分析报告。")
# ====================================================

# 初始化状态
if "raw_data" not in st.session_state:
    st.session_state.raw_data = None
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

with st.sidebar:
    st.header("平台选择")
    platform = st.radio("请选择平台：", ["抖音", "小红书"], index=0)
    st.info("💡 提示：小红书受限于平台强风控，推荐填写下方表单以确保分析准确。")

url_input = st.text_area("🔗 请输入作品分享链接或完整分享文本：", height=100, placeholder="例如：4.10 j@C.uF... https://v.douyin.com/...")

if st.button("🚀 开始分析", type="primary"):
    if not url_input:
        st.warning("请先输入内容或链接！")
    else:
        # 重置状态
        st.session_state.raw_data = None
        st.session_state.ai_result = None

        if platform == "抖音":
            with st.spinner("正在采集抖音数据（约 15 秒）..."):
                raw_data = asyncio.run(fetch_douyin_data(url_input, headless=True))
                if "error" in raw_data:
                    st.error(f"采集失败：{raw_data['error']}")
                else:
                    st.session_state.raw_data = raw_data
                    st.success("✅ 抖音数据采集成功！")
        elif platform == "小红书":
            # 小红书直接进入表单模式，保证体验绝对可用
            st.session_state.raw_data = {
                "platform": "xiaohongshu", "aweme_id": "manual", "author": "手动输入",
                "title": "", "description": "", "likes": 0, "comments": 0,
                "favorites": 0, "shares": 0, "publish_time": "未知", "video_url": url_input
            }
            st.success("✅ 请填写下方信息：")

# =============== 小红书强制表单区 ===============
if st.session_state.raw_data and st.session_state.raw_data.get("platform") == "xiaohongshu":
    with st.form("manual_input_form"):
        st.warning("⚠️ 请粘贴或补充以下真实数据，AI 分析将基于此生成：")

        new_title = st.text_input("作品标题", value=st.session_state.raw_data.get("title", ""))
        new_desc = st.text_area("作品文案（必填）", value=st.session_state.raw_data.get("description", ""), height=100)

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        new_likes = col_m1.number_input("点赞量", min_value=0, value=int(st.session_state.raw_data.get("likes", 0)))
        new_comments = col_m2.number_input("评论量", min_value=0, value=int(st.session_state.raw_data.get("comments", 0)))
        new_favorites = col_m3.number_input("收藏量", min_value=0,
                                            value=int(st.session_state.raw_data.get("favorites", 0)))
        new_shares = col_m4.number_input("分享量", min_value=0, value=int(st.session_state.raw_data.get("shares", 0)))

        submit_btn = st.form_submit_button("确认数据并生成 AI 洞察", type="primary")
        if submit_btn:
            st.session_state.raw_data["title"] = new_title
            st.session_state.raw_data["description"] = new_desc
            st.session_state.raw_data["likes"] = new_likes
            st.session_state.raw_data["comments"] = new_comments
            st.session_state.raw_data["favorites"] = new_favorites
            st.session_state.raw_data["shares"] = new_shares
            st.rerun()

# =============== 展示与 AI 分析区 ===============
if st.session_state.raw_data:
    raw_data = st.session_state.raw_data

    # 只有当文案不为空时，才展示图表和 AI 结果
    if raw_data.get("description"):
        st.subheader("📌 作品基础数据")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("点赞量", raw_data.get("likes"))
        col2.metric("评论量", raw_data.get("comments"))
        col3.metric("收藏量", raw_data.get("favorites"))
        col4.metric("分享量", raw_data.get("shares"))

        st.write(f"**文案：** {raw_data.get('description')}")

        st.markdown("##### 📈 互动数据占比分析")
        metrics = {
            "点赞": raw_data.get("likes") or 0, "评论": raw_data.get("comments") or 0,
            "收藏": raw_data.get("favorites") or 0, "分享": raw_data.get("shares") or 0
        }
        if sum(metrics.values()) > 0:
            fig = go.Figure(data=[go.Pie(labels=list(metrics.keys()), values=list(metrics.values()), hole=.4)])
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        if not st.session_state.ai_result:
            with st.spinner("正在调用 AI 进行深度分析..."):
                ai_result = analyze_content_with_ai(
                    title=raw_data.get("title", ""), content=raw_data.get("description", "")
                )
                st.session_state.ai_result = ai_result

        if "error" in st.session_state.ai_result:
            st.error(f"AI 分析失败：{st.session_state.ai_result['error']}")
        else:
            st.success("✅ AI 分析完成！")
            st.subheader("🧠 AI 深度内容洞察")
            ai_result = st.session_state.ai_result
            col_left, col_right = st.columns(2)
            with col_left:
                st.info(f"**🎯 选题类型：** {ai_result.get('topic_type', '无')}")
                st.info(f"**📝 标题结构：** {ai_result.get('title_structure', '无')}")
                st.info(f"**👥 目标受众：** {ai_result.get('target_audience', '无')}")
                st.info(f"**🎭 情绪特点：** {ai_result.get('emotion', '无')}")
            with col_right:
                st.warning(f"**💔 用户痛点：** {ai_result.get('pain_points', '无')}")
                st.success(f"**✨ 内容亮点：** {ai_result.get('highlights', '无')}")
                st.info(f"**🏷️ 关键词：** {ai_result.get('keywords', '无')}")

            st.divider()

            st.subheader("📥 导出分析报告")
            report_md = f"""# 新媒体内容分析报告

## 一、 作品基础数据
- **平台**: {raw_data.get('platform')}
- **文案**: {raw_data.get('description')}

**数据表现**: 点赞 {metrics['点赞']} | 评论 {metrics['评论']} | 收藏 {metrics['收藏']} | 分享 {metrics['分享']}

## 二、 AI 深度内容洞察
- **选题类型**: {ai_result.get('topic_type', '无')}
- **标题结构**: {ai_result.get('title_structure', '无')}
- **用户痛点**: {ai_result.get('pain_points', '无')}
- **内容亮点**: {ai_result.get('highlights', '无')}
"""
            st.download_button(
                label="📄 下载 Markdown 分析报告", data=report_md,
                file_name=f"内容分析报告_{raw_data.get('aweme_id', '未知')}.md", mime="text/markdown"
            )
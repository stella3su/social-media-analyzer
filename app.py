import streamlit as st
import asyncio
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from collectors import fetch_douyin_data
from analyzer import analyze_content_with_ai

# 1. 本地运行：加载 .env 文件
load_dotenv()

# 2. 云端运行：从 Streamlit Secrets 读取密钥并注入到环境变量中
if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

# 1. 页面基础设置
st.set_page_config(page_title="竞品内容智能分析系统", page_icon="📊", layout="wide")
st.title("📊 新媒体竞品内容智能分析系统")
st.markdown("粘贴抖音链接，一键获取作品数据并生成 AI 深度分析报告。")

# 2. 侧边栏
with st.sidebar:
    st.header("平台选择")
    platform = st.radio("请选择平台：", ["抖音", "小红书 (暂未开放)"], index=0)
    st.info("💡 提示：支持直接粘贴抖音 App 的整段分享文本。")

# 3. 主界面输入区
url_input = st.text_area("🔗 请输入作品分享链接或完整分享文本：", height=100, placeholder="例如：4.10 j@C.uF... https://v.douyin.com/...")

if st.button("🚀 开始分析", type="primary"):
    if not url_input:
        st.warning("请先输入作品链接！")
    elif platform == "小红书 (暂未开放)":
        st.error("小红书模块正在开发中。")
    else:
        # =============== 阶段 1：采集 ===============
        with st.spinner("正在启动浏览器采集数据（约 10 秒）..."):
            raw_data = asyncio.run(fetch_douyin_data(url_input, headless=True))

        if "error" in raw_data:
            st.error(f"采集失败：{raw_data['error']}")
            st.stop()

        st.success("✅ 数据采集成功！")

        # --- 数据展示区 ---
        st.subheader("📌 作品基础数据")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("点赞量", raw_data.get("likes", "无"))
        col2.metric("评论量", raw_data.get("comments", "无"))
        col3.metric("收藏量", raw_data.get("favorites", "无"))
        col4.metric("分享量", raw_data.get("shares", "无"))

        st.write(f"**作者：** {raw_data.get('author')} | **发布时间：** {raw_data.get('publish_time')}")
        st.write(f"**文案：** {raw_data.get('description')}")

        # --- 图表展示区 ---
        st.markdown("##### 📈 互动数据占比分析")
        metrics = {
            "点赞": raw_data.get("likes") or 0,
            "评论": raw_data.get("comments") or 0,
            "收藏": raw_data.get("favorites") or 0,
            "分享": raw_data.get("shares") or 0
        }
        # 只有当有数据时才画图
        if sum(metrics.values()) > 0:
            fig = go.Figure(data=[go.Pie(labels=list(metrics.keys()), values=list(metrics.values()), hole=.4)])
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无互动数据，无法生成图表。")

        st.divider()

        # =============== 阶段 2：AI 分析 ===============
        with st.spinner("正在调用 AI 进行深度分析..."):
            ai_result = analyze_content_with_ai(
                title=raw_data.get("title", ""),
                content=raw_data.get("description", "")
            )

        if "error" in ai_result:
            st.error(f"AI 分析失败：{ai_result['error']}")
            st.stop()

        st.success("✅ AI 分析完成！")

        st.subheader("🧠 AI 深度内容洞察")
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

        # =============== 阶段 3：报告导出 ===============
        st.subheader("📥 导出分析报告")

        report_md = f"""# 新媒体竞品分析报告

## 一、 作品基础数据
- **平台**: {raw_data.get('platform')}
- **作者**: {raw_data.get('author')}
- **发布时间**: {raw_data.get('publish_time')}
- **链接**: {raw_data.get('video_url')}
- **文案**: {raw_data.get('description')}

**数据表现**: 点赞 {metrics['点赞']} | 评论 {metrics['评论']} | 收藏 {metrics['收藏']} | 分享 {metrics['分享']}

## 二、 AI 深度内容洞察
- **选题类型**: {ai_result.get('topic_type', '无')}
- **标题结构**: {ai_result.get('title_structure', '无')}
- **目标受众**: {ai_result.get('target_audience', '无')}
- **情绪特点**: {ai_result.get('emotion', '无')}
- **关键词**: {ai_result.get('keywords', '无')}

### 用户痛点
{ai_result.get('pain_points', '无')}

### 内容亮点
{ai_result.get('highlights', '无')}
"""
        st.download_button(
            label="📄 下载 Markdown 分析报告",
            data=report_md,
            file_name=f"竞品分析报告_{raw_data.get('aweme_id', '未知')}.md",
            mime="text/markdown"
        )
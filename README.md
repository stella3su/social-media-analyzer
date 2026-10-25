# 社交媒体内容智能分析系统

## 项目简介

本项目是一款面向新媒体内容运营场景的竞品分析工具，支持抖音内容数据采集及小红书内容分析辅助录入，通过 AI 对内容主题、标题结构、用户痛点、目标受众、情绪倾向、关键词和内容亮点进行结构化分析，并生成可视化图表与 Markdown 分析报告。

项目旨在帮助内容运营人员提高竞品研究效率，为选题策划、标题优化和内容策略调整提供参考。

## 核心功能

- **双平台分析入口**：支持抖音与小红书两类内容分析场景。
- **内容数据采集**：通过 Playwright 获取抖音公开内容信息；小红书支持手动补充内容文本及互动数据。
- **AI 内容分析**：调用 DeepSeek API，从七个维度提取内容特征与运营洞察。
- **数据可视化**：使用 Plotly 展示互动数据及相关指标。
- **报告导出**：支持生成 Markdown 格式的分析报告。
- **交互式界面**：基于 Streamlit 构建，支持在本地浏览器中操作。

## 技术栈

| 技术 | 应用场景 |
|---|---|
| Python | 核心开发语言 |
| Streamlit | Web 交互界面 |
| Playwright | 浏览器自动化与网页数据采集 |
| DeepSeek API | AI 内容分析 |
| Pandas | 数据处理 |
| Plotly | 数据可视化 |

## AI 分析维度

1. 内容主题类型
2. 标题结构与表达方式
3. 用户痛点
4. 目标受众
5. 情绪倾向
6. 关键词提取
7. 内容亮点与运营启示

## 本地运行

### 1. 获取项目

```bash
git clone https://github.com/stella3su/social-media-analyzer.git
cd social-media-analyzer
```

### 2. 安装依赖

建议使用 Python 3.9 或兼容版本，并创建虚拟环境。

```bash
python -m venv .venv
```

Windows：

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 3. 配置 API Key

在项目根目录创建 `.env` 文件，填写：

```env
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
```

请勿将 `.env` 或真实 API Key 上传至公开仓库。

### 4. 启动应用

```bash
streamlit run app.py
```

浏览器打开终端显示的本地访问地址，通常为 `http://localhost:8501`。

## 项目说明与限制

- 抖音数据采集依赖网页结构、登录状态及平台访问策略，采集结果可能受页面变化影响。
- 小红书当前采用手动补充内容和互动数据的方式完成分析流程，不代表已实现稳定的自动化采集。
- AI 输出为辅助分析结果，实际运营决策仍需结合账号定位、平台规则及人工判断。
- 使用本项目时应遵守相关平台规则，并仅处理有权访问和使用的数据。

## 项目价值

本项目将浏览器自动化、数据处理、AI 结构化分析、数据可视化与报告生成整合为完整的内容分析流程，体现了 Python 应用开发、第三方 API 集成及新媒体运营分析的综合实践能力。

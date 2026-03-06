# ⚡ AI 资讯聚合

> 一个轻量级本地 AI 资讯聚合工具，自动从国内外多个来源抓取最新 AI 资讯，通过大模型生成中文摘要和智能分类，在浏览器中一站式阅读。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ 功能特性

- 🌐 **多源聚合** — 内置 12+ 个中英文 RSS 源 + Hacker News API
- 🤖 **AI 摘要** — 通过 Qwen 大模型自动生成中文摘要
- 🏷️ **智能分类** — 自动分为：大模型 / AI应用 / 论文 / 行业动态 / 开源
- 🔍 **搜索筛选** — 支持关键词搜索、分类筛选、中英文切换
- ⏰ **定时更新** — 每 30 分钟自动抓取最新资讯
- 🌙 **深色主题** — 毛玻璃卡片 + 渐变配色 + 微动画

## 📸 界面预览

启动后访问 `http://127.0.0.1:8000`：

```
┌──────────────────────────────────────────────┐
│ ⚡ AI 资讯聚合  [LIVE]        🔍 搜索...  🔄 │
├──────────────────────────────────────────────┤
│ 185 总文章  97 今日新增  120 未读  12 来源    │
├────────┬─────────────────────────────────────┤
│ 分类    │  InfoQ中国  中文          43分钟前  │
│ 📋 全部  │  微软发布 Agent Framework...      │
│ 🧠 大模型│  AI: 微软推出Agent开发框架...      │
│ 🚀 AI应用│                                   │
│ 📄 论文  │  Hacker News  EN          2小时前  │
│ 📊 行业  │  Large-Scale Agentic RL for...    │
│ 💻 开源  │  AI: 大规模强化学习方法用于...      │
│         │               ...                  │
│ 语言    │                                     │
│ [全部]   │  ‹ 1 2 3 ... 10 ›                 │
│ [中文]   │                                    │
│ [EN]    │                                     │
└────────┴─────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装

```bash
# 克隆/进入项目目录
cd d:\Desktop\资讯收集

# 安装依赖
pip install -r requirements.txt
```

### 配置

编辑 `config.py`，填写你的 LLM API 信息：

```python
# 当前使用 ModelScope（魔搭）API
LLM_BASE_URL = "https://api-inference.modelscope.cn/v1"
LLM_API_KEY = "你的 ModelScope Token"
LLM_MODEL = "Qwen/Qwen3.5-35B-A3B"
```

也可以替换为其他 OpenAI 兼容的 API（如 DeepSeek、硅基流动、NVIDIA NIM 等），只需修改以上三项即可。

### 启动

**方式一：双击 bat 文件（推荐）**

- `1-启动服务.bat` — 启动服务并自动打开浏览器
- `2-停止服务.bat` — 关闭服务

**方式二：命令行**

```bash
python app.py
# 访问 http://127.0.0.1:8000
```

## 📁 项目结构

```
资讯收集/
├── app.py                  # FastAPI 主应用 & 启动入口
├── config.py               # 配置文件（API、RSS源、抓取频率）
├── database.py             # SQLite 数据库操作
├── requirements.txt        # Python 依赖
├── 1-启动服务.bat           # 快捷启动
├── 2-停止服务.bat           # 快捷停止
├── fetchers/
│   ├── rss_fetcher.py      # RSS 并发抓取
│   └── hn_fetcher.py       # Hacker News 抓取
├── services/
│   └── ai_summary.py       # AI 摘要 & 分类生成
└── static/
    ├── index.html           # 主页面
    ├── style.css            # 深色主题样式
    └── app.js               # 前端交互逻辑
```

## 📡 内置数据源

| 来源 | 语言 | 类型 |
|------|------|------|
| 机器之心 | 中文 | RSS |
| 量子位 | 中文 | RSS |
| 36氪 | 中文 | RSS |
| InfoQ 中国 | 中文 | RSS |
| TechCrunch AI | 英文 | RSS |
| The Verge AI | 英文 | RSS |
| MIT Technology Review | 英文 | RSS |
| Ars Technica | 英文 | RSS |
| OpenAI Blog | 英文 | RSS |
| Google AI Blog | 英文 | RSS |
| VentureBeat AI | 英文 | RSS |
| Towards AI | 英文 | RSS |
| Hacker News | 英文 | API |

在 `config.py` 的 `RSS_SOURCES` 列表中添加或删除源即可自定义。

## ⚙️ 配置说明

`config.py` 中的主要配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `LLM_BASE_URL` | ModelScope API | LLM 接口地址 |
| `LLM_MODEL` | `Qwen/Qwen3.5-35B-A3B` | 模型名称 |
| `LLM_SUMMARY_DELAY` | `3.0` | 摘要请求间隔（秒） |
| `FETCH_INTERVAL_MINUTES` | `30` | 自动抓取间隔（分钟） |
| `REQUEST_TIMEOUT` | `15` | 单个请求超时（秒） |
| `MAX_ARTICLES_PER_SOURCE` | `20` | 每源最大文章数 |
| `HOST` | `127.0.0.1` | 服务地址 |
| `PORT` | `8000` | 服务端口 |

## 🔌 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 主页面 |
| `GET` | `/api/articles` | 文章列表（支持 `page`、`category`、`language`、`search` 参数） |
| `GET` | `/api/articles/{id}` | 单篇文章详情 |
| `POST` | `/api/articles/{id}/read` | 标记已读 |
| `POST` | `/api/fetch` | 手动触发抓取 |
| `GET` | `/api/stats` | 统计数据 |

## 🛠️ 技术栈

- **后端**: Python + FastAPI + uvicorn
- **数据库**: SQLite (aiosqlite)
- **抓取**: feedparser + httpx + Hacker News Firebase API
- **定时任务**: APScheduler
- **AI 摘要**: OpenAI SDK（兼容 ModelScope / NVIDIA NIM / DeepSeek 等）
- **前端**: HTML + CSS + Vanilla JS（无框架依赖）

## 📄 License

MIT

---

## 🗂️ Git 版本管理

项目已内置 `.gitignore`，以下文件**不会**被提交到仓库：

| 文件 / 目录 | 原因 |
|---|---|
| `config.py` | 含真实 API Key，敏感信息 |
| `*.db` | 本地数据库，体积大且无需共享 |
| `__pycache__/` | Python 编译缓存 |
| `.venv/` / `venv/` | 虚拟环境 |
| `*.log` | 运行日志 |

### 初始化仓库

```bash
git init
git add .
git commit -m "init: AI 资讯聚合工具"
```

### 新成员快速上手

```bash
git clone <仓库地址>
cd 资讯收集

# 1. 从模板创建配置文件
cp config.example.py config.py
# 编辑 config.py，填写自己的 API Key

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python app.py
# 访问 http://127.0.0.1:8000
```

"""
AI 资讯聚合工具 - 配置模板
复制此文件为 config.py 后，配置环境变量 LLM_API_KEY 再启动服务。
"""
import os

# ===================== LLM API 配置 =====================
# 支持任何 OpenAI 兼容 API，常见选项：
#   ModelScope（魔搭）: https://api-inference.modelscope.cn/v1
#   DeepSeek:          https://api.deepseek.com/v1
#   硅基流动:           https://api.siliconflow.cn/v1
#   NVIDIA NIM:        https://integrate.api.nvidia.com/v1
#
# 运行前请先设置环境变量（Windows PowerShell 示例）：
#   临时（当前终端）：$env:LLM_API_KEY="你的真实API Key"
#   永久（当前用户）：setx LLM_API_KEY "你的真实API Key"

LLM_BASE_URL = "https://api-inference.modelscope.cn/v1"
LLM_API_KEY  = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL    = "Qwen/Qwen3.5-35B-A3B"   # 替换为你所用 API 支持的模型名称
LLM_MAX_TOKENS    = 300      # AI 摘要最大 token 数（勿设太大）
LLM_SUMMARY_DELAY = 3.0      # 每篇文章生成摘要的间隔秒数，防止触发限速

# ===================== 抓取配置 =====================
FETCH_INTERVAL_MINUTES   = 30   # 定时抓取间隔（分钟）
REQUEST_TIMEOUT          = 15   # 单个 HTTP 请求超时时间（秒）
MAX_ARTICLES_PER_SOURCE  = 20   # 每个来源最多抓取的文章数

# ===================== 数据库配置 =====================
# 默认存储在项目根目录下的 ai_news.db，无需修改
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "ai_news.db")

# ===================== 服务配置 =====================
HOST = "127.0.0.1"   # 监听地址，本地使用无需修改
PORT = 8000          # 监听端口，如有冲突可更改

# ===================== RSS 源列表 =====================
# filter_ai: True  = 综合媒体，通过关键词过滤只保留 AI 相关文章
#            False = AI 专属媒体，全量收录

RSS_SOURCES = [
    # —— 中文来源 ——
    {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/rss",
        "language": "zh",
        "filter_ai": False,
    },
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "language": "zh",
        "filter_ai": False,
    },
    {
        "name": "36氪",
        "url": "https://36kr.com/feed",
        "language": "zh",
        "filter_ai": True,
    },
    {
        "name": "InfoQ中国",
        "url": "https://www.infoq.cn/feed",
        "language": "zh",
        "filter_ai": True,
    },
    # —— 英文来源 ——
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "language": "en",
        "filter_ai": False,
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "language": "en",
        "filter_ai": False,
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "language": "en",
        "filter_ai": True,
    },
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "language": "en",
        "filter_ai": True,
    },
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "language": "en",
        "filter_ai": False,
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "language": "en",
        "filter_ai": False,
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "language": "en",
        "filter_ai": False,
    },
    {
        "name": "Towards AI",
        "url": "https://pub.towardsai.net/feed",
        "language": "en",
        "filter_ai": False,
    },
    # —— 自定义来源（在此添加更多 RSS 源）——
    # {
    #     "name": "你的来源名称",
    #     "url": "https://example.com/feed.xml",
    #     "language": "zh",    # zh 或 en
    #     "filter_ai": True,   # 综合媒体设 True，AI 专属设 False
    # },
]

# ===================== AI 过滤关键词 =====================
# 综合媒体（filter_ai=True）的文章标题或内容含以下任一关键词才会入库
RSS_AI_KEYWORDS = [
    # 英文
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "llm", "gpt", "openai", "anthropic", "claude", "gemini", "mistral",
    "neural network", "transformer", "diffusion", "stable diffusion",
    "midjourney", "chatbot", "copilot", "agent", "rag",
    "fine-tuning", "fine tuning", "langchain", "hugging face",
    "deepseek", "qwen", "llama", "sora", "dall-e", "dalle",
    "generative", "foundation model", "multimodal", "embedding",
    "inference", "gpu cluster", "nvidia ai", "large language",
    # 中文
    "人工智能", "机器学习", "深度学习", "大模型", "语言模型",
    "神经网络", "生成式", "智能体", "推理", "训练",
    "向量模型", "嵌入向量", "强化学习", "多模态",
    "大规模", "基础模型", "微调", "提示词", "智能对话",
    "ai应用", "ai模型", "ai工具", "ai芯片", "ai发展",
    "智能化", "智慧城市", "智慧制造", "智慧医疗",
    "chatgpt", "claude", "deepseek", "qwen", "kimi", "wenxin", "文心", "通义千问",
]

# HN 关键词复用以上列表
HN_AI_KEYWORDS = RSS_AI_KEYWORDS

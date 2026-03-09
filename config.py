"""
AI 资讯聚合工具 - 配置文件
"""
import os

# ===================== LLM API 配置 =====================
LLM_BASE_URL = "https://api-inference.modelscope.cn/v1"
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = "Qwen/Qwen3.5-35B-A3B"
LLM_MAX_TOKENS = 300
LLM_SUMMARY_DELAY = 3.0  # 每篇文章间的延迟（秒），避免请求过快

# ===================== 抓取配置 =====================
FETCH_INTERVAL_MINUTES = 30  # 定时抓取间隔（分钟）
REQUEST_TIMEOUT = 15  # 单个请求超时时间（秒）
MAX_ARTICLES_PER_SOURCE = 20  # 每个来源最多抓取的文章数

# ===================== 数据库配置 =====================
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "ai_news.db")

# ===================== 服务配置 =====================
HOST = "127.0.0.1"
PORT = 8000

# ===================== RSS 源列表 =====================
RSS_SOURCES = [
    # —— 中文来源 ——
    {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/rss",
        "language": "zh",
        "filter_ai": False,   # 专注 AI，全量收录
    },
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "language": "zh",
        "filter_ai": False,   # 专注 AI，全量收录
    },
    {
        "name": "36氪",
        "url": "https://36kr.com/feed",
        "language": "zh",
        "filter_ai": True,    # 综合科技媒体，需过滤
    },
    {
        "name": "InfoQ中国",
        "url": "https://www.infoq.cn/feed",
        "language": "zh",
        "filter_ai": True,    # 综合科技媒体，需过滤
    },
    # —— 英文来源 ——
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "language": "en",
        "filter_ai": False,   # AI 专栏，全量收录
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "language": "en",
        "filter_ai": False,   # AI 专栏，全量收录
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "language": "en",
        "filter_ai": True,    # 综合科技媒体，需过滤
    },
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "language": "en",
        "filter_ai": True,    # 综合科技媒体，需过滤
    },
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "language": "en",
        "filter_ai": False,   # 专注 AI，全量收录
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "language": "en",
        "filter_ai": False,   # 专注 AI，全量收录
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "language": "en",
        "filter_ai": False,   # AI 专栏，全量收录
    },
    {
        "name": "Towards AI",
        "url": "https://pub.towardsai.net/feed",
        "language": "en",
        "filter_ai": False,   # 专注 AI，全量收录
    },
]

# RSS 过滤关键词（中英文，用于综合媒体的 AI 相关性判断）
RSS_AI_KEYWORDS = [
    # 英文关键词
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "llm", "gpt", "openai", "anthropic", "claude", "gemini", "mistral",
    "neural network", "transformer", "diffusion", "stable diffusion",
    "midjourney", "chatbot", "copilot", "agent", "rag",
    "fine-tuning", "fine tuning", "langchain", "hugging face",
    "deepseek", "qwen", "llama", "sora", "dall-e", "dalle",
    "generative", "foundation model", "multimodal", "embedding",
    "inference", "gpu cluster", "nvidia ai", "large language",
    # 中文关键词
    "人工智能", "机器学习", "深度学习", "大模型", "语言模型",
    "神经网络", "生成式", "智能体", "推理", "训练",
    "向量模型", "嵌入向量", "强化学习", "多模态",
    "大规模", "基础模型", "微调", "提示词", "智能对话",
    "ai应用", "ai模型", "ai工具", "ai芯片", "ai发展",
    "智能化", "智慧城市", "智慧制造", "智慧医疗", "智慧别",
    "chatgpt", "claude", "deepseek", "qwen", "kimi", "wenxin", "文心", "通義千问",
]

# HN 过滤关键词（舍弃，快捷引用 RSS_AI_KEYWORDS）
HN_AI_KEYWORDS = RSS_AI_KEYWORDS


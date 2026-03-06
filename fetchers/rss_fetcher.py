"""
AI 资讯聚合工具 - RSS 源抓取模块
"""
import asyncio
import re
from datetime import datetime
from html import unescape

import feedparser
import httpx

import config


def _is_ai_related(title: str, content: str = "") -> bool:
    """检查标题或内容是否与 AI 相关（中英文关键词）"""
    text = (title + " " + content).lower()
    return any(kw in text for kw in config.RSS_AI_KEYWORDS)


def _clean_html(text: str) -> str:
    """去除 HTML 标签，保留纯文本"""
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _parse_date(entry) -> str | None:
    """从 feedparser entry 中提取发布时间"""
    for attr in ("published_parsed", "updated_parsed"):
        time_struct = getattr(entry, attr, None)
        if time_struct:
            try:
                dt = datetime(*time_struct[:6])
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
    # 尝试直接解析字符串
    for attr in ("published", "updated"):
        date_str = getattr(entry, attr, None)
        if date_str:
            return date_str[:19]  # 粗略截取
    return None


async def fetch_single_rss(source: dict, client: httpx.AsyncClient) -> list[dict]:
    """抓取单个 RSS 源"""
    articles = []
    try:
        response = await client.get(
            source["url"],
            timeout=config.REQUEST_TIMEOUT,
            follow_redirects=True,
        )
        response.raise_for_status()
        feed = feedparser.parse(response.text)

        for entry in feed.entries[: config.MAX_ARTICLES_PER_SOURCE]:
            title = _clean_html(getattr(entry, "title", ""))
            if not title:
                continue

            link = getattr(entry, "link", "")
            if not link:
                continue

            # 提取内容摘要
            content = ""
            if hasattr(entry, "summary"):
                content = _clean_html(entry.summary)
            elif hasattr(entry, "content") and entry.content:
                content = _clean_html(entry.content[0].get("value", ""))
            elif hasattr(entry, "description"):
                content = _clean_html(entry.description)

            # 截取前 500 字符作为片段
            snippet = content[:500] if content else ""

            # 如果该来源需要过滤，检查是否与 AI 相关
            if source.get("filter_ai", False):
                if not _is_ai_related(title, snippet):
                    continue

            articles.append(
                {
                    "title": title,
                    "url": link,
                    "source": source["name"],
                    "language": source.get("language", "zh"),
                    "published_at": _parse_date(entry),
                    "content_snippet": snippet,
                }
            )

        # 显示过滤后的数量
        total = len(feed.entries[:config.MAX_ARTICLES_PER_SOURCE])
        filtered_note = f"（过滤后）" if source.get("filter_ai") else ""
        print(f"  ✅ {source['name']}: 获取 {len(articles)} 篇文章{filtered_note}")

    except httpx.TimeoutException:
        print(f"  ⏰ {source['name']}: 请求超时，跳过")
    except httpx.HTTPStatusError as e:
        print(f"  ❌ {source['name']}: HTTP {e.response.status_code}，跳过")
    except Exception as e:
        print(f"  ❌ {source['name']}: {type(e).__name__}: {e}")

    return articles


async def fetch_all_rss() -> list[dict]:
    """抓取所有 RSS 源"""
    print("\n📡 开始抓取 RSS 源...")
    all_articles = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 AI-News-Aggregator/1.0"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [
            fetch_single_rss(source, client) for source in config.RSS_SOURCES
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                print(f"  ❌ 抓取异常: {result}")

    print(f"📡 RSS 抓取完成，共获取 {len(all_articles)} 篇文章\n")
    return all_articles

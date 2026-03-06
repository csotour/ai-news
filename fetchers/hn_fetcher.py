"""
AI 资讯聚合工具 - Hacker News 抓取模块
通过 Firebase API 获取 HN 上 AI 相关的帖子
"""
import asyncio

import httpx

import config

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


def _is_ai_related(title: str) -> bool:
    """检查标题是否与 AI 相关"""
    title_lower = title.lower()
    return any(kw in title_lower for kw in config.HN_AI_KEYWORDS)


async def _fetch_item(item_id: int, client: httpx.AsyncClient) -> dict | None:
    """获取单个 HN 帖子"""
    try:
        resp = await client.get(
            f"{HN_API_BASE}/item/{item_id}.json",
            timeout=config.REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


async def fetch_hn_articles(max_items: int = 100) -> list[dict]:
    """
    获取 Hacker News Top Stories 中 AI 相关的帖子。
    max_items: 检查前多少个帖子
    """
    print("\n🟠 开始抓取 Hacker News...")
    articles = []

    try:
        async with httpx.AsyncClient() as client:
            # 获取 Top Stories ID 列表
            resp = await client.get(
                f"{HN_API_BASE}/topstories.json",
                timeout=config.REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            story_ids = resp.json()[:max_items]

            # 并发获取帖子详情（分批以避免过多并发）
            batch_size = 20
            for i in range(0, len(story_ids), batch_size):
                batch = story_ids[i : i + batch_size]
                tasks = [_fetch_item(sid, client) for sid in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for item in results:
                    if not item or isinstance(item, Exception):
                        continue
                    if not isinstance(item, dict):
                        continue

                    title = item.get("title", "")
                    url = item.get("url", "")

                    if not title or not _is_ai_related(title):
                        continue

                    # 如果没有外链，使用 HN 讨论页面
                    if not url:
                        url = f"https://news.ycombinator.com/item?id={item['id']}"

                    from datetime import datetime

                    timestamp = item.get("time")
                    published_at = (
                        datetime.fromtimestamp(timestamp).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        if timestamp
                        else None
                    )

                    score = item.get("score", 0)
                    descendants = item.get("descendants", 0)
                    snippet = f"HN 评分: {score} | 评论数: {descendants}"

                    articles.append(
                        {
                            "title": title,
                            "url": url,
                            "source": "Hacker News",
                            "language": "en",
                            "published_at": published_at,
                            "content_snippet": snippet,
                        }
                    )

        print(f"🟠 Hacker News: 获取 {len(articles)} 篇 AI 相关文章\n")

    except Exception as e:
        print(f"❌ Hacker News 抓取失败: {e}\n")

    return articles

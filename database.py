"""
AI 资讯聚合工具 - 数据库模块
使用 aiosqlite 进行异步 SQLite 操作
"""
import aiosqlite
import config

DB_PATH = config.DATABASE_PATH


async def init_db():
    """初始化数据库，创建表结构"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                language TEXT DEFAULT 'zh',
                category TEXT DEFAULT '综合',
                published_at TEXT,
                fetched_at TEXT DEFAULT (datetime('now', 'localtime')),
                summary TEXT,
                content_snippet TEXT,
                is_read INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_published
            ON articles(published_at DESC)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_category
            ON articles(category)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_source
            ON articles(source)
        """)
        await db.commit()


async def insert_article(article: dict) -> bool:
    """
    插入一篇文章，如果 URL 已存在则跳过。
    返回 True 表示插入成功，False 表示已存在。
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                """
                INSERT INTO articles (title, url, source, language, category, published_at, content_snippet, summary)
                VALUES (:title, :url, :source, :language, :category, :published_at, :content_snippet, :summary)
                """,
                {
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", ""),
                    "language": article.get("language", "zh"),
                    "category": article.get("category", "综合"),
                    "published_at": article.get("published_at"),
                    "content_snippet": article.get("content_snippet", ""),
                    "summary": article.get("summary"),
                },
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def insert_articles_batch(articles: list[dict]) -> int:
    """批量插入文章，返回成功插入的数量"""
    inserted = 0
    async with aiosqlite.connect(DB_PATH) as db:
        for article in articles:
            try:
                await db.execute(
                    """
                    INSERT INTO articles (title, url, source, language, category, published_at, content_snippet, summary)
                    VALUES (:title, :url, :source, :language, :category, :published_at, :content_snippet, :summary)
                    """,
                    {
                        "title": article.get("title", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", ""),
                        "language": article.get("language", "zh"),
                        "category": article.get("category", "综合"),
                        "published_at": article.get("published_at"),
                        "content_snippet": article.get("content_snippet", ""),
                        "summary": article.get("summary"),
                    },
                )
                inserted += 1
            except aiosqlite.IntegrityError:
                continue
        await db.commit()
    return inserted


async def get_articles(
    page: int = 1,
    per_page: int = 20,
    category: str = None,
    language: str = None,
    search: str = None,
    source: str = None,
) -> dict:
    """
    获取文章列表，支持分页、分类筛选、语言筛选和搜索。
    """
    conditions = []
    params = {}

    if category and category != "全部":
        conditions.append("category = :category")
        params["category"] = category

    if language and language != "all":
        conditions.append("language = :language")
        params["language"] = language

    if source:
        conditions.append("source = :source")
        params["source"] = source

    if search:
        conditions.append("(title LIKE :search OR summary LIKE :search)")
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    offset = (page - 1) * per_page

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # 总数
        cursor = await db.execute(
            f"SELECT COUNT(*) as total FROM articles WHERE {where_clause}", params
        )
        row = await cursor.fetchone()
        total = row[0]

        # 文章列表
        cursor = await db.execute(
            f"""
            SELECT * FROM articles
            WHERE {where_clause}
            ORDER BY published_at DESC, fetched_at DESC
            LIMIT :limit OFFSET :offset
            """,
            {**params, "limit": per_page, "offset": offset},
        )
        rows = await cursor.fetchall()
        articles = [dict(row) for row in rows]

    return {
        "articles": articles,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if total > 0 else 1,
    }


async def get_article_by_id(article_id: int) -> dict | None:
    """获取单篇文章"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def mark_as_read(article_id: int) -> bool:
    """标记文章为已读"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "UPDATE articles SET is_read = 1 WHERE id = ?", (article_id,)
        )
        await db.commit()
        return cursor.rowcount > 0


async def update_article_summary(article_id: int, summary: str, category: str = None):
    """更新文章的 AI 摘要和分类"""
    async with aiosqlite.connect(DB_PATH) as db:
        if category:
            await db.execute(
                "UPDATE articles SET summary = ?, category = ? WHERE id = ?",
                (summary, category, article_id),
            )
        else:
            await db.execute(
                "UPDATE articles SET summary = ? WHERE id = ?",
                (summary, article_id),
            )
        await db.commit()


async def get_articles_without_summary(limit: int = 10) -> list[dict]:
    """获取尚未生成摘要的文章"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM articles
            WHERE summary IS NULL OR summary = ''
            ORDER BY fetched_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_stats() -> dict:
    """获取统计数据"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # 总文章数
        cursor = await db.execute("SELECT COUNT(*) as total FROM articles")
        total = (await cursor.fetchone())[0]

        # 今日新增
        cursor = await db.execute(
            "SELECT COUNT(*) FROM articles WHERE date(fetched_at) = date('now', 'localtime')"
        )
        today = (await cursor.fetchone())[0]

        # 未读数
        cursor = await db.execute(
            "SELECT COUNT(*) FROM articles WHERE is_read = 0"
        )
        unread = (await cursor.fetchone())[0]

        # 各分类数量
        cursor = await db.execute(
            "SELECT category, COUNT(*) as count FROM articles GROUP BY category ORDER BY count DESC"
        )
        categories = {row["category"]: row["count"] for row in await cursor.fetchall()}

        # 各来源数量
        cursor = await db.execute(
            "SELECT source, COUNT(*) as count FROM articles GROUP BY source ORDER BY count DESC"
        )
        sources = {row["source"]: row["count"] for row in await cursor.fetchall()}

    return {
        "total": total,
        "today": today,
        "unread": unread,
        "categories": categories,
        "sources": sources,
    }

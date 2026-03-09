"""
AI 资讯聚合工具 - FastAPI 主应用
"""
import asyncio
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import config
import database
from fetchers.hn_fetcher import fetch_hn_articles
from fetchers.rss_fetcher import fetch_all_rss
from services.ai_summary import process_pending_articles

# ===================== 定时任务 =====================
scheduler = AsyncIOScheduler()
_is_fetching = False


def _config_self_check():
    """启动配置自检，输出必要提示。"""
    print("=" * 50)
    print("🔍 启动配置自检")
    print(f"  HOST/PORT: {config.HOST}:{config.PORT}")
    print(f"  抓取间隔: 每 {config.FETCH_INTERVAL_MINUTES} 分钟")
    print(f"  RSS 源数量: {len(config.RSS_SOURCES)}")
    if config.LLM_API_KEY:
        print(f"  LLM 摘要: 已启用（模型: {config.LLM_MODEL}）")
    else:
        print("  ⚠️ LLM 摘要: 未启用（缺少环境变量 LLM_API_KEY）")
        print("     仍可抓取和浏览资讯，仅不会生成 AI 摘要。")
    print("=" * 50)


async def scheduled_fetch():
    """定时抓取任务"""
    global _is_fetching
    if _is_fetching:
        print("⚠️  上一次抓取尚未完成，跳过本次")
        return

    _is_fetching = True
    try:
        print("=" * 50)
        print("⏰ 开始定时抓取任务...")
        print("=" * 50)

        # 1. 抓取 RSS
        rss_articles = await fetch_all_rss()
        rss_inserted = await database.insert_articles_batch(rss_articles)
        print(f"📥 RSS: 新增 {rss_inserted} 篇文章")

        # 2. 抓取 Hacker News
        hn_articles = await fetch_hn_articles()
        hn_inserted = await database.insert_articles_batch(hn_articles)
        print(f"📥 HN: 新增 {hn_inserted} 篇文章")

        # 3. 生成 AI 摘要
        if config.LLM_API_KEY:
            await process_pending_articles(batch_size=15, delay=1.5)
        else:
            print("⚠️  未配置 LLM API Key，跳过摘要生成")

        stats = await database.get_stats()
        print(f"📊 数据库总计: {stats['total']} 篇 | 今日: {stats['today']} 篇")
        print("=" * 50)
        print("✅ 抓取任务完成\n")

    except Exception as e:
        print(f"❌ 抓取任务异常: {e}")
    finally:
        _is_fetching = False


# ===================== 应用生命周期 =====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭事件"""
    # 启动
    _config_self_check()
    await database.init_db()
    print("✅ 数据库初始化完成")

    # 启动时立即执行一次抓取
    asyncio.create_task(scheduled_fetch())

    # 设置定时任务
    scheduler.add_job(
        scheduled_fetch,
        "interval",
        minutes=config.FETCH_INTERVAL_MINUTES,
        id="fetch_articles",
    )
    scheduler.start()
    print(f"⏰ 定时任务已启动（每 {config.FETCH_INTERVAL_MINUTES} 分钟抓取一次）")
    print(f"🌐 请访问 http://{config.HOST}:{config.PORT}")

    yield

    # 关闭
    scheduler.shutdown()
    print("👋 服务已关闭")


# ===================== FastAPI 应用 =====================
app = FastAPI(title="AI 资讯聚合", lifespan=lifespan)

# 挂载静态文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def index():
    """返回主页面"""
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/api/articles")
async def get_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    language: str = Query(None),
    search: str = Query(None),
    source: str = Query(None),
):
    """获取文章列表"""
    return await database.get_articles(
        page=page,
        per_page=per_page,
        category=category,
        language=language,
        search=search,
        source=source,
    )


@app.get("/api/articles/{article_id}")
async def get_article(article_id: int):
    """获取单篇文章"""
    article = await database.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article


@app.post("/api/articles/{article_id}/read")
async def mark_read(article_id: int):
    """标记文章为已读"""
    success = await database.mark_as_read(article_id)
    return {"success": success}


@app.post("/api/fetch")
async def manual_fetch():
    """手动触发抓取"""
    global _is_fetching
    if _is_fetching:
        return {"status": "busy", "message": "抓取正在进行中，请稍后再试"}

    asyncio.create_task(scheduled_fetch())
    return {"status": "started", "message": "抓取任务已开始，请稍后刷新查看"}


@app.get("/api/stats")
async def get_stats():
    """获取统计数据"""
    return await database.get_stats()


# ===================== 启动入口 =====================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
    )

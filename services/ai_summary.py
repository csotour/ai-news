"""
AI 资讯聚合工具 - AI 摘要生成服务
使用 ModelScope API (Qwen3.5) 生成中文摘要并自动分类
"""
import asyncio
import json
import traceback

from openai import AsyncOpenAI

import config
import database

# 初始化客户端
client = AsyncOpenAI(
    base_url=config.LLM_BASE_URL,
    api_key=config.LLM_API_KEY,
)

SYSTEM_PROMPT = """你是一个专业的AI资讯编辑。你的任务是：
1. 为给定的文章生成简短的中文摘要（不超过100字）
2. 从以下类别中选择最合适的一个进行分类：大模型、AI应用、论文、行业动态、开源

请严格以JSON格式返回，不要包含其他内容：
{"summary": "中文摘要内容", "category": "分类名称"}"""


async def generate_summary_for_article(article: dict) -> dict | None:
    """
    为单篇文章生成 AI 摘要和分类。
    返回 {"summary": "...", "category": "..."} 或 None
    """
    content = article.get("content_snippet", "") or ""
    title = article.get("title", "")
    source = article.get("source", "")

    user_prompt = f"标题：{title}\n来源：{source}\n内容：{content[:600]}"

    try:
        response = await client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=config.LLM_MAX_TOKENS,
            temperature=0.3,
            extra_body={"enable_thinking": False},  # 关闭思考模式，直接输出结果
        )

        result_text = response.choices[0].message.content.strip()

        # 尝试提取 JSON（处理可能的 markdown 包裹）
        if "```" in result_text:
            # 去除 markdown 代码块
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()

        result = json.loads(result_text)

        # 验证分类
        valid_categories = ["大模型", "AI应用", "论文", "行业动态", "开源"]
        if result.get("category") not in valid_categories:
            result["category"] = "综合"

        return result

    except json.JSONDecodeError:
        print(f"  ⚠️  JSON解析失败: {title[:30]}...")
        return None
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, "response"):
            try:
                error_msg += f" - {e.response.text}"
            except:
                pass
        print(f"  ❌ 摘要生成失败 [{title[:30]}...]: {type(e).__name__}: {error_msg}")
        return None


async def process_pending_articles(batch_size: int = 10, delay: float = None):
    """
    为尚未生成摘要的文章批量生成摘要。
    delay: 每篇文章间的延迟（秒），用于速率限制保护。默认从 config 读取。
    """
    if delay is None:
        delay = getattr(config, 'LLM_SUMMARY_DELAY', 3.0)
    articles = await database.get_articles_without_summary(limit=batch_size)

    if not articles:
        print("✨ 所有文章都已有摘要")
        return 0

    print(f"\n🤖 开始生成 AI 摘要（共 {len(articles)} 篇）...")
    success_count = 0

    for article in articles:
        result = await generate_summary_for_article(article)
        if result:
            await database.update_article_summary(
                article["id"],
                summary=result.get("summary", ""),
                category=result.get("category"),
            )
            success_count += 1
            print(f"  ✅ [{article['source']}] {article['title'][:40]}...")
        else:
            # 失败时设置一个默认摘要，避免反复重试
            await database.update_article_summary(
                article["id"],
                summary="（摘要生成失败）",
            )

        # 速率限制延迟
        await asyncio.sleep(delay)

    print(f"🤖 摘要生成完成: {success_count}/{len(articles)} 篇成功\n")
    return success_count

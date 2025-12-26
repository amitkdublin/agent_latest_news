import logging
import uuid
import datetime
from pathlib import Path
from fastapi import FastAPI
import inngest.fast_api
from dotenv import load_dotenv
import inngest

from custom_types import NewsletterRequest
from newsletter_service import NewsletterService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

inngest_client = inngest.Inngest(
    app_id="newsletter",
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

Path("newsletters").mkdir(exist_ok=True)


@inngest_client.create_function(
    fn_id="Generate Newsletter",
    trigger=inngest.TriggerEvent(event="newsletter/generate")
)
async def generate_newsletter(ctx: inngest.Context):
    """generate AI newsletter from topic"""

    logger.info(f"Generating AI newsletter: {ctx.event.id}")

    async def _search_articles(request: NewsletterRequest):
        return await NewsletterService.search_web_simple(request.topic, request.max_articles)

    def _save_newsletter(request: NewsletterRequest, newsletter_text: str, articles_count: int):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = request.topic.replace(" ", "_").replace("/", "_")
        filename = f"{safe_topic}_{timestamp}_{str(uuid.uuid4())[:8]}.md"
        file_path = Path("newsletters") / filename

        with open(file_path, "w") as f:
            f.write(f"# {request.topic} Newsletter\n\n{newsletter_text}")

        logger.info(f"Newsletter saved to: {file_path}")

        return {
            "file_path": str(file_path),
            "topic": request.topic,
            "articles_found": articles_count
        }

    request = NewsletterRequest(**ctx.event.data)

    search_results = await ctx.step.run(
        "search-articles", lambda: _search_articles(request)
    )

    newsletter_text = await NewsletterService.generate_newsletter(ctx, request.topic, search_results)

    result = await ctx.step.run(
        "save-newsletter",
        lambda: _save_newsletter(request, newsletter_text, 1),
    )

    return result


app = FastAPI(title="Newsletter API")
inngest.fast_api.serve(app, inngest_client, [generate_newsletter])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
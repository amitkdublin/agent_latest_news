import os
import asyncio
import concurrent.futures
from dotenv import load_dotenv
from inngest.experimental import ai

from langchain_brightdata import BrightDataSERP
from prompts import NEWSLETTER_SYSTEM_PROMPT, get_newsletter_prompt

load_dotenv()


class NewsletterService:

    @classmethod
    def _search_web_blocking(cls, topic: str, max_articles: int) -> str:
        try:
            print("Searching with BrightData SERP for:", topic)

            serp_tool = BrightDataSERP(
                bright_data_api_key=os.getenv("BRIGHT_DATA_API_KEY"),
                search_engine="google",
                country="us",
                language="en",
                results=max_articles,
                parse_results=True,
            )

            search_query = f"{topic} news recent developments"

            results = serp_tool.invoke(search_query)

            print(f"Got results for: {topic}")

            if isinstance(results, dict) and "organic" in results:
                essential_results = []
                for result in results["organic"][:max_articles]:
                    essential_results.append(
                        {
                            "title": result.get("title", ""),
                            "description": result.get("description", ""),
                            "source": result.get("source", "")
                        }
                    )
                return str({"query": topic, "results": essential_results})
            else:
                return str(results)

        except Exception as e:
            print(e)
            return ""

    @classmethod
    async def search_web_simple(cls, topic: str, max_articles: int) -> str:
        loop = asyncio.get_event_loop()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            result = await loop.run_in_executor(
                executor, cls._search_web_blocking, topic, max_articles
            )

        return result

    @staticmethod
    async def generate_newsletter(ctx, topic: str, search_results: str) -> str:
        prompt = get_newsletter_prompt(topic, search_results)

        openai_api_key = os.getenv("OPENAI_API_KEY")

        adapter = ai.openai.Adapter(auth_key=openai_api_key, model="gpt-4o-mini")

        res = await ctx.step.ai.infer(
            "generate-newsletter-content",
            adapter=adapter,
            body={
                "max_tokens": 2500,
                "temperature": 0.6,
                "messages": [
                    {"role": "system", "content": NEWSLETTER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            }
        )

        return res["choices"][0]["message"]["content"].strip()
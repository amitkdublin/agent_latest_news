import pydantic


class NewsletterRequest(pydantic.BaseModel):
    topic: str
    max_articles: int = 3
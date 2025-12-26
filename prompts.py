"""
Newsletter generation prompts
"""

NEWSLETTER_SYSTEM_PROMPT = "You are a professional newsletter writer specializing in AI and technology content."

def get_newsletter_prompt(topic: str, articles_text: str) -> str:
    """Generate the main newsletter creation prompt"""
    return f"""Create a newsletter about "{topic}" using these articles:

{articles_text}

Write a professional newsletter with:
1. Catchy headline
2. Brief introduction
3. Key highlights from the articles
4. Conclusion with takeaways

Keep it concise and engaging. Use markdown formatting."""
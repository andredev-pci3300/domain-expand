import os
from groq import AsyncGroq
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config.settings as settings

class GroqClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            # For robustness, we might want to log this but raise for now
            print("Warning: GROQ_API_KEY not found in environment")
        self.client = AsyncGroq(api_key=api_key)
        self.model = "openai/gpt-oss-120b"

    async def generate_reply(self, tweet_text, author_name):
        """Generates a reply using the defined persona asynchronously."""
        # Wrapper for generic generation with specific prompt construction
        if tweet_text == "GENERATE_NEWS_POST" or tweet_text.startswith("GENERATE_"):
             # Backward compatibility or hack fix
             return None

        prompt = f"""
        {settings.PERSONA_PROMPT}

        TWEET AUTHOR: @{author_name}
        TWEET TEXT: "{tweet_text}"

        YOUR REPLY:
        """
        return await self._call_llm(prompt)

    async def generate_content(self, prompt):
        """Generates content based on a specific prompt."""
        return await self._call_llm(prompt)

    async def _call_llm(self, user_prompt):
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": settings.PERSONA_PROMPT, 
                        # Note: We might want to pass system prompt as arg if it varies heavily, 
                        # but PERSONA_PROMPT is the base identity.
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=280,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating content: {e}")
            return None


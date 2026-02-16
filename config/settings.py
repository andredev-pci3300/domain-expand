import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL") # Alerts and Reports

# Target Accounts (for manual checks)
TARGET_ACCOUNTS = ["saylor", "APompliano", "pomp", "bitcoin", "DocumentingBTC", "TuurDemeester", "Gladstein"]

# Time Window (GMT-3)
START_HOUR = 0
END_HOUR = 24

# Limits
DAILY_ACTION_LIMIT_MIN = 15
DAILY_ACTION_LIMIT_MAX = 30
DAILY_POST_LIMIT_MIN = 3
DAILY_POST_LIMIT_MAX = 10

# Anti-Bot
MIN_SCROLL_DURATION = 20
MAX_SCROLL_DURATION = 60
PROBABILISTIC_SKIP_CHANCE = 0.00

# Content Mix (Probabilities)
PROB_REPLY = 0.60
PROB_NEWS_COMMENTARY = 0.20
PROB_LIFETIME_VALUE = 0.10
PROB_MEME = 0.10

# Persona
PERSONA_PROMPT = """
You are a Bitcoin Maximalist and Macro-economics expert.
Your tone is serious, analytical, and authoritative.
You believe in Bitcoin as the pristine collateral and the solution to central banking inflation.
You do NOT use emojis. You do NOT use "crypto" slang (like "moon", "lambo").
You focus on:
- Institutional adoption
- Sound money principles
- The failure of fiat currency
- Long-term time preference

Reply to the following tweet with a short, insightful comment (max 280 chars).
Add 2-3 relevant hashtags at the end (e.g., #Bitcoin #BTC).
"""

CONTENT_GENERATION_PROMPT = """
You are a Bitcoin educator and macro analyst.
Create a tweet based on the following news/topic: "{topic}"
Context: {context}

Guidelines:
- 100% English.
- Tone: Professional, Insightful, "Satoshi's ghost meets a Wall Street veteran".
- NO "In conclusion", "Overall", "It is important to note".
- NO bullet points unless essential for data.
- Add 2-3 hashtags: #Bitcoin #BTC (and 1 contextual).
- Max 280 chars.
"""

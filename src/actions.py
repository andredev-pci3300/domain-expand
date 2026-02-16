import asyncio
import random
import os
from src.auth import TwitterClient
from src.llm import GroqClient
from src.cache import CacheManager
from src.utils import is_within_time_window, random_sleep, should_skip_probabilistic
import config.settings as settings

import asyncio
import random
import os
from src.auth import TwitterClient
from src.llm import GroqClient
from src.cache import CacheManager
from src.utils import is_within_time_window, random_sleep, should_skip_probabilistic
from src.foryou_monitor import ForYouMonitor
from src.news_monitor import NewsMonitor
from src.strategist import ContentStrategist
import config.settings as settings

class BotActions:
    def __init__(self):
        self.twitter = TwitterClient()
        self.llm = GroqClient()
        self.cache = CacheManager()
        self.foryou_monitor = ForYouMonitor(self.twitter)
        self.news_monitor = NewsMonitor()
        self.strategist = ContentStrategist()

    async def initialize(self):
        await self.twitter.login()

    async def run_cycle(self):
        print("Starting bot cycle (ADVANCED)...")

        # 1. Time Window Check
        if not is_within_time_window():
            # Override for manual testing if needed, but keeping strict for prod
            print("Outside operational hours. Sleeping.")
            return

        # 2. Daily Limit Check
        daily_count = self.cache.get_daily_count()
        if daily_count >= settings.DAILY_ACTION_LIMIT_MAX:
            print(f"Daily limit reached ({daily_count}). Stopping.")
            return

        # 3. Probabilistic Skip
        if should_skip_probabilistic():
            print("Skipping cycle (Probabilistic).")
            return

        # 4. Decide Action
        action = self.strategist.decide_next_action()
        print(f"Decided Strategy: {action}")

        target_tweet = None
        prompt_context = ""
        
        if action == 'REPLY':
            await self._handle_reply_strategy()
        elif action == 'NEWS_POST':
            await self._handle_news_strategy()
        elif action == 'VALUE_POST':
            await self._handle_value_strategy()
        elif action == 'MEME':
            await self._handle_meme_strategy()

        print("Cycle complete.")

    async def _handle_reply_strategy(self):
        # Fetch For You tweets
        print("Scraping For You timeline...")
        foryou_tweets = await self.foryou_monitor.get_for_you_tweets(count=20)
        candidates = self.foryou_monitor.filter_high_engagement(foryou_tweets)
        
        # If no good candidates in For You, fall back to Target Accounts
        if not candidates:
            print("No suitable For You tweets found. Checking targets...")
            target_user = random.choice(settings.TARGET_ACCOUNTS)
            candidates = await self.twitter.get_latest_tweets(target_user, count=5)

        # Process candidates
        for tweet in candidates:
            if self.cache.is_tweet_processed(tweet.id):
                continue
            
            print(f"Replying to tweet: {tweet.text[:50]}...")
            
            # Anti-Bot Delay
            await random_sleep(settings.MIN_SCROLL_DURATION, settings.MAX_SCROLL_DURATION)
            
            # Generate Reply
            reply_text = await self.llm.generate_reply(tweet.text, tweet.user.screen_name)
            if not reply_text: continue

            # Post
            await self._post_tweet(reply_text, reply_to_id=tweet.id)
            break # One action per cycle

    async def _handle_news_strategy(self):
        news_items = await self.news_monitor.get_hot_news()
        if not news_items:
            print("No news found. Falling back to Value Post.")
            await self._handle_value_strategy()
            return

        # Select top news
        news = news_items[0]
        prompt = self.strategist.get_content_prompt('NEWS_POST', context=self.news_monitor.format_news_prompt(news))
        
        # Anti-Bot (Simulate reading news)
        await random_sleep(settings.MIN_SCROLL_DURATION, settings.MAX_SCROLL_DURATION)

        # Generate Tweet
        tweet_text = await self.llm.generate_content(prompt)
        if tweet_text:
            print(f"Generated News Tweet: {tweet_text}")
            await self._post_tweet(tweet_text)

    async def _handle_value_strategy(self):
        prompt = self.strategist.get_content_prompt('VALUE_POST')
        await random_sleep(settings.MIN_SCROLL_DURATION, settings.MAX_SCROLL_DURATION)
        
        tweet_text = await self.llm.generate_content(prompt)
        if tweet_text:
             print(f"Generated Value Tweet: {tweet_text}")
             await self._post_tweet(tweet_text)

    async def _handle_meme_strategy(self):
        prompt = self.strategist.get_content_prompt('MEME')
        await random_sleep(settings.MIN_SCROLL_DURATION, settings.MAX_SCROLL_DURATION)
        
        tweet_text = await self.llm.generate_content(prompt)
        if tweet_text:
             print(f"Generated Meme Tweet: {tweet_text}")
             await self._post_tweet(tweet_text)
        
    async def _post_tweet(self, text, reply_to_id=None):
        """Helper to post tweet or reply with Dry Run check."""
        # Clean text (remove quotes if LLM added them)
        text = text.strip('"')

        if os.getenv("DRY_RUN") == "true":
            print(f"[DRY RUN] Would post: {text} (Reply to: {reply_to_id})")
            success = True
        else:
            if reply_to_id:
                success = await self.twitter.reply(reply_to_id, text)
            else:
                success = await self.twitter.create_tweet(text)

        if success:
             # If it's a new tweet, we don't have an ID to dedup against easily unless we track our own activity
             # For replies, we track the target tweet ID
             if reply_to_id:
                self.cache.log_tweet_processed(reply_to_id, "reply")
             
             self.cache.increment_daily_count()
             print("Action completed successfully.")

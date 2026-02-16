from src.auth import TwitterClient
import random

class ForYouMonitor:
    def __init__(self, twitter_client: TwitterClient):
        self.client = twitter_client

    async def get_for_you_tweets(self, count=20):
        """Fetches tweets from the 'For You' timeline (Home)."""
        # In twikit, get_timeline() fetches the "For You" feed by default if not specified otherwise, 
        # or 'Home' depending on account settings. 
        # We will assume get_timeline() gives us the algorithmic feed.
        try:
            tweets = await self.client.client.get_timeline(count=count, tweet_type='Recommended') 
            # tweet_type='Recommended' forces 'For You' usually, but 'Top' is also a valid param in some endpoints.
            # Twikit documentation says get_timeline() gets "Home" timeline.
            return tweets
        except Exception as e:
            print(f"Error fetching For You timeline: {e}")
            return []

    def filter_high_engagement(self, tweets):
        """Filters tweets based on engagement capability and relevance."""
        relevant_tweets = []
        keywords = ["bitcoin", "btc", "inflation", "fed", "monetary", "economy", "etf", "mining", "hashrate"]
        ignore_keywords = ["crypto", "nft", "airdrop", "solana", "eth", "ethereum", "memecoin", "pepe", "doge"]

        for tweet in tweets:
            text_lower = tweet.text.lower()

            # 1. Keyword Check
            if not any(k in text_lower for k in keywords):
                continue
            if any(k in text_lower for k in ignore_keywords):
                continue

            # 2. Engagement Check (Heuristics)
            # We want "rising" tweets or established high-eng tweets to ride the wave.
            # Note: Twikit tweet objects should have favorite_count, etc.
            try:
                likes = tweet.favorite_count
                replies = tweet.reply_count
            except:
                # If attributes missing, skip or be lenient
                continue

            if likes > 500 and replies > 50:
                relevant_tweets.append(tweet)

        return relevant_tweets

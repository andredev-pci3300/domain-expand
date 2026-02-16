from twikit import Client
import json
import os
import asyncio

COOKIES_PATH = "data/cookies.json"

class TwitterClient:
    def __init__(self):
        self.client = Client('en-US')

    async def login(self):
        """Loads cookies if available, otherwise expects environment variables for login."""
        if os.path.exists(COOKIES_PATH):
            print("Loading cookies...")
            self.client.load_cookies(COOKIES_PATH)
        else:
            print("No cookies found. Login required.")
            username = os.getenv("TWITTER_USERNAME")
            email = os.getenv("TWITTER_EMAIL")
            password = os.getenv("TWITTER_PASSWORD")
            
            if username and password:
                print("Logging in with credentials...")
                await self.client.login(
                    auth_info_1=username,
                    auth_info_2=email,
                    password=password
                )
                self.client.save_cookies(COOKIES_PATH)
                print("Login successful and cookies saved.")
            else:
                raise Exception("Credentials not provided and cookies missing.")

    async def get_latest_tweets(self, username, count=5):
        """Fetches latest tweets from a user."""
        try:
            user = await self.client.get_user_by_screen_name(username)
            tweets = await user.get_tweets('Tweets', count=count)
            return tweets
        except Exception as e:
            print(f"Error fetching tweets from {username}: {e}")
            return []

    async def reply(self, tweet_id, text):
        """Replies to a tweet."""
        try:
            # Twikit's create_tweet with reply_to argument
            await self.client.create_tweet(text=text, reply_to_tweet_id=tweet_id)
            print(f"Replied to {tweet_id}")
            return True
        except Exception as e:
            print(f"Error replying to {tweet_id}: {e}")
            return False

    async def create_tweet(self, text):
        """Creates a new tweet."""
        try:
            await self.client.create_tweet(text=text)
            print("Tweet created successfully.")
            return True
        except Exception as e:
            print(f"Error creating tweet: {e}")
            return False


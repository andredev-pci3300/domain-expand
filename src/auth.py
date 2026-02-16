from twikit import Client
import json
import os
import asyncio
from fake_useragent import UserAgent

COOKIES_PATH = "data/cookies.json"

class TwitterClient:
    def __init__(self):
        # Use a real/random User-Agent to avoid Cloudflare blocks
        try:
            ua = UserAgent(browsers=['chrome', 'edge'])
            user_agent = ua.random
        except:
             user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        
        print(f"Using User-Agent: {user_agent}")
        self.client = Client(
            language='en-US',
            user_agent=user_agent
        )

    async def login(self):
        """Loads cookies if available, otherwise expects environment variables for login."""
        if os.path.exists(COOKIES_PATH):
            print(f"Loading cookies from {COOKIES_PATH}...")
            self.client.load_cookies(COOKIES_PATH)
            
            # Explicitly verify headers
            cookies = self.client.get_cookies()
            if 'ct0' in cookies:
                # Twikit sets this automatically usually
                print("CSRF Token (ct0) found in cookies.")
            else:
                print("WARNING: ct0 cookie not found. Auth may fail.")
                
            if 'auth_token' in cookies:
                print("Auth Token detected.")
            else:
                print("WARNING: auth_token cookie not found.")

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

    async def get_my_metrics(self):
        """Fetches current user metrics."""
        try:
            user = await self.client.user()
            return {
                "followers": user.followers_count,
                "following": user.following_count,
                "statuses": user.statuses_count,
                "name": user.name,
                "screen_name": user.screen_name
            }
        except Exception as e:
            print(f"Error fetching metrics: {e}")
            return None

    async def save_session(self):
        """Saves the current session cookies to file."""
        try:
            self.client.save_cookies(COOKIES_PATH)
            print("Session cookies saved.")
        except Exception as e:
            print(f"Error saving cookies: {e}")




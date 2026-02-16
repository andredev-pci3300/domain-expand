from twikit import Client
import json
import os
import asyncio
from fake_useragent import UserAgent

COOKIES_PATH = "data/cookies.json"

class TwitterClient:
    def __init__(self):
        # Reverting to Twikit's default User-Agent handling
        # Manual overrides might be breaking header consistency
        # Wrapper for Twikit Client with Proxy Support
        proxy_url = os.getenv("PROXY_URL")
        # Updated to a more modern and common User-Agent (Chrome 133)
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
        
        if proxy_url:
            print(f"Using Proxy: {proxy_url.split('@')[-1]}")
            self.client = Client(language='en-US', proxy=proxy_url, user_agent=user_agent)
        else:
            print("No Proxy configured. Using direct connection.")
            self.client = Client(language='en-US', user_agent=user_agent)

    async def login(self):
        """Loads cookies if available, otherwise expects environment variables for login."""
        if os.path.exists(COOKIES_PATH):
            print(f"Loading cookies from {COOKIES_PATH}...")
            self.client.load_cookies(COOKIES_PATH)
            
            # Debug: Print loaded cookie keys to verify strictly cleaned version
            loaded_cookies = self.client.get_cookies()
            print(f"Loaded Cookie Keys: {list(loaded_cookies.keys())}")
            
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
            await self.client.create_tweet(text=text, reply_to=tweet_id)
            print(f"Replied to {tweet_id}")
            return True
        except Exception as e:
            error_msg = str(e)
            print(f"Error replying to {tweet_id}: {type(e).__name__} - {error_msg}")
            
            # Specific handling for the 'code' KeyError which indicates a non-JSON (Cloudflare) response
            if "'code'" in error_msg:
                print("⚠️ CRITICAL: Cloudflare Blocked the POST request. The response was not JSON.")
                print("💡 Recommendation: Rotate Proxy IP or check if User-Agent matches exactly your current browser.")
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
            # Fallback for metrics if client.user() fails
            try:
                user = await self.client.user()
            except:
                # Try getting own user by screen name if stored in env
                username = os.getenv("TWITTER_USERNAME")
                if username:
                    user = await self.client.get_user_by_screen_name(username)
                else:
                    raise

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




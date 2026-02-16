import asyncio
import os
import sys
from dotenv import load_dotenv
from twikit import Client

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env variables (credentials + PROXY_URL)
load_dotenv()

async def main():
    print("=== X Bot: Proxy Authentication Tool ===")
    
    username = os.getenv("TWITTER_USERNAME")
    email = os.getenv("TWITTER_EMAIL")
    password = os.getenv("TWITTER_PASSWORD")
    proxy_url = os.getenv("PROXY_URL")

    if not all([username, email, password, proxy_url]):
        print("❌ Error: Missing credentials or PROXY_URL in .env file.")
        return

    print(f"📡 Connecting via Proxy: {proxy_url.split('@')[-1]}")
    
    client = Client(language='en-US', proxy=proxy_url)

    try:
        print("🔐 Attempting login...")
        # Login (interactive mode might be triggered inside twikit if needed, 
        # but usually it needs manual handling for codes if not using totp)
        await client.login(
            auth_info_1=username,
            auth_info_2=email,
            password=password
        )
        
        print("✅ Login Successful!")
        
        # Save cookies
        cookies_path = "data/cookies.json"
        os.makedirs("data", exist_ok=True)
        client.save_cookies(cookies_path)
        print(f"🍪 Cookies saved to: {cookies_path}")
        
        # Verify
        user = await client.user()
        print(f"👤 Authenticated as: {user.name} (@{user.screen_name})")
        print(f"📊 Followers: {user.followers_count}")
        
        print("\n⚠️  NEXT STEP: Run 'python scripts/clean_cookies.py' (or fix_cookies.py) and update GitHub Secrets!")

    except Exception as e:
        print(f"❌ Login Failed: {e}")
        if "226" in str(e) or "32" in str(e):
            print("💡 Tip: Account might be locked or requiring email code. Try logging in manually in a browser with this IP first if possible.")

if __name__ == "__main__":
    asyncio.run(main())

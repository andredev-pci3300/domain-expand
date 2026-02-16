import asyncio
from src.auth import TwitterClient

async def verify():
    print("Verifying login...")
    try:
        client = TwitterClient()
        await client.login()
        
        user = await client.client.user()
        print(f"Logged in as: {user.name} (@{user.screen_name})")
        print(f"Followers: {user.followers_count}")
        print("SUCCESS: Login verified.")
    except Exception as e:
        print(f"Login Verification Failed: {e}")
        if hasattr(e, 'message'):
            print(f"Response Snippet: {str(e.message)[:200]}")

if __name__ == "__main__":
    asyncio.run(verify())

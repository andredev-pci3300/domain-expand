import asyncio
from playwright.async_api import async_playwright
import os
import json
from dotenv import load_dotenv

load_dotenv()

PROXY_URL = os.getenv("PROXY_URL")
USERNAME = os.getenv("TWITTER_USERNAME")
PASSWORD = os.getenv("TWITTER_PASSWORD")
EMAIL = os.getenv("TWITTER_EMAIL")

async def main():
    print(f"📡 Connecting to Proxy: {PROXY_URL.split('@')[-1]}")
    
    # Parse proxy for Playwright
    # Format: http://user:pass@host:port -> {server, username, password}
    if "://" in PROXY_URL:
        protocol, rest = PROXY_URL.split("://")
        auth, address = rest.split("@")
        user, pwd = auth.split(":")
        
        proxy_config = {
            "server": f"{protocol}://{address}",
            "username": user,
            "password": pwd
        }
    else:
        print("❌ Invalid Proxy URL format")
        return

    async with async_playwright() as p:
        # Launch browser with Proxy
        browser = await p.firefox.launch(
            headless=False, # Must be FALSE to solve Cloudflare
            proxy=proxy_config
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("🌍 Navigating to X.com...")
        try:
            await page.goto("https://x.com/i/flow/login", timeout=60000)
        except Exception as e:
            print(f"⚠️ Navigation timeout or error: {e}")

        print("⌨️  Please log in manually in the browser window if script doesn't auto-type...")
        
        # Human-like interaction attempt
        try:
            await page.wait_for_selector("input[autocomplete='username']", timeout=10000)
            await page.fill("input[autocomplete='username']", USERNAME)
            await page.get_by_text("Next").click()
            
            # Check for unusual activity/email check
            try:
                await page.wait_for_selector("input[name='password']", timeout=5000)
            except:
                print("⚠️ Possible email verification or captcha needed. Handle manually!")
                # Wait for user to handle email/captcha
            
            await page.fill("input[name='password']", PASSWORD)
            await page.get_by_test_id("LoginForm_Login_Button").click()
            
        except Exception as e:
            print(f"ℹ️ Auto-login failed/interrupted: {e}")
            print("👉 Please finish login manually!")

        print("⏳ Waiting for login completion (checking for home/profile)...")
        # Wait until we are redirected to home
        try:
            await page.wait_for_url("**/home", timeout=120000) # 2 mins to login manually
            print("✅ Login detected!")
            
            # Save cookies
            cookies = await context.cookies()
            auth_cookies = {c['name']: c['value'] for c in cookies if c['name'] in ['auth_token', 'ct0']}
            
            if 'auth_token' in auth_cookies and 'ct0' in auth_cookies:
                os.makedirs("data", exist_ok=True)
                with open("data/cookies.json", "w") as f:
                    json.dump(auth_cookies, f, indent=4)
                print(f"🍪 Cookies saved to data/cookies.json (Count: {len(cookies)})")
            else:
                print("❌ auth_token or ct0 missing in captured cookies.")

        except Exception as e:
            print("❌ Timeout waiting for login. Did you log in?")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

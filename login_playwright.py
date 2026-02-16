import asyncio
import json
import os
from playwright.async_api import async_playwright

COOKIES_PATH = "data/cookies.json"

async def main():
    print("Launching browser for manual login (Stealth Mode)...")
    async with async_playwright() as p:
        # Launch with arguments to hide automation
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        # Use a real/common User-Agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        # Add avoiding detection script
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()
        
        await page.goto("https://x.com/login")
        
        print("Please log in to X in the opened browser window.")
        print("Once you are logged in and on the Home timeline, press Enter here.")
        input("Press Enter to save cookies...")
        
        cookies = await context.cookies()
        
        # Convert to dictionary format for twikit (or verify if list is OK)
        # Twikit load_cookies supports list of dicts if they have name/value/domain
        # But simple dict {name: value} is safest.
        
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
            
        with open(COOKIES_PATH, 'w') as f:
            json.dump(cookie_dict, f, indent=4)
            
        print(f"Cookies saved to {COOKIES_PATH}")
        print(f"Captured {len(cookie_dict)} cookies.")
        
        ua = await page.evaluate("navigator.userAgent")
        print(f"User Agent used: {ua}")
        print("You might want to update src/auth.py with this User Agent if problems persist.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

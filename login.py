import asyncio
import os
from twikit import Client
from dotenv import load_dotenv

load_dotenv()

COOKIES_PATH = "data/cookies.json"

async def login():
    client = Client('en-US')
    
    print("Welcome to the X Bot Login Helper.")
    print("This script will help you generate the initial cookies.json file.")

    username = input("Enter your X Username: ")
    email = input("Enter your X Email: ")
    password = input("Enter your X Password: ")

    try:
        print("Attempting to login...")
        await client.login(
            auth_info_1=username,
            auth_info_2=email,
            password=password
        )
        client.save_cookies(COOKIES_PATH)
        print(f"Login successful! Cookies saved to {COOKIES_PATH}")
    except Exception as e:
        print(f"Login failed: {e}")
        print("Please check your credentials or try again later.")

if __name__ == "__main__":
    asyncio.run(login())

import asyncio
import os
import sys
from src.actions import BotActions

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main():
    print("Initializing X Automation Bot...")
    bot = BotActions()
    
    try:
        await bot.initialize()
        await bot.run_cycle()
    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally log error to file or notification service

if __name__ == "__main__":
    asyncio.run(main())

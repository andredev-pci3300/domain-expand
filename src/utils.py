import random
import time
import asyncio
from datetime import datetime
import pytz
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config.settings as settings

def get_current_time_gmt3():
    """Returns current time in GMT-3."""
    tz = pytz.timezone('Etc/GMT+3') # Note: Etc/GMT+3 is actually GMT-3
    return datetime.now(tz)

def is_within_time_window():
    """Checks if current time is within allowed window (07:00 - 23:00 GMT-3)."""
    now = get_current_time_gmt3()
    return settings.START_HOUR <= now.hour < settings.END_HOUR

async def random_sleep(min_seconds, max_seconds):
    """Sleeps for a random amount of time."""
    sleep_time = random.uniform(min_seconds, max_seconds)
    print(f"Sleeping for {sleep_time:.2f} seconds...")
    await asyncio.sleep(sleep_time)

def should_skip_probabilistic():
    """Returns True if the bot should skip this cycle based on probability."""
    return random.random() < settings.PROBABILISTIC_SKIP_CHANCE

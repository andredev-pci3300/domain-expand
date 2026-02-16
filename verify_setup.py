import sys
import os

print("Verifying imports...")

try:
    import twikit
    print(f"twikit version: {twikit.__version__}")
except ImportError:
    print("Failed to import twikit")

try:
    import groq
    print("groq imported")
except ImportError:
    print("Failed to import groq")

try:
    from dotenv import load_dotenv
    print("dotenv imported")
except ImportError:
    print("Failed to import dotenv")

try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from src.actions import BotActions
    from src.utils import is_within_time_window
    print("Project modules imported successfully")
except Exception as e:
    print(f"Failed to import project modules: {e}")

print("Verification complete.")

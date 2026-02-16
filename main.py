import asyncio
import os
import sys
import datetime
from src.actions import BotActions
from src.notifications import NotificationManager

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main():
    print("Initializing X Automation Bot...")
    notifier = NotificationManager()
    bot = BotActions()

    # --- Initialization & Login Check ---
    try:
        # We assume BotActions init sets up clients, but we explicitly test auth
        if not bot.twitter:
             raise Exception("TwitterClient not initialized.")
        
        # Test connection/auth by fetching own metrics
        print("Verifying authentication...")
        try:
             # This serves as a "whoami" check
             await bot.twitter.get_my_metrics()
        except Exception as auth_err:
             raise Exception(f"Authentication failed: {auth_err}")

    except Exception as e:
        print(f"CRITICAL: Initialization failed: {e}")
        notifier.send_error_alert("Initialization Failure", str(e))
        return

    # --- Daily Reporting & Metrics ---
    try:
        # Check if we should generate a report (e.g., if we haven't logged info for today)
        if not bot.cache.get_todays_report_status():
            print("Fetching metrics for Daily Report...")
            metrics = await bot.twitter.get_my_metrics()
            
            if metrics:
                new_followers = bot.cache.log_metrics(
                    metrics['followers'],
                    metrics['following'],
                    metrics['statuses']
                )
                
                print(f"Metrics Logged. Growth: {new_followers}")
                
                # Generate executive summary using LLM
                report_prompt = f"""
                You are a social media manager. clearly analyze these X account stats for today:
                - Account: @{metrics.get('screen_name', 'Unknown')}
                - Followers: {metrics['followers']} (Change: {new_followers:+})
                - Following: {metrics['following']}
                - Total Tweets: {metrics['statuses']}
                
                Write a SHORT, professional executive summary email for the owner.
                Highlight the growth and suggest one generic focus area for tomorrow.
                Subject line not needed, just the body.
                """
                
                report_body = await bot.llm.generate_content(report_prompt)
                
                if report_body:
                    if notifier.send_daily_report(report_body):
                        print("Daily report email sent.")
                    else:
                        print("Failed to send daily report email.")
            else:
                print("Could not fetch metrics. report skipped.")
        else:
            print("Daily metrics already logged. Skipping report.")

    except Exception as e:
        print(f"Error during reporting phase: {e}")
        notifier.send_error_alert("Daily Report Error", str(e))

    # --- Main Bot Execution Cycle ---
    print("Starting bot cycle...")
    try:
        await bot.run_cycle()
        print("Cycle complete.")
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error during bot cycle: {error_msg}")
        
        # Classify errors
        error_type = "Runtime Error"
        if "captcha" in error_msg.lower() or "suspicious" in error_msg.lower() or "locked" in error_msg.lower():
            error_type = "CRITICAL: CAPTCHA/Lock Detected"
        elif "rate limit" in error_msg.lower():
            error_type = "Rate Limit"
            # We might not want to alert on simple rate limits if handled, but let's alert for now.
        
        notifier.send_error_alert(error_type, error_msg)
    
    finally:
        # Attempt to save session cookies regardless of success/error
        try:
            await bot.twitter.save_session()
        except Exception as e:
            print(f"Failed to save session: {e}")

if __name__ == "__main__":
    asyncio.run(main())

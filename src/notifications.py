import requests
import os
import sys

# Ensure config is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config.settings as settings

class NotificationManager:
    def __init__(self):
        self.webhook_url = settings.GOOGLE_SCRIPT_URL
        if not self.webhook_url:
            print("[WARN] GOOGLE_SCRIPT_URL not found. Notifications disabled.")

    def send_email(self, subject, body):
        """Sends an email via the Google Apps Script Webhook."""
        if not self.webhook_url:
            print(f"[Simulation] would send email: {subject}")
            return False

        payload = {
            "subject": subject,
            "body": body
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print(f"Email notification sent: {subject}")
                return True
            else:
                print(f"Failed to send notification. Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
            
    def send_error_alert(self, error_type, details):
        """Helper for sending error alerts."""
        subject = f"⚠️ BOT ERROR: {error_type}"
        body = f"An error occurred in the X Automation Bot:\n\nType: {error_type}\nDetails: {details}\n\nPlease check the logs and take action if necessary."
        self.send_email(subject, body)
        
    def send_daily_report(self, report_text):
        """Helper for sending daily reports."""
        subject = "📊 Daily X Bot Report"
        self.send_email(subject, report_text)

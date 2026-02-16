import feedparser
import os
import sys

# Ensure config is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config.settings as settings

class NewsMonitor:
    def __init__(self):
        # Google News RSS for Bitcoin, optimized for US English
        self.rss_url = "https://news.google.com/rss/search?q=bitcoin+OR+macroeconomics+when:1d&hl=en-US&gl=US&ceid=US:en"

    async def get_hot_news(self):
        """Fetches top news from Google News RSS."""
        try:
            feed = feedparser.parse(self.rss_url)
            
            if not feed.entries:
                print("No news found in RSS feed.")
                return []

            # Return top 5 entries
            return feed.entries[:5]
        except Exception as e:
            print(f"Error fetching RSS: {e}")
            return []

    def format_news_prompt(self, news_item):
        """Formats a news item for the LLM prompt."""
        title = news_item.get("title", "No Title")
        link = news_item.get("link", "")
        published = news_item.get("published", "")
        
        return f"News: {title}\nPublished: {published}\nLink: {link}"

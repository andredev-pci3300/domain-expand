import random
import sys
import os

# Ensure config is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config.settings as settings

class ContentStrategist:
    def __init__(self):
        pass

    def decide_next_action(self):
        """
        Decides the next action based on configured probabilities in settings.py.
        Returns one of: 'REPLY', 'NEWS_POST', 'VALUE_POST', 'MEME'
        """
        # Load probabilities
        p_reply = settings.PROB_REPLY
        p_news = settings.PROB_NEWS_COMMENTARY
        p_value = settings.PROB_LIFETIME_VALUE
        p_meme = settings.PROB_MEME

        # Create weighted list
        actions = ['REPLY', 'NEWS_POST', 'VALUE_POST', 'MEME']
        weights = [p_reply, p_news, p_value, p_meme]
        
        # Select action
        action = random.choices(actions, weights=weights, k=1)[0]
        return action

    def get_content_prompt(self, action_type, context=None):
        """Returns the appropriate prompt for the LLM based on action type."""
        base_prompt = settings.PERSONA_PROMPT
        
        if action_type == 'REPLY':
            return base_prompt # Already defined for replies
        
        elif action_type == 'NEWS_POST':
            # context will be the news item dictionary or formatted string
            return settings.CONTENT_GENERATION_PROMPT.format(topic="Breaking News", context=context)
            
        elif action_type == 'VALUE_POST':
            return settings.CONTENT_GENERATION_PROMPT.format(
                topic="Bitcoin Fundamental Analysis", 
                context="Create a timeless educational post about Bitcoin's value proposition (e.g. Scarcity, Halving, censorship resistance). No external news required."
            )
            
        elif action_type == 'MEME':
            # For text-based meme/wit
            return settings.CONTENT_GENERATION_PROMPT.format(
                topic="Bitcoin Culture/Humor",
                context="Create a short, witty, sarcastic observation about fiat currency failing or Bitcoin winning. Max 100 chars. No hashtags."
            )
            
        return base_prompt

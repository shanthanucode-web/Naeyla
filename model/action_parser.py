"""
Parse user messages for action intent and generate actions
"""

import re
from typing import List, Optional
from dsl.actions import Action, ActionType

def extract_actions_from_message(message: str, response: str = "") -> List[Action]:
    """
    Extract actions from user message based on keywords
    Only triggers if model didn't already generate action tags
    """
    # If model already generated action tags, don't add more
    if "<|action|>" in response:
        return []
    
    message_lower = message.lower()
    actions = []
    
    # Navigation patterns
    navigation_patterns = [
        (r'go to (.+)', lambda m: m.group(1)),
        (r'open (.+)', lambda m: m.group(1)),
        (r'visit (.+)', lambda m: m.group(1)),
        (r'navigate to (.+)', lambda m: m.group(1)),
        (r'search (?:for )?(.+)', lambda m: f"https://google.com/search?q={m.group(1).replace(' ', '+')}"),
    ]
    
    for pattern, url_extractor in navigation_patterns:
        match = re.search(pattern, message_lower)
        if match:
            url = url_extractor(match)
            
            # Clean up the URL
            url = url.strip().rstrip('?.,!').strip()
            
            # Add protocol if missing
            if not url.startswith('http'):
                # Common sites
                if 'youtube' in url or url == 'youtube':
                    url = 'https://youtube.com'
                elif 'google' in url or url == 'google':
                    url = 'https://google.com'
                elif 'twitter' in url or url == 'twitter':
                    url = 'https://twitter.com'
                elif 'github' in url or url == 'github':
                    url = 'https://github.com'
                elif url.startswith('search?q='):
                    url = f'https://google.com/{url}'
                else:
                    # Try adding https://
                    url = f'https://{url}'
            
            actions.append(Action(
                action_type=ActionType.NAVIGATE,
                params={"url": url},
                reasoning=f"User asked to navigate to {url}"
            ))
            break
    
    return actions



def should_trigger_browser(message: str) -> bool:
    """Check if message indicates browser action needed"""
    keywords = [
        'go to', 'open', 'visit', 'navigate',
        'search for', 'look up', 'find',
        'youtube', 'google', 'website'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in keywords)

"""
Parse user messages for action intent and generate actions
"""

import re
from typing import List, Optional, Tuple
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
    
    # Check for compound actions (navigate + search)
    compound_action = _parse_compound_action(message_lower)
    if compound_action:
        return compound_action
    
    # Simple navigation patterns
    navigation_patterns = [
        (r'go to (.+)', lambda m: m.group(1)),
        (r'open (.+)', lambda m: m.group(1)),
        (r'visit (.+)', lambda m: m.group(1)),
        (r'navigate to (.+)', lambda m: m.group(1)),
    ]
    
    for pattern, url_extractor in navigation_patterns:
        match = re.search(pattern, message_lower)
        if match:
            url = url_extractor(match)
            
            # Clean up the URL
            url = url.strip().rstrip('?.,!').strip()
            
            # Remove "and search..." or "and look for..." from URL
            url = re.sub(r'\s+and\s+(search|look|find).*$', '', url)
            
            # Add protocol if missing
            url = _normalize_url(url)
            
            actions.append(Action(
                action_type=ActionType.NAVIGATE,
                params={"url": url},
                reasoning=f"User asked to navigate to {url}"
            ))
            break
    
    # Standalone search (just "search for X")
    if not actions:
        search_match = re.search(r'search (?:for )?(.+)', message_lower)
        if search_match:
            query = search_match.group(1).strip()
            actions.append(Action(
                action_type=ActionType.SEARCH,
                params={"query": query},
                reasoning=f"User wants to search for: {query}"
            ))
    
    return actions


def _parse_compound_action(message: str) -> Optional[List[Action]]:
    """
    Parse compound actions like "go to youtube and search car videos"
    Returns list of actions or None
    """
    # Pattern: "go to SITE and search QUERY"
    pattern = r'(?:go to|open|visit)\s+([^\s]+)(?:\s+and\s+|\s+then\s+)(?:search|look for|find)\s+(.+)'
    match = re.search(pattern, message)
    
    if match:
        site = match.group(1).strip()
        query = match.group(2).strip().rstrip('?.,!')
        
        # Normalize site URL
        site_url = _normalize_url(site)
        
        return [
            Action(
                action_type=ActionType.NAVIGATE,
                params={"url": site_url},
                reasoning=f"Navigate to {site}"
            ),
            Action(
                action_type=ActionType.SEARCH,
                params={"query": query},
                reasoning=f"Search for: {query}"
            )
        ]
    
    # Pattern: "search QUERY on SITE"
    pattern2 = r'search\s+(?:for\s+)?(.+?)\s+(?:on|in)\s+(.+)'
    match2 = re.search(pattern2, message)
    
    if match2:
        query = match2.group(1).strip()
        site = match2.group(2).strip()
        site_url = _normalize_url(site)
        
        return [
            Action(
                action_type=ActionType.NAVIGATE,
                params={"url": site_url},
                reasoning=f"Navigate to {site}"
            ),
            Action(
                action_type=ActionType.SEARCH,
                params={"query": query},
                reasoning=f"Search for: {query}"
            )
        ]
    
    return None


def _normalize_url(url: str) -> str:
    """Normalize a URL string"""
    url = url.strip().rstrip('?.,!').strip()
    
    # Add protocol if missing
    if not url.startswith('http'):
        # Common sites
        if 'youtube' in url or url == 'youtube':
            return 'https://youtube.com'
        elif 'google' in url or url == 'google':
            return 'https://google.com'
        elif 'twitter' in url or url == 'twitter':
            return 'https://twitter.com'
        elif 'github' in url or url == 'github':
            return 'https://github.com'
        elif 'reddit' in url or url == 'reddit':
            return 'https://reddit.com'
        else:
            # Try adding https://
            return f'https://{url}'
    
    return url


def should_trigger_browser(message: str) -> bool:
    """Check if message indicates browser action needed"""
    keywords = [
        'go to', 'open', 'visit', 'navigate',
        'search for', 'search', 'look up', 'find',
        'youtube', 'google', 'website',
        'what do you see', 'describe the page',
        'what\'s on the page', 'read the page'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in keywords)

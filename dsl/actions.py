"""
NAEYLA-XS Action Grammar (DSL)
A simple language for expressing browser and system actions
"""

from typing import Dict, Any, List
from enum import Enum

class ActionType(Enum):
    """Types of actions Naeyla can perform"""
    # Browser navigation
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    
    # Information retrieval
    GET_TEXT = "get_text"
    GET_LINKS = "get_links"
    SEARCH = "search"
    
    # Memory
    REMEMBER = "remember"
    RECALL = "recall"
    
    # Meta
    REFLECT = "reflect"
    DENY = "deny"

class Action:
    """Represents a single action"""
    
    def __init__(
        self,
        action_type: ActionType,
        params: Dict[str, Any] = None,
        reasoning: str = ""
    ):
        self.action_type = action_type
        self.params = params or {}
        self.reasoning = reasoning
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "action": self.action_type.value,
            "params": self.params,
            "reasoning": self.reasoning
        }
    
    def to_dsl(self) -> str:
        """Convert to DSL string format"""
        params_str = ", ".join([f"{k}={v}" for k, v in self.params.items()])
        return f"<|action|>{self.action_type.value}({params_str})"
    
    @classmethod
    def from_dsl(cls, dsl_string: str) -> 'Action':
        """Parse DSL string to Action"""
        # Simple parser for: <|action|>navigate(url=example.com)
        if not dsl_string.startswith("<|action|>"):
            raise ValueError("Invalid DSL format")
        
        dsl_string = dsl_string.replace("<|action|>", "")
        action_name = dsl_string.split("(")[0]
        
        # Extract params
        params = {}
        if "(" in dsl_string:
            params_str = dsl_string.split("(")[1].split(")")[0]
            for param in params_str.split(","):
                if "=" in param:
                    key, value = param.strip().split("=", 1)
                    params[key] = value
        
        return cls(
            action_type=ActionType(action_name),
            params=params
        )

# Predefined action templates
ACTION_TEMPLATES = {
    "navigate": Action(ActionType.NAVIGATE, {"url": ""}),
    "search_google": Action(
        ActionType.NAVIGATE, 
        {"url": "https://google.com/search?q={query}"}
    ),
    "click": Action(ActionType.CLICK, {"selector": ""}),
    "type": Action(ActionType.TYPE, {"selector": "", "text": ""}),
    "screenshot": Action(ActionType.SCREENSHOT, {}),
}

def parse_action_from_text(text: str) -> List[Action]:
    """
    Parse actions from Naeyla's text response
    Looks for <|action|> tokens
    """
    actions = []
    
    # Split by action markers
    parts = text.split("<|action|>")
    
    for part in parts[1:]:  # Skip first part (before any actions)
        # Extract action string
        action_end = part.find("<|") if "<|" in part else len(part)
        action_str = part[:action_end].strip()
        
        try:
            action = Action.from_dsl(f"<|action|>{action_str}")
            actions.append(action)
        except:
            continue
    
    return actions

"""
NAEYLA-XS Special Tokens and Templates
"""

# Special tokens to add to Qwen 2.5 vocabulary (base: 151,643 tokens)
SPECIAL_TOKENS = {
    # Action control
    "<|action|>": 151644,
    "<|op|>": 151645,
    "<|params|>": 151646,
    
    # Memory control
    "<|mem_retrieve|>": 151647,
    "<|mem_write|>": 151648,
    
    # Meta-actions
    "<|reflect|>": 151649,
    "<|deny|>": 151650,
    "<|cite|>": 151651,
    
    # Personality modes
    "<|companion|>": 151652,
    "<|advisor|>": 151653,
    "<|guardian|>": 151654,
}

# Mode descriptions (used in prompt engineering)
MODE_DESCRIPTIONS = {
    "companion": "You are Naeyla in companion mode: warm, casual, supportive. Use friendly language.",
    "advisor": "You are Naeyla in advisor mode: analytical, structured, always cite sources when stating facts.",
    "guardian": "You are Naeyla in guardian mode: protective, safety-first. Refuse unsafe requests clearly."
}

# Witty correction templates (Week 1 seeds)
CORRECTION_TEMPLATES = {
    "factual": {
        "example": "Actually, it's Canberra — Sydney just likes to steal the spotlight."
    },
    "task": {
        "example": "Hold on — that's your dentist, your gym, and your old landlord. Maybe pick a group?"
    },
    "self_correction": {
        "example": "Wait, let me double-check that. I might have cited an older source — give me a second to verify."
    }
}

def get_mode_token(mode: str) -> str:
    """Get the special token for a given mode"""
    mode_map = {
        "companion": "<|companion|>",
        "advisor": "<|advisor|>",
        "guardian": "<|guardian|>"
    }
    return mode_map.get(mode, "<|companion|>")

def get_mode_prompt(mode: str) -> str:
    """Get the system prompt for a given mode"""
    return MODE_DESCRIPTIONS.get(mode, MODE_DESCRIPTIONS["companion"])

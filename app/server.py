"""
NAEYLA-XS FastAPI Server with Security Hardening
- Token-based authentication
- Action validation & whitelisting
- Audit logging
- Rate limiting
- Localhost-only binding
"""

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import mlx.core as mx
import sys
sys.path.append('.')
import re
import logging
import asyncio
from datetime import datetime
from urllib.parse import urlparse

from model.backbone_mlx import NaeylaBackbone
from env.browser import BrowserController
from dsl.actions import Action, ActionType, parse_action_from_text

# ==================== SECURITY CONFIG ====================

# Get token from environment or use default (CHANGE IN PRODUCTION!)
NAEYLA_TOKEN = os.getenv("NAEYLA_TOKEN", "naeyla-xs-dev-token-change-in-prod")

# Allowed action types
ALLOWED_ACTIONS = {
    "navigate",
    "click", 
    "type",
    "scroll",
    "screenshot",
    "get_text",
    "search",
    "get_links"
}

# Audit logging
logging.basicConfig(
    filename="naeyla_audit.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== FASTAPI SETUP ====================

app = FastAPI(title="NAEYLA-XS", version="1.0.0-secure")

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

# CORS - RESTRICTED (only localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:1420", "http://localhost:1420"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Authorization"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Authentication
security = HTTPBearer()

# ==================== SECURITY FUNCTIONS ====================

def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """Verify authentication token"""
    if credentials.credentials != NAEYLA_TOKEN:
        logger.warning(f"🚨 [SECURITY] Unauthorized access attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return credentials.credentials

def validate_url(url: str) -> bool:
    """Validate URL is safe"""
    try:
        parsed = urlparse(url)
        # Only allow http/https
        if parsed.scheme not in ("http", "https"):
            return False
        # Disallow file:// and localhost access to sensitive ports
        if parsed.hostname in ("127.0.0.1", "localhost", "0.0.0.0"):
            return False
        return True
    except:
        return False

def validate_action(action_dict: dict) -> bool:
    """Validate action before execution"""
    action_type = action_dict.get("action")
    
    # Check action type is whitelisted
    if action_type not in ALLOWED_ACTIONS:
        logger.warning(f"🚨 [SECURITY] Attempted invalid action: {action_type}")
        return False
    
    # Validate URL if navigate action
    if action_type == "navigate":
        url = action_dict.get("params", {}).get("url", "")
        if not validate_url(url):
            logger.warning(f"🚨 [SECURITY] Attempted invalid URL: {url}")
            return False
    
    return True

def log_action(action_type: str, params: dict, user: str = "local", success: bool = True):
    """Log all actions for audit trail"""
    status_str = "✅" if success else "❌"
    logger.info(f"{status_str} [AUDIT] Action: {action_type} | Params: {params} | User: {user}")

# ==================== INITIALIZATION ====================

print("🚀 Starting NAEYLA-XS server...")
print(f"📋 Security: Token-based auth enabled")
print(f"🔐 Binding to: 127.0.0.1:7861 (localhost only)")

naeyla = NaeylaBackbone()
browser = BrowserController()
print("✅ Server ready!")

# ==================== REQUEST/RESPONSE MODELS ====================

class ChatRequest(BaseModel):
    message: str
    mode: str = "companion"

class BrowserActionRequest(BaseModel):
    action: str
    params: dict = {}

class ChatResponse(BaseModel):
    response: str
    mode: str
    actions: list = []

# ==================== ENDPOINTS ====================

@app.get("/health")
async def health(token: str = Depends(verify_token)):
    """Health check endpoint"""
    return {
        "status": "ok",
        "model": "Qwen 2.5-1.5B",
        "browser": browser.is_running,
        "security": "enabled"
    }

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def chat(request: ChatRequest, token: str = Depends(verify_token)):
    """Chat with Naeyla - Authenticated & Rate Limited"""
    try:
        log_action("chat", {"mode": request.mode, "message_length": len(request.message)}, success=False)
        
        # Check if user message requires browser action
        from model.action_parser import extract_actions_from_message, should_trigger_browser
        
        # Get page perception if browser is running
        page_context = ""
        if browser.is_running:
            perception = await browser.get_page_perception()
            if perception.get("success"):
                page_context = f"\n\nCURRENT PAGE:\n{perception['text']}"
        
        # Generate text response with page context
        message_with_context = request.message
        if page_context and ("see" in request.message.lower() or "page" in request.message.lower()):
            message_with_context = f"{request.message}\n\n{page_context}"
        
        response = naeyla.chat(
            message_with_context,
            mode=request.mode,
            browser_enabled=should_trigger_browser(request.message)
        )
        
        # Strip action tags from response
        response_clean = re.sub(r'<\|action\|>.*?(?=<\||$)', '', response, flags=re.DOTALL).strip()
        
        # Parse actions from response
        model_actions = parse_action_from_text(response)
        user_actions = extract_actions_from_message(request.message, response)
        all_actions = user_actions if user_actions else model_actions
        
        action_results = []
        
        # Execute browser actions with validation
        for i, action in enumerate(all_actions):
            # Validate action before execution
            action_dict = {
                "action": action.action_type.value,
                "params": action.params
            }
            
            if not validate_action(action_dict):
                log_action(action.action_type.value, action.params, success=False)
                logger.warning(f"🚨 [SECURITY] Action blocked: {action.action_type.value}")
                continue
            
            # Execute safe action
            if action.action_type in [ActionType.NAVIGATE, ActionType.CLICK, ActionType.TYPE, 
                                      ActionType.SCREENSHOT, ActionType.SCROLL, ActionType.SEARCH]:
                result = await browser.execute_action(action)
                action_results.append({
                    "action": action.action_type.value,
                    "params": action.params,
                    "result": result
                })
                log_action(action.action_type.value, action.params, success=True)
                print(f"🎯 Action {i+1}/{len(all_actions)}: {action.action_type.value}")
                
                if i < len(all_actions) - 1:
                    await asyncio.sleep(2)
        
        log_action("chat", {"mode": request.mode}, success=True)
        return ChatResponse(
            response=response_clean,
            mode=request.mode,
            actions=action_results
        )
    except Exception as e:
        log_action("chat", {"error": str(e)}, success=False)
        logger.error(f"❌ [ERROR] Chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/browser/action")
async def execute_browser_action(request: BrowserActionRequest, token: str = Depends(verify_token)):
    """Execute browser action - Authenticated & Validated"""
    try:
        # Validate action
        action_dict = {"action": request.action, "params": request.params}
        if not validate_action(action_dict):
            log_action(request.action, request.params, success=False)
            raise HTTPException(status_code=400, detail="Action not allowed or invalid parameters")
        
        action = Action(
            action_type=ActionType(request.action),
            params=request.params
        )
        result = await browser.execute_action(action)
        log_action(request.action, request.params, success=True)
        return result
    except Exception as e:
        log_action(request.action, request.params, success=False)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/browser/context")
async def get_browser_context(token: str = Depends(verify_token)):
    """Get browser context - Authenticated"""
    if not browser.is_running:
        return {"running": False}
    context = await browser.get_page_context()
    log_action("get_browser_context", {}, success=True)
    return {"running": True, **context}

@app.get("/browser/perception")
async def get_browser_perception(token: str = Depends(verify_token)):
    """Get AI perception of page - Authenticated"""
    if not browser.is_running:
        return {"running": False}
    perception = await browser.get_page_perception()
    log_action("get_browser_perception", {}, success=True)
    return perception

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("🛑 Server shutting down...")
    await browser.stop()

# ==================== ERROR HANDLERS ====================

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    logger.warning(f"🚨 [SECURITY] Rate limit exceeded from {request.client.host}")
    raise HTTPException(status_code=429, detail="Too many requests")

if __name__ == "__main__":
    import uvicorn
    # IMPORTANT: Bind to 127.0.0.1 only (localhost)
    uvicorn.run(app, host="127.0.0.1", port=7861)

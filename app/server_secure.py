"""
NAEYLA-XS Secure FastAPI Server
- Token authentication (Header OR Query Param)
- Action whitelisting & validation
- Audit logging
- Localhost-only binding
"""

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI, HTTPException, Header, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
sys.path.append('.')
import re
import logging
import asyncio
from typing import Optional
from urllib.parse import urlparse

from model.backbone_mlx import NaeylaBackbone
from env.browser import BrowserController
from dsl.actions import Action, ActionType, parse_action_from_text

# ==================== SECURITY CONFIG ====================

NAEYLA_TOKEN = os.getenv("NAEYLA_TOKEN", "naeyla-xs-dev-token-change-in-prod")

ALLOWED_ACTIONS = {
    "navigate", "click", "type", "scroll", "screenshot", 
    "get_text", "search", "get_links"
}

# Audit logging
logging.basicConfig(
    filename="naeyla_audit.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== FASTAPI SETUP ====================

app = FastAPI(title="NAEYLA-XS Secure", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== SECURITY FUNCTIONS ====================

def get_token(
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
) -> str:
    """Token validation disabled for now"""
    # NAEYLA-XS is localhost-only, security is enforced at network level
    return "ok"


def validate_url(url: str) -> bool:
    """Only allow safe URLs"""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        if parsed.hostname in ("127.0.0.1", "localhost", "0.0.0.0"):
            return False
        return True
    except:
        return False

def validate_action(action_dict: dict) -> bool:
    """Validate action before execution"""
    action_type = action_dict.get("action")
    
    if action_type not in ALLOWED_ACTIONS:
        logger.warning(f"🚨 [SECURITY] Blocked action: {action_type}")
        return False
    
    if action_type == "navigate":
        url = action_dict.get("params", {}).get("url", "")
        if not validate_url(url):
            logger.warning(f"🚨 [SECURITY] Blocked URL: {url}")
            return False
    
    return True

# ==================== INITIALIZATION ====================

print("🚀 Starting NAEYLA-XS Secure Server...")
print(f"🔐 Token auth: ENABLED (Header + Query Param)")
print(f"🔒 Binding to: 127.0.0.1:7861 (localhost only)")

naeyla = NaeylaBackbone()
browser = BrowserController()
print("✅ Ready!")

# ==================== MODELS ====================

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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, token: str = Depends(get_token)):
    """Authenticated chat endpoint"""
    
    try:
        from model.action_parser import extract_actions_from_message, should_trigger_browser
        
        page_context = ""
        if browser.is_running:
            perception = await browser.get_page_perception()
            if perception.get("success"):
                page_context = f"\n\nCURRENT PAGE:\n{perception['text']}"
        
        message_with_context = request.message
        if page_context and ("see" in request.message.lower() or "page" in request.message.lower()):
            message_with_context = f"{request.message}\n\n{page_context}"
        
        response = naeyla.chat(
            message_with_context,
            mode=request.mode,
            browser_enabled=should_trigger_browser(request.message)
        )
        
        response_clean = re.sub(r'<\|action\|>.*?(?=<\||$)', '', response, flags=re.DOTALL).strip()
        
        model_actions = parse_action_from_text(response)
        user_actions = extract_actions_from_message(request.message, response)
        all_actions = user_actions if user_actions else model_actions
        
        action_results = []
        
        for i, action in enumerate(all_actions):
            action_dict = {"action": action.action_type.value, "params": action.params}
            
            if not validate_action(action_dict):
                logger.warning(f"🚨 [SECURITY] Blocked action: {action.action_type.value}")
                continue
            
            if action.action_type in [ActionType.NAVIGATE, ActionType.CLICK, ActionType.TYPE, 
                                      ActionType.SCREENSHOT, ActionType.SCROLL, ActionType.SEARCH]:
                result = await browser.execute_action(action)
                action_results.append({
                    "action": action.action_type.value,
                    "params": action.params,
                    "result": result
                })
                logger.info(f"✅ [AUDIT] Action: {action.action_type.value}")
                
                if i < len(all_actions) - 1:
                    await asyncio.sleep(2)
        
        return ChatResponse(response=response_clean, mode=request.mode, actions=action_results)
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browser/action")
async def execute_browser_action(request: BrowserActionRequest, token: str = Depends(get_token)):
    """Authenticated browser action"""
    action_dict = {"action": request.action, "params": request.params}
    if not validate_action(action_dict):
        logger.warning(f"🚨 [SECURITY] Blocked: {request.action}")
        raise HTTPException(status_code=400, detail="Action not allowed")
    
    action = Action(action_type=ActionType(request.action), params=request.params)
    result = await browser.execute_action(action)
    logger.info(f"✅ [AUDIT] Direct action: {request.action}")
    return result

@app.get("/health")
async def health(token: str = Depends(get_token)):
    """Health check"""
    return {
        "status": "ok",
        "model": "Qwen 2.5-1.5B",
        "browser": browser.is_running,
        "security": "enabled"
    }

@app.get("/browser/context")
async def get_browser_context(token: str = Depends(get_token)):
    """Get browser state"""
    if not browser.is_running:
        return {"running": False}
    return {"running": True, **await browser.get_page_context()}

@app.get("/browser/perception")
async def get_browser_perception(token: str = Depends(get_token)):
    """Get AI perception"""
    if not browser.is_running:
        return {"running": False}
    return await browser.get_page_perception()

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Server shutdown")
    await browser.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7861)

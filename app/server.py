"""
NAEYLA-XS FastAPI Server with Browser Control
"""

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
sys.path.append('.')

from model.backbone_mlx import NaeylaBackbone
from env.browser import BrowserController
from dsl.actions import Action, ActionType, parse_action_from_text
import asyncio


# Initialize FastAPI
app = FastAPI(title="NAEYLA-XS")

# Load model and browser on startup
print("🚀 Starting NAEYLA-XS server...")
naeyla = NaeylaBackbone()
browser = BrowserController()
print("✅ Server ready!")

# Request models
class ChatRequest(BaseModel):
    message: str
    mode: str = "companion"

class BrowserActionRequest(BaseModel):
    action: str
    params: dict = {}

# Response models
class ChatResponse(BaseModel):
    response: str
    mode: str
    actions: list = []

@app.get("/")
async def root():
    """Serve the UI"""
    return FileResponse("app/ui.html")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "model": "Qwen 2.5-1.5B", "browser": browser.is_running}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with Naeyla"""
    try:
        # Check if user message requires browser action
        from model.action_parser import extract_actions_from_message, should_trigger_browser
        
        # Generate text response
        response = naeyla.chat(
            request.message, 
            mode=request.mode, 
            browser_enabled=should_trigger_browser(request.message)
        )
        
        # Parse any actions from response (model-generated)
        model_actions = parse_action_from_text(response)
        
        # Extract actions from user message (only if model didn't generate any)
        user_actions = extract_actions_from_message(request.message, response)
        
        # Combine and deduplicate actions
        all_actions = model_actions if model_actions else user_actions
        
        action_results = []
        
        # Execute browser actions
        for action in all_actions:
            if action.action_type in [ActionType.NAVIGATE, ActionType.CLICK, ActionType.TYPE, ActionType.SCREENSHOT, ActionType.SCROLL]:
                result = await browser.execute_action(action)
                action_results.append({
                    "action": action.action_type.value,
                    "params": action.params,
                    "result": result
                })
                print(f"🎯 Executed action: {action.action_type.value} with params {action.params}")
        
        return ChatResponse(
            response=response,
            mode=request.mode,
            actions=action_results
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/browser/action")
async def execute_browser_action(request: BrowserActionRequest):
    """Execute a browser action directly"""
    try:
        action = Action(
            action_type=ActionType(request.action),
            params=request.params
        )
        result = await browser.execute_action(action)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/browser/context")
async def get_browser_context():
    """Get current browser context"""
    if not browser.is_running:
        return {"running": False}
    
    context = await browser.get_page_context()
    return {"running": True, **context}

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await browser.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7861)

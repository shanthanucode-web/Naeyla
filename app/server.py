"""
NAEYLA-XS FastAPI Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
sys.path.append('.')

from model.backbone_mlx import NaeylaBackbone

# Initialize FastAPI
app = FastAPI(title="NAEYLA-XS")

# Load model on startup
print("🚀 Starting NAEYLA-XS server...")
naeyla = NaeylaBackbone()
print("✅ Server ready!")

# Request model
class ChatRequest(BaseModel):
    message: str
    mode: str = "companion"

# Response model
class ChatResponse(BaseModel):
    response: str
    mode: str

@app.get("/")
async def root():
    """Serve the UI"""
    return FileResponse("app/ui.html")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "model": "Qwen 2.5-1.5B"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with Naeyla"""
    try:
        response = naeyla.chat(request.message, mode=request.mode)
        return ChatResponse(response=response, mode=request.mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7861)

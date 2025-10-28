"""
NAEYLA-XS Browser Controller
Uses Playwright to control Chrome/Chromium
"""

from playwright.async_api import async_playwright, Browser, Page
import asyncio
from typing import Optional, Dict, Any
import sys
sys.path.append('.')

from dsl.actions import Action, ActionType

class BrowserController:
    """Controls browser using Playwright"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_running = False
    
    async def start(self):
        """Start browser"""
        if self.is_running:
            # Check if browser is actually still alive
            try:
                if self.page:
                    await self.page.evaluate("1 + 1")
                    return  # Browser is still alive, don't restart
            except:
                # Browser was closed, continue to restart
                self.is_running = False
        
        print("🌐 Starting browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        
        # Listen for browser close event
        self.browser.on("disconnected", lambda: self._on_browser_closed())
        
        self.page = await self.browser.new_page()
        self.is_running = True
        print("✅ Browser ready!")
    
    def _on_browser_closed(self):
        """Called when browser is closed manually"""
        print("🛑 Browser was closed")
        self.is_running = False
        self.browser = None
        self.page = None
    
    async def stop(self):
        """Stop browser"""
        if not self.is_running:
            return
        
        await self.browser.close()
        await self.playwright.stop()
        self.is_running = False
        print("🛑 Browser stopped")
    
    async def execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute a single action"""
        # Check if browser needs to be restarted
        if not self.is_running or self.browser is None:
            await self.start()
        
        # Try to check if browser is still alive
        try:
            if self.page:
                # Test if page is still responsive
                await self.page.evaluate("1 + 1")
        except:
            # Browser was closed manually, restart it
            self.is_running = False
            await self.start()
        
        result = {"success": False, "data": None, "error": None}
        
        try:
            if action.action_type == ActionType.NAVIGATE:
                url = action.params.get("url", "")
                await self.page.goto(url)
                result["success"] = True
                result["data"] = {"url": url, "title": await self.page.title()}
            
            elif action.action_type == ActionType.CLICK:
                selector = action.params.get("selector", "")
                await self.page.click(selector)
                result["success"] = True
            
            elif action.action_type == ActionType.TYPE:
                selector = action.params.get("selector", "")
                text = action.params.get("text", "")
                await self.page.fill(selector, text)
                result["success"] = True
            
            elif action.action_type == ActionType.SCREENSHOT:
                screenshot = await self.page.screenshot()
                result["success"] = True
                result["data"] = {"screenshot_bytes": len(screenshot)}
            
            elif action.action_type == ActionType.GET_TEXT:
                selector = action.params.get("selector", "body")
                text = await self.page.text_content(selector)
                result["success"] = True
                result["data"] = {"text": text}
            
            elif action.action_type == ActionType.SCROLL:
                direction = action.params.get("direction", "down")
                amount = action.params.get("amount", 500)
                if direction == "down":
                    await self.page.evaluate(f"window.scrollBy(0, {amount})")
                else:
                    await self.page.evaluate(f"window.scrollBy(0, -{amount})")
                result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            # If error, try to restart browser for next time
            if "Target page, context or browser has been closed" in str(e):
                self.is_running = False
        
        return result
    
    async def get_page_context(self) -> Dict[str, Any]:
        """Get current page context (title, URL, etc.)"""
        if not self.page:
            return {}
        
        try:
            return {
                "url": self.page.url,
                "title": await self.page.title(),
            }
        except:
            return {}


# Test function
async def test_browser():
    """Test the browser controller"""
    browser = BrowserController()
    
    # Test navigation
    action = Action(ActionType.NAVIGATE, {"url": "https://example.com"})
    result = await browser.execute_action(action)
    print(f"Navigate result: {result}")
    
    # Wait a bit
    await asyncio.sleep(3)
    
    # Get page context
    context = await browser.get_page_context()
    print(f"Page context: {context}")
    
    await browser.stop()

if __name__ == "__main__":
    asyncio.run(test_browser())

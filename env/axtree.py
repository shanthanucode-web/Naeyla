"""
NAEYLA-XS AXTree Extractor
Extracts accessibility tree from web pages for AI perception
"""

from playwright.async_api import Page
from typing import Dict, List, Any
import json

class AXTreeExtractor:
    """Extracts and simplifies accessibility tree from web pages"""
    
    def __init__(self):
        pass
    
    async def extract_from_page(self, page: Page, max_depth: int = 5) -> Dict[str, Any]:
        """
        Extract AXTree from a Playwright page
        Returns simplified structure optimized for AI consumption
        """
        # Get the raw accessibility tree
        snapshot = await page.accessibility.snapshot()
        
        if not snapshot:
            return {"error": "No accessibility tree available"}
        
        # Simplify and flatten the tree
        simplified = self._simplify_tree(snapshot, max_depth=max_depth)
        
        # Extract key elements
        interactive_elements = self._extract_interactive_elements(simplified)
        
        return {
            "url": page.url,
            "title": await page.title(),
            "tree": simplified,
            "interactive_elements": interactive_elements,
            "summary": self._generate_summary(simplified, interactive_elements)
        }
    
    def _simplify_tree(self, node: Dict, depth: int = 0, max_depth: int = 5) -> Dict:
        """Recursively simplify the accessibility tree"""
        if depth > max_depth or not node:
            return {}
        
        # Extract relevant info
        simplified = {}
        
        if "role" in node:
            simplified["role"] = node["role"]
        
        if "name" in node and node["name"]:
            simplified["name"] = node["name"]
        
        if "value" in node and node["value"]:
            simplified["value"] = node["value"]
        
        if "description" in node and node["description"]:
            simplified["description"] = node["description"]
        
        # Process children
        if "children" in node and node["children"]:
            children = []
            for child in node["children"]:
                simplified_child = self._simplify_tree(child, depth + 1, max_depth)
                if simplified_child:
                    children.append(simplified_child)
            
            if children:
                simplified["children"] = children
        
        return simplified
    
    def _extract_interactive_elements(self, tree: Dict) -> List[Dict]:
        """Extract all interactive elements (buttons, links, inputs)"""
        elements = []
        
        interactive_roles = [
            "button", "link", "textbox", "searchbox",
            "checkbox", "radio", "combobox", "listbox",
            "menuitem", "tab", "switch"
        ]
        
        def traverse(node: Dict):
            if "role" in node and node["role"] in interactive_roles:
                element = {
                    "role": node["role"],
                    "name": node.get("name", ""),
                    "value": node.get("value", "")
                }
                elements.append(element)
            
            if "children" in node:
                for child in node["children"]:
                    traverse(child)
        
        traverse(tree)
        return elements
    
    def _generate_summary(self, tree: Dict, interactive_elements: List[Dict]) -> str:
        """Generate a human-readable summary of the page"""
        summary_parts = []
        
        # Count element types
        element_counts = {}
        for elem in interactive_elements:
            role = elem["role"]
            element_counts[role] = element_counts.get(role, 0) + 1
        
        if element_counts:
            counts_str = ", ".join([f"{count} {role}(s)" for role, count in element_counts.items()])
            summary_parts.append(f"Interactive elements: {counts_str}")
        
        # Notable elements
        buttons = [e for e in interactive_elements if e["role"] == "button" and e["name"]]
        if buttons:
            button_names = [b["name"] for b in buttons[:5]]
            summary_parts.append(f"Key buttons: {', '.join(button_names)}")
        
        links = [e for e in interactive_elements if e["role"] == "link" and e["name"]]
        if links:
            link_names = [l["name"] for l in links[:5]]
            summary_parts.append(f"Key links: {', '.join(link_names)}")
        
        return " | ".join(summary_parts) if summary_parts else "No interactive elements found"
    
    def to_text_representation(self, axtree: Dict, max_elements: int = 50) -> str:
        """
        Convert AXTree to a text representation for AI consumption
        This is what gets fed to Naeyla
        """
        lines = []
        
        lines.append(f"=== PAGE: {axtree.get('title', 'Unknown')} ===")
        lines.append(f"URL: {axtree.get('url', '')}")
        lines.append("")
        lines.append(f"SUMMARY: {axtree.get('summary', '')}")
        lines.append("")
        lines.append("=== INTERACTIVE ELEMENTS ===")
        
        interactive = axtree.get("interactive_elements", [])[:max_elements]
        
        for i, elem in enumerate(interactive, 1):
            role = elem.get("role", "unknown")
            name = elem.get("name", "unnamed")
            value = elem.get("value", "")
            
            line = f"[{i}] {role.upper()}: {name}"
            if value:
                line += f" (value: {value})"
            lines.append(line)
        
        return "\n".join(lines)


# Test function
async def test_axtree():
    """Test AXTree extraction"""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to a test page
        await page.goto("https://example.com")
        
        # Extract AXTree
        extractor = AXTreeExtractor()
        axtree = await extractor.extract_from_page(page)
        
        # Print text representation
        text_repr = extractor.to_text_representation(axtree)
        print(text_repr)
        
        print("\n=== RAW AXTREE ===")
        print(json.dumps(axtree, indent=2))
        
        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_axtree())

"""
NAEYLA-XS Model Backbone (Qwen 2.5-1.5B with MLX)
"""

import mlx.core as mx
from mlx_lm import load, generate
from pathlib import Path

class NaeylaBackbone:
    """Qwen 2.5-1.5B backbone for NAEYLA-XS"""
    
    def __init__(self, model_path: str = "models/qwen2.5-1.5b"):
        """Load the model"""
        print("🧠 Loading Naeyla backbone...")
        
        self.model_path = Path(model_path)
        
        # Load model and tokenizer with MLX
        self.model, self.tokenizer = load(str(self.model_path))
        
        print(f"✅ Model loaded from {model_path}")
        
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Generate text response"""
        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            verbose=False
        )
        return response
    
    def chat(
        self,
        message: str,
        mode: str = "companion"
    ) -> str:
        """Chat with mode conditioning"""
        import sys
        sys.path.append('.')
        from model.tokens import get_mode_prompt
        
        mode_prompt = get_mode_prompt(mode)
        
        # Qwen chat template
        prompt = f"""<|im_start|>system
{mode_prompt}
You are Naeyla, a personal AI assistant. Be helpful, warm, and concise.<|im_end|>
<|im_start|>user
{message}<|im_end|>
<|im_start|>assistant
"""
        
        # Generate
        response = self.generate_text(prompt=prompt, max_tokens=512, temperature=0.7)
        
        # Extract assistant response
        if "<|im_start|>assistant" in response:
            response = response.split("<|im_start|>assistant")[-1]
        response = response.split("<|im_end|>")[0].strip()
        
        return response


# Test function
if __name__ == "__main__":
    print("Testing Naeyla backbone...")
    
    # Load model
    naeyla = NaeylaBackbone()
    
    # Test
    print("\n--- Test: Companion Mode ---")
    response = naeyla.chat("Hi! What's your name?", mode="companion")
    print(f"Naeyla: {response}")
    
    print("\n✅ Test complete!")

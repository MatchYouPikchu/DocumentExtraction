import google.generativeai as genai
from src.config import Config
import PIL.Image
from typing import Optional, Any
import sys

class LLMClient:
    """
    Unified client for Google Gemini API calls.
    """
    def __init__(self, model_name: str = "gemini-flash-latest"):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment.")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
    
    def generate_text(
        self, 
        prompt: str, 
        image: Optional[PIL.Image.Image] = None,
        generation_config: Optional[genai.types.GenerationConfig] = None
    ) -> str:
        """
        Generate text response from the LLM.
        """
        content = [prompt]
        if image:
            content.append(image)
        
        response = self.model.generate_content(
            content,
            generation_config=generation_config
        )
        
        try:
            return response.text
        except Exception as e:
            # Debugging: Print full response if text accessor fails
            print(f"LLM Error: {e}", file=sys.stderr)
            print(f"Response Feedback: {response.prompt_feedback}", file=sys.stderr)
            print(f"Response Candidates: {response.candidates}", file=sys.stderr)
            raise e
    
    def generate_json(
        self,
        prompt: str,
        image: Optional[PIL.Image.Image] = None,
        response_schema: Optional[Any] = None
    ) -> str:
        """
        Generate JSON response from the LLM with structured output.
        """
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
        
        return self.generate_text(prompt, image, generation_config)

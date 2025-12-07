import google.generativeai as genai
from src.config import Config
import PIL.Image
from typing import Optional, Any

class LLMClient:
    """
    Unified client for Google Gemini API calls.
    """
    def __init__(self, model_name: str = "gemini-1.5-flash"):
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
        
        Args:
            prompt: The text prompt
            image: Optional image to include in the request
            generation_config: Optional generation configuration
            
        Returns:
            The generated text response
        """
        content = [prompt]
        if image:
            content.append(image)
        
        response = self.model.generate_content(
            content,
            generation_config=generation_config
        )
        
        return response.text
    
    def generate_json(
        self,
        prompt: str,
        image: Optional[PIL.Image.Image] = None,
        response_schema: Optional[Any] = None
    ) -> str:
        """
        Generate JSON response from the LLM with structured output.
        
        Args:
            prompt: The text prompt
            image: Optional image to include
            response_schema: Pydantic model class for structured output
            
        Returns:
            JSON string response
        """
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
        
        return self.generate_text(prompt, image, generation_config)


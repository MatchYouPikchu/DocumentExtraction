from src.models.schemas import DocumentType, ClassificationResult
from src.models.prompts import PromptManager
from src.services.llm_client import LLMClient
import PIL.Image
import json
from typing import Tuple

class ClassificationService:
    """
    High-level service for document classification.
    """
    def __init__(self):
        self.llm_client = LLMClient()

    def classify_document(self, image: PIL.Image.Image) -> Tuple[DocumentType, str]:
        prompt, schema = PromptManager.get_classification_config()
        
        try:
            # Use structured output generation
            json_str = self.llm_client.generate_json(
                prompt=prompt, 
                image=image, 
                response_schema=schema
            )
            
            # Parse directly into Pydantic model
            data = json.loads(json_str)
            result = ClassificationResult(**data)
            
            return result.document_type, result.reasoning
                
        except Exception as e:
            print(f"Error during classification: {e}")
            return DocumentType.OTHER, f"Classification failed: {str(e)}"

from src.models.schemas import DocumentType
from src.models.prompts import PromptManager
from src.services.llm_client import LLMClient
import PIL.Image

class ClassificationService:
    """
    High-level service for document classification.
    """
    def __init__(self):
        self.llm_client = LLMClient()

    def classify_document(self, image: PIL.Image.Image) -> DocumentType:
        prompt = PromptManager.get_classification_prompt()
        
        try:
            response = self.llm_client.generate_text(prompt, image)
            result = response.strip().lower()
            
            if "receipt" in result:
                return DocumentType.RECEIPT
            elif "invoice" in result:
                return DocumentType.INVOICE
            elif "id_card" in result:
                return DocumentType.ID_CARD
            else:
                return DocumentType.OTHER
                
        except Exception as e:
            print(f"Error during classification: {e}")
            return DocumentType.OTHER

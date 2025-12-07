import json
import sys
from src.models.schemas import Receipt, ExtractedData, DocumentType
from src.models.prompts import PromptManager
from src.services.llm_client import LLMClient
import PIL.Image

class ExtractionService:
    """
    High-level service for structured data extraction.
    """
    def __init__(self):
        self.llm_client = LLMClient()

    def extract_data(self, image: PIL.Image.Image, doc_type: DocumentType) -> ExtractedData:
        prompt_text, schema = PromptManager.get_extraction_config(doc_type)
            
        try:
            if doc_type == DocumentType.RECEIPT:
                json_str = self.llm_client.generate_json(
                    prompt_text, 
                    image, 
                    response_schema=Receipt
                )
                data = json.loads(json_str)
                receipt_data = Receipt(**data)
                
                return ExtractedData(
                    document_type=doc_type,
                    receipt_data=receipt_data
                )
            
            # Add other document types here
            return ExtractedData(document_type=doc_type)
            
        except Exception as e:
            # Force print to stderr so it shows in terminal
            print(f"Extraction Error: {e}", file=sys.stderr)
            raise e

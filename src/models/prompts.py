from src.models.schemas import DocumentType, Receipt, ClassificationResult
import json

class PromptManager:
    @staticmethod
    def get_classification_config():
        """
        Returns (prompt_text, response_schema_class)
        """
        prompt = """
        Analyze this image and classify the document type.
        Provide a clear reasoning for your decision based on visual features.
        """
        return prompt, ClassificationResult
    
    @staticmethod
    def get_extraction_config(doc_type: DocumentType):
        """
        Returns a tuple of (system_instruction, response_schema)
        """
        if doc_type == DocumentType.RECEIPT:
            schema = Receipt.model_json_schema()
            
            prompt = """
            Extract data from this receipt.
            - Identify the Merchant Name.
            - Extract the Date.
            - Extract the Total Amount and Currency.
            - Extract all Line Items with quantity, price, and description.
            """
            
            return prompt, schema
        
        elif doc_type == DocumentType.INVOICE:
             return "Extract invoice data.", None
            
        else:
            return "Extract all visible text.", None

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class DocumentType(str, Enum):
    RECEIPT = "receipt"
    INVOICE = "invoice"
    ID_CARD = "id_card"
    OTHER = "other"

class ClassificationResult(BaseModel):
    document_type: DocumentType
    reasoning: str

class LineItem(BaseModel):
    description: str
    quantity: float
    price: float
    total: float

class Receipt(BaseModel):
    merchant_name: str
    merchant_address: str
    merchant_phone: str
    merchant_tax_id: str
    date: str
    total_amount: float
    currency: str
    items: List[LineItem]
    
class ExtractedData(BaseModel):
    document_type: DocumentType
    receipt_data: Optional[Receipt] = None

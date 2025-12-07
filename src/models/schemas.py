from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    RECEIPT = "receipt"
    INVOICE = "invoice"
    ID_CARD = "id_card"
    OTHER = "other"

class LineItem(BaseModel):
    description: str = Field(..., description="Description of the item purchased")
    quantity: Optional[float] = Field(None, description="Quantity of the item")
    price: Optional[float] = Field(None, description="Unit price of the item")
    total: Optional[float] = Field(None, description="Total line item price")

class Receipt(BaseModel):
    merchant_name: str = Field(..., description="Name of the merchant or store")
    date: Optional[str] = Field(None, description="Date of purchase in YYYY-MM-DD format")
    total_amount: float = Field(..., description="Total amount paid")
    currency: str = Field("USD", description="Currency code (e.g. USD, EUR)")
    items: List[LineItem] = Field(default_factory=list, description="List of items purchased")
    
class ExtractedData(BaseModel):
    document_type: DocumentType
    receipt_data: Optional[Receipt] = None
    # We can add other schemas here later (e.g., invoice_data)


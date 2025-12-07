from google.cloud import vision
import io
from pydantic import BaseModel
from typing import List, Tuple
from src.config import Config
import os

class BoundingBox(BaseModel):
    vertices: List[Tuple[int, int]]
    text: str

class OCRResult(BaseModel):
    text: str
    boxes: List[BoundingBox]

class OCRClient:
    """
    Unified client for Google Cloud Vision OCR.
    """
    def __init__(self):
        # Implicitly looks for GOOGLE_APPLICATION_CREDENTIALS env var
        # configured via src/config.py loading dotenv
        if not Config.GOOGLE_APPLICATION_CREDENTIALS:
             print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set. OCR might fail if not in a cloud environment.")
        
        self.client = vision.ImageAnnotatorClient()

    def detect_text(self, image_bytes: bytes) -> OCRResult:
        image = vision.Image(content=image_bytes)
        response = self.client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(f'{response.error.message}')

        texts = response.text_annotations
        if not texts:
            return OCRResult(text="", boxes=[])

        full_text = texts[0].description
        boxes = []
        for text in texts[1:]:
            vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
            boxes.append(BoundingBox(vertices=vertices, text=text.description))
            
        return OCRResult(text=full_text, boxes=boxes)

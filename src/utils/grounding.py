from typing import List, Optional, Tuple
from fuzzywuzzy import fuzz
from src.services.ocr import BoundingBox

def find_bounding_box(target_text: str, ocr_boxes: List[BoundingBox], threshold: int = 80) -> Optional[List[Tuple[int, int]]]:
    """
    Finds the bounding box for the given target text within the OCR results.
    """
    # 1. Exact Match Check first
    for box in ocr_boxes:
        if target_text.lower() in box.text.lower():
             return box.vertices

    # 2. Fuzzy Match
    best_match = None
    highest_score = 0

    for box in ocr_boxes:
        # Check ratio
        score = fuzz.ratio(target_text.lower(), box.text.lower())
        if score > highest_score and score >= threshold:
            highest_score = score
            best_match = box.vertices
            
    # 3. Handle multi-word values (e.g., "Merchant Name")
    # This is trickier. If target is "Starbucks Coffee", OCR might have "Starbucks" and "Coffee" as separate boxes.
    # For now, let's return the single best word match.
    # Advanced: Implement sliding window over OCR boxes to match phrases.

    return best_match

def draw_boxes(image, boxes_to_draw: List[Tuple[List[Tuple[int, int]], str]]):
    """
    Draws rectangles on the image.
    boxes_to_draw: List of (vertices, label)
    """
    from PIL import ImageDraw
    
    draw = ImageDraw.Draw(image)
    for vertices, label in boxes_to_draw:
        # vertices is [(x,y), (x,y)...]
        # PIL polygon expects flattened list or sequence of tuples
        draw.polygon(vertices, outline="red", width=3)
        # Optionally draw label text
        
    return image


import streamlit as st
import os
from PIL import Image
import pdf2image
import io
import tempfile

from src.config import Config
from src.services.classification import ClassificationService
from src.services.extraction import ExtractionService
from src.services.ocr import OCRClient
from src.utils.grounding import find_bounding_box, draw_boxes
from src.models.schemas import DocumentType

st.set_page_config(page_title="Document Extractor", layout="wide")

st.title("📄 Smart Document Extractor with Grounding")

# Check Configuration
try:
    Config.validate()
    st.sidebar.success("Configuration Loaded from Environment ✅")
except ValueError as e:
    st.sidebar.warning(f"Configuration Warning: {e}")
    st.sidebar.info("Please set .env file or enter keys below.")

# Sidebar Overrides
with st.sidebar:
    st.header("Settings")
    
    with st.expander("API Configuration"):
        gemini_key = st.text_input("Google API Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")
        if gemini_key:
            os.environ["GOOGLE_API_KEY"] = gemini_key
            
        service_account = st.file_uploader("Service Account JSON (OCR)", type=["json"])
        if service_account:
             with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
                f.write(service_account.read())
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f.name
                st.success("Service Account Updated")

def load_image(uploaded_file):
    if uploaded_file.type == "application/pdf":
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        if images:
            return images[0]
        return None
    else:
        return Image.open(uploaded_file)

uploaded_file = st.file_uploader("Choose a document", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    image = load_image(uploaded_file)
    
    if image:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format if image.format else 'PNG')
        img_bytes = img_byte_arr.getvalue()

        with col1:
            st.subheader("Original Document")
            image_placeholder = st.empty()
            image_placeholder.image(image, use_column_width=True)
            
        with col2:
            st.subheader("Extracted Data")
            
            if st.button("Extract & Ground Data"):
                try:
                    # Initialize services (they will pick up env vars)
                    ocr_service = OCRClient()
                    classifier = ClassificationService()
                    extractor = ExtractionService()

                    with st.spinner("Running OCR (Vision API)..."):
                        ocr_result = ocr_service.detect_text(img_bytes)
                    
                    with st.spinner("Classifying..."):
                        doc_type = classifier.classify_document(image)
                        st.info(f"Type: **{doc_type.value.upper()}**")
                    
                    with st.spinner("Extracting Fields..."):
                        result = extractor.extract_data(image, doc_type)
                        extracted_data = result.receipt_data
                        
                    if extracted_data:
                        st.success("Extraction Complete!")
                        st.json(extracted_data.model_dump(exclude={'items'}))
                        
                        if extracted_data.items:
                            st.dataframe(extracted_data.items)

                        # Grounding
                        boxes_to_draw = []
                        if extracted_data.total_amount:
                            box = find_bounding_box(str(extracted_data.total_amount), ocr_result.boxes)
                            if box: boxes_to_draw.append((box, "Total"))
                                
                        if extracted_data.merchant_name:
                            box = find_bounding_box(extracted_data.merchant_name, ocr_result.boxes)
                            if box: boxes_to_draw.append((box, "Merchant"))

                        if boxes_to_draw:
                            grounded_image = image.copy()
                            grounded_image = draw_boxes(grounded_image, boxes_to_draw)
                            image_placeholder.image(grounded_image, use_column_width=True, caption="Grounded Data")
                        else:
                            st.warning("Could not visually match extracted text.")
                    else:
                        st.warning("No structured data found.")
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")

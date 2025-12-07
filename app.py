import streamlit as st
import os
from PIL import Image
import pdf2image
import io
import tempfile
import plotly.graph_objects as go
import numpy as np

from src.config import Config
from src.services.classification import ClassificationService
from src.services.extraction import ExtractionService
from src.services.ocr import OCRClient
from src.utils.grounding import find_bounding_box
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
        # Load image and fix orientation if needed (using ExifTags ideally, but PIL mostly handles it)
        return Image.open(uploaded_file)

def plot_grounding(image, boxes_with_labels):
    """
    Draws interactive boxes using Plotly
    """
    img_width, img_height = image.size
    
    # Create figure
    fig = go.Figure()
    
    # Add image as background
    fig.add_trace(go.Image(z=image))
    
    # Add rectangles
    for vertices, label in boxes_with_labels:
        # vertices is [(x,y), (x,y), (x,y), (x,y)]
        # We need distinct x and y lists, closing the loop
        x_coords = [v[0] for v in vertices] + [vertices[0][0]]
        y_coords = [v[1] for v in vertices] + [vertices[0][1]]
        
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='lines',
            line=dict(color='red', width=3),
            name=label,
            text=[label] * len(x_coords),
            hoverinfo='text+name'
        ))
        
    # Configure axes to match image dimensions
    fig.update_layout(
        width=700,
        height=700 * (img_height / img_width),
        xaxis=dict(range=[0, img_width], visible=False),
        yaxis=dict(range=[img_height, 0], visible=False, scaleanchor="x"), # Note: y-axis flipped for images
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

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
            # Rotate button
            if 'rotation' not in st.session_state:
                st.session_state.rotation = 0
                
            if st.button("Rotate 90°"):
                st.session_state.rotation = (st.session_state.rotation + 90) % 360
                
            if st.session_state.rotation != 0:
                image = image.rotate(-st.session_state.rotation, expand=True)
                # Re-save bytes for OCR if rotated
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
            
            st.image(image, use_container_width=True)
            
        with col2:
            st.subheader("Extracted Data")
            
            if st.button("Extract & Ground Data"):
                try:
                    # Initialize services
                    ocr_service = OCRClient()
                    classifier = ClassificationService()
                    extractor = ExtractionService()

                    # 1. OCR Step
                    with st.spinner("Running OCR (Vision API)..."):
                        ocr_result = ocr_service.detect_text(img_bytes)
                    
                    # Debug: Show OCR Text
                    with st.expander("Debug: Raw OCR Output"):
                        st.text_area("Full Text", ocr_result.text, height=200)
                        st.write(f"Detected {len(ocr_result.boxes)} word boxes.")

                    # 2. Classification
                    with st.spinner("Classifying..."):
                        doc_type, reasoning = classifier.classify_document(image)
                        st.info(f"Type: **{doc_type.value.upper()}**")
                        st.caption(f"Reasoning: {reasoning}")
                    
                    # 3. Extraction
                    with st.spinner("Extracting Fields..."):
                        result = extractor.extract_data(image, doc_type)
                        extracted_data = result.receipt_data
                        
                    if extracted_data:
                        st.success("Extraction Complete!")
                        st.json(extracted_data.model_dump(exclude={'items'}))
                        
                        if extracted_data.items:
                            items_data = [item.model_dump() for item in extracted_data.items]
                            st.dataframe(items_data)

                        # 4. Grounding
                        boxes_to_draw = []
                        
                        # Match Total
                        if extracted_data.total_amount:
                            box = find_bounding_box(str(extracted_data.total_amount), ocr_result.boxes)
                            if box: boxes_to_draw.append((box, f"Total: {extracted_data.total_amount}"))
                                
                        # Match Merchant
                        if extracted_data.merchant_name:
                            box = find_bounding_box(extracted_data.merchant_name, ocr_result.boxes)
                            if box: boxes_to_draw.append((box, f"Merchant: {extracted_data.merchant_name}"))

                        # Plot Interactive
                        if boxes_to_draw:
                            fig = plot_grounding(image, boxes_to_draw)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Could not visually match extracted text to document.")
                    else:
                        st.warning("No structured data found.")
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")

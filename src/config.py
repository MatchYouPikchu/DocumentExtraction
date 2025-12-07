import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GOOGLE_API_KEY")
        # Optional: warn if OCR credentials missing
        # if not cls.GOOGLE_APPLICATION_CREDENTIALS:
        #     missing.append("GOOGLE_APPLICATION_CREDENTIALS")
            
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")


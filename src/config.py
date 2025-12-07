import os
from dotenv import load_dotenv
from pathlib import Path

# Explicitly find the .env file in the project root
# current file is in src/config.py, so root is two levels up (parents[1])
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from the specific path
load_dotenv(dotenv_path=ENV_PATH)

class Config:
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # If the path is relative, make it absolute based on project root
    if GOOGLE_APPLICATION_CREDENTIALS and not os.path.isabs(GOOGLE_APPLICATION_CREDENTIALS):
        GOOGLE_APPLICATION_CREDENTIALS = str(BASE_DIR / GOOGLE_APPLICATION_CREDENTIALS)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    @classmethod
    def validate(cls):
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GOOGLE_API_KEY")
            
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

import os
from pathlib import Path
from dotenv import load_dotenv

# Project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Database and metadata paths
DATABASE_PATH = BASE_DIR / "database" / "ecommerce.db"
METADATA_PATH = BASE_DIR / "metadata" / "schema_metadata.json"

# Existing Gemini settings (temporary)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# New Groq settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# SQL settings
MAX_RESULT_ROWS = 100
MAX_SQL_RETRIES = 2
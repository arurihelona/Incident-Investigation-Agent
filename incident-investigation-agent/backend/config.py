import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from incident-investigation-agent root or backend directory
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

load_dotenv(ROOT_DIR / ".env")
load_dotenv(BASE_DIR / ".env")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").lower()  # "auto", "openai", "gemini", "anthropic", "local", "heuristic"
LLM_API_KEY = os.getenv("LLM_API_KEY", "") or os.getenv("OPENAI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini" if "openai" in LLM_PROVIDER else "gemini-1.5-flash")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")

# Server & Vector Store Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db"))
DATA_PATH = os.getenv("DATA_PATH", str(BASE_DIR / "data" / "documents.json"))
MAX_HOPS = int(os.getenv("MAX_HOPS", "3"))

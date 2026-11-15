# config.py - all settings in one place
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _load_dotenv(path):
    """Tiny .env reader (no extra package). Real environment variables win; empty values are ignored."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        if value:
            os.environ.setdefault(key.strip(), value)


_load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
KB_DIR = DATA_DIR / "knowledge_base"
DB_PATH = DATA_DIR / "healthassist.db"
CHROMA_DIR = DATA_DIR / "chroma"
KEY_FILE = DATA_DIR / "secret.key"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")   # second model for comparison: gemma2:9b

TOP_K = 4                                                # passages retrieved per question
MAX_DISTANCE = float(os.getenv("MAX_DISTANCE", "0.55"))  # cosine distance, bigger = less similar
CONSENT_VERSION = "1.0"

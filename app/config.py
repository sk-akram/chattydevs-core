import os


from dotenv import load_dotenv

load_dotenv()
# =========================
# Core App
# =========================

APP_ENV = os.getenv("APP_ENV", "development")

INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN")

if not INTERNAL_SERVICE_TOKEN:
    raise RuntimeError("❌ INTERNAL_SERVICE_TOKEN missing")

# =========================
# Crawl Settings
# =========================

CRAWL_TIMEOUT = int(os.getenv("CRAWL_TIMEOUT", "10"))

CRAWL_MAX_PAGES = int(
    os.getenv("CRAWL_MAX_PAGES", "20")
)

CRAWL_USER_AGENT = os.getenv(
    "CRAWL_USER_AGENT",
    "ChattyDevsBot/1.0 (+https://chattydevs.com)",
)


# =========================
# Chunking / Tokenization
# =========================

TOKEN_ENCODING = os.getenv(
    "TOKEN_ENCODING",
    "cl100k_base",
)

CHUNK_TOKEN_SIZE = int(
    os.getenv("CHUNK_TOKEN_SIZE", "300")
)


# =========================
# Qdrant
# =========================

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

QDRANT_SCROLL_LIMIT = int(
    os.getenv("QDRANT_SCROLL_LIMIT", "100")
)

QDRANT_UPSERT_BATCH_SIZE = int(
    os.getenv("QDRANT_UPSERT_BATCH_SIZE", "50")
)


# =========================
# Gemini
# =========================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_EMBED_MODEL = os.getenv(
    "GEMINI_EMBED_MODEL",
    "models/text-embedding-004",
)


# =========================
# Validation
# =========================

REQUIRED_VARS = [
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME,
    GEMINI_API_KEY,
]

missing = [name for name, val in zip(
    [
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "QDRANT_COLLECTION_NAME",
        "GEMINI_API_KEY",
    ],
    REQUIRED_VARS
) if not val]

# =========================
# Safety / Performance
# =========================

MIN_CHUNK_CHAR_LENGTH = int(
    os.getenv("MIN_CHUNK_CHAR_LENGTH", "50")
)

GEMINI_TIMEOUT_SECONDS = int(
    os.getenv("GEMINI_TIMEOUT_SECONDS", "20")
)

QDRANT_TIMEOUT_SECONDS = int(
    os.getenv("QDRANT_TIMEOUT_SECONDS", "30")
)

def validate_required():
    if missing:
        raise RuntimeError(
            f"❌ Missing required environment variables: {', '.join(missing)}"
        )

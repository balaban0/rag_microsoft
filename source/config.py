"""Central configuration for the local RAG assistant."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "rag.db"

# Foundry Local model aliases (resolved to concrete model ids at runtime).
CHAT_MODEL_ALIAS = "phi-3.5-mini"
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

CHUNK_MAX_CHARS = 800
TOP_K = 3

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using ONLY the "
    "provided context.\n\n"
    "If the user's message is a greeting or casual small talk (e.g. "
    "\"hello\", \"hi\", \"thanks\", \"how are you\") rather than an actual "
    "question, do NOT treat it as an unanswered question. Instead, reply "
    "naturally and briefly, and mention in one sentence the kinds of "
    "topics you can help with based on your documents.\n\n"
    "For real questions: if the answer is not contained in the context, "
    "reply exactly: \"I don't have that information in my documents.\" Do "
    "not use outside knowledge or make things up. When you do answer, "
    "mention which source document(s) the information came from."
)

"""Chunk documents from docs/, embed each chunk with Foundry Local, and
store the results in the local SQLite database.
"""
import source.config as config
import source.db as db


def chunk_text(text, max_chars=config.CHUNK_MAX_CHARS):
    """Group paragraphs into ~1-3 paragraph passages, capped at max_chars."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) > max_chars and current:
            chunks.append(current)
            current = para
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def load_documents():
    docs = {}
    for path in sorted(config.DOCS_DIR.glob("*.md")) + sorted(config.DOCS_DIR.glob("*.txt")):
        docs[path.name] = path.read_text(encoding="utf-8")
    return docs


def run_ingestion(client):
    db.init_db()
    db.clear_chunks()

    documents = load_documents()
    if not documents:
        raise SystemExit(f"No documents found in {config.DOCS_DIR}")

    total = 0
    for source, text in documents.items():
        chunks = chunk_text(text)
        if not chunks:
            continue
        embeddings = client.embed(chunks)
        for content, embedding in zip(chunks, embeddings):
            db.insert_chunk(source, content, embedding)
            total += 1
        print(f"  ingested {len(chunks)} chunk(s) from {source}")

    print(f"Done. {total} chunks stored in {config.DB_PATH}")
    return total

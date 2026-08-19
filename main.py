"""CLI entry point for the offline local RAG Q&A assistant.

Usage:
    python main.py               # ingest (if needed) and start an interactive Q&A session
    python main.py --reingest    # force re-ingestion of docs/ before starting
"""
import argparse
import sys

import config
import db
import ingest
import retrieval
from foundry_client import FoundryClient


def build_context(chunks):
    parts = [f"[Source: {c['source']}]\n{c['content']}" for c in chunks]
    return "\n\n---\n\n".join(parts)


def answer_query(client, question):
    query_embedding = client.embed([question])[0]
    top_chunks = retrieval.get_top_chunks(query_embedding)
    if not top_chunks:
        return "I don't have that information in my documents.", []

    context = build_context(top_chunks)
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
    answer = client.chat(config.SYSTEM_PROMPT, user_prompt)
    return answer, top_chunks


def main():
    parser = argparse.ArgumentParser(description="Local offline RAG Q&A assistant")
    parser.add_argument(
        "--reingest",
        action="store_true",
        help="Re-run document ingestion even if the database already has data",
    )
    args = parser.parse_args()

    print("Initializing Foundry Local models (first run may take a while)...")
    client = FoundryClient(config.CHAT_MODEL_ALIAS, config.EMBEDDING_MODEL_ALIAS)

    db.init_db()
    if args.reingest or db.count_chunks() == 0:
        print(f"Running ingestion from {config.DOCS_DIR} ...")
        ingest.run_ingestion(client)

    # Guards against a stray leading BOM, which some terminals/redirected
    # input sources (e.g. PowerShell piping text into stdin) prepend to
    # the first line, which would otherwise stop "exit"/"quit" matching.
    bom = chr(0xFEFF)

    print("\nLocal RAG assistant ready. Type a question, or 'exit' to quit.\n")
    while True:
        try:
            question = input("> ").strip().lstrip(bom)
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        answer, chunks = answer_query(client, question)
        print(f"\n{answer}\n")
        sources = sorted({c["source"] for c in chunks})
        if sources:
            print(f"(retrieved from: {', '.join(sources)})\n")


if __name__ == "__main__":
    sys.exit(main() or 0)

# Python Project Structure

This project follows a simple, beginner-friendly Python project layout
rather than a complex package hierarchy. Each concern lives in its own
flat module in the `rag_assistant/` folder: `config.py` for settings,
`db.py` for SQLite access, `ingest.py` for document chunking and
embedding, `retrieval.py` for similarity search, `foundry_client.py` for
talking to the local model runtime, and `main.py` as the entry point that
ties everything together behind a `if __name__ == "__main__":` guard.

Dependencies are declared in `requirements.txt` and installed with
`pip install -r requirements.txt`. Modules import each other directly
(e.g. `import config`, `import db`) since they all live in the same
directory and the project is run as plain scripts (`python main.py`)
rather than an installed package.

This structure keeps the project easy to read end to end: a newcomer can
open `main.py`, follow the imports, and understand the whole pipeline
without navigating nested packages or complex build tooling.

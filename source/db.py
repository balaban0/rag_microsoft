"""SQLite storage for document chunks and their embedding vectors.

Embeddings are stored as JSON-serialized lists in a TEXT column. This keeps
the schema trivial (a single file, no extensions) which is appropriate for
the small document collections this assistant targets.
"""
import json
import sqlite3
from contextlib import contextmanager

import source.config as config

SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding TEXT NOT NULL
);
"""


@contextmanager
def connect():
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with connect() as conn:
        conn.execute(SCHEMA)
        conn.commit()


def clear_chunks():
    with connect() as conn:
        conn.execute("DELETE FROM chunks")
        conn.commit()


def insert_chunk(source, content, embedding):
    with connect() as conn:
        conn.execute(
            "INSERT INTO chunks (source, content, embedding) VALUES (?, ?, ?)",
            (source, content, json.dumps(embedding)),
        )
        conn.commit()


def all_chunks():
    with connect() as conn:
        rows = conn.execute("SELECT source, content, embedding FROM chunks").fetchall()
    return [
        {"source": r[0], "content": r[1], "embedding": json.loads(r[2])}
        for r in rows
    ]


def count_chunks():
    with connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]

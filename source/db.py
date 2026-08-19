"""Blender Stack Exchange rehberleri ve embedding'leri için SQLite depolama.

Embedding'ler bir TEXT sütununda JSON olarak saklanır. Bu, şemayı basit
tutar (tek bir dosya, ek uzantı yok) -- bu asistanın hedeflediği rehber
koleksiyonu boyutu (birkaç bin satır) için yeterli.
"""
import json
import sqlite3
from contextlib import contextmanager

import source.config as config

SCHEMA = """
CREATE TABLE IF NOT EXISTS tutorials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    tags TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    score INTEGER NOT NULL,
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


def clear_tutorials():
    with connect() as conn:
        conn.execute("DELETE FROM tutorials")
        conn.commit()


def insert_tutorial(source_id, title, tags, question, answer, score, embedding):
    with connect() as conn:
        conn.execute(
            "INSERT INTO tutorials "
            "(source_id, title, tags, question, answer, score, embedding) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                source_id,
                title,
                json.dumps(tags),
                question,
                answer,
                score,
                json.dumps(embedding),
            ),
        )
        conn.commit()


def all_tutorials():
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, source_id, title, tags, question, answer, score, embedding "
            "FROM tutorials"
        ).fetchall()
    return [
        {
            "id": r[0],
            "source_id": r[1],
            "title": r[2],
            "tags": json.loads(r[3]),
            "question": r[4],
            "answer": r[5],
            "score": r[6],
            "embedding": json.loads(r[7]),
        }
        for r in rows
    ]


def count_tutorials():
    with connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM tutorials").fetchone()[0]

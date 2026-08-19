"""Brute-force cosine-similarity retrieval over chunks stored in SQLite.

For the small document collections this assistant targets (a handful of
short documents), loading every embedding into memory and scoring them in
Python is simple and fast enough -- no vector database needed.
"""
import numpy as np

import source.config as config
import source.db as db


def cosine_similarity(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def get_top_chunks(query_embedding, k=config.TOP_K):
    chunks = db.all_chunks()
    scored = [(cosine_similarity(query_embedding, c["embedding"]), c) for c in chunks]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [c for _, c in scored[:k]]

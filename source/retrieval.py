"""SQLite'ta saklanan Blender rehberleri üzerinde hibrit getirme.

Her rehberi şu iki bileşenin ağırlıklı karışımıyla sıralar:
  - etiket/anahtar-kelime örtüşmesi: rehberin etiketlerinden (ve başlık
    kelimelerinden) kaçının kullanıcının kendi ifadesinde geçtiği --
    Blender terminolojisi (modifier, UV, rigging, low-poly...) Türkçe bir
    cümle içinde de genelde İngilizce kaldığından, bu araç/teknik
    isimlerinin birebir geçtiği durumları yakalıyor.
  - semantik benzerlik: sorgu embedding'i ile rehberin embedding'i
    arasındaki kosinüs benzerliği -- çok dilli bir embedding modeli
    kullanıldığından, Türkçe bir soruyu İngilizce içerikle asıl
    köprüleyen bileşen bu.

Bu asistanın hedeflediği rehber koleksiyonu boyutunda (birkaç bin satır),
her embedding'i belleğe yükleyip Python'da skorlamak basit ve yeterince
hızlı -- ayrı bir vektör veritabanına gerek yok.
"""
import re

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


def _keywords(tutorial):
    words = set(tutorial["tags"])
    words.update(re.findall(r"[a-zA-Z][a-zA-Z0-9\-]{2,}", tutorial["title"]))
    return {w.lower() for w in words}


def tag_overlap_score(query_text, tutorial):
    keywords = _keywords(tutorial)
    if not keywords:
        return 0.0
    query_lower = query_text.lower()
    hits = sum(1 for kw in keywords if kw in query_lower)
    return hits / len(keywords)


def get_candidates(query_text, query_embedding, exclude_ids=None, k=config.TOP_K):
    exclude_ids = exclude_ids or set()
    tutorials = [t for t in db.all_tutorials() if t["id"] not in exclude_ids]

    scored = []
    for tutorial in tutorials:
        semantic = cosine_similarity(query_embedding, tutorial["embedding"])
        tag_overlap = tag_overlap_score(query_text, tutorial)
        hybrid = config.TAG_WEIGHT * tag_overlap + config.SEMANTIC_WEIGHT * semantic
        scored.append((hybrid, tutorial))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [t for _, t in scored[:k]]

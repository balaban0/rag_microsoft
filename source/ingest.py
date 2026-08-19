"""Hazırlanmış Blender soru-cevap veri setini (dataset_raw/blender_qa.json)
yükler, her rehberin başlık+etiket+soru metnini embed eder ve sonuçları
yerel SQLite veritabanına yazar.

Ham Stack Exchange veri dökümünden dataset_raw/blender_qa.json'ı üretmek
için önce source/prepare_dataset.py'yi çalıştırın.
"""
import json

import source.config as config
import source.db as db

EMBED_BATCH_SIZE = 50


def load_dataset():
    if not config.DATASET_JSON_PATH.exists():
        raise SystemExit(
            f"{config.DATASET_JSON_PATH} bulunamadı. Önce "
            "`python -m source.prepare_dataset` komutunu çalıştırın (bkz. README.md)."
        )
    with open(config.DATASET_JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def embedding_text(record):
    tags = ", ".join(record["tags"])
    return f"{record['title']}\nTags: {tags}\n{record['question']}"


def run_ingestion(client):
    db.init_db()
    db.clear_tutorials()

    records = load_dataset()
    if not records:
        raise SystemExit(f"{config.DATASET_JSON_PATH} içinde rehber bulunamadı")

    total = 0
    for start in range(0, len(records), EMBED_BATCH_SIZE):
        batch = records[start:start + EMBED_BATCH_SIZE]
        texts = [embedding_text(r) for r in batch]
        embeddings = client.embed(texts)
        for record, embedding in zip(batch, embeddings):
            db.insert_tutorial(
                source_id=record["id"],
                title=record["title"],
                tags=record["tags"],
                question=record["question"],
                answer=record["answer"],
                score=record["score"],
                embedding=embedding,
            )
            total += 1
        print(f"  {total}/{len(records)} rehber embed edildi")

    print(f"Tamamlandı. {total} rehber {config.DB_PATH} içine kaydedildi")
    return total

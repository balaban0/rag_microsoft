"""Offline Blender öğrenme rehberi asistanı için CLI giriş noktası.

Kullanım:
    python -m source.main               # gerekirse ingest eder, interaktif oturum başlatır
    python -m source.main --reingest    # dataset_raw/blender_qa.json'ı yeniden ingest etmeye zorlar
"""
import argparse
import sys

import source.config as config
import source.db as db
import source.ingest as ingest
import source.retrieval as retrieval
from source.foundry_client import FoundryClient


def build_context(tutorial):
    tags = ", ".join(tutorial["tags"])
    return (
        f"Gerçek Blender Stack Exchange sorusu: {tutorial['title']}\n"
        f"Etiketler: {tags}\n"
        f"Problem açıklaması: {tutorial['question']}\n\n"
        f"Kabul edilen cevap:\n{tutorial['answer']}"
    )


def is_another_request(text):
    lowered = text.lower()
    return any(phrase in lowered for phrase in config.ANOTHER_REQUEST_PHRASES)


def get_recommendation(client, query_text, exclude_ids=None):
    query_embedding = client.embed([query_text])[0]
    candidates = retrieval.get_candidates(query_text, query_embedding, exclude_ids=exclude_ids, k=1)
    if not candidates:
        return config.NO_MATCH_MESSAGE, None

    tutorial = candidates[0]
    context = build_context(tutorial)
    user_prompt = f"Kullanıcı isteği: {query_text}\n\nBağlam:\n{context}"
    answer = client.chat(config.SYSTEM_PROMPT, user_prompt)
    return answer, tutorial


def main():
    parser = argparse.ArgumentParser(description="Offline Blender öğrenme rehberi asistanı")
    parser.add_argument(
        "--reingest",
        action="store_true",
        help="Veritabanında zaten veri olsa bile rehber ingest'ini yeniden çalıştır",
    )
    args = parser.parse_args()

    print("Foundry Local modelleri başlatılıyor (ilk çalıştırma biraz sürebilir)...")
    client = FoundryClient(config.CHAT_MODEL_ALIAS, config.EMBEDDING_MODEL_ALIAS)

    db.init_db()
    if args.reingest or db.count_tutorials() == 0:
        print(f"{config.DATASET_JSON_PATH} üzerinden ingest çalıştırılıyor ...")
        ingest.run_ingestion(client)

    bom = chr(0xFEFF)

    last_query = None
    shown_ids = set()

    print("\nBlender öğrenme rehberi hazır. Ne yapmak istediğini anlat, çıkmak için")
    print("'exit' yaz. Bir sonraki en iyi eşleşme için 'başka' de.\n")
    while True:
        try:
            question = input("> ").strip().lstrip(bom)
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        if is_another_request(question) and last_query is not None:
            query = last_query
        else:
            query = question
            last_query = question
            shown_ids = set()

        answer, tutorial = get_recommendation(client, query, exclude_ids=shown_ids)
        print(f"\n{answer}\n")
        if tutorial:
            shown_ids.add(tutorial["id"])
            print(f"(şuna dayanıyor: {tutorial['title']})\n")


if __name__ == "__main__":
    sys.exit(main() or 0)

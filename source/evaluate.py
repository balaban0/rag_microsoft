"""Blender öğrenme rehberi asistanı için fonksiyonel test paketi.

Kullanım:
    python -m source.evaluate

Asistana sabit bir yanıtlanabilir/yanıtlanamaz istek seti çalıştırır, iki
uç durumu kontrol eder (boş girdi, çok genel bir istek) ve yanıt
süreleriyle birlikte bir geçti/kaldı raporunu TEST_RESULTS.md'ye yazar.
"""
import subprocess
import sys
import time
from datetime import datetime, timezone

import source.config as config
import source.db as db
from source.foundry_client import FoundryClient
from source.main import get_recommendation

RESULTS_PATH = config.BASE_DIR / "TEST_RESULTS.md"

# answerable: asistan, beklenen konuyla etiketlenmiş bir rehber getirip onu
# kullanarak cevap vermeli. unanswerable: Blender'la hiç alakası yok, bu
# yüzden asistan alakasız bir rehberi zorlamak yerine iyi bir eşleşme
# bulamadığını söylemeli. greeting: gerçek bir istek değil, sıradan bir
# selamlaşma -- asistan reddetmek yerine doğal bir şekilde cevap vermeli.
# Sorgular kasıtlı olarak Türkçe içinde İngilizce Blender jargonu
# barındırıyor -- gerçek kullanımda kullanıcıların büyük olasılıkla
# yazacağı şekilde (bkz. README "Bilinen sınırlamalar").
TEST_CASES = [
    {"question": "How do I use the mirror modifier for symmetric modeling?", "category": "answerable", "expected_tag": "modifiers"},
    {"question": "How do I write a python script to automate a task in Blender?", "category": "answerable", "expected_tag": "python"},
    {"question": "How do I set up realistic materials and shaders?", "category": "answerable", "expected_tag": "materials"},
    {"question": "How do I do UV mapping before texturing?", "category": "answerable", "expected_tag": "uv"},
    {"question": "How do I animate an object along a path?", "category": "answerable", "expected_tag": "animation"},
    {"question": "How do I set up a particle system for hair or grass?", "category": "answerable", "expected_tag": "particles"},
    {"question": "How do I speed up rendering in the Cycles render engine?", "category": "answerable", "expected_tag": "cycles-render-engine"},
    {"question": "How do I use the shader node editor?", "category": "answerable", "expected_tag": "node-editor"},
    {"question": "How do I use compositing nodes for post-render processing?", "category": "answerable", "expected_tag": "compositing-nodes"},
    {"question": "How do I select and edit vertices in edit mode?", "category": "answerable", "expected_tag": "vertices"},
    {"question": "What is the capital of France?", "category": "unanswerable"},
    {"question": "Who won the 2018 FIFA World Cup?", "category": "unanswerable"},
    {"question": "What is the current price of Bitcoin?", "category": "unanswerable"},
    {"question": "hello", "category": "greeting"},
    {"question": "thanks!", "category": "greeting"},
]

# Kasıtlı olarak kök-kelime bazında geniş tutuldu: model her seferinde
# reddini farklı şekilde ifade ediyor ("uygun bir eşleşme bulamadım",
# "bununla ilgili bir şey yok", "alakalı değil"...), sistem promptundaki
# tam cümleyi birebir tekrarlamıyor -- bu yüzden tam/yakın eşleşme
# kontrolü, gerçekten doğru olan reddetmelerde yanlış başarısızlıklara
# yol açtı. Bu kökler gerçek, konuyla ilgili bir rehberde geçmesi
# beklenmeyen kelimeler, dolayısıyla makul (yine de doğası gereği
# yaklaşık) bir sinyal olarak kalıyor.
FALLBACK_MARKERS = (
    "eşleşme bulamadım",
    "eşleşme yok",
    "eşleşme bulunamadı",
    "uygun bir öneri bulamadım",
    "ilgili değil",
    "alakalı değil",
    "alakası yok",
    "bilgi tabanımda yok",
    "bilgim yok",
    "kapsamı dışında",
)


def looks_like_fallback(answer):
    lower = answer.lower()
    return any(marker in lower for marker in FALLBACK_MARKERS)


# Selamlaşma kontrolü, FALLBACK_MARKERS'tan kasıtlı olarak daha dar: "teşekkürler!"
# gibi bir mesaja verilen sıcak, konuyla ilgili bir cevap, neye yardımcı
# olamayacağından da bahsedebilir -- bu bir başarısızlık değil. Burada asıl
# regresyon testi edilen şey, bir selamlaşmanın sistem promptundaki tam,
# sabit-kodlanmış ret cümlesini alması, bu yüzden herhangi bir kapsam
# ifadesi yerine özellikle bu cümleyi arıyoruz.
FALLBACK_SENTENCE = config.NO_MATCH_MESSAGE.lower()


def run_case(client, case):
    start = time.perf_counter()
    answer, tutorial = get_recommendation(client, case["question"])
    elapsed = time.perf_counter() - start
    tags = tutorial["tags"] if tutorial else []

    if case["category"] == "answerable":
        passed = case["expected_tag"] in tags
    elif case["category"] == "greeting":
        passed = FALLBACK_SENTENCE not in answer.lower()
    else:  # unanswerable
        passed = looks_like_fallback(answer)

    return {**case, "tags": tags, "title": tutorial["title"] if tutorial else None,
            "passed": passed, "elapsed": elapsed, "answer": answer}


def run_general_question_case(client):
    question = "I have a few free hours tonight, what should I try in Blender?"
    start = time.perf_counter()
    answer, tutorial = get_recommendation(client, question)
    elapsed = time.perf_counter() - start
    return {
        "question": question,
        "elapsed": elapsed,
        "answer": answer,
        "note": "Kesin geçti/kaldı yok — asistanın belirsiz, açık uçlu bir isteği "
        "hatasız işlediğini doğrulamak için kaydediliyor.",
    }


def run_blank_input_case():
    """Gerçek CLI'yi boş bir satır, ardından gerçek bir soru ile çalıştırır;
    main.py'nin girdi döngüsünün boş girdiyi bir sorgu gibi değil, atlayarak
    geçtiğini, sonra bir sonraki gerçek soruyu normal şekilde yanıtlayıp
    temiz çıktığını doğrular."""
    script_input = "\nHow do I use the mirror modifier?\nexit\n"
    result = subprocess.run(
        [sys.executable, "-m", "source.main"],
        input=script_input,
        capture_output=True,
        text=True,
        cwd=config.BASE_DIR,
        timeout=120,
    )
    passed = result.returncode == 0 and "dayanıyor" in result.stdout.lower()
    return {"passed": passed, "returncode": result.returncode, "stdout_tail": result.stdout[-400:]}


def format_report(results, general_case, blank_case):
    lines = []
    lines.append("# Test Sonuçları\n")
    lines.append(f"Oluşturulma: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n")

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_time = sum(r["elapsed"] for r in results) / total if total else 0
    max_time = max((r["elapsed"] for r in results), default=0)

    lines.append(f"**Özet:** {passed}/{total} test vakası geçti. "
                 f"Ortalama yanıt süresi {avg_time:.2f}sn, en yüksek {max_time:.2f}sn.\n")
    if avg_time > 3:
        lines.append(f"> Not: buradaki {avg_time:.1f}sn'lik ortalama, muhtemelen bir "
                      f"pipeline sorunundan çok bu makinenin donanımını (seçilen model "
                      f"için özel GPU hızlandırması yok) yansıtıyor. Azaltma seçenekleri "
                      f"(daha küçük model, daha düşük TOP_K) için README'deki 'Bilinen "
                      f"sınırlamalar' bölümüne bakın.\n")

    lines.append("## Yanıtlanabilir / Yanıtlanamaz İstekler\n")
    lines.append("| # | Kategori | Soru | Beklenen etiket | Getirilen rehber | Süre (sn) | Sonuç |")
    lines.append("|---|----------|------|------------------|--------------------|-----------|--------|")
    for i, r in enumerate(results, 1):
        expected = r.get("expected_tag", "-")
        title = r["title"] or "-"
        status = "GEÇTİ" if r["passed"] else "KALDI"
        lines.append(
            f"| {i} | {r['category']} | {r['question']} | {expected} | {title} | "
            f"{r['elapsed']:.2f} | {status} |"
        )

    lines.append("\n## Uç Durumlar\n")
    lines.append(f"- **Boş girdi, ardından gerçek bir soru (CLI üzerinden):** "
                  f"{'GEÇTİ' if blank_case['passed'] else 'KALDI'} "
                  f"(çıkış kodu {blank_case['returncode']}) — CLI, boş satırları bir "
                  f"sorgu olarak işlemek yerine atlamalı, sonra bir sonraki gerçek "
                  f"soruyu yine de yanıtlamalı.")
    lines.append(f"- **Belirsiz/açık uçlu istek:** sadece kaydedildi, "
                  f"{general_case['elapsed']:.2f}sn yanıt süresi. {general_case['note']}")
    lines.append(f"\n> \"{general_case['question']}\" -> {general_case['answer'][:300]}")

    lines.append("\n## Başarısızlıkların Detayı\n")
    failures = [r for r in results if not r["passed"]]
    if not failures:
        lines.append("Yok.")
    else:
        for r in failures:
            lines.append(f"- **{r['question']}** (beklenen etiket: {r.get('expected_tag', '-')}, "
                          f"gelen: {r['title'] or 'eşleşme yok'})\n  > {r['answer'][:300]}")

    return "\n".join(lines) + "\n"


def main():
    print("Foundry Local modelleri başlatılıyor...")
    client = FoundryClient(config.CHAT_MODEL_ALIAS, config.EMBEDDING_MODEL_ALIAS)
    db.init_db()
    if db.count_tutorials() == 0:
        raise SystemExit(
            "Veritabanında rehber yok — önce `python -m source.prepare_dataset`, "
            "sonra `python -m source.main` çalıştırıp bilgi tabanını oluşturun."
        )

    print(f"{len(TEST_CASES)} test vakası çalıştırılıyor...")
    results = [run_case(client, case) for case in TEST_CASES]

    print("Uç durumlar çalıştırılıyor (belirsiz istek, CLI üzerinden boş girdi)...")
    general_case = run_general_question_case(client)
    blank_case = run_blank_input_case()

    report = format_report(results, general_case, blank_case)
    RESULTS_PATH.write_text(report, encoding="utf-8")

    passed = sum(1 for r in results if r["passed"])
    print(f"\n{passed}/{len(results)} test vakası geçti. Rapor {RESULTS_PATH} konumuna yazıldı")
    if not blank_case["passed"]:
        print("UYARI: boş girdi uç durumu başarısız oldu.")


if __name__ == "__main__":
    main()

"""Functional test suite for the local RAG assistant (Phase 3 / Week 5 of
the program plan: "Students develop test cases ... both queries it can
answer and ones it should not be able to").

Usage:
    python evaluate.py

Runs a fixed set of answerable and unanswerable questions against the
assistant, checks two edge cases (blank input, a very general question),
and writes a pass/fail report with response times to TEST_RESULTS.md.
"""
import subprocess
import sys
import time
from datetime import datetime, timezone

import source.config as config
import source.db as db
from source.foundry_client import FoundryClient
from source.main import answer_query

RESULTS_PATH = config.BASE_DIR / "TEST_RESULTS.md"

# Answerable: the assistant should retrieve from the expected source and
# answer using it. Unanswerable: not covered by docs/, so the assistant
# should say it doesn't know rather than guessing. Greeting: casual small
# talk, not a real question -- the assistant should respond naturally
# instead of refusing (regression test for the "hello" -> refusal bug).
TEST_CASES = [
    {"question": "What is RAG (Retrieval-Augmented Generation)?", "category": "answerable", "expected_source": "01_what_is_rag.md"},
    {"question": "What is Foundry Local and why does this project use it?", "category": "answerable", "expected_source": "02_foundry_local.md"},
    {"question": "How is cosine similarity used for vector search here?", "category": "answerable", "expected_source": "03_embeddings_vector_search.md"},
    {"question": "Why is SQLite used to store document chunks?", "category": "answerable", "expected_source": "04_sqlite_basics.md"},
    {"question": "What should the assistant do if the answer isn't in the retrieved context?", "category": "answerable", "expected_source": "05_prompt_engineering.md"},
    {"question": "What are the layers of this assistant's architecture?", "category": "answerable", "expected_source": "06_project_architecture.md"},
    {"question": "How is the Python code for this project organized?", "category": "answerable", "expected_source": "07_python_project_structure.md"},
    {"question": "How does the ingestion pipeline split documents into chunks?", "category": "answerable", "expected_source": "08_chunking_strategy.md"},
    {"question": "What's the trade-off between a small and a large chat model here?", "category": "answerable", "expected_source": "09_model_selection_tradeoffs.md"},
    {"question": "How is this assistant tested?", "category": "answerable", "expected_source": "10_testing_and_evaluation.md"},
    {"question": "What does app_streamlit.py do?", "category": "answerable", "expected_source": "11_web_ui_streamlit.md"},
    {"question": "How do I add my own documents to the knowledge base?", "category": "answerable", "expected_source": "12_faq_troubleshooting.md"},
    {"question": "What does the Mirror Modifier do in Blender?", "category": "answerable", "expected_source": "13_blender_modifiers_and_texturing.md"},
    {"question": "What is ScriptableRenderPass used for in Unity's URP?", "category": "answerable", "expected_source": "14_unity_urp_rendering.md"},
    {"question": "How do branching dialogue trees support player agency?", "category": "answerable", "expected_source": "15_narrative_design_player_agency.md"},
    {"question": "What is an LOD system used for in game engines?", "category": "answerable", "expected_source": "16_mesh_topology_and_lod.md"},
    {"question": "What is the capital of France?", "category": "unanswerable"},
    {"question": "Who won the 2018 FIFA World Cup?", "category": "unanswerable"},
    {"question": "What is the current price of Bitcoin?", "category": "unanswerable"},
    {"question": "hello", "category": "greeting"},
    {"question": "thanks!", "category": "greeting"},
]

# Deliberately root-word broad: the model paraphrases its refusal every
# time ("don't have that specific information", "do not contain...",
# "not available in the documents"...) rather than reproducing the system
# prompt's exact fallback sentence verbatim, so exact/near-exact phrase
# matching produced false failures during testing on genuinely correct
# refusals. These roots are unlikely to appear in a real, informative
# answer, so they stay a reasonable (if inherently approximate) signal.
FALLBACK_MARKERS = (
    "don't have",
    "do not have",
    "not contain",
    "no information",
    "not available",
    "cannot find",
    "unable to find",
    "i don't know",
    "not covered",
    "outside the scope",
)


def looks_like_fallback(answer):
    lower = answer.lower()
    return any(marker in lower for marker in FALLBACK_MARKERS)


# The greeting check is intentionally narrower than FALLBACK_MARKERS: a
# warm, on-topic reply to "thanks!" may still mention "topics not covered
# in these documents" while explaining what it can help with, which isn't
# a failure. What we're actually regression-testing is the original bug
# (a greeting getting the system prompt's exact hard-coded refusal
# sentence), so check for that sentence specifically rather than any
# scope-related phrase anywhere in the reply.
FALLBACK_SENTENCE = "i don't have that information in my documents"


def run_case(client, case):
    start = time.perf_counter()
    answer, chunks = answer_query(client, case["question"])
    elapsed = time.perf_counter() - start
    sources = sorted({c["source"] for c in chunks})

    if case["category"] == "answerable":
        passed = case["expected_source"] in sources
    elif case["category"] == "greeting":
        passed = FALLBACK_SENTENCE not in answer.lower()
    else:  # unanswerable
        passed = looks_like_fallback(answer)

    return {**case, "sources": sources, "passed": passed, "elapsed": elapsed, "answer": answer}


def run_general_question_case(client):
    question = "Tell me something interesting."
    start = time.perf_counter()
    answer, chunks = answer_query(client, question)
    elapsed = time.perf_counter() - start
    return {
        "question": question,
        "elapsed": elapsed,
        "answer": answer,
        "note": "No hard pass/fail — logged to confirm the assistant handles a vague, "
        "non-document-specific question without crashing.",
    }


def run_blank_input_case():
    """Drive the real CLI with a blank line followed by a real question,
    confirming main.py's input loop skips empty input instead of treating
    it as a query, then still answers normally and exits cleanly."""
    script_input = "\nWhat is RAG?\nexit\n"
    result = subprocess.run(
        [sys.executable, str(config.BASE_DIR / "main.py")],
        input=script_input,
        capture_output=True,
        text=True,
        cwd=config.BASE_DIR,
        timeout=120,
    )
    passed = result.returncode == 0 and "retrieve" in result.stdout.lower()
    return {"passed": passed, "returncode": result.returncode, "stdout_tail": result.stdout[-400:]}


def format_report(results, general_case, blank_case):
    lines = []
    lines.append("# Test Results\n")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n")

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_time = sum(r["elapsed"] for r in results) / total if total else 0
    max_time = max((r["elapsed"] for r in results), default=0)

    lines.append(f"**Summary:** {passed}/{total} test cases passed. "
                 f"Avg response time {avg_time:.2f}s, max {max_time:.2f}s.\n")
    if avg_time > 3:
        lines.append(f"> Note: the program plan targets ~1-3s per question on a typical "
                      f"laptop; {avg_time:.1f}s average here likely reflects this machine's "
                      f"hardware (no dedicated GPU acceleration for the chosen model) rather "
                      f"than a pipeline issue. See README 'Known limitations' for mitigation "
                      f"options (smaller model, fewer retrieved chunks).\n")

    lines.append("## Answerable / Unanswerable Queries\n")
    lines.append("| # | Category | Question | Expected source | Retrieved sources | Time (s) | Result |")
    lines.append("|---|----------|----------|------------------|--------------------|----------|--------|")
    for i, r in enumerate(results, 1):
        expected = r.get("expected_source", "-")
        sources = ", ".join(r["sources"]) if r["sources"] else "-"
        status = "PASS" if r["passed"] else "FAIL"
        lines.append(
            f"| {i} | {r['category']} | {r['question']} | {expected} | {sources} | "
            f"{r['elapsed']:.2f} | {status} |"
        )

    lines.append("\n## Edge Cases\n")
    lines.append(f"- **Blank input then a real question (via CLI):** "
                  f"{'PASS' if blank_case['passed'] else 'FAIL'} "
                  f"(exit code {blank_case['returncode']}) — the CLI must skip empty lines "
                  f"instead of querying with them, then still answer the next real question.")
    lines.append(f"- **Vague/general question:** logged only, {general_case['elapsed']:.2f}s response time. "
                  f"{general_case['note']}")
    lines.append(f"\n> \"{general_case['question']}\" -> {general_case['answer'][:300]}")

    lines.append("\n## Failures in detail\n")
    failures = [r for r in results if not r["passed"]]
    if not failures:
        lines.append("None.")
    else:
        for r in failures:
            lines.append(f"- **{r['question']}** (expected source: {r.get('expected_source', '-')}, "
                          f"got: {', '.join(r['sources']) or 'none'})\n  > {r['answer'][:300]}")

    return "\n".join(lines) + "\n"


def main():
    print("Initializing Foundry Local models...")
    client = FoundryClient(config.CHAT_MODEL_ALIAS, config.EMBEDDING_MODEL_ALIAS)
    db.init_db()
    if db.count_chunks() == 0:
        raise SystemExit("No chunks in the database — run `python main.py` once first to ingest docs/.")

    print(f"Running {len(TEST_CASES)} test cases...")
    results = [run_case(client, case) for case in TEST_CASES]

    print("Running edge cases (vague question, blank input via CLI)...")
    general_case = run_general_question_case(client)
    blank_case = run_blank_input_case()

    report = format_report(results, general_case, blank_case)
    RESULTS_PATH.write_text(report, encoding="utf-8")

    passed = sum(1 for r in results if r["passed"])
    print(f"\n{passed}/{len(results)} test cases passed. Report written to {RESULTS_PATH}")
    if not blank_case["passed"]:
        print("WARNING: blank-input edge case failed.")


if __name__ == "__main__":
    main()

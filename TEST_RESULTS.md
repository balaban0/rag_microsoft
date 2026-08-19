# Test Results

Generated: 2026-08-16T16:22:32+00:00

**Summary:** 21/21 test cases passed. Avg response time 11.01s, max 19.57s.

> Note: the program plan targets ~1-3s per question on a typical laptop; 11.0s average here likely reflects this machine's hardware (no dedicated GPU acceleration for the chosen model) rather than a pipeline issue. See README 'Known limitations' for mitigation options (smaller model, fewer retrieved chunks).

## Answerable / Unanswerable Queries

| # | Category | Question | Expected source | Retrieved sources | Time (s) | Result |
|---|----------|----------|------------------|--------------------|----------|--------|
| 1 | answerable | What is RAG (Retrieval-Augmented Generation)? | 01_what_is_rag.md | 01_what_is_rag.md, 10_testing_and_evaluation.md | 10.81 | PASS |
| 2 | answerable | What is Foundry Local and why does this project use it? | 02_foundry_local.md | 02_foundry_local.md, 04_sqlite_basics.md, 06_project_architecture.md | 19.41 | PASS |
| 3 | answerable | How is cosine similarity used for vector search here? | 03_embeddings_vector_search.md | 03_embeddings_vector_search.md, 04_sqlite_basics.md, 06_project_architecture.md | 8.30 | PASS |
| 4 | answerable | Why is SQLite used to store document chunks? | 04_sqlite_basics.md | 04_sqlite_basics.md, 08_chunking_strategy.md | 6.89 | PASS |
| 5 | answerable | What should the assistant do if the answer isn't in the retrieved context? | 05_prompt_engineering.md | 01_what_is_rag.md, 05_prompt_engineering.md, 06_project_architecture.md | 11.20 | PASS |
| 6 | answerable | What are the layers of this assistant's architecture? | 06_project_architecture.md | 01_what_is_rag.md, 06_project_architecture.md, 07_python_project_structure.md | 14.86 | PASS |
| 7 | answerable | How is the Python code for this project organized? | 07_python_project_structure.md | 07_python_project_structure.md, 11_web_ui_streamlit.md | 19.57 | PASS |
| 8 | answerable | How does the ingestion pipeline split documents into chunks? | 08_chunking_strategy.md | 08_chunking_strategy.md, 12_faq_troubleshooting.md | 11.11 | PASS |
| 9 | answerable | What's the trade-off between a small and a large chat model here? | 09_model_selection_tradeoffs.md | 09_model_selection_tradeoffs.md, 12_faq_troubleshooting.md | 12.19 | PASS |
| 10 | answerable | How is this assistant tested? | 10_testing_and_evaluation.md | 01_what_is_rag.md, 05_prompt_engineering.md, 10_testing_and_evaluation.md | 14.02 | PASS |
| 11 | answerable | What does app_streamlit.py do? | 11_web_ui_streamlit.md | 11_web_ui_streamlit.md | 8.20 | PASS |
| 12 | answerable | How do I add my own documents to the knowledge base? | 12_faq_troubleshooting.md | 01_what_is_rag.md, 05_prompt_engineering.md, 12_faq_troubleshooting.md | 8.65 | PASS |
| 13 | answerable | What does the Mirror Modifier do in Blender? | 13_blender_modifiers_and_texturing.md | 13_blender_modifiers_and_texturing.md | 10.62 | PASS |
| 14 | answerable | What is ScriptableRenderPass used for in Unity's URP? | 14_unity_urp_rendering.md | 14_unity_urp_rendering.md, 16_mesh_topology_and_lod.md | 10.66 | PASS |
| 15 | answerable | How do branching dialogue trees support player agency? | 15_narrative_design_player_agency.md | 01_what_is_rag.md, 15_narrative_design_player_agency.md | 13.75 | PASS |
| 16 | answerable | What is an LOD system used for in game engines? | 16_mesh_topology_and_lod.md | 02_foundry_local.md, 06_project_architecture.md, 16_mesh_topology_and_lod.md | 12.48 | PASS |
| 17 | unanswerable | What is the capital of France? | - | 01_what_is_rag.md, 05_prompt_engineering.md, 06_project_architecture.md | 8.65 | PASS |
| 18 | unanswerable | Who won the 2018 FIFA World Cup? | - | 01_what_is_rag.md, 06_project_architecture.md, 14_unity_urp_rendering.md | 5.15 | PASS |
| 19 | unanswerable | What is the current price of Bitcoin? | - | 01_what_is_rag.md, 02_foundry_local.md, 06_project_architecture.md | 5.68 | PASS |
| 20 | greeting | hello | - | 01_what_is_rag.md, 05_prompt_engineering.md, 10_testing_and_evaluation.md | 5.71 | PASS |
| 21 | greeting | thanks! | - | 01_what_is_rag.md, 10_testing_and_evaluation.md, 12_faq_troubleshooting.md | 13.23 | PASS |

## Edge Cases

- **Blank input then a real question (via CLI):** PASS (exit code 0) — the CLI must skip empty lines instead of querying with them, then still answer the next real question.
- **Vague/general question:** logged only, 5.58s response time. No hard pass/fail — logged to confirm the assistant handles a vague, non-document-specific question without crashing.

> "Tell me something interesting." ->  I don't have that information in my documents. For interesting facts or general knowledge, I recommend checking reliable online sources or databases.

## Failures in detail

None.

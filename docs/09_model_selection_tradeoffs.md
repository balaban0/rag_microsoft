# Model Selection Trade-offs

Foundry Local's catalog offers models of many sizes, and choosing one is
a trade-off between speed and answer quality. Smaller models (roughly
1-4 billion parameters, such as `phi-3.5-mini` or `qwen3-1.7b`) load
faster, use less memory, and respond more quickly, which matters most
when running on a laptop without a dedicated GPU. Larger models (7 billion
parameters and up, such as `qwen2.5-14b` or `phi-4`) generally produce
more accurate and nuanced answers, but take longer to respond and need
more RAM/VRAM.

This project defaults to `phi-3.5-mini` for chat and the small
`qwen3-embedding-0.6b` for embeddings, prioritizing fast feedback during
development and demos over maximum answer quality. Both are configured
in `config.py` via `CHAT_MODEL_ALIAS` and `EMBEDDING_MODEL_ALIAS`, and can
be swapped for any alias listed by `foundry model list` if more accuracy
is needed and the extra latency is acceptable. Response time also depends
on how many chunks are retrieved per question (`TOP_K` in `config.py`) --
retrieving fewer chunks means a shorter prompt and a faster reply.

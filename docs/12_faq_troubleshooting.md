# FAQ and Troubleshooting

**How do I add my own documents?** Drop `.md` or `.txt` files into
`docs/` and run `python main.py --reingest` (or `python evaluate.py`
afterward to confirm nothing broke). Keep documents reasonably short and
focused, similar to course notes or an FAQ page -- long, unfocused
documents chunk and retrieve less accurately.

**Why does it say "I don't have that information in my documents"?**
That means none of the retrieved chunks were relevant enough to answer
the question. This is intentional: the assistant is instructed not to
guess using outside knowledge. If the topic should be covered, check
whether a document about it exists in `docs/` and was ingested.

**Why is it slow to answer?** Response time depends on the chat model
size, the number of chunks retrieved (`TOP_K` in `config.py`), and
whether the machine has GPU acceleration available. Try a smaller model
alias or a lower `TOP_K` value first.

**Does it need the internet?** Only the first time, to download the
chosen models through Foundry Local. After that, ingestion, retrieval,
and answer generation all run on-device with no network calls.

**Why doesn't a "hello" get treated like an unanswered question?** The
system prompt explicitly tells the model to recognize greetings and
casual small talk and respond to them naturally, instead of running them
through the strict "answer only from documents" rule meant for real
questions.

"""Streamlit web UI for the local RAG assistant (program plan Week 4,
"Option B: Streamlit or Gradio UI"). A thin front end over the same
answer_query() pipeline used by the CLI in main.py.

Run with: streamlit run app_streamlit.py
"""
import streamlit as st

import source.config as config
import source.db as db
from source.foundry_client import FoundryClient
from source.main import answer_query

st.set_page_config(page_title="Local RAG Assistant")


@st.cache_resource(show_spinner="Starting Foundry Local and loading models...")
def get_client():
    client = FoundryClient(config.CHAT_MODEL_ALIAS, config.EMBEDDING_MODEL_ALIAS)
    db.init_db()
    return client


st.title("Local RAG Q&A Assistant")
st.caption("Fully offline — retrieval + generation both run on-device via Microsoft Foundry Local.")

client = get_client()

if db.count_chunks() == 0:
    st.warning(f"No documents ingested yet. Run `python main.py` once to ingest {config.DOCS_DIR}.")
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []

question = st.chat_input("Ask a question about the knowledge base...")

for entry in st.session_state.history:
    with st.chat_message("user"):
        st.write(entry["question"])
    with st.chat_message("assistant"):
        st.write(entry["answer"])
        if entry["sources"]:
            st.caption(f"Retrieved from: {', '.join(entry['sources'])}")

if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, chunks = answer_query(client, question)
        st.write(answer)
        sources = sorted({c["source"] for c in chunks})
        if sources:
            st.caption(f"Retrieved from: {', '.join(sources)}")
    st.session_state.history.append({"question": question, "answer": answer, "sources": sources})

with st.sidebar:
    st.subheader("Knowledge base")
    for path in sorted(config.DOCS_DIR.glob("*.md")) + sorted(config.DOCS_DIR.glob("*.txt")):
        st.markdown(f"- {path.name}")

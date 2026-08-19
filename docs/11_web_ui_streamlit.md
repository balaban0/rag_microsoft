# Web UI with Streamlit

Besides the console (CLI) interface in `main.py`, this project includes
an optional web front end in `app_streamlit.py`, built with Streamlit --
a Python framework for turning scripts into simple, interactive web apps
without writing HTML, CSS, or JavaScript by hand.

`app_streamlit.py` reuses the exact same `answer_query()` function the
CLI uses, so both interfaces share one retrieval-and-generation pipeline;
only the presentation differs. It renders a chat-style interface with
`st.chat_input` and `st.chat_message`, keeps the conversation history in
`st.session_state` so previous questions stay visible, and lists the
ingested source documents in a sidebar for reference. The Foundry Local
client is created once and cached across interactions with
`@st.cache_resource`, so models are not reloaded on every question.

Run it with `streamlit run app_streamlit.py`, which starts a local web
server (by default at http://localhost:8501) and opens the app in a
browser. Like the CLI, it runs entirely offline once models are
downloaded -- no data leaves the machine.

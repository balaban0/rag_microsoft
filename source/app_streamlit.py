"""Offline Blender öğrenme rehberi asistanı için Streamlit web arayüzü.
CLI'de (main.py) kullanılan aynı get_recommendation() pipeline'ı üzerine
kurulu ince bir ön yüz -- "başka bir şey öner" takip özelliği dahil.

Çalıştırmak için: streamlit run source/app_streamlit.py
"""
import streamlit as st

import source.config as config
import source.db as db
from source.foundry_client import FoundryClient
from source.main import get_recommendation

st.set_page_config(page_title="Blender Öğrenme Rehberi")


@st.cache_resource(show_spinner="Foundry Local başlatılıyor ve modeller yükleniyor...")
def get_client():
    client = FoundryClient(config.CHAT_MODEL_ALIAS, config.EMBEDDING_MODEL_ALIAS)
    db.init_db()
    return client


st.title("Blender Öğrenme Rehberi")
st.caption(
    "Tamamen offline — Blender'da ne yapmak istediğini anlat, gerçek "
    "Blender Stack Exchange cevaplarından türetilmiş, Microsoft Foundry "
    "Local ile cihaz üzerinde üretilmiş adım adım bir rehber al."
)

client = get_client()

if db.count_tutorials() == 0:
    st.warning(
        "Henüz rehber ingest edilmedi. Bilgi tabanını oluşturmak için önce "
        "`python -m source.prepare_dataset`, sonra `python -m source.main` "
        "çalıştır."
    )
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []
if "last_query" not in st.session_state:
    st.session_state.last_query = None
if "shown_ids" not in st.session_state:
    st.session_state.shown_ids = set()

question = st.chat_input("Blender'da ne yapmak istiyorsun?")
another = st.button(
    "🔁 Başka bir şey öner",
    disabled=st.session_state.last_query is None,
    help="Son isteğine bir sonraki en iyi eşleşmeyi iste",
)

for entry in st.session_state.history:
    with st.chat_message("user"):
        st.write(entry["question"])
    with st.chat_message("assistant"):
        st.write(entry["answer"])
        if entry["title"]:
            st.caption(f"Şuna dayanıyor: {entry['title']}")

turn_input = None
if question:
    turn_input = question
    st.session_state.last_query = question
    st.session_state.shown_ids = set()
elif another and st.session_state.last_query:
    turn_input = "başka bir şey öner"

if turn_input:
    display_question = question if question else "🔁 (başka bir şey öner)"
    with st.chat_message("user"):
        st.write(display_question)
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            query = st.session_state.last_query
            answer, tutorial = get_recommendation(
                client, query, exclude_ids=st.session_state.shown_ids
            )
        st.write(answer)
        title = tutorial["title"] if tutorial else None
        if title:
            st.caption(f"Şuna dayanıyor: {title}")
    if tutorial:
        st.session_state.shown_ids.add(tutorial["id"])
    st.session_state.history.append(
        {"question": display_question, "answer": answer, "title": title}
    )

with st.sidebar:
    st.subheader("Bilgi tabanı")
    st.markdown(f"Blender Stack Exchange'den {db.count_tutorials()} rehber")
    sample_tags = set()
    for tutorial in db.all_tutorials()[:200]:
        sample_tags.update(tutorial["tags"])
    if sample_tags:
        st.caption("Örnek konular: " + ", ".join(sorted(sample_tags)[:20]))

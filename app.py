import os
import warnings

warnings.filterwarnings("ignore", message=r"`langchain-community` is being sunset", category=DeprecationWarning)

import streamlit as st
from dotenv import load_dotenv

from atbot.components import init_session, render_footer, render_pdf_chat, render_sidebar
from atbot.constants import SESSION_DEFAULTS
from atbot.theme import inject_theme

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

st.set_page_config(
    page_title="AT BOT",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)
load_dotenv()
inject_theme()
init_session(SESSION_DEFAULTS)

model_label, k = render_sidebar()

if not os.getenv("GROQ_API_KEY"):
    st.error("Add GROQ_API_KEY to your .env file and restart the app.")
    st.stop()

render_pdf_chat(model_label, k)
render_footer()

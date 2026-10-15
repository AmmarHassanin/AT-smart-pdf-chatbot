import os
import warnings

warnings.filterwarnings("ignore", message=r"`langchain-community` is being sunset", category=DeprecationWarning)

import streamlit as st
from dotenv import load_dotenv

from atbot.components import init_session, render_footer, render_navbar, render_pdf_chat, render_sidebar
from atbot.constants import SESSION_DEFAULTS
from atbot.i18n import inject_layout, t
from atbot.theme import inject_theme

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

st.set_page_config(
    page_title="AT PDF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_dotenv()
inject_theme()
inject_layout()
init_session(SESSION_DEFAULTS)

render_navbar()
model_label, k = render_sidebar()

if not os.getenv("GROQ_API_KEY"):
    st.error(t("groq_missing"))
    st.stop()

render_pdf_chat(model_label, k)
render_footer()

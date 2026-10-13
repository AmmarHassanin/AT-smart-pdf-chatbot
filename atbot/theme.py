import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Alexandria:wght@500;600;700&display=swap');

:root {
  --bg: #0B0D12;
  --sidebar: #10131A;
  --card: #151922;
  --elevated: #1B202B;
  --gold: #F5C451;
  --gold-dim: rgba(245, 196, 81, 0.14);
  --gold-border: rgba(245, 196, 81, 0.35);
  --gold-glow: rgba(245, 196, 81, 0.22);
  --text: #F5F7FA;
  --muted: #9CA3AF;
  --border: #292F3A;
  --success: #34D399;
  --error: #F87171;
  --radius-sm: 10px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --transition: 180ms ease;
  --font-ui: "Inter", "Segoe UI", system-ui, sans-serif;
  --font-display: "Alexandria", "Inter", sans-serif;
  --app-footer-h: 2.5rem;
  --content-max: 780px;
}

html, body, [class*="css"], .stApp, input, textarea, button {
  font-family: var(--font-ui);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
.stApp { background: var(--bg); color: var(--text); }

header[data-testid="stHeader"] {
  visibility: visible !important;
  height: 3rem;
  min-height: 3rem;
  background: rgba(11, 13, 18, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}
[data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
header[data-testid="stHeader"] [data-testid="stSidebarCollapsedControl"] {
  z-index: 1003 !important;
  color: var(--text) !important;
  background: var(--elevated) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  transition: border-color var(--transition), box-shadow var(--transition);
}
[data-testid="stSidebarCollapseButton"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover {
  border-color: var(--gold-border) !important;
  box-shadow: 0 0 12px var(--gold-glow);
}

.block-container {
  max-width: var(--content-max);
  padding-top: 2.5rem;
  padding-bottom: calc(7.5rem + var(--app-footer-h) + env(safe-area-inset-bottom, 0px));
}
@media (max-width: 768px) {
  .block-container { padding-top: 3.25rem; padding-left: 1rem; padding-right: 1rem; }
  [data-testid="stSidebarCollapsedControl"] {
    position: fixed !important;
    top: 0.5rem;
    left: 0.65rem;
  }
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--sidebar) !important;
  border-right: 1px solid var(--border);
  min-width: 280px !important;
}
[data-testid="stSidebar"] > div:first-child {
  background: var(--sidebar);
}
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.25rem 0 1.25rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
}
.sidebar-brand__mark {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: linear-gradient(145deg, var(--gold-dim), transparent);
  border: 1px solid var(--gold-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}
.sidebar-brand__text {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.15rem;
  letter-spacing: 0.02em;
  color: var(--text);
}
.sidebar-brand__text span { color: var(--gold); }
.sidebar-section-label {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0.5rem 0 0.65rem;
}
[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text);
  font-weight: 500;
  font-size: 0.875rem;
  padding: 0.55rem 0.85rem;
  transition: background var(--transition), border-color var(--transition), box-shadow var(--transition), transform 120ms ease;
  text-align: left;
  justify-content: flex-start;
}
[data-testid="stSidebar"] .stButton > button:hover {
  border-color: var(--gold-border);
  background: var(--elevated);
  box-shadow: 0 0 14px var(--gold-glow);
}
[data-testid="stSidebar"] .stButton > button:active { transform: scale(0.98); }
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: linear-gradient(135deg, rgba(245, 196, 81, 0.22), rgba(245, 196, 81, 0.08));
  border-color: var(--gold-border);
  color: var(--gold);
  font-weight: 600;
  margin-bottom: 0.75rem;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
  box-shadow: 0 0 18px var(--gold-glow);
}
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
  gap: 0.35rem;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  padding: 0.65rem 0.85rem !important;
  transition: border-color var(--transition), background var(--transition), box-shadow var(--transition);
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  border-color: rgba(245, 196, 81, 0.28) !important;
  background: var(--elevated) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
[data-testid="stSidebar"] [data-testid="stRadio"] div[aria-checked="true"] label {
  border-color: var(--gold-border) !important;
  background: var(--gold-dim) !important;
  box-shadow: inset 0 0 0 1px rgba(245, 196, 81, 0.08);
}
[data-testid="stSidebar"] [data-testid="stRadio"] label p {
  font-size: 0.84rem !important;
  font-weight: 500 !important;
  color: var(--text) !important;
}
.sidebar-footer {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}
.sidebar-footer-note {
  font-size: 0.75rem;
  color: var(--muted);
  line-height: 1.45;
}

/* Hero */
.welcome-block { text-align: center; margin: 0 auto 1.5rem; max-width: 36rem; }
.hero-robot {
  position: relative;
  width: min(100%, 200px);
  height: 160px;
  margin: 0 auto 0.75rem;
}
.hero-robot__glow {
  position: absolute;
  inset: 10% 5% 25%;
  background: radial-gradient(circle at 50% 55%, var(--gold-glow), transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.hero-robot__img {
  position: relative;
  z-index: 1;
  max-height: 150px;
  width: auto;
  margin: 0 auto;
  display: block;
  filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.45)) drop-shadow(0 0 20px var(--gold-glow));
}
.welcome-title {
  font-family: var(--font-display);
  font-size: clamp(1.65rem, 4vw, 2rem);
  font-weight: 700;
  color: var(--text);
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}
.welcome-subtitle {
  color: var(--muted);
  font-size: 0.95rem;
  line-height: 1.55;
  margin: 0 auto 1.25rem;
  max-width: 28rem;
}

/* Cards & upload */
.upload-card {
  background: var(--card);
  border: 1px dashed var(--border);
  border-radius: var(--radius-lg);
  padding: 1.35rem 1.25rem 0.35rem;
  margin: 0 auto 1rem;
  max-width: 36rem;
  transition: border-color var(--transition), box-shadow var(--transition);
}
.upload-card:hover {
  border-color: var(--gold-border);
  box-shadow: 0 0 20px var(--gold-glow);
}
.upload-card__head {
  text-align: center;
  margin-bottom: 0.85rem;
}
.upload-card__icon {
  width: 44px;
  height: 44px;
  margin: 0 auto 0.65rem;
  border-radius: var(--radius-md);
  background: var(--elevated);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gold);
}
.upload-card__title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--text);
  margin: 0 0 0.25rem;
}
.upload-card__hint {
  font-size: 0.82rem;
  color: var(--muted);
  margin: 0;
}
.upload-card__limit {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 0.35rem;
  opacity: 0.85;
}
section.main [data-testid="stFileUploader"] {
  border: none !important;
  background: transparent !important;
  padding: 0 !important;
  box-shadow: none !important;
}
section.main [data-testid="stFileUploader"] label,
section.main [data-testid="stFileUploader"] p,
section.main [data-testid="stFileUploader"] span,
section.main [data-testid="stFileUploader"] small {
  color: var(--muted) !important;
  font-size: 0.8rem !important;
}

.file-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: var(--elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.5rem;
  font-size: 0.84rem;
}
.file-chip__meta { color: var(--muted); font-size: 0.78rem; margin-top: 0.15rem; }
.file-chip__name { color: var(--text); font-weight: 600; word-break: break-all; }

.prompt-grid { margin: 0.5rem auto 1.25rem; max-width: 36rem; }
.prompt-grid-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--muted);
  margin-bottom: 0.65rem;
  text-align: center;
}
[data-testid="stHorizontalBlock"]:has(.prompt-grid) .stButton > button,
.prompt-grid + div .stButton > button,
section.main .prompt-grid ~ div [data-testid="column"] .stButton > button {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border) !important;
  background: var(--card) !important;
  color: var(--text) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  padding: 0.85rem 0.65rem !important;
  min-height: 3.25rem;
  line-height: 1.35 !important;
  transition: border-color var(--transition), box-shadow var(--transition), background var(--transition);
  white-space: normal !important;
  height: auto !important;
}
section.main [data-testid="column"] .stButton > button:hover {
  border-color: var(--gold-border) !important;
  box-shadow: 0 0 14px var(--gold-glow);
  background: var(--elevated) !important;
  color: var(--gold) !important;
}

.page-header {
  max-width: 36rem;
  margin: 0 auto 1.5rem;
  text-align: center;
}
.page-header h1 {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
  color: var(--text);
}
.page-header p {
  color: var(--muted);
  font-size: 0.92rem;
  line-height: 1.55;
  margin: 0;
}
.empty-state {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 2rem 1.5rem;
  text-align: center;
  max-width: 32rem;
  margin: 1rem auto;
}
.empty-state__icon { font-size: 2rem; margin-bottom: 0.75rem; opacity: 0.9; }
.empty-state h2 { font-size: 1.1rem; margin: 0 0 0.5rem; color: var(--text); }
.empty-state p { font-size: 0.88rem; color: var(--muted); line-height: 1.55; margin: 0; }

.hub-hint {
  color: var(--muted);
  font-size: 0.85rem;
  margin: 0.75rem 0;
  text-align: center;
  direction: rtl;
  unicode-bidi: plaintext;
}

section.main [data-testid="stExpander"] details {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  background: var(--card) !important;
}
section.main [data-testid="stExpander"] summary {
  color: var(--text) !important;
  font-weight: 600;
  font-size: 0.875rem;
}
section.main [data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  background: var(--elevated) !important;
}

/* Chat */
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none; }
[data-testid="stChatMessage"] {
  background: transparent;
  padding: 0.4rem 0;
  border: none;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  direction: rtl;
  justify-content: flex-start;
  margin: 0.75rem 0 0.35rem;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
  background: var(--elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg) var(--radius-lg) 4px var(--radius-lg);
  padding: 0.75rem 1rem;
  max-width: min(88%, 34rem);
  margin-inline-start: auto;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
  direction: ltr;
  margin: 0.35rem 0 0.85rem;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 0.85rem 1.05rem;
  max-width: 100%;
}
[data-testid="stChatMessageContent"] {
  font-size: 0.925rem;
  line-height: 1.75;
  unicode-bidi: plaintext;
  text-align: start;
  color: var(--text);
}
[data-testid="stChatMessageContent"] code {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 0.86em;
  background: rgba(0, 0, 0, 0.35);
  padding: 0.15rem 0.4rem;
  border-radius: 6px;
  border: 1px solid var(--border);
}
[data-testid="stChatMessageContent"] pre {
  background: #0a0c10 !important;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.85rem !important;
  overflow-x: auto;
}
[data-testid="stChatMessageContent"] table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin: 0.5rem 0;
}
[data-testid="stChatMessageContent"] th,
[data-testid="stChatMessageContent"] td {
  border: 1px solid var(--border);
  padding: 0.45rem 0.6rem;
}
[data-testid="stChatMessageContent"] th {
  background: var(--elevated);
  font-weight: 600;
}

.msg-actions .stButton > button {
  font-size: 0.75rem !important;
  padding: 0.25rem 0.65rem !important;
  min-height: 2rem;
  border-radius: 8px !important;
  border: 1px solid var(--border) !important;
  background: transparent !important;
  color: var(--muted) !important;
}
.msg-actions .stButton > button:hover {
  color: var(--gold) !important;
  border-color: var(--gold-border) !important;
}

[data-testid="stChatMessage"] [data-testid="stExpander"] details {
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--elevated);
}
.source { font-size: 0.84rem; padding: 0.55rem 0; border-bottom: 1px solid var(--border); }
.source:last-child { border-bottom: none; }
.source span { display: block; color: var(--muted); font-size: 0.78rem; margin-top: 0.2rem; }

.stButton > button {
  border-radius: var(--radius-md);
  transition: border-color var(--transition), box-shadow var(--transition), transform 120ms ease;
}
.stButton > button:active { transform: scale(0.98); }

.chat-footer-credit {
  position: fixed;
  left: 0; right: 0; bottom: 0;
  height: calc(var(--app-footer-h) + env(safe-area-inset-bottom, 0px));
  z-index: 990;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  padding-bottom: env(safe-area-inset-bottom, 0px);
  background: rgba(16, 19, 26, 0.96);
  border-top: 1px solid var(--border);
}
.chat-footer-credit a.dev-footer {
  pointer-events: auto;
  color: var(--muted) !important;
  font-size: 0.8rem;
  font-weight: 500;
  text-decoration: none;
  transition: color var(--transition);
}
.chat-footer-credit a.dev-footer:hover { color: var(--gold) !important; }

[data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
  bottom: calc(var(--app-footer-h) + env(safe-area-inset-bottom, 0px)) !important;
  z-index: 1000 !important;
}
[data-testid="stBottom"] > div {
  background: linear-gradient(180deg, transparent, var(--bg) 28%);
  padding-top: 0.5rem;
}
[data-testid="stChatInput"] {
  border-radius: var(--radius-lg) !important;
  border: 1px solid var(--border) !important;
  background: var(--card) !important;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
  transition: border-color var(--transition), box-shadow var(--transition);
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--gold-border) !important;
  box-shadow: 0 0 0 1px var(--gold-border), 0 0 18px var(--gold-glow);
}
[data-testid="stChatInput"] textarea {
  font-size: 0.94rem;
  line-height: 1.6;
  direction: rtl;
  unicode-bidi: plaintext;
  color: var(--text);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
""",
        unsafe_allow_html=True,
    )

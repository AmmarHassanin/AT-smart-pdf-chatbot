import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Alexandria:wght@500;600;700&display=swap');

html[data-theme="dark"], :root {
  --bg: #08090c;
  --sidebar: #0e1014;
  --card: #12151c;
  --elevated: #181c24;
  --gold: #d4b87a;
  --gold-dim: rgba(212, 184, 122, 0.12);
  --gold-border: rgba(212, 184, 122, 0.38);
  --gold-glow: rgba(212, 184, 122, 0.18);
  --text: #f3f4f6;
  --muted: #9ca3af;
  --border: #252a33;
  --success: #34d399;
  --error: #f87171;
  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-lg: 18px;
  --transition: 180ms ease;
  --font-ui: "Inter", "Segoe UI", system-ui, sans-serif;
  --font-display: "Alexandria", "Inter", sans-serif;
  --app-footer-h: 2.5rem;
  --content-max: 920px;
  --workspace-max: 1440px;
  --shadow-soft: 0 8px 32px rgba(0, 0, 0, 0.35);
  --panel-bg: rgba(18, 21, 28, 0.72);
  --surface-hover: rgba(212, 184, 122, 0.06);
}
html[data-theme="light"] {
  --bg: #f4f5f7;
  --sidebar: #ffffff;
  --card: #ffffff;
  --elevated: #eef0f4;
  --gold: #9a7b4f;
  --gold-dim: rgba(154, 123, 79, 0.12);
  --gold-border: rgba(154, 123, 79, 0.35);
  --gold-glow: rgba(154, 123, 79, 0.12);
  --text: #111827;
  --muted: #6b7280;
  --border: #e5e7eb;
  --shadow-soft: 0 8px 28px rgba(17, 24, 39, 0.08);
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
  max-width: min(100%, calc(var(--content-max) + 4rem));
  padding-top: 2rem;
  padding-left: 1.25rem;
  padding-right: 1.25rem;
  padding-bottom: calc(7.5rem + var(--app-footer-h) + env(safe-area-inset-bottom, 0px));
}
@media (max-width: 768px) {
  .block-container { padding-top: 3.25rem; padding-left: 1rem; padding-right: 1rem; }
  .feature-grid { grid-template-columns: 1fr !important; }
  .at-pdf-canvas-wrap { max-height: 360px; }
  [data-testid="stSidebarCollapsedControl"] {
    position: fixed !important;
    top: 0.5rem;
    left: 0.65rem;
  }
}

/* Sidebar — fixed in viewport; main content scrolls independently */
[data-testid="stAppViewContainer"] {
  align-items: flex-start !important;
}
[data-testid="stSidebar"] {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  bottom: 0 !important;
  height: 100dvh !important;
  max-height: 100dvh !important;
  width: var(--sidebar-width, 21rem) !important;
  min-width: 280px !important;
  max-width: 21rem !important;
  overflow: hidden !important;
  z-index: 998 !important;
  background: var(--sidebar) !important;
  border-right: 1px solid var(--border);
  flex-shrink: 0 !important;
}
html[dir="rtl"] [data-testid="stSidebar"] {
  left: auto !important;
  right: 0 !important;
  border-right: none;
  border-left: 1px solid var(--border);
}
[data-testid="stSidebar"] > div:first-child {
  background: var(--sidebar);
  height: 100% !important;
  max-height: 100dvh !important;
  overflow: hidden !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  height: 100% !important;
  max-height: 100dvh !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  overscroll-behavior: contain;
}
section.main {
  margin-left: var(--sidebar-width, 21rem) !important;
  width: calc(100% - var(--sidebar-width, 21rem)) !important;
  min-height: 100dvh;
}
html[dir="rtl"] section.main {
  margin-left: 0 !important;
  margin-right: var(--sidebar-width, 21rem) !important;
}
[data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="false"]) section.main {
  margin-left: 0 !important;
  margin-right: 0 !important;
  width: 100% !important;
}
[data-testid="stSidebar"][aria-expanded="false"] {
  transform: translateX(-110%) !important;
  pointer-events: none !important;
}
html[dir="rtl"] [data-testid="stSidebar"][aria-expanded="false"] {
  transform: translateX(110%) !important;
}
@media (max-width: 768px) {
  section.main {
    margin-left: 0 !important;
    margin-right: 0 !important;
    width: 100% !important;
  }
  [data-testid="stSidebar"] {
    box-shadow: 8px 0 32px rgba(0, 0, 0, 0.45);
  }
}
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] > div:first-child > div {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.st-key-sidebar_top { flex-shrink: 0; }
.st-key-sidebar_chat_list {
  flex: 1 1 auto;
  overflow-y: auto;
  min-height: 0;
}
.st-key-sidebar_bottom {
  margin-top: auto;
  flex-shrink: 0;
  padding-top: 0.85rem;
  border-top: 1px solid var(--border);
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

/* Translate / language — horizontal EN ↔ AR toggle */
.tr-dir-label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 0.45rem;
}
.st-key-tr_dir_toggle [data-testid="stSegmentedControl"],
.st-key-lang_nav_toggle [data-testid="stSegmentedControl"] {
  width: 100%;
  background: var(--elevated) !important;
  border: 1px solid var(--border) !important;
  border-radius: 999px !important;
  padding: 3px !important;
}
.st-key-tr_dir_toggle [data-baseweb="segmented-control"],
.st-key-lang_nav_toggle [data-baseweb="segmented-control"] {
  width: 100% !important;
  background: transparent !important;
}
.st-key-tr_dir_toggle [data-baseweb="segmented-control"] button,
.st-key-lang_nav_toggle [data-baseweb="segmented-control"] button {
  flex: 1 !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  border-radius: 999px !important;
  color: var(--muted) !important;
  background: transparent !important;
  border: none !important;
  transition: color var(--transition), background var(--transition), box-shadow var(--transition) !important;
}
.st-key-tr_dir_toggle [data-baseweb="segmented-control"] button[aria-selected="true"],
.st-key-lang_nav_toggle [data-baseweb="segmented-control"] button[aria-selected="true"] {
  color: var(--text) !important;
  background: linear-gradient(135deg, var(--gold-dim), var(--card)) !important;
  box-shadow: 0 0 12px var(--gold-glow), inset 0 0 0 1px var(--gold-border) !important;
}
html[dir="rtl"] .st-key-tr_dir_toggle [data-baseweb="segmented-control"],
html[dir="rtl"] .st-key-lang_nav_toggle [data-baseweb="segmented-control"] {
  flex-direction: row-reverse;
}

.lang-switch-wrap { margin-bottom: 0.65rem; }
.lang-switch-wrap [data-testid="stColumn"] { padding: 0 2px !important; }
.lang-switch-wrap button {
  font-size: 0.68rem !important;
  font-weight: 600 !important;
  padding: 0.28rem 0.35rem !important;
  min-height: 1.75rem !important;
  line-height: 1.1 !important;
}

.sidebar-section-label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  color: var(--muted);
  margin: 0.9rem 0 0.5rem;
}

/* New-chat pill button */
.st-key-new_chat_wrap { margin-bottom: 0.75rem; }
.st-key-new_chat_wrap .stButton button {
  border-radius: 999px !important;
  justify-content: center !important;
  text-align: center !important;
  font-weight: 700 !important;
}

/* Search input with icon */
.st-key-chat_search_wrap { margin-bottom: 0.35rem; }
.st-key-chat_search_wrap input {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.3-4.3'/%3E%3C/svg%3E") !important;
  background-repeat: no-repeat !important;
  background-position: 0.65rem center !important;
  padding-left: 2.1rem !important;
}
html[dir="rtl"] .st-key-chat_search_wrap input {
  background-position: right 0.65rem center !important;
  padding-left: 0.65rem !important;
  padding-right: 2.1rem !important;
}

/* Chat list rows */
[class*="st-key-chat_row_"] {
  position: relative;
  margin-bottom: 0.3rem;
}
[class*="st-key-chat_row_"] [data-testid="stVerticalBlockBorderWrapper"] { gap: 0 !important; }
[class*="st-key-chat_switch_"] {
  position: absolute;
  inset: 0;
  z-index: 1;
}
[class*="st-key-chat_switch_"] .stButton { height: 100%; margin: 0 !important; }
[class*="st-key-chat_switch_"] .stButton button {
  width: 100%;
  height: 100%;
  opacity: 0;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}
[class*="st-key-chat_actions_"] {
  position: absolute;
  top: 0.4rem;
  right: 0.4rem;
  z-index: 2;
  width: 4.2rem;
}
html[dir="rtl"] [class*="st-key-chat_actions_"] { right: auto; left: 0.4rem; }
[class*="st-key-chat_actions_"] [data-testid="stHorizontalBlock"] { gap: 0.25rem; }
[class*="st-key-chat_actions_"] .stButton button {
  width: 1.7rem;
  height: 1.7rem;
  min-height: 1.7rem;
  padding: 0;
  border-radius: 7px;
  font-size: 0;
  background: var(--elevated);
  border: 1px solid var(--border);
  background-repeat: no-repeat;
  background-position: center;
  background-size: 13px;
  opacity: 0;
  transition: opacity var(--transition), border-color var(--transition);
}
[class*="st-key-chat_row_"]:hover [class*="st-key-chat_actions_"] .stButton button { opacity: 1; }
[class*="st-key-chat_actions_"] [data-testid="stColumn"]:nth-of-type(1) .stButton button {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z'/%3E%3C/svg%3E");
}
[class*="st-key-chat_actions_"] [data-testid="stColumn"]:nth-of-type(2) .stButton button {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%23f87171' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0-1 14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2L4 6h16z'/%3E%3C/svg%3E");
}
[class*="st-key-chat_actions_"] .stButton button:hover { border-color: var(--gold-border); }

.chat-card {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.6rem 2.6rem 0.6rem 0.7rem;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: border-color var(--transition), background var(--transition);
}
html[dir="rtl"] .chat-card { padding: 0.6rem 0.7rem 0.6rem 2.6rem; }
[class*="st-key-chat_row_"]:hover .chat-card { background: var(--surface-hover); border-color: var(--border); }
.chat-card.is-active { background: var(--gold-dim); border-color: var(--gold-border); }
.chat-card__icon { color: var(--muted); margin-top: 1px; flex-shrink: 0; }
.chat-card.is-active .chat-card__icon { color: var(--gold); }
.chat-card__body { display: flex; flex-direction: column; overflow: hidden; min-width: 0; }
.chat-card__title {
  font-size: 0.84rem; font-weight: 600; color: var(--text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.chat-card.is-active .chat-card__title { color: var(--gold); }
.chat-card__time { font-size: 0.7rem; color: var(--muted); margin-top: 0.1rem; }

/* Settings row */
.st-key-settings_wrap [data-testid="stExpander"] summary {
  display: flex; align-items: center; gap: 0.5rem;
}
.st-key-settings_wrap [data-testid="stExpander"] summary::before {
  content: "";
  width: 15px; height: 15px; flex-shrink: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='1.6'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
}

/* Top navbar — EN | AR pill toggle (UI language) */
.st-key-top_navbar {
  position: sticky;
  top: 0.55rem;
  z-index: 1004;
  width: min(100%, 12.5rem);
  margin-inline-start: auto;
  margin-bottom: -2.75rem;
  padding: 0 !important;
}
html[dir="rtl"] .st-key-top_navbar {
  margin-inline-start: 0;
  margin-inline-end: auto;
}
.st-key-top_navbar [data-testid="stVerticalBlock"] {
  gap: 0 !important;
}
.st-key-top_navbar .st-key-lang_nav_toggle {
  width: 100%;
}
.st-key-top_navbar [data-testid="stSegmentedControl"] {
  width: 100%;
  background: var(--elevated) !important;
  border: 1px solid var(--border) !important;
  border-radius: 999px !important;
  padding: 3px !important;
  box-shadow: var(--shadow-soft);
}
.st-key-top_navbar [data-baseweb="segmented-control"] {
  width: 100% !important;
  background: transparent !important;
  min-height: 2.1rem !important;
}
.st-key-top_navbar [data-baseweb="segmented-control"] button {
  flex: 1 !important;
  font-size: 0.74rem !important;
  font-weight: 600 !important;
  border-radius: 999px !important;
  color: var(--muted) !important;
  background: transparent !important;
  border: none !important;
  padding: 0.35rem 0.5rem !important;
  transition: color var(--transition), background var(--transition), box-shadow var(--transition) !important;
}
.st-key-top_navbar [data-baseweb="segmented-control"] button[aria-selected="true"] {
  color: var(--text) !important;
  background: linear-gradient(135deg, var(--gold-dim), var(--card)) !important;
  box-shadow: 0 0 12px var(--gold-glow), inset 0 0 0 1px var(--gold-border) !important;
}
.st-key-top_navbar [data-testid="stWidgetLabel"] { display: none !important; }
@media (max-width: 768px) {
  .st-key-top_navbar {
    top: 0.4rem;
    width: min(calc(100% - 3.5rem), 11rem);
    margin-inline-end: 0.65rem;
  }
  html[dir="rtl"] .st-key-top_navbar { margin-inline-start: 0.65rem; margin-inline-end: 0; }
}
[data-testid="stSidebar"] .stButton button {
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
[data-testid="stSidebar"] .stButton button:hover {
  border-color: var(--gold-border);
  background: var(--elevated);
  box-shadow: 0 0 14px var(--gold-glow);
}
[data-testid="stSidebar"] .stButton button:active { transform: scale(0.98); }
[data-testid="stSidebar"] .stButton button[kind="primary"] {
  background: linear-gradient(135deg, rgba(245, 196, 81, 0.22), rgba(245, 196, 81, 0.08));
  border-color: var(--gold-border);
  color: var(--gold);
  font-weight: 600;
  margin-bottom: 0.75rem;
}
[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
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
.sidebar-profile {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: 1rem;
  padding: 0.65rem 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--card);
}
.sidebar-profile__avatar {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border-radius: 50%;
  background: linear-gradient(145deg, var(--gold-dim), transparent);
  border: 1px solid var(--gold-border);
  color: var(--gold);
  font-weight: 700;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sidebar-profile__meta { display: flex; flex-direction: column; line-height: 1.3; }
.sidebar-profile__name { font-size: 0.85rem; font-weight: 600; color: var(--text); }
.sidebar-profile__plan { font-size: 0.72rem; color: var(--muted); }

/* Hero */
.welcome-hero { margin: 0.5rem auto 1.5rem; max-width: var(--workspace-max); }
section.stMain [data-testid="stColumn"]:has(.hero-robot) { display: flex; align-items: center; justify-content: center; }
.hero-robot {
  position: relative;
  width: min(100%, 280px);
  height: 240px;
  margin: 0 auto;
  perspective: 900px;
}
.hero-robot__glow {
  position: absolute;
  inset: 10% 5% 25%;
  background: radial-gradient(circle at 50% 55%, var(--gold-glow), transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.hero-robot__shadow {
  position: absolute;
  left: 50%;
  bottom: 6%;
  width: 46%;
  height: 14px;
  margin-left: -23%;
  background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.45), transparent 72%);
  border-radius: 50%;
  pointer-events: none;
}
.hero-robot__img {
  position: relative;
  z-index: 1;
  max-height: 230px;
  width: auto;
  margin: 0 auto;
  display: block;
  transform-style: preserve-3d;
  transform: rotateY(-12deg) rotateX(2deg);
  filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.45)) drop-shadow(0 0 20px var(--gold-glow));
}
@media (prefers-reduced-motion: reduce) {
  .hero-robot__img, .hero-robot__glow, .hero-robot__shadow { animation: none !important; }
}
.welcome-title {
  font-family: var(--font-ui);
  font-size: clamp(1.9rem, 3.2vw, 2.6rem);
  font-weight: 800;
  line-height: 1.15;
  color: var(--text);
  margin: 0 0 0.6rem;
  letter-spacing: -0.02em;
}
.welcome-title .accent { color: var(--gold); display: block; }
.welcome-subtitle {
  color: var(--muted);
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 1.25rem;
  max-width: 32rem;
}
@media (max-width: 1150px) {
  section.stMain [data-testid="stHorizontalBlock"]:has(.hero-robot) { flex-direction: column !important; }
  .welcome-title, .welcome-subtitle { text-align: center; }
  .feature-grid { max-width: 40rem; margin-left: auto; margin-right: auto; }
}

/* Cards & upload */
.upload-card {
  background: var(--card);
  border: 1px dashed var(--border);
  border-radius: 20px;
  padding: 1.85rem 1.5rem 0.35rem;
  margin: 0 auto 1rem;
  max-width: var(--workspace-max);
  transition: border-color var(--transition), box-shadow var(--transition);
}
.upload-card:hover {
  border-color: var(--gold);
  box-shadow: 0 0 22px var(--gold-glow);
}
.st-key-upload_dropzone:hover .upload-card {
  border: 2px dashed var(--gold);
  box-shadow: 0 0 28px var(--gold-glow), 0 0 0 1px rgba(212, 184, 122, 0.12);
}
.st-key-upload_dropzone:hover .upload-card__icon {
  border-color: var(--gold);
  box-shadow: 0 0 14px var(--gold-glow);
}
.upload-card__head {
  text-align: center;
  margin-bottom: 0.85rem;
}
.upload-card__icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 0.85rem;
  border-radius: 50%;
  background: linear-gradient(145deg, var(--gold-dim), transparent);
  border: 1px solid var(--gold-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gold);
}
.upload-card__title {
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--text);
  margin: 0 0 0.3rem;
}
.upload-card__hint {
  font-size: 0.85rem;
  color: var(--muted);
  margin: 0;
}
.upload-card__limit {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.74rem;
  color: var(--gold);
  margin-top: 0.6rem;
  opacity: 0.9;
}
.upload-card__limit svg { flex-shrink: 0; }
.st-key-upload_dropzone { position: relative; }
.st-key-upload_dropzone [data-testid="stElementContainer"]:has(.upload-card) {
  pointer-events: none;
}
.st-key-upload_dropzone [data-testid="stElementContainer"]:has([data-testid="stFileUploader"]) {
  position: absolute !important;
  inset: 0 !important;
  z-index: 2;
  margin: 0 !important;
  width: 100% !important;
  height: 100% !important;
}
.st-key-upload_dropzone [data-testid="stFileUploader"] {
  width: 100%;
  height: 100%;
}
.st-key-upload_dropzone [data-testid="stFileUploader"] section,
.st-key-upload_dropzone [data-testid="stFileUploaderDropzone"] {
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  border: none !important;
  background: transparent !important;
  padding: 0 !important;
  box-shadow: none !important;
}
.st-key-upload_dropzone [data-testid="stFileUploader"] label { display: none !important; }
.st-key-upload_dropzone [data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
.st-key-upload_dropzone [data-testid="stFileUploader"] ul { display: none !important; }

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
[data-testid="stHorizontalBlock"]:has(.prompt-grid) .stButton button,
.prompt-grid + div .stButton button,
section.stMain .prompt-grid ~ div [data-testid="stColumn"] .stButton button {
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
section.stMain [data-testid="stColumn"] .stButton button:hover {
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

section.stMain [data-testid="stExpander"] details {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  background: var(--card) !important;
}
section.stMain [data-testid="stExpander"] summary {
  color: var(--text) !important;
  font-weight: 600;
  font-size: 0.875rem;
}
section.stMain [data-testid="stSelectbox"] [role="group"] {
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
  justify-content: flex-end;
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
html[dir="rtl"] [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
  border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) 4px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
  justify-content: flex-start;
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

.msg-actions .stButton button {
  font-size: 0.75rem !important;
  padding: 0.25rem 0.65rem !important;
  min-height: 2rem;
  border-radius: 8px !important;
  border: 1px solid var(--border) !important;
  background: transparent !important;
  color: var(--muted) !important;
}
.msg-actions .stButton button:hover {
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

.stButton button {
  border-radius: var(--radius-md);
  transition: border-color var(--transition), box-shadow var(--transition), transform 120ms ease;
}
.stButton button:active { transform: scale(0.98); }

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
  unicode-bidi: plaintext;
  color: var(--text);
}
html[dir="rtl"] .at-composer textarea { direction: rtl; text-align: right; }
html[dir="ltr"] .at-composer textarea { direction: ltr; text-align: left; }
.at-copy-btn {
  font-size: 12px; padding: 6px 12px; border-radius: 8px;
  border: 1px solid var(--border); background: var(--card);
  color: var(--muted); cursor: pointer; transition: border-color var(--transition), color var(--transition);
}
.at-copy-btn:hover { border-color: var(--gold-border); color: var(--gold); }

.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 0.85rem; margin: 1.25rem auto 1.25rem; max-width: none; }
.feature-card {
  position: relative;
  background: linear-gradient(145deg, var(--card), var(--elevated));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.1rem 1.15rem 1.35rem;
  text-align: start;
  box-shadow: var(--shadow-soft);
  transition: border-color var(--transition), transform 120ms ease;
  min-height: 9rem;
}
.feature-card__icon {
  width: 36px; height: 36px; margin-bottom: 0.75rem;
  border-radius: 10px;
  background: linear-gradient(145deg, var(--gold-dim), transparent);
  border: 1px solid var(--gold-border);
  display: flex; align-items: center; justify-content: center;
  color: var(--gold);
}
.feature-card__title { font-weight: 700; font-size: 0.92rem; color: var(--text); margin: 0 0 0.3rem; }
.feature-card__desc { font-size: 0.78rem; color: var(--muted); line-height: 1.5; margin: 0; }
.feature-card__arrow {
  position: absolute; right: 1rem; bottom: 0.9rem;
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: var(--muted); border: 1px solid var(--border);
  transition: color var(--transition), border-color var(--transition), transform var(--transition);
}
html[dir="rtl"] .feature-card__arrow { right: auto; left: 1rem; transform: scaleX(-1); }
[class*="st-key-feature_card_"] { position: relative; }
[class*="st-key-feature_card_"] .stButton {
  position: absolute; inset: 0; margin: 0 !important; z-index: 1;
}
[class*="st-key-feature_card_"] .stButton button {
  width: 100%; height: 100%; opacity: 0; padding: 0; border: none; background: transparent; cursor: pointer;
}
[class*="st-key-feature_card_"]:hover .feature-card { border-color: var(--gold-border); transform: translateY(-2px); box-shadow: 0 0 18px var(--gold-glow); }
[class*="st-key-feature_card_"]:hover .feature-card__arrow { color: var(--gold); border-color: var(--gold-border); }
html[dir="rtl"] [class*="st-key-feature_card_"]:hover .feature-card__arrow { transform: scaleX(-1) translateX(2px); }
html[dir="ltr"] [class*="st-key-feature_card_"]:hover .feature-card__arrow { transform: translateX(2px); }
.doc-status {
  max-width: var(--content-max); margin: 0 auto 0.75rem; padding: 0.65rem 0.85rem;
  border-radius: var(--radius-md); border: 1px solid var(--border); background: var(--card); font-size: 0.84rem;
}
.doc-status--ready { border-color: var(--gold-border); }
.doc-workspace { max-width: var(--content-max); margin: 0 auto 1rem; }
.at-pdf-toolbar { display: flex; gap: 0.35rem; align-items: center; justify-content: center; flex-wrap: wrap;
  padding: 0.35rem; background: var(--elevated); border: 1px solid var(--border); border-radius: var(--radius-sm) var(--radius-sm) 0 0; }
.at-pdf-toolbar button { background: var(--card); border: 1px solid var(--border); color: var(--text); border-radius: 8px; padding: 0.25rem 0.55rem; cursor: pointer; }
.at-pdf-canvas-wrap { overflow: auto; max-height: 520px; background: #1a1a1a; border: 1px solid var(--border); border-top: none; border-radius: 0 0 var(--radius-sm) var(--radius-sm); display: flex; justify-content: center; }
html[dir="rtl"] .block-container { text-align: right; }
html[dir="rtl"] [data-testid="stChatInput"] textarea { direction: rtl; }
html[dir="ltr"] [data-testid="stChatInput"] textarea { direction: ltr; }
.sidebar-brand__text { letter-spacing: 0.06em; }
.sidebar-brand__text span { color: var(--gold); font-weight: 700; }
.sidebar-brand__mark svg { color: var(--gold); display: block; }
[data-testid="stSidebar"] .stButton button[kind="primary"] {
  background: linear-gradient(135deg, var(--gold-dim), transparent) !important;
  border: 1px solid var(--gold-border) !important;
  color: var(--text) !important;
  font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
  box-shadow: 0 0 16px var(--gold-glow) !important;
}
[data-testid="stSidebar"] .stTextInput input {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.84rem !important;
  padding: 0.45rem 0.65rem !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
  border-color: var(--gold-border) !important;
  box-shadow: 0 0 0 1px var(--gold-glow) !important;
}

section.stMain:has(.at-workspace-marker) .block-container,
section.stMain:has(.welcome-hero) .block-container {
  max-width: min(100%, var(--workspace-max));
  padding-top: 1.25rem;
}
.st-key-workspace_pdf_panel, .st-key-workspace_ai_panel {
  background: var(--panel-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 0.75rem 0.85rem 1rem;
  box-shadow: var(--shadow-soft);
}
.st-key-workspace_ai_panel { min-height: 32rem; }
.at-ai-panel__head {
  display: flex; align-items: center; gap: 0.65rem;
  margin-bottom: 0.75rem; padding-bottom: 0.65rem; border-bottom: 1px solid var(--border);
}
.at-ai-panel__avatar {
  width: 32px; height: 32px; border-radius: 10px;
  background: linear-gradient(145deg, var(--gold-dim), transparent);
  border: 1px solid var(--gold-border);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.72rem; font-weight: 700; color: var(--gold); letter-spacing: 0.04em;
}
.at-ai-panel__title { font-weight: 600; font-size: 0.95rem; color: var(--text); margin: 0; }
.at-ai-panel__sub { font-size: 0.75rem; color: var(--muted); margin: 0; }
.st-key-chat_scroll_area { max-height: 22rem; overflow-y: auto; padding-right: 0.25rem; margin-bottom: 0.65rem; }
.stTabs [data-baseweb="tab-list"] {
  gap: 0.35rem; background: transparent; border-bottom: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  font-size: 0.78rem !important; font-weight: 600 !important;
  padding: 0.45rem 0.65rem !important; color: var(--muted) !important;
  background: transparent !important; border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
}
.stTabs [aria-selected="true"] {
  color: var(--gold) !important;
  box-shadow: inset 0 -2px 0 var(--gold) !important;
}
.st-key-ai_toolbar { margin-bottom: 0.75rem; }
.st-key-ai_toolbar [data-testid="stHorizontalBlock"] { gap: 0.3rem; }
.st-key-ai_toolbar .stButton button {
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  padding: 0.4rem 0.3rem !important;
  min-height: 2rem !important;
  border-radius: var(--radius-sm) !important;
  white-space: nowrap;
}
.st-key-ai_toolbar .stButton button[kind="secondary"] {
  background: transparent !important;
  border-color: var(--border) !important;
  color: var(--muted) !important;
}
.st-key-ai_toolbar .stButton button[kind="primary"] {
  background: var(--gold-dim) !important;
  border-color: var(--gold-border) !important;
  color: var(--gold) !important;
}
.feature-card:hover { border-color: var(--gold-border); transform: translateY(-1px); }
.at-pdf-shell { border-radius: var(--radius-md); overflow: hidden; border: 1px solid var(--border); }
.at-pdf-toolbar--rich {
  display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0.5rem;
  padding: 0.55rem 0.75rem; background: var(--elevated); border-bottom: 1px solid var(--border);
}
.at-pdf-toolbar__name { font-size: 0.82rem; font-weight: 600; color: var(--text); display: block; }
.at-pdf-toolbar__meta { font-size: 0.72rem; color: var(--muted); }
.at-pdf-toolbar__controls { display: flex; align-items: center; gap: 0.35rem; flex-wrap: wrap; }
.at-pdf-btn {
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--card); border: 1px solid var(--border); color: var(--text);
  border-radius: 8px; padding: 0.2rem 0.5rem; cursor: pointer; font-size: 0.78rem;
  text-decoration: none; line-height: 1.4;
  transition: border-color var(--transition), background var(--transition);
}
.at-pdf-btn:hover { border-color: var(--gold-border); background: var(--surface-hover); }
.at-pdf-btn--ghost { opacity: 0.85; }
.at-pdf-page, .at-pdf-zoom { font-size: 0.75rem; color: var(--muted); min-width: 3.5rem; text-align: center; }
.at-pdf-sep { width: 1px; height: 1.25rem; background: var(--border); margin: 0 0.15rem; }
.at-pdf-canvas-wrap {
  overflow: auto; max-height: min(58vh, 520px); background: #0d0f12;
  display: flex; justify-content: center; padding: 0.5rem;
}
.at-pdf-thumbs {
  display: flex; gap: 0.35rem; padding: 0.45rem 0.55rem; overflow-x: auto;
  background: var(--card); border-top: 1px solid var(--border);
}
.at-pdf-thumb {
  min-width: 2rem; height: 2rem; border-radius: 6px; border: 1px solid var(--border);
  background: var(--elevated); color: var(--muted); font-size: 0.72rem; cursor: pointer;
}
.at-pdf-thumb.is-active { border-color: var(--gold); color: var(--gold); }
.at-composer textarea { font-size: 0.88rem !important; }
section.stMain:has(.at-workspace-marker) .at-workspace-grid ~ div [data-testid="stChatMessage"],
section.stMain:has(.at-workspace-marker) .at-workspace-grid ~ div [data-testid="stStatusWidget"] {
  display: none !important;
}
section.stMain:has(.at-workspace-marker) [data-testid="stBottom"] {
  max-width: min(42rem, 46vw);
  margin-inline-start: auto;
  margin-inline-end: 1.25rem;
}
html[dir="rtl"] section.stMain:has(.at-workspace-marker) [data-testid="stBottom"] {
  margin-inline-start: 1.25rem;
  margin-inline-end: auto;
}
@media (max-width: 1100px) {
  section.stMain:has(.at-workspace-marker) [data-testid="stBottom"] { max-width: 100%; margin: 0; }
  .st-key-workspace_pdf_panel, .st-key-workspace_ai_panel { min-height: auto !important; }
}
@media (max-width: 900px) {
  section.stMain:has(.at-workspace-marker) [data-testid="stHorizontalBlock"]:has(.st-key-workspace_pdf_panel) {
    flex-direction: column !important;
  }
  .st-key-workspace_pdf_panel, .st-key-workspace_ai_panel {
    width: 100% !important; margin-bottom: 0.75rem;
  }
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

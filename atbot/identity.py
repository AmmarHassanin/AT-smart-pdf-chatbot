import re

import streamlit as st
import streamlit.components.v1 as components

from atbot.env import is_production

_UID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.I,
)


def _uid_from_query() -> str | None:
    raw = st.query_params.get("atbot_uid")
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    if raw and _UID_PATTERN.match(str(raw)):
        return str(raw)
    return None


def _prompt_browser_uid() -> None:
    components.html(
        """
<script>
(function () {
  const KEY = "atbot_user_id";
  let id = localStorage.getItem(KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(KEY, id);
  }
  const url = new URL(window.parent.location.href);
  if (url.searchParams.get("atbot_uid") !== id) {
    url.searchParams.set("atbot_uid", id);
    window.parent.location.replace(url.toString());
  }
})();
</script>
        """,
        height=0,
        width=0,
    )


def resolve_user_id() -> str:
    if not is_production():
        return "dev"

    if st.session_state.get("atbot_user_id"):
        return st.session_state.atbot_user_id

    uid = _uid_from_query()
    if uid:
        st.session_state.atbot_user_id = uid
        return uid

    _prompt_browser_uid()
    st.stop()

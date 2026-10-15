import base64

import streamlit as st

from atbot.constants import ROBOT_IMAGE


@st.cache_data(show_spinner=False)
def robot_image_png() -> bytes | None:
    if not ROBOT_IMAGE.is_file():
        return None
    return ROBOT_IMAGE.read_bytes()


@st.cache_data(show_spinner=False)
def robot_hero_html() -> str | None:
    png = robot_image_png()
    if not png:
        return None
    uri = base64.b64encode(png).decode("ascii")
    return f"""
<div class="hero-robot" aria-hidden="true">
  <div class="hero-robot__glow"></div>
  <img class="hero-robot__img" src="data:image/png;base64,{uri}" alt="" />
  <div class="hero-robot__shadow"></div>
</div>
"""

import base64
from io import BytesIO

import streamlit as st

from atbot.constants import ROBOT_IMAGE


@st.cache_data(show_spinner=False)
def robot_image_png() -> bytes | None:
    if not ROBOT_IMAGE.is_file():
        return None
    from PIL import Image, ImageEnhance

    img = Image.open(ROBOT_IMAGE).convert("RGBA")
    out = []
    for r, g, b, a in img.getdata():
        m = min(r, g, b)
        if m >= 248:
            out.append((r, g, b, 0))
        elif m >= 218:
            fade = int((248 - m) / 30 * 255)
            out.append((r, g, b, fade))
        else:
            out.append((r, g, b, 255))
    img.putdata(out)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Sharpness(img).enhance(1.08)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


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
</div>
"""

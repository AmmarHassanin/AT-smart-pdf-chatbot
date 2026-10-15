"""Embedded PDF viewer with toolbar, thumbnails, and zoom."""

from __future__ import annotations

import base64
import html
import json

import streamlit.components.v1 as components


def render_pdf_viewer(
    pdf_bytes: bytes,
    *,
    filename: str,
    meta_line: str,
    page: int,
    zoom: float,
    element_id: str,
    height: int = 580,
) -> None:
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    safe_id = html.escape(element_id, quote=True)
    safe_name = html.escape(filename)
    safe_meta = html.escape(meta_line)
    page = max(1, int(page))
    zoom_pct = max(50, min(200, int(zoom * 100)))
    id_canvas = safe_id + "-canvas"
    id_prev = safe_id + "-prev"
    id_next = safe_id + "-next"
    id_label = safe_id + "-page-label"
    id_zin = safe_id + "-zoom-in"
    id_zout = safe_id + "-zoom-out"
    id_zlabel = safe_id + "-zoom-label"
    id_fs = safe_id + "-fs"
    id_wrap = safe_id + "-wrap"
    id_thumbs = safe_id + "-thumbs"

    components.html(
        f"""
<div class="at-pdf-shell" id="{id_wrap}">
  <div class="at-pdf-toolbar at-pdf-toolbar--rich">
    <div class="at-pdf-toolbar__file">
      <span class="at-pdf-toolbar__name">{safe_name}</span>
      <span class="at-pdf-toolbar__meta">{safe_meta}</span>
    </div>
    <div class="at-pdf-toolbar__controls">
      <button type="button" class="at-pdf-btn" id="{id_prev}" title="Previous">&#9664;</button>
      <span class="at-pdf-page" id="{id_label}">1 / ?</span>
      <button type="button" class="at-pdf-btn" id="{id_next}" title="Next">&#9654;</button>
      <span class="at-pdf-sep"></span>
      <button type="button" class="at-pdf-btn" id="{id_zout}">−</button>
      <span class="at-pdf-zoom" id="{id_zlabel}">{zoom_pct}%</span>
      <button type="button" class="at-pdf-btn" id="{id_zin}">+</button>
      <button type="button" class="at-pdf-btn at-pdf-btn--ghost" id="{id_fs}" title="Fullscreen">&#9974;</button>
      <a class="at-pdf-btn at-pdf-btn--ghost" href="data:application/pdf;base64,{b64}" download="{safe_name}" title="Download">&#8595;</a>
    </div>
  </div>
  <div class="at-pdf-canvas-wrap">
    <canvas id="{id_canvas}"></canvas>
  </div>
  <div class="at-pdf-thumbs" id="{id_thumbs}"></div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<script>
(function() {{
  const pdfData = atob({json.dumps(b64)});
  const bytes = new Uint8Array(pdfData.length);
  for (let i = 0; i < pdfData.length; i++) bytes[i] = pdfData.charCodeAt(i);
  const pdfjsLib = window.pdfjsLib;
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

  let pdfDoc = null;
  let pageNum = {page};
  let scale = {zoom_pct / 100};
  const canvas = document.getElementById({json.dumps(id_canvas)});
  const ctx = canvas.getContext('2d');
  const label = document.getElementById({json.dumps(id_label)});
  const zoomLabel = document.getElementById({json.dumps(id_zlabel)});
  const thumbs = document.getElementById({json.dumps(id_thumbs)});
  const wrap = document.getElementById({json.dumps(id_wrap)});

  function renderPage(num) {{
    pdfDoc.getPage(num).then(function(page) {{
      const viewport = page.getViewport({{ scale }});
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      page.render({{ canvasContext: ctx, viewport }}).promise.then(function() {{
        label.textContent = num + ' / ' + pdfDoc.numPages;
        zoomLabel.textContent = Math.round(scale * 100) + '%';
        [...thumbs.querySelectorAll('.at-pdf-thumb')].forEach(function(el) {{
          el.classList.toggle('is-active', parseInt(el.dataset.page, 10) === num);
        }});
      }});
    }});
  }}

  function buildThumbs() {{
    const max = Math.min(pdfDoc.numPages, 10);
    thumbs.innerHTML = '';
    for (let i = 1; i <= max; i++) {{
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'at-pdf-thumb';
      btn.dataset.page = String(i);
      btn.textContent = i;
      btn.onclick = function() {{ pageNum = i; renderPage(pageNum); }};
      thumbs.appendChild(btn);
    }}
  }}

  pdfjsLib.getDocument({{ data: bytes }}).promise.then(function(pdf) {{
    pdfDoc = pdf;
    pageNum = Math.min(Math.max(1, pageNum), pdf.numPages);
    buildThumbs();
    renderPage(pageNum);
  }}).catch(function(err) {{
    label.textContent = 'PDF error';
    console.error(err);
  }});

  document.getElementById({json.dumps(id_prev)}).onclick = function() {{
    if (!pdfDoc || pageNum <= 1) return;
    pageNum--;
    renderPage(pageNum);
  }};
  document.getElementById({json.dumps(id_next)}).onclick = function() {{
    if (!pdfDoc || pageNum >= pdfDoc.numPages) return;
    pageNum++;
    renderPage(pageNum);
  }};
  document.getElementById({json.dumps(id_zin)}).onclick = function() {{
    scale = Math.min(2, scale + 0.1);
    renderPage(pageNum);
  }};
  document.getElementById({json.dumps(id_zout)}).onclick = function() {{
    scale = Math.max(0.5, scale - 0.1);
    renderPage(pageNum);
  }};
  document.getElementById({json.dumps(id_fs)}).onclick = function() {{
    if (!wrap.requestFullscreen) return;
    wrap.requestFullscreen().catch(function() {{}});
  }};
}})();
</script>
""",
        height=height,
    )

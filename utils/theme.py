"""Loads the shared CSS theme and exposes small HTML-snippet helpers used
across every page so pages don't repeat raw markup."""
from __future__ import annotations

import os
import base64
import mimetypes
import streamlit as st

CSS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "styles", "theme.css")

def image_to_data_uri(path):
    if not path or not os.path.exists(path):
        return None
    mime, _ = mimetypes.guess_type(path)
    mime = mime or "image/png"
    try:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
    except OSError:
        return None
    return f"data:{mime};base64,{encoded}"

def inject_css() -> None:
    if not os.path.exists(CSS_PATH):
        return
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def hero(title: str, subtitle: str, pill_text: str = "Premier League Intelligence") -> None:
    st.markdown(
        f"""
        <div class="pli-hero">
            <span class="pli-pill">{pill_text}</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    st.markdown(
        f'<div class="pli-section-title"><span class="pli-accent-bar"></span>{text}</div>',
        unsafe_allow_html=True,
    )


def insight_box(text: str) -> None:
    st.markdown(f'<div class="pli-insight">💡 {text}</div>', unsafe_allow_html=True)


def pill(text: str, kind: str = "") -> str:
    cls = f"pli-pill {kind}".strip()
    return f'<span class="{cls}">{text}</span>'



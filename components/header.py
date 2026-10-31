"""Shared page header."""
from pathlib import Path
import streamlit as st


def render_header(title, subtitle=""):
    css = (Path(__file__).resolve().parents[1] / "assets" / "style.css").read_text(encoding="utf-8")
    with st.sidebar:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    st.markdown(f'<div class="page-heading"><div class="eyebrow">CRICKETIQ · MATCH INTELLIGENCE</div><h1>{title}</h1></div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

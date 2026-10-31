"""Shared sidebar content."""
from pathlib import Path
import streamlit as st
from services.cricket_api import get_live_matches, match_display_fields, CricketFeedError


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_live_matches():
    return get_live_matches()


def render_sidebar():
    css = (Path(__file__).resolve().parents[1] / "assets" / "style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.markdown('<div class="brand"><span class="brand-mark">🏏</span><div><strong>CricketIQ</strong><small>INSIGHT STUDIO</small></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-note">Your game, in every detail.</div>', unsafe_allow_html=True)
        if st.button("↻ Sync live Cricbuzz data", use_container_width=True, key="global_live_sync"):
            _fetch_live_matches.clear()
            try:
                st.session_state["live_matches"] = _fetch_live_matches()
                st.session_state["selected_live_match"] = 0
                st.session_state.pop("live_matches_error", None)
            except CricketFeedError as error:
                st.session_state["live_matches_error"] = str(error)
        if "live_matches_error" in st.session_state:
            st.error(st.session_state["live_matches_error"])
        matches = st.session_state.get("live_matches", [])
        if matches:
            labels = []
            for i, match in enumerate(matches):
                fields = match_display_fields(match)
                labels.append(f"{fields['team1_name']} vs {fields['team2_name']}")
            st.selectbox("Active match for all features", range(len(labels)),
                         format_func=lambda i: labels[i], key="selected_live_match")
            st.caption(f"Shared live feed · {len(matches)} match(es)")

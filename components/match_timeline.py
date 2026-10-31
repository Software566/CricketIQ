"""Render match events in chronological order."""
import streamlit as st


def render_timeline(events):
    for event in events:
        st.write(f"• {event}")

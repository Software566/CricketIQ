"""Render a compact innings score."""
import streamlit as st


def render_scorecard(team, runs, wickets, overs):
    st.metric(team, f"{runs}/{wickets}", f"{overs} overs")

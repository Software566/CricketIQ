"""Render a player summary card."""
import streamlit as st


def render_player_card(player):
    st.markdown(f"**{player.get('name', 'Unknown player')}**")
    st.caption(player.get("role", "Player"))

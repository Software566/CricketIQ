"""Conversational explanations grounded in the currently selected match."""
import streamlit as st
from components.header import render_header
from services.ai_engine import explain_match, player_reference
from utils.live_match import selected_match, display_fields
from utils.data_processor import load_sample

render_header("AI Match Explainer", "Ask questions and follow up about the same match.")
match = selected_match()
if match:
    fields = display_fields(match)
    match_key = str(match.get("id") or match.get("matchId") or f"{fields['team1_name']}:{fields['team2_name']}")
    st.success(f"LIVE DATA · {fields['team1_name']} vs {fields['team2_name']}")
    st.caption(f"{fields['status']} · {fields['series']}")
else:
    match = load_sample("sample_matches.json")[0]
    match_key = "demo-match"
    st.info("No live feed loaded; answers use the bundled demo match.")

if st.session_state.get("explainer_match_key") != match_key:
    st.session_state["explainer_match_key"] = match_key
    st.session_state["explainer_messages"] = []
    st.session_state["explainer_player_context"] = None

if st.button("Clear conversation", key="clear_explainer"):
    st.session_state["explainer_messages"] = []
    st.session_state["explainer_player_context"] = None

for message in st.session_state["explainer_messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask about the score, top run-scorer, leading wicket-taker, or a follow-up")
if prompt:
    previous_player = st.session_state.get("explainer_player_context") if match_key != "demo-match" else None
    if match_key == "demo-match":
        answer = explain_match({**match, "question": prompt})
    else:
        answer = explain_match({"live_match": match, "question": prompt, "previous_player": previous_player})
        st.session_state["explainer_player_context"] = player_reference(match, prompt, previous_player)
    st.session_state["explainer_messages"].extend([
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": answer},
    ])
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        st.markdown(answer)

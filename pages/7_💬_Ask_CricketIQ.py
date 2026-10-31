"""Question answering over the selected match and scorecard."""
import streamlit as st
from components.header import render_header
from services.ai_engine import explain_match
from utils.live_match import selected_match, display_fields
from utils.data_processor import load_sample

render_header("Ask CricketIQ", "Answers grounded in the selected match data.")
match = selected_match()
question = st.text_input("Your question", placeholder="Who has scored the most runs?")
if st.button("Ask", disabled=not question.strip()):
    if match:
        st.write(explain_match({"live_match": match, "question": question}))
    else:
        sample = load_sample("sample_matches.json")[0]
        st.info("Using demo match data. Sync live Cricbuzz data from the sidebar for current scores.")
        st.write(explain_match({**sample, "question": question}))
if match:
    fields = display_fields(match)
    st.caption(f"Current context: {fields['team1_name']} vs {fields['team2_name']} · {fields['status']}")

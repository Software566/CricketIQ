"""Charts built from the selected live match scorecard."""
import streamlit as st
import pandas as pd
from components.header import render_header
from utils.live_match import selected_match, display_fields, innings_summary_rows, batting_rows
from utils.data_processor import load_sample

render_header("Match Analytics", "Score and player charts from the selected match.")
match = selected_match()
if match:
    fields = display_fields(match)
    st.success(f"LIVE SCORECARD · {fields['team1_name']} vs {fields['team2_name']}")
    innings = innings_summary_rows(match)
    if innings:
        st.subheader("Runs by innings")
        frame = pd.DataFrame(innings).set_index("Team")[["Runs", "Wickets"]]
        st.bar_chart(frame)
        st.dataframe(pd.DataFrame(innings), use_container_width=True, hide_index=True)
    batters = batting_rows(match)
    if batters:
        st.subheader("Batting contributions")
        frame = pd.DataFrame(batters).sort_values("runs", ascending=False).head(10)
        st.bar_chart(frame.set_index("name")[["runs", "fours", "sixes"]])
    if not innings and not batters:
        st.info("No innings scorecard is available yet. Sync again after play begins.")
    st.caption("The selected actor provides innings and player scorecards, not over-by-over ball events. These charts use only returned scorecard totals.")
else:
    st.info("Sync live Cricbuzz data from the sidebar to chart the current match. Showing the bundled sample chart.")
    players = load_sample("sample_players.json")
    if players:
        st.bar_chart(pd.DataFrame({"Runs": [p["runs"] for p in players]}, index=[p["name"] for p in players]))

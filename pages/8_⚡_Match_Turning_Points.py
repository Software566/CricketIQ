"""Identify scorecard-supported high-impact batting partnerships and innings."""
import streamlit as st
import pandas as pd
from components.header import render_header
from utils.live_match import selected_match, display_fields, innings_summary_rows, partnership_rows, fall_of_wicket_rows, batting_rows
from utils.data_processor import load_sample

render_header("Match Turning Points", "Scorecard indicators from the selected match.")
match = selected_match()
if match:
    fields = display_fields(match)
    st.success(f"LIVE SCORECARD · {fields['team1_name']} vs {fields['team2_name']}")
    partnerships = partnership_rows(match)
    wickets = fall_of_wicket_rows(match)
    innings = innings_summary_rows(match)
    if partnerships:
        st.subheader("Partnerships")
        data = pd.DataFrame(partnerships)
        value_col = next((key for key in ("runs", "partnership_runs", "total_runs") if key in data.columns), None)
        if value_col:
            data = data.sort_values(value_col, ascending=False)
            st.caption("Largest partnerships in the available scorecard")
        st.dataframe(data.head(10), use_container_width=True, hide_index=True)
    if wickets:
        st.subheader("Fall of wickets")
        st.dataframe(pd.DataFrame(wickets), use_container_width=True, hide_index=True)
    if innings:
        st.subheader("Innings scores")
        st.bar_chart(pd.DataFrame(innings).set_index("Team")[["Runs", "Wickets"]])
    if not partnerships and not wickets:
        batters = batting_rows(match)
        if batters:
            top = max(batters, key=lambda row: row["runs"])
            st.info(f"Highest individual score in the available card: {top['name']} — {top['runs']} runs. This actor does not provide ball-by-ball events for over-level turning points.")
        else:
            st.info("No scorecard events are available yet for turning point analysis.")
else:
    st.info("Sync live Cricbuzz data from the sidebar to inspect the current match. Sample data has no real turning-point events.")

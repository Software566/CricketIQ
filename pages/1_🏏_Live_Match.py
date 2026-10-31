"""Live scoreboard and match scorecard."""
import streamlit as st
import pandas as pd
from components.header import render_header
from services.cricket_api import match_display_fields
from utils.live_match import selected_match, batting_rows, bowling_rows
from utils.data_processor import load_sample
from utils.calculations import run_rate, required_run_rate, balls_remaining

render_header("Live Match", "Live Cricbuzz score and scorecard.")
match = selected_match()
if match:
    fields = match_display_fields(match)
    st.success(f"LIVE DATA · {fields['state'] or fields['status']}")
    first, second = st.columns(2)
    first.metric(fields["team1_name"], fields["team1_score"])
    second.metric(fields["team2_name"], fields["team2_score"])
    st.subheader(fields["status"])
    detail = " · ".join(value for value in (fields["series"], fields["format"], fields["venue"]) if value)
    if detail:
        st.caption(detail)
    if fields["url"]:
        st.link_button("Open Cricbuzz match", fields["url"])
    if fields["scraped_at"]:
        st.caption(f"Updated {fields['scraped_at']}")
    batters, bowlers = batting_rows(match), bowling_rows(match)
    if batters:
        st.subheader("Batting scorecard")
        st.dataframe(pd.DataFrame(batters).drop(columns=["raw_dismissal"]), use_container_width=True, hide_index=True)
    if bowlers:
        st.subheader("Bowling scorecard")
        st.dataframe(pd.DataFrame(bowlers), use_container_width=True, hide_index=True)
    if not batters and not bowlers:
        st.info("No innings scorecard is available for this match yet.")
else:
    st.info("Use **Sync live Cricbuzz data** in the sidebar. The demo score below is shown until a live feed is loaded.")
    sample = load_sample("sample_matches.json")[0]
    team_a, team_b = sample["teams"]
    runs, _ = map(int, sample["score"].split("/"))
    balls_left = balls_remaining(sample["overs"])
    required = max(0, sample["target"] - runs)
    a, b, c, d = st.columns(4)
    a.metric(team_a, sample["score"], f"{sample['overs']} overs")
    b.metric("Run rate", run_rate(runs, float(sample["overs"])))
    c.metric("Target", sample["target"])
    d.metric("Required rate", required_run_rate(sample["target"], runs, balls_left), f"{required} runs · {balls_left} balls")
    st.caption(f"{team_b} · demo data")

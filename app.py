"""CricketIQ Streamlit home dashboard."""
import streamlit as st
from components.header import render_header
from components.sidebar import render_sidebar
from config.settings import PAGE_TITLE
from utils.data_processor import load_sample
from utils.calculations import run_rate, required_run_rate, balls_remaining
from utils.live_match import selected_match, display_fields

st.set_page_config(page_title=PAGE_TITLE, page_icon="🏏", layout="wide")
render_sidebar()
render_header("CricketIQ", "Your cricket, understood ball by ball.")

live = selected_match()
if live:
    fields = display_fields(live)
    st.subheader(f"{fields['team1_name']} vs {fields['team2_name']} · Live match")
    left, right, third, fourth = st.columns(4)
    left.metric(fields["team1_name"], fields["team1_score"])
    right.metric(fields["team2_name"], fields["team2_score"])
    third.metric("Match state", fields["state"] or "Live")
    fourth.metric("Format", fields["format"] or "Cricket")
    st.caption("Live match selected in the sidebar. All analysis pages use this same match and scorecard.")
else:
    matches = load_sample("sample_matches.json")
    match = matches[0] if matches else {"teams": ["Home", "Away"], "score": "0/0", "overs": "0.0", "target": 0}
    team_a, team_b = match["teams"]
    score_runs, _ = map(int, match["score"].split("/"))
    balls_left = balls_remaining(match["overs"])
    needed = max(0, int(match["target"]) - score_runs)
    st.subheader(f"{team_a} vs {team_b} · Demo match")
    left, right, third, fourth = st.columns(4)
    left.metric(team_a, match["score"], f"{match['overs']} overs")
    right.metric("Run rate", run_rate(score_runs, float(match["overs"])))
    third.metric("Target", match["target"])
    fourth.metric("Required rate", required_run_rate(int(match["target"]), score_runs, balls_left), f"{needed} from {balls_left} balls")
    st.info("Use **Sync live Cricbuzz data** in the sidebar. The selected live match will then power the feature pages.")
st.markdown("### Explore CricketIQ")
st.write("Use the pages in the left sidebar to inspect the score, analytics, players, fantasy points, and turning points.")

"""Player statistics from the selected live match scorecard."""
import streamlit as st
import pandas as pd
from components.header import render_header
from services.player_analyzer import batting_summary
from utils.live_match import selected_match, batting_rows, bowling_rows, display_fields
from utils.data_processor import load_sample

render_header("Player Intelligence", "Inspect batting and bowling performance from the selected match.")
match = selected_match()
if match:
    fields = display_fields(match)
    players = batting_rows(match)
    bowlers = bowling_rows(match)
    st.success(f"LIVE SCORECARD · {fields['team1_name']} vs {fields['team2_name']}")
    options = [f"{p['name']} · {p['team']} · innings {p['innings']}" for p in players]
    if options:
        chosen = st.selectbox("Select a batter", range(len(players)), format_func=lambda i: options[i])
        player = players[chosen]
        stats = batting_summary(player["runs"], player["balls"], player["fours"], player["sixes"])
        st.subheader(player["name"])
        cols = st.columns(4)
        cols[0].metric("Runs", stats["runs"])
        cols[1].metric("Balls", stats["balls"])
        cols[2].metric("Strike rate", stats["strike_rate"])
        cols[3].metric("Fours · sixes", f"{stats['fours']} · {stats['sixes']}")
        st.caption(f"{player['team']} · dismissal: {player['dismissal']}")
        st.bar_chart(pd.DataFrame({"Runs": [player["runs"]], "Boundary runs": [stats["boundary_runs"]]}, index=[player["name"]]))
    else:
        st.info("No batting scorecard is available yet for this match.")
    if bowlers:
        st.subheader("Bowling figures")
        st.dataframe(pd.DataFrame(bowlers), use_container_width=True, hide_index=True)
else:
    st.info("Sync live Cricbuzz data from the sidebar to load current players. Showing demo players for now.")
    players = load_sample("sample_players.json")
    if players:
        names = [p["name"] for p in players]
        player = next(p for p in players if p["name"] == st.selectbox("Select a demo player", names))
        stats = batting_summary(player["runs"], player.get("balls", 0), player.get("fours", 0), player.get("sixes", 0))
        st.subheader(player["name"])
        cols = st.columns(4)
        cols[0].metric("Runs", stats["runs"])
        cols[1].metric("Balls", stats["balls"])
        cols[2].metric("Strike rate", stats["strike_rate"])
        cols[3].metric("Boundaries", stats["boundaries"])

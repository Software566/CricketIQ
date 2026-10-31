"""Compare batters in the selected live match."""
import streamlit as st
import pandas as pd
from components.header import render_header
from services.comparison_engine import compare_players
from utils.live_match import selected_match, batting_rows, display_fields
from utils.data_processor import load_sample

render_header("Player Comparison", "Compare batting figures from one live match scorecard.")
match = selected_match()
if match:
    players = batting_rows(match)
    fields = display_fields(match)
    st.success(f"LIVE SCORECARD · {fields['team1_name']} vs {fields['team2_name']}")
    if len(players) >= 2:
        labels = [f"{p['name']} · {p['team']} · inns {p['innings']}" for p in players]
        first_index = st.selectbox("First batter", range(len(players)), format_func=lambda i: labels[i], key="compare_first")
        other_indexes = [i for i in range(len(players)) if i != first_index]
        second_index = st.selectbox("Second batter", other_indexes, format_func=lambda i: labels[i], key="compare_second")
        first, second = players[first_index], players[second_index]
        metrics = ["runs", "balls", "fours", "sixes", "strike_rate"]
        rows = compare_players(first, second, metrics)
        st.dataframe([{"Metric": row["metric"].replace("_", " ").title(), first["name"]: row["first"], second["name"]: row["second"]} for row in rows], use_container_width=True, hide_index=True)
        st.bar_chart(pd.DataFrame({first["name"]: [first["runs"], first["fours"], first["sixes"]],
                                   second["name"]: [second["runs"], second["fours"], second["sixes"]]},
                                  index=["Runs", "Fours", "Sixes"]))
    else:
        st.info("The live scorecard needs at least two batting entries for a comparison.")
else:
    st.info("Sync live Cricbuzz data from the sidebar to compare players in the live match.")
    players = load_sample("sample_players.json")
    if len(players) >= 2:
        names = [p["name"] for p in players]
        first = next(p for p in players if p["name"] == st.selectbox("First demo player", names, index=0))
        second = next(p for p in players if p["name"] == st.selectbox("Second demo player", names, index=1))
        rows = compare_players(first, second, ["runs", "balls", "fours", "sixes"])
        st.dataframe([{"Metric": row["metric"], first["name"]: row["first"], second["name"]: row["second"]} for row in rows], use_container_width=True, hide_index=True)

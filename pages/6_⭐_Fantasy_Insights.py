"""Fantasy points estimated from the selected live scorecard."""
import streamlit as st
import pandas as pd
from components.header import render_header
from services.fantasy_analyzer import rank_players
from utils.live_match import selected_match, batting_rows, bowling_rows, display_fields
from utils.data_processor import load_sample

render_header("Fantasy Insights", "Live fantasy ranking from the current match scorecard.")
match = selected_match()
if match:
    fields = display_fields(match)
    st.success(f"LIVE SCORECARD · {fields['team1_name']} vs {fields['team2_name']}")
    batters, bowlers = batting_rows(match), bowling_rows(match)
    stats = {}
    for row in batters:
        key = (row["name"], row["team"])
        item = stats.setdefault(key, {"runs": 0, "fours": 0, "sixes": 0, "wickets": 0, "catches": 0, "run_outs": 0})
        item["runs"] += row["runs"]
        item["fours"] += row["fours"]
        item["sixes"] += row["sixes"]
    for row in bowlers:
        key = (row["name"], row["team"])
        item = stats.setdefault(key, {"runs": 0, "fours": 0, "sixes": 0, "wickets": 0, "catches": 0, "run_outs": 0})
        item["wickets"] += int(row["wickets"] or 0)
    inputs = [{"name": f"{name} · {team}", "stats": value} for (name, team), value in stats.items()]
    ranked = rank_players(inputs)
    if ranked:
        st.caption("Points use scorecard runs, fours, sixes, and bowler wickets. Fielding points are omitted when unavailable in the actor output.")
        st.dataframe([{"Rank": i + 1, "Player": p["name"], "Fantasy points": p["points"]} for i, p in enumerate(ranked)], use_container_width=True, hide_index=True)
        chart = pd.DataFrame({"Fantasy points": [p["points"] for p in ranked]}, index=[p["name"] for p in ranked])
        st.bar_chart(chart)
        st.success(f"Current leader: {ranked[0]['name']} · {ranked[0]['points']} points")
    else:
        st.info("No player scorecard is available for fantasy scoring yet.")
else:
    st.info("Sync live Cricbuzz data from the sidebar to calculate fantasy points from the current match.")
    players = load_sample("sample_players.json")
    inputs = [{"name": p["name"], "stats": {"runs": p.get("runs", 0), "fours": p.get("fours", 0), "sixes": p.get("sixes", 0)}} for p in players]
    ranked = rank_players(inputs)
    if ranked:
        st.dataframe([{"Rank": i + 1, "Player": p["name"], "Fantasy points": p["points"]} for i, p in enumerate(ranked)], use_container_width=True, hide_index=True)

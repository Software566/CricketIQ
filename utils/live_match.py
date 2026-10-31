"""Shared helpers for the live Cricbuzz match selected in Streamlit session state."""
import streamlit as st
from services.cricket_api import match_display_fields


def live_matches():
    return [item for item in st.session_state.get("live_matches", []) if isinstance(item, dict)]


def selected_match():
    matches = live_matches()
    if not matches:
        return None
    selected = st.session_state.get("selected_live_match", 0)
    try:
        selected = int(selected)
    except (TypeError, ValueError):
        selected = 0
    return matches[selected] if 0 <= selected < len(matches) else matches[0]


def display_fields(match=None):
    match = match or selected_match()
    return match_display_fields(match) if match else None


def innings(match=None):
    match = match or selected_match()
    if not match:
        return []
    rows = match.get("scorecard") or []
    return rows if isinstance(rows, list) else []


def innings_summary_rows(match=None):
    match = match or selected_match()
    if not match:
        return []
    team_names = _teams(match)
    summaries = []
    for index, inning in enumerate(innings(match), 1):
        score = inning.get("score") or {}
        batting_team = inning.get("batting_team") or inning.get("battingTeam") or {}
        short = batting_team.get("short_name") if isinstance(batting_team, dict) else None
        team = (batting_team.get("name") if isinstance(batting_team, dict) else str(batting_team or "")) or team_names.get(short) or ("Team 1" if index % 2 else "Team 2")
        summaries.append({"Innings": index, "Team": team, "Runs": score.get("runs", 0),
                          "Wickets": score.get("wickets", 0), "Overs": score.get("overs", 0),
                          "Run rate": score.get("run_rate", 0)})
    return summaries


def _teams(match):
    result = {}
    for key in ("team1", "team2"):
        team = match.get(key)
        if isinstance(team, dict):
            short = team.get("short_name") or team.get("shortName")
            if short:
                result[short] = team.get("name") or short
    return result


def batting_rows(match=None):
    match = match or selected_match()
    if not match:
        return []
    team_names = _teams(match)
    rows = []
    for number, inning in enumerate(innings(match), 1):
        batting_team = inning.get("batting_team") or inning.get("battingTeam") or {}
        if isinstance(batting_team, dict):
            team = batting_team.get("name") or team_names.get(batting_team.get("short_name"), "Unknown team")
        else:
            team = str(batting_team or "Unknown team")
        for batter in inning.get("batting", []) or []:
            player = batter.get("player") or {}
            name = player.get("name") if isinstance(player, dict) else player
            rows.append({
                "name": name or batter.get("name", "Unknown player"), "team": team, "innings": number,
                "runs": int(batter.get("runs", 0) or 0), "balls": int(batter.get("balls", 0) or 0),
                "fours": int(batter.get("fours", 0) or 0), "sixes": int(batter.get("sixes", 0) or 0),
                "strike_rate": float(batter.get("strike_rate", batter.get("strikeRate", 0)) or 0),
                "dismissal": _dismissal(batter.get("dismissal")),
                "raw_dismissal": batter.get("dismissal", {}),
            })
    return rows


def bowling_rows(match=None):
    match = match or selected_match()
    if not match:
        return []
    team_names = _teams(match)
    rows = []
    for number, inning in enumerate(innings(match), 1):
        batting_team = inning.get("batting_team") or inning.get("battingTeam") or {}
        batting_short = batting_team.get("short_name") if isinstance(batting_team, dict) else None
        bowling_team = next((name for short, name in team_names.items() if short != batting_short), "Unknown team")
        entries = inning.get("bowling", inning.get("bowlers", [])) or []
        for bowler in entries:
            player = bowler.get("player") or bowler.get("bowler") or {}
            name = player.get("name") if isinstance(player, dict) else player
            rows.append({
                "name": name or bowler.get("name", "Unknown player"), "team": bowling_team, "innings": number,
                "overs": bowler.get("overs", bowler.get("overs_bowled", bowler.get("o", 0))),
                "maidens": bowler.get("maidens", bowler.get("m", 0)),
                "runs": bowler.get("runs", bowler.get("runs_conceded", bowler.get("r", 0))),
                "wickets": bowler.get("wickets", bowler.get("wickets_taken", bowler.get("wkts", bowler.get("w", 0)))),
                "economy": bowler.get("economy", bowler.get("econ", 0)),
            })
    return rows


def _dismissal(value):
    if isinstance(value, dict):
        return value.get("text") or value.get("type") or "not out"
    return value or "not out"


def partnership_rows(match=None):
    rows = []
    for number, inning in enumerate(innings(match), 1):
        for partnership in inning.get("partnerships", []) or []:
            if not isinstance(partnership, dict):
                continue
            rows.append({"innings": number, **partnership})
    return rows


def fall_of_wicket_rows(match=None):
    rows = []
    for number, inning in enumerate(innings(match), 1):
        for wicket in inning.get("fall_of_wickets", inning.get("fallOfWickets", [])) or []:
            if isinstance(wicket, dict):
                rows.append({"innings": number, **wicket})
    return rows

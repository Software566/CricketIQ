"""Fantasy score ranking."""
from utils.fantasy_points import calculate_points


def rank_players(players):
    ranked = [{**p, "points": calculate_points(**p.get("stats", {}))} for p in players]
    return sorted(ranked, key=lambda p: p["points"], reverse=True)

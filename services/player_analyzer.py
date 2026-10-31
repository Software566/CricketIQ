"""Player performance summaries."""
def batting_summary(runs, balls, fours=0, sixes=0):
    runs, balls, fours, sixes = map(int, (runs, balls, fours, sixes))
    return {"runs": runs, "balls": balls, "strike_rate": round(runs * 100 / balls, 2) if balls else 0.0,
            "fours": fours, "sixes": sixes, "boundaries": fours + sixes,
            "boundary_runs": fours * 4 + sixes * 6, "dot_ball_estimate": max(0, balls-runs)}

"""Match-level analysis helpers."""
from utils.calculations import run_rate


def innings_summary(runs, wickets, overs):
    return {"runs": int(runs), "wickets": int(wickets), "score": f"{runs}/{wickets}",
            "overs": str(overs), "run_rate": run_rate(runs, overs)}

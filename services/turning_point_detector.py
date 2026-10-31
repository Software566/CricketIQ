"""Flag high-impact overs as candidate turning points."""

def detect_turning_points(overs, threshold=12):
    values = [int(runs) for runs in overs]
    average = sum(values) / len(values) if values else 0
    return [{"over": i + 1, "runs": runs, "above_average": round(runs-average, 2),
             "impact": "High scoring" if runs >= threshold else ""}
            for i, runs in enumerate(values) if runs >= threshold]

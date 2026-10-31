"""Basic cricket scoring calculations using cricket's six-ball over notation."""

def run_rate(runs: int, overs: float) -> float:
    balls = overs_to_balls(overs)
    return round(runs * 6 / balls, 2) if balls else 0.0


def overs_to_balls(overs: float) -> int:
    """Convert notation such as 18.2 (18 overs, 2 balls) into legal balls."""
    value = str(overs).strip()
    if "." in value:
        whole_text, ball_text = value.split(".", 1)
        whole, balls = int(whole_text or 0), int(ball_text[:1] or 0)
    else:
        whole, balls = int(float(value)), 0
    if whole < 0 or balls < 0 or balls >= 6:
        raise ValueError("Overs must use cricket notation with 0 to 5 balls after the decimal point")
    return whole * 6 + balls


def required_run_rate(target: int, score: int, balls_remaining: int) -> float:
    return round(max(target - score, 0) * 6 / balls_remaining, 2) if balls_remaining > 0 else 0.0


def balls_remaining(overs, total_overs=20):
    return max(0, int(total_overs) * 6 - overs_to_balls(overs))

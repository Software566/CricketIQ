"""Small formatting helpers."""

def format_overs(balls):
    return f"{int(balls) // 6}.{int(balls) % 6}"

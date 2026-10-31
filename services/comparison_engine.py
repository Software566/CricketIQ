"""Compare two player statistic dictionaries."""

def compare_players(first, second, metrics):
    return [{"metric": key, "first": first.get(key, 0), "second": second.get(key, 0)} for key in metrics]

"""Simple momentum estimate from consecutive over run totals."""

def momentum_by_over(runs_by_over, window=3):
    values = [int(x) for x in runs_by_over]
    return [round(sum(values[max(0, i-window+1):i+1]) / min(i+1, window), 2) for i in range(len(values))]

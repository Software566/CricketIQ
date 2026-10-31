"""Transparent, configurable starter fantasy scoring."""

def calculate_points(runs=0, wickets=0, catches=0, run_outs=0, fours=0, sixes=0):
    return int(runs + wickets * 25 + catches * 8 + run_outs * 8 + fours + sixes * 2)

"""Grounded, local match explanations (no external AI provider required)."""
import re


def explain_match(match_data):
    live_match = match_data.get("live_match")
    if isinstance(live_match, dict):
        return _explain_live(live_match, str(match_data.get("question", "")).strip(),
                             match_data.get("previous_player"))
    teams = match_data.get("teams", ["Batting side", "Opposition"])
    runs, wickets = _score(match_data.get("score", "0/0"))
    overs = match_data.get("overs", "0.0")
    target = int(match_data.get("target", 0) or 0)
    balls = _balls(overs)
    remaining = max(0, target - runs)
    question = str(match_data.get("question", "")).strip()
    rate = round(runs * 6 / balls, 2) if balls else 0
    required = round(remaining * 6 / max(120 - balls, 1), 2)
    text = (f"{teams[0]} are {runs}/{wickets} after {overs} overs (run rate {rate:.2f}). "
            f"The target is {target}; they need {remaining} from {max(120-balls, 0)} balls "
            f"(required rate {required:.2f}).")
    if question:
        text += " " + _context(question, teams[0], runs, wickets, target, remaining, balls, required)
    return text


def _explain_live(match, question, previous_player=None):
    from services.cricket_api import match_display_fields
    from utils.live_match import batting_rows, bowling_rows, innings_summary_rows

    fields = match_display_fields(match)
    batters, bowlers = _aggregate_batters(batting_rows(match)), _aggregate_bowlers(bowling_rows(match))
    q = _normalize(question)
    bowling_intent = any(term in q for term in ("bowling", "bowler", "wicket", "economy", "conceded", "overs bowled"))
    batting_intent = any(term in q for term in ("batting", "batter", "runs", "score", "balls", "strike rate", "fours", "sixes"))
    explicit_batter = _find_named_player(q, batters)
    explicit_bowler = _find_named_player(q, bowlers)
    follow_up = any(term in q for term in ("he", "him", "his", "she", "her", "they", "them", "their", "what about", "how about", "and the", "other one", "second one"))
    if previous_player and follow_up and not (explicit_batter or explicit_bowler):
        q = f"{q} {_normalize(previous_player)}"

    if previous_player and any(term in q for term in ("other", "second one", "other one")):
        pool = bowlers if bowling_intent and bowlers else batters
        alternatives = [row for row in pool if row["name"] != previous_player]
        if alternatives:
            if bowling_intent:
                other = max(alternatives, key=lambda row: _number(row.get("wickets")))
                return _bowling_answer(other, lead="Next bowler in the available scorecard")
            other = max(alternatives, key=lambda row: _number(row.get("runs")))
            return _batting_answer(other, lead="Next highest scorer in the available scorecard")

    # Resolve a named player before broad match-level keywords. This prevents
    # follow-ups about a bowler's wickets from being answered with batting stats.
    named_bowler = _find_named_player(q, bowlers)
    named_batter = _find_named_player(q, batters)
    if bowling_intent and named_bowler:
        return _bowling_answer(named_bowler)
    if bowling_intent and named_batter and not named_bowler:
        return f"{named_batter['name']} appears in the batting card, but no bowling figures for them are present in this match scorecard."
    if batting_intent and named_batter:
        return _batting_answer(named_batter)
    if batting_intent and named_bowler and not named_batter:
        return f"{named_bowler['name']} appears in the bowling card, but no batting figures for them are present in this match scorecard."
    if named_bowler and not named_batter:
        return _bowling_answer(named_bowler)
    if named_batter and not named_bowler:
        return _batting_answer(named_batter)

    asks_top_batter = bool(re.search(r"\b(top|most|highest|leading|best)\s+(individual\s+)?(run|runs|scorer|batter)\b", q))
    asks_top_bowler = bool(re.search(r"\b(top|most|highest|leading|best)\s+(wicket|wickets|bowler|bowling)\b", q)) or "wicket taker" in q or "wicket takers" in q
    if asks_top_batter and asks_top_bowler:
        parts = []
        if batters:
            top_batter = max(batters, key=lambda row: row["runs"])
            parts.append(_batting_answer(top_batter, lead="Top run scorer"))
        else:
            parts.append("No batting figures are available in this match scorecard.")
        if bowlers:
            top_bowler = max(bowlers, key=lambda row: _number(row.get("wickets")))
            parts.append(_bowling_answer(top_bowler, lead="Leading wicket taker"))
        else:
            parts.append("No bowling figures are available in this match scorecard.")
        return " ".join(parts)
    if asks_top_batter and batters:
        player = max(batters, key=lambda row: row["runs"])
        return _batting_answer(player, lead="Top scorer in the available scorecard")
    if asks_top_bowler and bowlers:
        player = max(bowlers, key=lambda row: _number(row.get("wickets")))
        return _bowling_answer(player, lead="Leading wicket taker in the available scorecard")
    if "most economical" in q and bowlers:
        key = "economy" if "econom" in q else "wickets"
        player = min(bowlers, key=lambda row: _number(row.get(key), default=999))
        return _bowling_answer(player, lead="Most economical bowler in the available scorecard")
    if asks_top_batter and not batters:
        return "No batting figures are available in this match scorecard. Sync the selected live match again to fetch its detailed card."
    if asks_top_bowler and not bowlers:
        return "No bowling figures are available in this match scorecard. Sync the selected live match again to fetch its detailed card."
    if any(term in q for term in ("venue", "where is", "where was")) and fields["venue"]:
        return f"The match is at {fields['venue']}."
    if any(term in q for term in ("series", "tournament", "competition")) and fields["series"]:
        return f"This match is part of {fields['series']}."
    if any(term in q for term in ("status", "result", "who is winning", "who won")):
        return f"Match status: {fields['status']} ({fields['state']})."
    if any(term in q for term in ("target", "required rate", "run rate", "how many runs needed")):
        target = match.get("target")
        if target is not None:
            return f"The recorded target is {target} runs."
        return "The fetched Cricbuzz record does not include a target or required run rate, so I can’t calculate that reliably from this data."
    if any(term in q for term in ("score", "current runs", "current score")):
        return (f"Current score: {fields['team1_name']} {fields['team1_score']} · "
                f"{fields['team2_name']} {fields['team2_score']}. Match status: {fields['status']}.")
    innings = innings_summary_rows(match)
    summary = "; ".join(f"{row['Team']} {row['Runs']}/{row['Wickets']} in {row['Overs']} overs"
                         for row in innings if row["Runs"] or row["Overs"])
    score_text = f"Scorecard: {summary}. " if summary else ""
    leaders = ""
    if batters:
        best = max(batters, key=lambda row: row["runs"])
        leaders = f" Top batter in the available card: {best['name']} with {best['runs']} runs."
    if question:
        return (f"I couldn’t find that detail in the selected match’s fetched scorecard. "
                f"The available data is {fields['team1_name']} {fields['team1_score']} vs "
                f"{fields['team2_name']} {fields['team2_score']}; status: {fields['status']}.")
    return (f"{fields['team1_name']} vs {fields['team2_name']}: {fields['status']}. {score_text}{leaders} "
            "Ball-by-ball events are not included in this feed.").strip()


def p_name_matches(question, name):
    return _normalize(name) in _normalize(question)


def player_reference(match, question, previous_player=None):
    """Resolve the player context to carry into a conversational follow-up."""
    from utils.live_match import batting_rows, bowling_rows

    q = _normalize(question)
    batters, bowlers = batting_rows(match), bowling_rows(match)
    player = _find_named_player(q, bowlers) or _find_named_player(q, batters)
    if player:
        return player["name"]
    if previous_player and any(term in q for term in ("other", "second one")):
        pool = bowlers if any(term in q for term in ("bowler", "bowling", "wicket")) else batters
        candidates = [row for row in pool if row["name"] != previous_player]
        if candidates:
            best = max(candidates, key=lambda row: _number(row.get("wickets" if pool is bowlers else "runs")))
            return best["name"]
    if previous_player and any(term in q for term in ("he", "him", "his", "she", "her", "they", "them", "their", "what about", "how about", "and the")):
        return previous_player
    if batters and any(term in q for term in ("top scorer", "most runs", "highest score", "best batter", "top batter")):
        return max(batters, key=lambda row: row["runs"])["name"]
    if bowlers and any(term in q for term in ("top bowler", "most wickets", "wicket taker")):
        return max(bowlers, key=lambda row: _number(row.get("wickets")))["name"]
    return None


def _normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _find_named_player(question, rows):
    normalized = _normalize(question)
    ordered = sorted(rows, key=lambda row: len(_normalize(row.get("name", ""))), reverse=True)
    for row in ordered:
        name = _normalize(row.get("name", ""))
        if name and re.search(rf"\b{re.escape(name)}\b", normalized):
            return row
    # Support a unique surname/last-name reference in follow-up questions.
    tokens = normalized.split()
    matches = [row for row in ordered if _normalize(row.get("name", "")).split()[-1:] and
               _normalize(row.get("name", "")).split()[-1] in tokens]
    return matches[0] if len(matches) == 1 else None


def _number(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _batting_answer(player, lead=None):
    balls = int(player.get("balls", 0) or 0)
    rate = _number(player.get("strike_rate"))
    if not rate and balls:
        rate = player.get("runs", 0) * 100 / balls
    prefix = f"{lead}: " if lead else ""
    return (f"{prefix}{player['name']} ({player['team']}) scored {player['runs']} runs from {balls} balls "
            f"at a strike rate of {rate:.2f}, with {player['fours']} fours and {player['sixes']} sixes. "
            f"Dismissal: {player['dismissal']}.")


def _bowling_answer(player, lead=None):
    prefix = f"{lead}: " if lead else ""
    return (f"{prefix}{player['name']} ({player['team']}) took {player['wickets']} wickets, "
            f"conceding {player['runs']} runs in {player['overs']} overs; economy {player['economy']}.")


def _aggregate_batters(rows):
    grouped = {}
    for row in rows:
        key = (row["name"], row["team"])
        result = grouped.setdefault(key, {**row, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "dismissals": []})
        for stat in ("runs", "balls", "fours", "sixes"):
            result[stat] += _number(row.get(stat))
        if row.get("dismissal") and row["dismissal"] != "not out":
            result["dismissals"].append(row["dismissal"])
    output = []
    for row in grouped.values():
        row["runs"], row["balls"] = int(row["runs"]), int(row["balls"])
        row["fours"], row["sixes"] = int(row["fours"]), int(row["sixes"])
        row["strike_rate"] = round(row["runs"] * 100 / row["balls"], 2) if row["balls"] else 0
        row["dismissal"] = "; ".join(row.pop("dismissals")) or "not out"
        output.append(row)
    return output


def _aggregate_bowlers(rows):
    grouped = {}
    for row in rows:
        key = (row["name"], row["team"])
        result = grouped.setdefault(key, {**row, "overs_balls": 0, "runs": 0, "wickets": 0, "maidens": 0})
        result["overs_balls"] += _overs_to_balls(row.get("overs", 0))
        for stat in ("runs", "wickets", "maidens"):
            result[stat] += _number(row.get(stat))
    output = []
    for row in grouped.values():
        balls = row.pop("overs_balls")
        row["overs"] = f"{balls // 6}.{balls % 6}"
        row["runs"], row["wickets"] = int(row["runs"]), int(row["wickets"])
        row["economy"] = round(row["runs"] * 6 / balls, 2) if balls else 0
        output.append(row)
    return output


def _overs_to_balls(value):
    try:
        whole, dot, fraction = str(value).partition(".")
        return max(0, int(whole)) * 6 + (int(fraction[:1] or 0) if dot else 0)
    except (TypeError, ValueError):
        return 0


def _score(value):
    try:
        runs, wickets = str(value).split("/", 1)
        return max(0, int(runs)), max(0, int(wickets))
    except (TypeError, ValueError):
        return 0, 0


def _balls(overs):
    try:
        whole, dot, fraction = str(overs).partition(".")
        return max(0, int(whole)) * 6 + (int(fraction[:1] or 0) if dot else 0)
    except (TypeError, ValueError):
        return 0


def _context(question, team, runs, wickets, target, remaining, balls, required):
    q = question.lower()
    if "required" in q or "rate" in q:
        return f"The required rate is {required:.2f} runs per over, based on the remaining target and balls."
    if "target" in q:
        return f"The target is {target} runs."
    if "wicket" in q:
        return f"{team} have lost {wickets} wicket(s)."
    if "score" in q or "run" in q:
        return f"{team} have scored {runs} runs and need {remaining} more."
    return "This explanation uses only the supplied score, overs, and target; no events beyond that data are inferred."

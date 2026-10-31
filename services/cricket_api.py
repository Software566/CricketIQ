"""Apify-backed cricket feed. Actor credentials and input stay in local config."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class CricketFeedError(RuntimeError):
    """Raised when the configured Apify actor cannot provide match data."""


def get_live_matches():
    """Run the configured Apify actor and return its dataset items as a list."""
    token = os.getenv("APIFY_API_TOKEN", "").strip()
    actor_id = os.getenv("APIFY_ACTOR_ID", "W5NmnaYQD0uTEKACH").strip()
    if not token:
        raise CricketFeedError("Add APIFY_API_TOKEN to the local .env file.")
    if not actor_id:
        raise CricketFeedError("Add APIFY_ACTOR_ID to the local .env file.")
    try:
        actor_input = json.loads(os.getenv("APIFY_ACTOR_INPUT", "{}"))
    except json.JSONDecodeError as exc:
        raise CricketFeedError("APIFY_ACTOR_INPUT must contain valid JSON.") from exc
    url = ("https://api.apify.com/v2/actors/" + quote(actor_id, safe="~")
           + "/run-sync-get-dataset-items?token=" + quote(token, safe="")
           + "&format=json&clean=true")
    request = Request(url, data=json.dumps(actor_input).encode("utf-8"),
                      headers={"Content-Type": "application/json", "Accept": "application/json"},
                      method="POST")
    try:
        with urlopen(request, timeout=180) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise CricketFeedError(f"Apify returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError) as exc:
        raise CricketFeedError(f"Could not reach Apify: {exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CricketFeedError("Apify returned data that was not valid JSON.") from exc
    if isinstance(payload, dict):
        payload = payload.get("items", payload.get("matches", [payload]))
    if not isinstance(payload, list):
        raise CricketFeedError("Expected the actor to return a list of match records.")
    return payload


def match_display_fields(match):
    """Return the score and labels exposed by the Cricbuzz Apify actor."""
    def side(name, short, score_key):
        team = match.get(name)
        team_name = ((team.get("name") if isinstance(team, dict) else team if isinstance(team, str) else None)
                     or match.get(name + "Name") or match.get(short)
                     or "Team")
        score = match.get(score_key)
        if not score and isinstance(team, dict):
            innings = team.get("innings") or []
            if innings:
                inning = innings[-1]
                if isinstance(inning, dict) and "runs" in inning:
                    score = f"{inning.get('runs', 0)}/{inning.get('wickets', 0)}"
                    if inning.get("overs") is not None:
                        score += f" ({inning['overs']} ov)"
        return team_name, score or "—"

    team1_name, team1_score = side("team1", "team1ShortName", "team1Score")
    team2_name, team2_score = side("team2", "team2ShortName", "team2Score")
    innings = match.get("scorecard") or []
    team_shorts = {}
    for side_key, team_name in (("team1", team1_name), ("team2", team2_name)):
        team = match.get(side_key)
        if isinstance(team, dict) and team.get("short_name"):
            team_shorts[team["short_name"]] = team_name
    score_lines = {team1_name: [], team2_name: []}
    for index, inning in enumerate(innings):
        if not isinstance(inning, dict):
            continue
        score_data = inning.get("score", {})
        batting_team = inning.get("batting_team", {})
        short_name = batting_team.get("short_name") if isinstance(batting_team, dict) else None
        batting_name = team_shorts.get(short_name, team1_name if index % 2 == 0 else team2_name)
        if score_data:
            line = f"{score_data.get('runs', 0)}/{score_data.get('wickets', 0)}"
            if score_data.get("overs") is not None:
                line += f" ({score_data['overs']} ov)"
            score_lines[batting_name].append(line)
    if not team1_score and score_lines[team1_name]:
        team1_score = " & ".join(score_lines[team1_name])
    if not team2_score and score_lines[team2_name]:
        team2_score = " & ".join(score_lines[team2_name])
    venue = match.get("venue")
    if isinstance(venue, dict):
        venue = ", ".join(filter(None, [venue.get("name") or venue.get("ground"), venue.get("city")]))
    series = match.get("series")
    if isinstance(series, dict):
        series = series.get("name")
    return {
        "team1_name": team1_name, "team1_score": team1_score,
        "team2_name": team2_name, "team2_score": team2_score,
        "status": match.get("status") or match.get("shortStatus") or match.get("state") or "Status unavailable",
        "state": match.get("normalizedState") or match.get("state") or "",
        "series": match.get("seriesName") or series or match.get("description") or match.get("matchDesc") or "",
        "format": match.get("format") or match.get("matchFormat") or "",
        "venue": venue or "",
        "url": match.get("liveScoreUrl") or match.get("matchUrl") or match.get("link") or "",
        "scraped_at": match.get("scrapedAt") or match.get("scraped_at") or "",
    }

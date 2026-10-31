# 🏏 CricketIQ

### Cricket analysis, grounded in the match data

CricketIQ is a Streamlit dashboard for live match scores, scorecards, player comparisons, and match analysis. Load Cricbuzz data through Apify, then use the same selected match across the feature pages.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)

---

## Features

| Area | What you can do |
| --- | --- |
| **Live match** | Load Cricbuzz match scores, status, venue, and detailed scorecards. |
| **AI match explainer** | Ask scorecard questions, including follow-ups about players and their batting or bowling figures. |
| **Match analytics** | Chart runs and wickets by innings and compare batting contributions. |
| **Player intelligence** | Review a player's runs, balls, strike rate, boundaries, dismissal, and bowling figures. |
| **Player comparison** | Compare two batters from the selected match. |
| **Fantasy insights** | Rank players using the scorecard and CricketIQ's starter fantasy scoring rules. |
| **Turning points** | Explore partnerships, fall of wickets, and innings scores where available. |
| **Ask CricketIQ** | Ask questions grounded in the selected match and scorecard. |

Live data is shared across pages for the current Streamlit session. Use **Sync live Cricbuzz data** in the sidebar, then select the match you want to analyze.

### Data and analysis notes

- The explainer uses deterministic answers based on the fetched scorecard; it does not call a generative AI service.
- The configured Cricbuzz actor returns innings and player scorecards, not ball-by-ball events. Analytics therefore chart innings and player totals rather than over-by-over momentum.
- Fantasy points use available scorecard runs, fours, sixes, and wickets. Fielding points are omitted when the actor does not return the required details.
- Bundled JSON files provide sample data when no live feed has been loaded.

---

## Run locally

### Requirements

- Python 3.10 or newer
- An Apify API token for live match data (optional for sample-data pages)

### Install and start

From the project directory, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints the local address when the server starts, usually [http://localhost:8501](http://localhost:8501). Stop it with **Ctrl+C** in the terminal.

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

### Configure the live feed

Add your Apify credentials to the project’s ignored `.env` file. Do not put API tokens in Python files or commit them to the repository.

```dotenv
APIFY_API_TOKEN=your_apify_token
APIFY_ACTOR_ID=W5NmnaYQD0uTEKACH
APIFY_ACTOR_INPUT={"mode":"live","category":"all","maxResults":20,"scrapeDetails":true}
```

The actor is [Cricbuzz Scraper by Omkar Cloud](https://apify.com/omkar-cloud/cricbuzz-scraper). Each sidebar sync starts an Apify actor run; the app does not poll automatically. Detailed scorecards are billed per result, so review the actor's current pricing before syncing. After changing `.env`, restart Streamlit so it reloads the settings.

---

## Project structure

```text
CricketIQ/
├── app.py                 # Home dashboard
├── pages/                 # Streamlit feature pages
├── components/            # Shared headers, navigation, and UI elements
├── services/              # Apify feed and cricket analysis logic
├── utils/                 # Data, calculations, and live-match helpers
├── config/                # Application settings and constants
├── data/                  # Bundled sample datasets
├── assets/                # Styles and visual assets
└── tests/                 # Unit-test modules
```

## Development

Install dependencies with `python -m pip install -r requirements.txt`. Feature pages are discovered from `pages/`; shared calculations and data handling belong in `utils/` or `services/`.

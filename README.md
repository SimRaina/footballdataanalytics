# ⚽ Football Analytics Dashboard

A multi-page Streamlit dashboard for football analytics with support for Indian Super League. The app currently includes a full sample dataset for the Indian Super League (ISL).

## ✨ What’s included

- Multi-page experience for overview, teams, players, seasons, analytics, standings, fixtures, scouting, and extra charts
- Team and player stats, recent form, head-to-head history, and league trend analysis

## 🧭 Current app structure

- Entry point: app.py
- Pages are organized in the pages/ folder
- Shared UI helpers live in utils/
- League config lives in config/league_config.json
- League-specific data is stored under data/isl

## 📂 Data layout

Each league folder should contain these files:

- teams.csv
- players.csv
- matches.csv
- seasons.csv
- teams_socials.csv

The app also supports optional league-specific files such as isl_table.json for chart pages.

## 🏆 Supported leagues

- ISL

## 🚀 Getting started

### Prerequisites
- Python 3.10+
- Streamlit
- Pandas
- Plotly

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

The dashboard will open at http://localhost:8501.

## 🧪 Testing

### Run smoke tests locally

The project includes comprehensive smoke tests that validate:
- Data loading and integrity
- Core calculations (standings, efficiency stats)
- All page syntax and imports
- Utility modules

```bash
python tests/smoke_test.py
```

### Automated testing with GitHub Actions

Smoke tests automatically run on every push to `main`, `master`, or `develop` branches and on all pull requests. Tests are executed across Python 3.11.

View test status:
- Check the badge at the top of this README
- View detailed results in the [Actions](../../actions/workflows/smoke-tests.yml) tab on GitHub

## 📁 Project structure

```text
FootballAnalyticsDashboard/
├── app.py
├── config/
│   └── league_config.json
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Teams.py
│   ├── 3_Players.py
│   ├── 4_Seasons.py
│   ├── 5_Analytics.py
│   ├── 6_Standings.py
│   ├── 8_Fixtures.py
│   ├── 10_Player_Scouting.py
│   └── 11_MPLSoccer_Charts.py
├── utils/
│   ├── loader.py
│   ├── standings.py
│   ├── stats.py
│   ├── components.py
│   ├── sidebar.py
│   └── styles.py
├── tests/
│   ├── smoke_test.py
│   └── __pycache__/
├── data/
│   └── isl/
├── .github/
│   └── workflows/
│       └── smoke-tests.yml
└── assets/
    └── logos/
```

## 🎯 Future ideas

- Connect to live football APIs
- Expand scouting metrics and advanced analytics
- Add player photos and improved visuals

---

Last updated: July 2026


# AGENTS.md - ISL Dashboard Development Guide

## Project Overview
**ISL Dashboard** is a Streamlit-based web application for the Indian Super League (ISL) 2025-26 season. It provides comprehensive league analytics, team information, player statistics, and match tracking.

**Architecture**: Single-page Streamlit app (`app.py`) + multi-page structure in `pages/` + shared utilities in `utils/`

## Critical Data Flows

### 1. Data Loading Pipeline
- **Entry Point**: `utils/loader.py` - `load_data()` function
- **Data Source**: Four CSV files in `data/` directory:
  - `teams.csv` - 14 ISL teams with: team_id, team_name, city, logo_path, coach, stadium
  - `players.csv` - Active player roster with: player_id, name, team, position, goals, assists, minutes, nationality, age
  - `matches.csv` - Match records with: match_status (completed/upcoming), home_team, away_team, home_goals, away_goals, season, date
  - `seasons.csv` - Season metadata: season, winner, top_scorer, top_goals

**Key Detail**: Data is cached with `@st.cache_data` to optimize performance across page loads.

### 2. Standings Calculation
- **Source**: `utils/standings.py` - `calculate_standings()` function
- **Logic**: Processes only "completed" matches (filters by match_status), calculates W-D-L, points, goals for/against
- **Sorting**: Points (desc) → Goal Difference (desc) → Goals For (desc)
- **Used By**: Multiple pages (Teams, Standings, Analytics) - avoid duplicating logic

### 3. Season Filtering
- **Current Season**: Always "2025-26" (set in `utils/loader.py` - `get_current_season()`)
- **Pattern**: All pages filter matches by season before analysis
- **Example**: `season_matches = matches[matches["season"] == current_season]`

## Page Structure & Key Patterns

### Standard Page Template (All pages follow this):
```python
# 1. Load data
teams, players, matches, seasons = load_data()
current_season = get_current_season()

# 2. Streamlit config & styling
st.markdown("""<style>...</style>""", unsafe_allow_html=True)
st.title("🏟️ Teams")

# 3. Content
```

### Page Inventory
| File | Purpose | Key Outputs |
|------|---------|------------|
| 0_Home.py | Landing page | Season intro, quick stats |
| 1_Overview.py | Dashboard summary | Key metrics, standings widget, recent matches |
| 2_Teams.py | Team details | Logo, coach, stadium, squad stats |
| 3_Players.py | Player search | Filters (team, position, nationality), stats |
| 4_Seasons.py | Season analytics | Winner, top scorer, comparison charts |
| 5_Analytics.py | Advanced stats | Goals/defense analysis, efficiency metrics |
| 6_Standings.py | League table | Full standings with home/away splits |
| 7_Leaders.py | Top performers | Top scorers, assists, per-90 stats |
| 8_Fixtures.py | Match schedule | Upcoming & recent matches |
| 9_Team_Deep_Dive.py | Team analysis | Detailed performance breakdown |
| 10_Scouting_Report.py | Player scouting | Advanced player metrics |

## Common Tasks & Patterns

### Adding/Updating Player Stats
1. Update `data/players.csv` - ensure columns: player_id, name, team, position, goals, assists, minutes, nationality, age
2. Stats are season-specific (currently 2025-26)
3. Efficiency metrics: Goals/Assists per 90 minutes (calculated as `stats * 90 / minutes`)
4. Filter by `minutes >= 500` for reliability

### Adding/Updating Team Info
1. Update `data/teams.csv` - required columns: team_id, team_name, city, logo_path, coach, stadium
2. Logo path must be relative (e.g., `assets/logos/MumbaiCity.png`)
3. Used in 2_Teams.py line 35-37 for display

### Adding/Updating Match Data
1. Update `data/matches.csv` - required: home_team, away_team, home_goals, away_goals, match_status, season
2. match_status values: "completed" or "upcoming" (MUST be exact)
3. Only "completed" matches appear in standings/stats calculations
4. Season must match `get_current_season()` value for current season analytics

### Accessing Team Stats
```python
from utils.standings import calculate_standings
standings = calculate_standings(season_matches, teams, current_season)
team_stats = standings[standings["team_name"] == selected_team].iloc[0]
```

## Key Conventions

### Styling
- Dark theme: `background-color: #0e1117; color: white;`
- Metric boxes: Use `.stMetric { background-color: #1c1f26; }`
- Emojis for page titles: ⚽🏟️📅📊👥🏆🔍

### Filtering Pattern
```python
season_matches = matches[matches["season"] == current_season]
team_matches = season_matches[(season_matches["home_team"] == team) | 
                               (season_matches["away_team"] == team)]
```

### Column Access Safety
Use `.get()` for optional fields (may not exist in all CSVs):
```python
st.write(f"**Coach:** {team_info.get('coach', 'N/A')}")
st.write(f"**Stadium:** {team_info.get('stadium', 'N/A')}")
```

## External Dependencies
- **streamlit**: UI framework
- **pandas**: Data manipulation
- **plotly**: Interactive charts (px)
- Assets stored in `assets/logos/` with team logo PNGs

## Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `KeyError: 'total_goals'` | Column doesn't exist in CSV | Check CSV has column; use `.get()` for optional fields |
| Missing team logo | Path in CSV doesn't match file | Verify `logo_path` is relative and file exists |
| Standings incorrect | Upcoming matches included | Filter by `match_status == "completed"` |
| Season data empty | Season name mismatch | Ensure season value matches CSV exactly (e.g., "2025-26") |

## File Organization Best Practices
- Keep utilities in `utils/` (reuse across pages)
- One utility function per CSV operation
- Use `@st.cache_data` for expensive operations
- Avoid hardcoding season name - use `get_current_season()`


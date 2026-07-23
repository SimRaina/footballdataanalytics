import streamlit as st
import pandas as pd
from utils.loader import load_data, get_current_season, get_configured_league
from utils.standings import calculate_standings
from utils.components import display_match_result


st.set_page_config(page_title="Dashboard", layout="wide")

st.markdown("""
    <style>
    .metric-card {
        background-color: #1c1f26;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #30363d;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #58a6ff;
    }
    .metric-label {
        font-size: 14px;
        color: #8b949e;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

teams, players, matches, seasons, teams_socials = load_data()
league_config = get_configured_league()
current_season = get_current_season()

st.title(f"{league_config.get('emoji', '⚽')} {league_config.get('display_name', league_config['league_name'])} Dashboard")
st.markdown(f"**Season:** {current_season}")

# ============= METRICS SECTION =============
st.markdown("---")
st.subheader("📊 Key Statistics")

season_matches = matches[matches["season"] == current_season]
completed_matches = season_matches[season_matches["match_status"] == "completed"]
total_goals = completed_matches["home_goals"].sum() + completed_matches["away_goals"].sum()
total_matches = len(completed_matches)

# Row 1: Basic Stats
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">🏆</div>
        <div class="metric-label">Teams</div>
        <div class="metric-value">{len(teams)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">👥</div>
        <div class="metric-label">Players</div>
        <div class="metric-value">{len(players)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">⚽</div>
        <div class="metric-label">Matches Played</div>
        <div class="metric-value">{total_matches}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">🎯</div>
        <div class="metric-label">Total Goals</div>
        <div class="metric-value">{int(total_goals)}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    avg_goals = round(total_goals / total_matches, 2) if total_matches > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">📈</div>
        <div class="metric-label">Avg Goals/Match</div>
        <div class="metric-value">{avg_goals}</div>
    </div>
    """, unsafe_allow_html=True)

# Row 2: Player Stats
col1, col2, col3, col4, col5 = st.columns(5)

top_scorer = players.sort_values(by="goals", ascending=False).iloc[0]
top_assister = players.sort_values(by="assists", ascending=False).iloc[0]
avg_age = round(players["age"].astype(float).mean(), 1)
total_nationalities = players["nationality"].nunique()

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">⭐</div>
        <div class="metric-label">Top Scorer</div>
        <div style="font-size: 14px; color: #58a6ff; margin-top: 8px;">{top_scorer['name']}</div>
        <div style="font-size: 12px; color: #8b949e;">{int(top_scorer['goals'])} goals</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">🎨</div>
        <div class="metric-label">Top Assister</div>
        <div style="font-size: 14px; color: #58a6ff; margin-top: 8px;">{top_assister['name']}</div>
        <div style="font-size: 12px; color: #8b949e;">{int(top_assister['assists'])} assists</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">🎂</div>
        <div class="metric-label">Avg Player Age</div>
        <div class="metric-value">{avg_age}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">🌍</div>
        <div class="metric-label">Nationalities</div>
        <div class="metric-value">{total_nationalities}</div>
    </div>
    """, unsafe_allow_html=True)

# ============= STANDINGS SECTION =============
st.markdown("---")
st.subheader("⚡ Current League Standings")
standings = calculate_standings(completed_matches, teams, current_season)
display_standings = standings[["position", "team_name", "matches_played", "points", "goal_difference"]]
display_standings.columns = ["Pos", "Team", "P", "Pts", "GD"]
st.dataframe(display_standings, use_container_width=True, hide_index=True)

col1, col2 = st.columns(2)

with col1:
    st.caption(f"📍 Top team: **{standings.iloc[0]['team_name']}** with {int(standings.iloc[0]['points'])} points")

with col2:
    st.caption(f"🏆 Teams in competition: **{len(standings)}** teams")

# ============= RECENT MATCHES SECTION =============
st.markdown("---")
st.subheader("📋 Recent Matches")
recent_matches = completed_matches.copy()
recent_matches["date"] = pd.to_datetime(recent_matches["date"], format="%d-%m-%Y", errors='coerce')
recent_matches = recent_matches.sort_values("date", ascending=False).head(7)

if len(recent_matches) > 0:
    for _, match in recent_matches.iterrows():
        display_match_result(match)
else:
    st.info("No matches played yet.")

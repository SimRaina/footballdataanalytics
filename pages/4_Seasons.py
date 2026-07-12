import streamlit as st
import pandas as pd
from utils.loader import load_data, get_current_season

teams, players, matches, seasons, teams_socials = load_data()
current_season = get_current_season()

st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)
st.title("📅 Seasons")

# Season selector with current season as default
available_seasons = seasons["season"].unique().tolist()
default_index = available_seasons.index(current_season) if current_season in available_seasons else 0
season_selected = st.selectbox("Select Season", available_seasons, index=default_index)

season_data = seasons[seasons["season"] == season_selected].iloc[0]

col1, col2, col3 = st.columns([2, 2, 1])
col1.metric("Season Winner", season_data["winner"])
col2.metric("Top Scorer", season_data["top_scorer"] if pd.notna(season_data["top_scorer"]) else "N/A")
col3.metric("Top Goals", int(season_data["top_goals"]) if pd.notna(season_data["top_goals"]) else "N/A")

st.markdown("---")

# All seasons table
st.subheader("Historical Seasons")
seasons_sorted = seasons.sort_values("season", ascending=False).reset_index(drop=True)
seasons_display = seasons_sorted.rename(columns={
    "season": "Season",
    "winner": "Winner",
    "top_scorer": "Top Scorer",
    "top_goals": "Top Goals"
})
st.dataframe(seasons_display, use_container_width=True, hide_index=True)

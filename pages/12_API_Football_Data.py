"""
Experimental API Football Data Page
Fetches ISL data directly from api-football.com API
Free tier: 100 requests/day - Data is aggressively cached to preserve quota
"""

import streamlit as st
import pandas as pd
from utils.api_football import (
    get_isl_league_id, 
    get_isl_standings, 
    get_isl_teams,
    get_isl_fixtures,
    get_isl_top_scorers,
    get_isl_top_assists,
    get_isl_all_players,
    get_isl_league_info,
    get_api_quota_info
)
from utils.styles import apply_dark_theme

# Disable this page temporarily
ENABLE_PAGE = False
if not ENABLE_PAGE:
    st.set_page_config(page_title="API Football Data", page_icon="🌐", layout="wide")
    st.warning("This Feature is not available.")
    st.stop()

# Page config
st.set_page_config(page_title="API Football Data", page_icon="🌐", layout="wide")
apply_dark_theme()

# Title and description
st.markdown("""
    <style>
    .api-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .api-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5em;
    }
    .api-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 5px 0 0 0;
    }
    .quota-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class="api-header">
        <h1>🌐 API Football Data (Experimental)</h1>
        <p>Live ISL data from api-football.com • Free tier: 100 requests/day • Data cached for efficiency</p>
    </div>
    """, unsafe_allow_html=True)

# Season and Data View selectors - side by side
col_season, col_data = st.columns(2)

with col_season:
    season = st.selectbox(
        "Select Season",
        options=[2022, 2023, 2024],
        index=2,
        help="Free tier: 2022-2024 seasons only"
    )

with col_data:
    data_type = st.selectbox(
        "Select Data to View",
        ["📊 Standings", "👥 Teams", "⚽ Fixtures", "⚡ Top Scorers", "🎯 Top Assists", "👤 All Players", "ℹ️ League Info", "📈 API Status"],
        index=0,
        help="Choose which ISL data to display"
    )

# Quota warning
st.markdown("""
    <div class="quota-warning">
        ⚠️ <strong>Rate Limit Notice:</strong> Free API tier limited to 100 requests/day. Data is cached for 12 hours to preserve quota.
    </div>
    """, unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"### ISL {season} Season Data")

with col2:
    if st.button("🔄 Refresh Cache", help="Clear cache and fetch fresh data (uses API quota)"):
        st.cache_data.clear()
        st.success("✅ Cache cleared! Fetching fresh data...")
        st.rerun()

st.divider()

# Data display based on selection
if data_type == "📊 Standings":
    st.markdown("#### League Standings")
    
    with st.spinner("Fetching standings data..."):
        standings = get_isl_standings(season=season)
    
    if standings is not None:
        st.dataframe(
            standings,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Position": st.column_config.NumberColumn("Pos", width=50),
                "Team": st.column_config.TextColumn("Team", width=150),
                "Played": st.column_config.NumberColumn("P", width=50),
                "Won": st.column_config.NumberColumn("W", width=50),
                "Draw": st.column_config.NumberColumn("D", width=50),
                "Lost": st.column_config.NumberColumn("L", width=50),
                "Goals For": st.column_config.NumberColumn("GF", width=60),
                "Goals Against": st.column_config.NumberColumn("GA", width=60),
                "Goal Difference": st.column_config.NumberColumn("GD", width=60),
                "Points": st.column_config.NumberColumn("Pts", width=60),
            }
        )
    else:
        st.error("❌ Could not fetch standings data. ISL may not be available in this season on api-football.com")

elif data_type == "👥 Teams":
    st.markdown("#### ISL Teams")
    
    with st.spinner("Fetching teams data..."):
        teams = get_isl_teams(season=season)
    
    if teams is not None:
        st.dataframe(
            teams,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Team": st.column_config.TextColumn("Team Name", width=200),
                "Founded": st.column_config.NumberColumn("Founded", width=100),
                "Country": st.column_config.TextColumn("Country", width=150),
                "Venue": st.column_config.TextColumn("Stadium", width=250),
                "Capacity": st.column_config.NumberColumn("Capacity", width=100),
            }
        )
        
        st.metric("Total Teams", len(teams))
    else:
        st.error("❌ Could not fetch teams data. ISL may not be available on api-football.com")

elif data_type == "⚽ Fixtures":
    st.markdown(f"#### All ISL {season} Fixtures")
    
    with st.spinner("Fetching fixtures data..."):
        fixtures = get_isl_fixtures(season=season)
    
    if fixtures is not None:
        st.dataframe(
            fixtures,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": st.column_config.TextColumn("Date", width=180),
                "Home Team": st.column_config.TextColumn("Home", width=150),
                "Away Team": st.column_config.TextColumn("Away", width=150),
                "Home Score": st.column_config.TextColumn("Score", width=80),
                "Away Score": st.column_config.TextColumn("", width=80),
                "Status": st.column_config.TextColumn("Status", width=100),
            }
        )
        
        st.metric("Total Fixtures", len(fixtures))
    else:
        st.error("❌ Could not fetch fixtures data.")

elif data_type == "⚡ Top Scorers":
    st.markdown(f"#### Top Scorers in ISL {season}")
    
    with st.spinner("Fetching top scorers data..."):
        scorers = get_isl_top_scorers(season=season)
    
    if scorers is not None:
        st.dataframe(
            scorers,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Player": st.column_config.TextColumn("Player Name", width=200),
                "Team": st.column_config.TextColumn("Team", width=180),
                "Goals": st.column_config.NumberColumn("⚽ Goals", width=80),
                "Assists": st.column_config.NumberColumn("🎯 Assists", width=80),
            }
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Top Scorers", len(scorers))
        with col2:
            top_scorer = scorers.iloc[0]
            st.metric("Top Scorer", top_scorer["Player"], f"{top_scorer['Goals']} goals")
        with col3:
            top_assists = scorers.loc[scorers["Assists"].idxmax()]
            st.metric("Most Assists", top_assists["Player"], f"{top_assists['Assists']} assists")
    else:
        st.error("❌ Could not fetch top scorers data.")

elif data_type == "🎯 Top Assists":
    st.markdown(f"#### Top Assists in ISL {season}")
    
    with st.spinner("Fetching top assists data..."):
        assists = get_isl_top_assists(season=season)
    
    if assists is not None:
        st.dataframe(
            assists,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Player": st.column_config.TextColumn("Player Name", width=200),
                "Team": st.column_config.TextColumn("Team", width=180),
                "Assists": st.column_config.NumberColumn("🎯 Assists", width=80),
            }
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Players with Assists", len(assists))
        with col2:
            if len(assists) > 0:
                top_assist = assists.iloc[0]
                st.metric("Top Playmaker", top_assist["Player"], f"{top_assist['Assists']} assists")
    else:
        st.error("❌ Could not fetch top assists data.")

elif data_type == "👤 All Players":
    st.markdown(f"#### All Players in ISL {season}")
    
    with st.spinner("Fetching all players data..."):
        players = get_isl_all_players(season=season)
    
    if players is not None:
        st.dataframe(
            players,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Player": st.column_config.TextColumn("Player Name", width=180),
                "Team": st.column_config.TextColumn("Team", width=150),
                "Age": st.column_config.NumberColumn("Age", width=60),
                "Position": st.column_config.TextColumn("Position", width=100),
                "Goals": st.column_config.NumberColumn("⚽ Goals", width=80),
                "Assists": st.column_config.NumberColumn("🎯 Assists", width=80),
                "Appearances": st.column_config.NumberColumn("Apps", width=80),
            }
        )
        
        st.metric("Total Players Listed", len(players))
    else:
        st.error("❌ Could not fetch players data.")

elif data_type == "ℹ️ League Info":
    st.markdown(f"#### ISL League Information")
    
    with st.spinner("Fetching league info..."):
        league_info = get_isl_league_info()
    
    if league_info is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("League Details")
            league = league_info.get("league", {})
            st.write(f"**Name:** {league.get('name', 'N/A')}")
            st.write(f"**Type:** {league.get('type', 'N/A')}")
            st.write(f"**ID:** {league.get('id', 'N/A')}")
            
            country = league_info.get("country", {})
            st.write(f"**Country:** {country.get('name', 'N/A')}")
            st.write(f"**Country Code:** {country.get('code', 'N/A')}")
        
        with col2:
            st.subheader("Logo")
            logo_url = league.get('logo', '')
            if logo_url:
                st.image(logo_url, width=200)
        
        st.divider()
        st.subheader("Available Seasons")
        seasons = league_info.get("seasons", [])
        if seasons:
            seasons_df = pd.DataFrame(seasons)
            st.dataframe(
                seasons_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "year": st.column_config.NumberColumn("Year", width=80),
                    "start": st.column_config.TextColumn("Start Date", width=120),
                    "end": st.column_config.TextColumn("End Date", width=120),
                    "current": st.column_config.CheckboxColumn("Current", width=80),
                }
            )
        
        st.metric("Total Seasons Available", len(seasons))
    else:
        st.error("❌ Could not fetch league info.")

elif data_type == "📈 API Status":
    st.markdown("#### API Quota & Status Information")
    
    with st.spinner("Fetching API status..."):
        quota_info = get_api_quota_info()
    
    if "error" not in quota_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if "requests_remaining" in quota_info:
                st.metric(
                    "Requests Remaining",
                    quota_info.get("requests_remaining", "N/A"),
                    delta=f"Today limit: {quota_info.get('requests_limit_day', 'N/A')}"
                )
        
        with col2:
            if "requests_current" in quota_info:
                st.metric("Requests Used Today", quota_info.get("requests_current", "N/A"))
        
        with col3:
            st.metric("API Version", quota_info.get("version", "v3"))
        
        # Detailed status
        st.subheader("Full Status Response")
        st.json(quota_info)
    else:
        st.warning(f"⚠️ Could not fetch API status: {quota_info.get('error', 'Unknown error')}")

# Footer with useful info
st.divider()
st.markdown("""
    ### 📝 About API Football Integration
    
    This experimental page fetches **live ISL data directly from api-football.com**.
    
    **Available Data Sources (Free Tier):**
    - 📊 **Standings**: Full league table with W-D-L and goal statistics
    - 👥 **Teams**: All ISL teams (11 teams) with venue information
    - ⚽ **Fixtures**: All 117 matches from selected season
    - ⚡ **Top Scorers**: 19 top goal scorers with assists
    - 🎯 **Top Assists**: 18 top playmakers/assist providers
    - 👤 **All Players**: Complete squad list (20+ players) with stats
    - ℹ️ **League Info**: League metadata, logo, and season information
    
    **Performance & Quota:**
    - ✅ All data is cached for **12 hours** to preserve the 100 req/day quota
    - ✅ Free tier limited to **2022-2024 seasons** (selector at top)
    - ✅ Free tier does NOT support pagination (last/next parameters)
    - Cache clears automatically after 12 hours or manually via "Refresh Cache" button
    - ⚠️ Each manual refresh uses API requests (respect the quota!)
    
    **Not Available (Paid Plan Only):**
    - ✗ Top Cards (yellow/red card tracking)
    - ✗ Coaches/Managers data
    - ✗ Player Injury reports
    - ✗ Match Predictions
    - ✗ Advanced League Statistics
    
    **Development:**
    - API interactions: `utils/api_football.py`
    - Secrets stored in: `.streamlit/secrets.toml` (auto-gitignored)
    - Page file: `pages/12_API_Football_Data.py`
    - API Reference: https://www.api-sports.io/documentation/football
""")

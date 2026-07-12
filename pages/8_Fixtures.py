import streamlit as st
import pandas as pd
from utils.loader import load_data, get_current_season, get_completed_matches, get_upcoming_matches
from utils.styles import apply_dark_theme
from utils.components import display_matches_table

st.set_page_config(page_title="Fixtures", layout="wide")

apply_dark_theme()

st.title("🗓️ Fixtures & Results")

teams, players, matches, seasons, teams_socials = load_data()
current_season = get_current_season()

# Filter matches by season
completed = get_completed_matches(matches, current_season).sort_values("date", ascending=False)
upcoming = get_upcoming_matches(matches, current_season).sort_values("date", ascending=True)

# Create tabs
tab1, tab2 = st.tabs(["Results", "Upcoming Fixtures"])

with tab1:
    st.subheader("📋 Match Results")
    
    if len(completed) > 0:
        # Group by gameweek
        gameweeks = sorted(completed["gameweek"].unique(), reverse=True)
        
        selected_gameweek = st.selectbox(
            "Select Gameweek",
            gameweeks,
            key="gw_results"
        )
        
        gw_matches = completed[completed["gameweek"] == selected_gameweek].sort_values("date", ascending=False)
        
        st.write(f"**Gameweek {selected_gameweek}**")
        
        for _, match in gw_matches.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
            
            with col1:
                st.write(f"**{match['home_team']}**")
            with col2:
                st.write(f"{int(match['home_goals'])}")
            with col3:
                st.write("-")
            with col4:
                st.write(f"{int(match['away_goals'])}")
            with col5:
                st.write(f"**{match['away_team']}**")
            
            st.caption(f"{match['date']} at {match['venue']}")
            st.divider()
        
        # Show all results table
        st.subheader("All Results")
        display_matches_table(completed, sort_by="date", ascending=False)
    else:
        st.info("No completed matches yet.")

with tab2:
    st.subheader("📅 Upcoming Matches")
    
    if len(upcoming) > 0:
        # Group by gameweek
        gameweeks = sorted(upcoming["gameweek"].unique())
        
        selected_gameweek = st.selectbox(
            "Select Gameweek",
            gameweeks,
            key="gw_upcoming"
        )
        
        gw_matches = upcoming[upcoming["gameweek"] == selected_gameweek].sort_values("date", ascending=True)
        
        st.write(f"**Gameweek {selected_gameweek}**")
        
        for _, match in gw_matches.iterrows():
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.write(f"**{match['home_team']}** vs")
            with col3:
                st.write(f"**{match['away_team']}**")
            
            st.caption(f"{match['date']} at {match['venue']}")
            st.divider()
        
        # Show all upcoming matches table
        st.subheader("All Upcoming Matches")
        display_matches_table(upcoming, sort_by="date", ascending=True)
    else:
        st.info("No upcoming matches scheduled.")


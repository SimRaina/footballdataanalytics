import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pathlib import Path
from utils.loader import load_data, get_current_season, get_configured_league
from utils.components import _resolve_logo_path
from utils.standings import calculate_standings, get_team_stats
from utils.stats import get_recent_form, get_head_to_head

# Helper function to safely convert values to int
def safe_int(value, default=0):
    """Safely convert value to int, handling malformed data like '28-232'"""
    if pd.isna(value) or value == '' or value == 'N/A':
        return default
    try:
        # If it's already a number, convert directly
        return int(float(value))
    except (ValueError, TypeError):
        # If it has special characters, try to extract first numeric part
        try:
            numeric_part = ''.join(c for c in str(value) if c.isdigit() or c == '.')
            if numeric_part:
                return int(float(numeric_part))
        except (ValueError, TypeError):
            pass
        return default

st.set_page_config(page_title="Teams", layout="wide")

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

st.title("🏟️ Teams")

teams, players, matches, seasons, teams_socials = load_data()
current_season = get_current_season()
league_config = get_configured_league()
league_data_dir = Path(league_config.get("data_dir", "data/isl"))

# Add cache clearing button in sidebar for debugging
with st.sidebar:
    if st.button("🔄 Clear Cache"):
        st.cache_data.clear()
        st.rerun()

# Team selector
team_selected = st.selectbox("Select Team", teams["team_name"])

team_info = teams[teams["team_name"] == team_selected].iloc[0]
team_players = players[players["team"] == team_selected]
season_matches = matches[matches["season"] == current_season]
team_matches = season_matches[
    (season_matches["home_team"] == team_selected) |
    (season_matches["away_team"] == team_selected)
]

# Display team header with logo
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    logo_path = team_info.get("logo_path", "")
    if logo_path:
        resolved_logo = _resolve_logo_path(logo_path, league_data_dir=league_data_dir)
        if resolved_logo is not None:
            st.image(str(resolved_logo), width=150)
        else:
            st.write("🏟️ Logo")
            st.caption("(Logo not found)")
    else:
        st.write("🏟️ Logo")
        st.caption("(Logo not found)")

with col2:
    st.subheader(team_info["team_name"])
    st.write(f"**City:** {team_info['city']}")
    st.write(f"**Coach:** {team_info.get('coach', 'N/A')}")
    st.write(f"**Stadium:** {team_info.get('stadium', 'N/A')}")

st.markdown("---")

# Social Media Links
team_social = teams_socials[teams_socials["team_name"] == team_selected]
if len(team_social) > 0:
    team_social = team_social.iloc[0]
    st.subheader("📱 Team Socials")
    
    social_cols = st.columns(5)
    
    if pd.notna(team_social.get('website')) and team_social.get('website') != '':
        with social_cols[0]:
            st.link_button("🌐 Website", team_social['website'])
    
    if pd.notna(team_social.get('instagram')) and team_social.get('instagram') != '':
        with social_cols[1]:
            st.link_button("📷 Instagram", team_social['instagram'])
    
    if pd.notna(team_social.get('twitter_X')) and team_social.get('twitter_X') != '':
        with social_cols[2]:
            st.link_button("𝕏 Twitter/X", team_social['twitter_X'])
    
    if pd.notna(team_social.get('facebook')) and team_social.get('facebook') != '':
        with social_cols[3]:
            st.link_button("f Facebook", team_social['facebook'])
    
    if pd.notna(team_social.get('youtube')) and team_social.get('youtube') != '':
        with social_cols[4]:
            st.link_button("▶️ YouTube", team_social['youtube'])
    
    st.markdown("---")

# Team standings stats
standings = calculate_standings(season_matches, teams, current_season)
team_standing = standings[standings["team_name"] == team_selected]

if len(team_standing) > 0:
    team_standing = team_standing.iloc[0]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Position", f"#{int(team_standing['position'])}")
    col2.metric("Points", int(team_standing["points"]))
    col3.metric("Matches", int(team_standing["matches_played"]))
    col4.metric("Wins", int(team_standing["wins"]))
    col5.metric("GD", int(team_standing["goal_difference"]))

st.markdown("---")

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Squad", "Match Record", "Recent Form", "Statistics", "Comparisons", "H2H History"
])

with tab1:
    st.subheader("Squad Information")
    if len(team_players) > 0:
        display_squad = team_players[["name", "position", "nationality", "age", "goals", "assists", "minutes"]].copy()
        display_squad.columns = ["Player", "Position", "Nationality", "Age", "Goals", "Assists", "Minutes"]
        
        # Handle missing values for nationality without tripping over pandas categoricals
        display_squad["Nationality"] = (
            display_squad["Nationality"].astype("string").fillna("N/A").astype(str)
        )
        
        # Convert Age using safe_int and handle display
        display_squad["Age"] = display_squad["Age"].apply(lambda x: safe_int(x) if safe_int(x) > 0 else None)
        display_squad["Age"] = display_squad["Age"].apply(lambda x: str(x) if x is not None else "N/A")
        
        # Convert numeric columns to int
        display_squad["Goals"] = display_squad["Goals"].apply(lambda x: int(safe_int(x)))
        display_squad["Assists"] = display_squad["Assists"].apply(lambda x: int(safe_int(x)))
        display_squad["Minutes"] = display_squad["Minutes"].apply(lambda x: int(safe_int(x)))
        
        st.dataframe(display_squad, use_container_width=True, hide_index=True)
    else:
        st.info("No players in this team")

with tab2:
    st.subheader("Home & Away Record")
    team_stats = get_team_stats(season_matches, teams, team_selected, current_season)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Home Record**")
        st.metric("Wins", team_stats["home_wins"])
        st.metric("Draws", team_stats["home_draws"])
        st.metric("Losses", team_stats["home_losses"])
    
    with col2:
        st.write("**Away Record**")
        st.metric("Wins", team_stats["away_wins"])
        st.metric("Draws", team_stats["away_draws"])
        st.metric("Losses", team_stats["away_losses"])

with tab3:
    st.subheader("Recent Match Form")
    
    recent_form = get_recent_form(season_matches, team_selected, limit=10)
    
    if len(recent_form) > 0:
        display_form = recent_form[[
            "date", "opponent", "location", "for", "against", "result"
        ]].copy()
        display_form.columns = ["Date", "Opponent", "Venue", "Goals For", "Goals Against", "Result"]
        
        st.dataframe(display_form, use_container_width=True, hide_index=True)
        
        # Form visualization
        recent_form_copy = recent_form.sort_values("date")
        recent_form_copy["result_numeric"] = recent_form_copy["result"].map({"W": 3, "D": 1, "L": 0})
        
        fig = px.bar(
            recent_form_copy,
            x="date",
            y="result_numeric",
            title="Points Earned in Recent Matches",
            labels={"result_numeric": "Points", "date": "Date"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No recent matches found.")

with tab4:
    st.subheader("Team Statistics")
    
    team_stats = get_team_stats(season_matches, teams, team_selected, current_season)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Home Performance**")
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        col_h1.metric("Home W", team_stats["home_wins"])
        col_h2.metric("Home D", team_stats["home_draws"])
        col_h3.metric("Home L", team_stats["home_losses"])
        col_h4.metric("Home P", team_stats["home_wins"] + team_stats["home_draws"] + team_stats["home_losses"])
    
    with col2:
        st.write("**Away Performance**")
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        col_a1.metric("Away W", team_stats["away_wins"])
        col_a2.metric("Away D", team_stats["away_draws"])
        col_a3.metric("Away L", team_stats["away_losses"])
        col_a4.metric("Away P", team_stats["away_wins"] + team_stats["away_draws"] + team_stats["away_losses"])
    
    # Team goals breakdown
    st.subheader("Goals Analysis")
    team_season_matches = season_matches[
        (season_matches["match_status"] == "completed") &
        ((season_matches["home_team"] == team_selected) | (season_matches["away_team"] == team_selected))
    ]
    
    goals_for = 0
    goals_against = 0
    
    for _, match in team_season_matches.iterrows():
        home_goals = 0 if pd.isna(match["home_goals"]) else int(match["home_goals"])
        away_goals = 0 if pd.isna(match["away_goals"]) else int(match["away_goals"])
        
        if match["home_team"] == team_selected:
            goals_for += home_goals
            goals_against += away_goals
        else:
            goals_for += away_goals
            goals_against += home_goals
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Goals For", goals_for)
    col2.metric("Goals Against", goals_against)
    col3.metric("Goal Difference", goals_for - goals_against)

with tab5:
    st.subheader("Team Comparisons")
    
    compare_team = st.selectbox(
        "Compare with another team",
        [t for t in teams["team_name"].unique() if t != team_selected]
    )
    
    if compare_team:
        team1_stand = standings[standings["team_name"] == team_selected].iloc[0]
        team2_stand = standings[standings["team_name"] == compare_team].iloc[0]
        
        comparison_data = pd.DataFrame({
            team_selected: [
                int(team1_stand["position"]),
                int(team1_stand["points"]),
                int(team1_stand["matches_played"]),
                int(team1_stand["wins"]),
                int(team1_stand["goals_for"]),
                int(team1_stand["goals_against"]),
            ],
            compare_team: [
                int(team2_stand["position"]),
                int(team2_stand["points"]),
                int(team2_stand["matches_played"]),
                int(team2_stand["wins"]),
                int(team2_stand["goals_for"]),
                int(team2_stand["goals_against"]),
            ]
        }, index=["Position", "Points", "Matches Played", "Wins", "Goals For", "Goals Against"])
        
        st.dataframe(comparison_data, use_container_width=True)
        
        # Comparison chart
        fig = px.bar(
            comparison_data.T,
            title=f"{team_selected} vs {compare_team}",
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.subheader("Head-to-Head History")
    
    h2h_team = st.selectbox(
        "Select opponent for H2H",
        [t for t in teams["team_name"].unique() if t != team_selected],
        key="h2h_opponent"
    )
    
    if h2h_team:
        h2h_matches, h2h_stats = get_head_to_head(season_matches, team_selected, h2h_team)
        
        if h2h_matches is not None:
            col1, col2, col3 = st.columns(3)
            col1.metric(f"{team_selected} Wins", h2h_stats[f"{team_selected}_wins"])
            col2.metric("Draws", h2h_stats["draws"])
            col3.metric(f"{h2h_team} Wins", h2h_stats[f"{h2h_team}_wins"])
            
            st.subheader("Match History")
            display_h2h = h2h_matches[[
                "date", "home_team", "home_goals", "away_team", "away_goals"
            ]].copy()
            display_h2h.columns = ["Date", "Home", "HG", "Away", "AG"]
            st.dataframe(display_h2h, use_container_width=True, hide_index=True)
        else:
            st.info(f"No H2H history between {team_selected} and {h2h_team}")


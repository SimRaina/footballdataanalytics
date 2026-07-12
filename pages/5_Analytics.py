import streamlit as st
import plotly.express as px
import pandas as pd
from utils.loader import load_data, get_current_season, get_configured_league
from utils.stats import get_top_scorers, get_top_assists, get_efficiency_stats, get_assists_per_90, get_goalkeeper_stats

st.set_page_config(page_title="Analytics & Statistics", layout="wide")

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

st.title("📊 Analytics & Statistics")

league_config = get_configured_league()
teams, players, matches, seasons, teams_socials = load_data(league_config=league_config)
current_season = get_current_season(league_config)

season_matches = matches[matches["season"] == current_season]
season_matches_completed = season_matches[season_matches["match_status"] == "completed"]

# Tab-based layout with combined tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Team Performance", 
    "Top Scorer & Assists",
    "Efficiency Metrics",
    "Player Comparison",
    "Team Composition",
    "Goalkeeper Stats"
])

with tab1:
    st.subheader("Team Performance Metrics")
    
    # Goals Analysis Charts
    st.markdown("#### 📊 Goals Analysis")
    
    col_goals1, col_goals2 = st.columns(2)
    
    with col_goals1:
        # Goals by team
        home_goals = season_matches_completed.groupby("home_team")["home_goals"].sum()
        away_goals = season_matches_completed.groupby("away_team")["away_goals"].sum()
        
        total_goals = home_goals.add(away_goals, fill_value=0).reset_index()
        total_goals.columns = ["team", "goals"]
        total_goals = total_goals.sort_values("goals", ascending=False).head(10)
        
        fig = px.bar(total_goals, x="team", y="goals", title="Top 10 Teams by Total Goals", color="goals")
        st.plotly_chart(fig, use_container_width=True)
    
    with col_goals2:
        # Goals conceded
        home_conceded = season_matches_completed.groupby("home_team")["away_goals"].sum()
        away_conceded = season_matches_completed.groupby("away_team")["home_goals"].sum()
        
        total_conceded = home_conceded.add(away_conceded, fill_value=0).reset_index()
        total_conceded.columns = ["team", "goals_conceded"]
        total_conceded = total_conceded.sort_values("goals_conceded", ascending=True).head(10)
        
        fig = px.bar(total_conceded, x="team", y="goals_conceded", title="Best Defenses (Goals Conceded)", color="goals_conceded")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### 🏟️ Home vs Away Performance")
    
    # Home vs Away performance
    home_performance = []
    away_performance = []
    
    for team in teams["team_name"].unique():
        home = season_matches_completed[season_matches_completed["home_team"] == team]
        away = season_matches_completed[season_matches_completed["away_team"] == team]
        
        if len(home) > 0:
            home_performance.append({
                "Team": team,
                "Venue": "Home",
                "Matches": len(home),
                "Wins": len(home[home["home_goals"] > home["away_goals"]]),
                "Draws": len(home[home["home_goals"] == home["away_goals"]]),
                "Losses": len(home[home["home_goals"] < home["away_goals"]]),
                "Goals For": home["home_goals"].sum(),
                "Goals Against": home["away_goals"].sum(),
            })
        
        if len(away) > 0:
            away_performance.append({
                "Team": team,
                "Venue": "Away",
                "Matches": len(away),
                "Wins": len(away[away["away_goals"] > away["home_goals"]]),
                "Draws": len(away[away["away_goals"] == away["home_goals"]]),
                "Losses": len(away[away["away_goals"] < away["home_goals"]]),
                "Goals For": away["away_goals"].sum(),
                "Goals Against": away["home_goals"].sum(),
            })
    
    performance_df = pd.DataFrame(home_performance + away_performance)
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_data = performance_df[performance_df["Venue"] == "Home"].sort_values("Wins", ascending=False).head(8)
        fig = px.bar(home_data, x="Team", y=["Wins", "Draws", "Losses"], title="Home Performance (Top Teams)", barmode="stack")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        away_data = performance_df[performance_df["Venue"] == "Away"].sort_values("Wins", ascending=False).head(8)
        fig = px.bar(away_data, x="Team", y=["Wins", "Draws", "Losses"], title="Away Performance (Top Teams)", barmode="stack")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Home vs Away Performance Table")
    
    # Create home vs away performance table
    home_away_stats = []
    for team in teams["team_name"]:
        home = season_matches_completed[season_matches_completed["home_team"] == team]
        away = season_matches_completed[season_matches_completed["away_team"] == team]
        
        home_wins = len(home[home["home_goals"] > home["away_goals"]])
        away_wins = len(away[away["away_goals"] > away["home_goals"]])
        
        home_away_stats.append({
            "Team": team,
            "Home P": len(home),
            "Home W": home_wins,
            "Away P": len(away),
            "Away W": away_wins,
        })
    
    home_away_df = pd.DataFrame(home_away_stats)
    st.dataframe(home_away_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader(f"🥅 Top Scorers & 🎯 Assists - {current_season} Season")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🥅 Top Scorers")
        top_scorers = get_top_scorers(players, limit=15)
        
        # Format and display
        display_scorers = top_scorers.copy()
        display_scorers.columns = ["Player", "Team", "Position", "Goals", "Minutes"]
        display_scorers["Avg Goals/Match"] = (display_scorers["Goals"] / (display_scorers["Minutes"] / 90)).round(2)
        
        st.dataframe(display_scorers, use_container_width=True, hide_index=True)
        
        # Visualization
        top_scorers_chart = players.nlargest(10, "goals")[["name", "goals", "team"]]
        fig = px.bar(top_scorers_chart, x="name", y="goals", color="team", title="Top 10 Scorers")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎯 Top Assist Providers")
        top_assists = get_top_assists(players, limit=15)
        
        # Format and display
        display_assists = top_assists.copy()
        display_assists.columns = ["Player", "Team", "Position", "Assists", "Minutes"]
        display_assists["Avg Assists/Match"] = (display_assists["Assists"] / (display_assists["Minutes"] / 90)).round(2)
        
        st.dataframe(display_assists, use_container_width=True, hide_index=True)
        
        # Visualization
        top_assists_chart = players.nlargest(10, "assists")[["name", "assists", "team"]]
        fig = px.bar(top_assists_chart, x="name", y="assists", color="team", title="Top 10 Assist Providers")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Efficiency Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Goals per 90 Minutes (Min. 500 mins)**")
        efficiency = get_efficiency_stats(players, limit=15)
        
        if len(efficiency) > 0:
            display_efficiency = efficiency.copy()
            display_efficiency.columns = ["Player", "Team", "Position", "Goals", "Minutes", "Goals/90"]
            st.dataframe(display_efficiency, use_container_width=True, hide_index=True)
            
            # Chart
            fig = px.bar(display_efficiency, x="Player", y="Goals/90", color="Team", title="Goals per 90 Minutes")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No players have reached 500 minutes of play yet.")
    
    with col2:
        st.write("**Assists per 90 Minutes (Min. 500 mins)**")
        assists_eff = get_assists_per_90(players, limit=15)
        
        if len(assists_eff) > 0:
            display_assists_eff = assists_eff.copy()
            display_assists_eff.columns = ["Player", "Team", "Position", "Assists", "Minutes", "Assists/90"]
            st.dataframe(display_assists_eff, use_container_width=True, hide_index=True)
            
            # Chart
            fig = px.bar(display_assists_eff, x="Player", y="Assists/90", color="Team", title="Assists per 90 Minutes")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No players have reached 500 minutes of play yet.")

with tab4:
    st.subheader("📊 Compare Multiple Players")
    
    selected_players = st.multiselect(
        "Select players to compare",
        players["name"].unique(),
        default=players.nlargest(3, "goals")["name"].tolist()
    )
    
    if selected_players:
        comparison_data = players[players["name"].isin(selected_players)][
            ["name", "team", "position", "goals", "assists", "minutes", "nationality"]
        ].copy()
        
        # Add calculated metrics
        comparison_data["Goals/90"] = (comparison_data["goals"] / (comparison_data["minutes"] / 90)).round(2)
        comparison_data["Assists/90"] = (comparison_data["assists"] / (comparison_data["minutes"] / 90)).round(2)
        
        st.dataframe(comparison_data, use_container_width=True, hide_index=True)
        
        # Show visualization
        if len(comparison_data) > 1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.bar_chart(comparison_data.set_index("name")[["goals", "assists"]])
            
            with col2:
                st.bar_chart(comparison_data.set_index("name")[["Goals/90", "Assists/90"]])

with tab5:
    st.subheader("Team Composition Analysis")
    
    # Calculate average age by team
    team_age_analysis = []
    team_nationality_analysis = []
    
    for team_name in teams["team_name"].unique():
        team_players = players[players["team"] == team_name]
        
        if len(team_players) > 0:
            # Average age
            avg_age = team_players["age"].dropna().mean()
            team_age_analysis.append({
                "Team": team_name,
                "Average Age": round(avg_age, 1)
            })
            
            # Nationality breakdown
            india_count = len(team_players[team_players["nationality"] == "India"])
            foreign_count = len(team_players[team_players["nationality"] != "India"])
            
            team_nationality_analysis.append({
                "Team": team_name,
                "India": india_count,
                "Foreign": foreign_count,
                "Total": len(team_players)
            })
    
    age_df = pd.DataFrame(team_age_analysis).sort_values("Average Age", ascending=False)
    nationality_df = pd.DataFrame(team_nationality_analysis)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Team Age Distribution**")
        
        # Youngest teams
        youngest = age_df.tail(5).sort_values("Average Age")
        fig_youngest = px.bar(youngest, x="Team", y="Average Age", title="5 Youngest Teams (Avg Age)", color="Average Age")
        st.plotly_chart(fig_youngest, use_container_width=True)
        
        # Oldest teams
        oldest = age_df.head(5)
        fig_oldest = px.bar(oldest, x="Team", y="Average Age", title="5 Oldest Teams (Avg Age)", color="Average Age")
        st.plotly_chart(fig_oldest, use_container_width=True)
    
    with col2:
        st.write("**Team Nationality Breakdown**")
        
        # Teams with most India players
        india_focused = nationality_df.nlargest(5, "India")[["Team", "India", "Foreign"]]
        fig_india = px.bar(india_focused, x="Team", y=["India", "Foreign"], title="Teams with Most Indian Players", barmode="stack")
        st.plotly_chart(fig_india, use_container_width=True)
        
        # Teams with most foreign players
        foreign_focused = nationality_df.nlargest(5, "Foreign")[["Team", "India", "Foreign"]]
        fig_foreign = px.bar(foreign_focused, x="Team", y=["India", "Foreign"], title="Teams with Most Foreign Players", barmode="stack")
        st.plotly_chart(fig_foreign, use_container_width=True)
    col1, col2 = st.columns(2)
    
    with col1:
        avg_team_age = age_df["Average Age"].mean()
        st.metric("League Avg Age", f"{avg_team_age:.1f} years")
    
    with col2:
        total_india_players = nationality_df["India"].sum()
        total_foreign_players = nationality_df["Foreign"].sum()
        india_percentage = (total_india_players / (total_india_players + total_foreign_players) * 100)
        st.metric("India Players %", f"{india_percentage:.1f}%")
    
    # Row 2 - Oldest Team (Full Width)
    oldest_team = age_df.iloc[0]
    st.metric("Oldest Team", f"{oldest_team['Team']} - Average Age: {oldest_team['Average Age']} years")
    
    # Row 3 - Youngest Team (Full Width)
    youngest_team = age_df.iloc[-1]
    st.metric("Youngest Team", f"{youngest_team['Team']} - Average Age: {youngest_team['Average Age']} years")

with tab6:
    st.subheader("🧤 Goalkeeper Statistics")
    
    # Get goalkeeper stats
    gk_stats = get_goalkeeper_stats(players, matches, teams)
    
    if len(gk_stats) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Best clean sheet records
            best_clean_sheets = gk_stats.nlargest(10, "Clean Sheets")[["name", "Clean Sheets", "team", "Matches"]]
            fig = px.bar(best_clean_sheets, x="name", y="Clean Sheets", color="team", title="Goalkeepers with Most Clean Sheets")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Best goal conceded records (fewest)
            best_defense = gk_stats.nsmallest(10, "Goals Conceded")[["name", "Goals Conceded", "team", "Matches"]]
            fig = px.bar(best_defense, x="name", y="Goals Conceded", color="team", title="Goalkeepers with Fewest Goals Conceded")
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Display full goalkeeper stats table
        st.write("**Complete Goalkeeper Statistics**")
        display_gk = gk_stats.sort_values("Clean Sheets", ascending=False)
        st.dataframe(display_gk, use_container_width=True, hide_index=True)
    else:
        st.info("No goalkeeper data available")


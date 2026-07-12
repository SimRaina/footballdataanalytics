from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from utils.loader import load_data, get_current_season, get_configured_league

st.set_page_config(page_title="MPLSoccer Charts", layout="wide")

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
    .tab-content {
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ MPLSoccer Charts")
st.markdown("**Advanced football analytics and visualizations using MPLSoccer**")

league_config = get_configured_league()
teams, players, matches, seasons, teams_socials = load_data(league_config=league_config)
current_season = get_current_season(league_config)

# Load ISL table data
@st.cache_data
def load_isl_table():
    with open(Path(league_config.get("data_dir", "data/isl")) / "isl_table.json", "r") as f:
        return json.load(f)

# Tab-based layout
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Bumpy",
    "Heat Map",
    "Pass Map",
    "Shot Map",
    "Radar",
    "Pizza"
])

with tab1:
    st.subheader("📈 Bumpy Chart - ISL Team Standings Progression")
    
    isl_table = load_isl_table()
    
    # Prepare data for bumpy chart
    seasons_list = ["2022-23", "2023-24", "2024-25", "2026"]
    
    # Create a dataframe for plotting
    bumpy_data = []
    for team, positions in isl_table.items():
        for season_idx, season in enumerate(seasons_list):
            position = positions[season_idx]
            if position > 0:  # Only include teams that participated in that season
                bumpy_data.append({
                    "Team": team,
                    "Season": season,
                    "Position": position
                })
    
    bumpy_df = pd.DataFrame(bumpy_data)
    
    # Define colors for each team
    team_colors = {
        "Mohun Bagan": "#1B4B3F",
        "Mumbai City FC": "#00509E",
        "East Bengal": "#DC143C",
        "FC Goa": "#FF6B35",
        "Bengaluru FC": "#003D7A",
        "Kerala Blasters FC": "#FDB913",
        "Chennayin FC": "#0066CC",
        "NorthEast United FC": "#E30613",
        "Odisha FC": "#FF6B00",
        "Jamshedpur FC": "#FF0000",
        "Punjab FC": "#DC143C",
        "Mohammedan SC": "#000000",
        "Inter Kashi": "#FF7F00",
        "SC Delhi": "#003366"
    }
    
    # Create interactive bumpy chart using plotly
    fig = go.Figure()
    
    for team in bumpy_df["Team"].unique():
        team_data = bumpy_df[bumpy_df["Team"] == team]
        team_data_sorted = team_data.sort_values("Season")
        
        fig.add_trace(go.Scatter(
            x=team_data_sorted["Season"],
            y=team_data_sorted["Position"],
            mode='lines+markers',
            name=team,
            line=dict(
                color=team_colors.get(team, "#7F8C8D"),
                width=2
            ),
            marker=dict(
                size=8,
                symbol="circle"
            ),
            hovertemplate=f"<b>{team}</b><br>Season: %{{x}}<br>Position: %{{y}}<extra></extra>"
        ))
    
    fig.update_layout(
        title="ISL Team Standings Progression Across Seasons",
        xaxis_title="Season",
        yaxis_title="League Position",
        hovermode="x unified",
        height=600,
        template="plotly_dark",
        yaxis=dict(
            autorange="reversed",  # Reverse so position 1 is at top
            tickmode="linear",
            tick0=1,
            dtick=1
        ),
        xaxis=dict(showgrid=True),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,  # Move legend outside chart to the right
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="white",
            borderwidth=1,
            font=dict(size=10)
        ),
        margin=dict(r=300)  # Add right margin to accommodate legend
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display insights
    st.markdown("---")
    st.subheader("📊 Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Best improvement
        improvements = []
        for team in bumpy_df["Team"].unique():
            team_data = bumpy_df[bumpy_df["Team"] == team].sort_values("Season")
            if len(team_data) >= 2:
                first_pos = team_data.iloc[0]["Position"]
                last_pos = team_data.iloc[-1]["Position"]
                if first_pos > 0 and last_pos > 0:
                    improvement = first_pos - last_pos
                    improvements.append((team, improvement))
        
        if improvements:
            best_team, best_improvement = max(improvements, key=lambda x: x[1])
            st.metric("🔺 Most Improved", best_team, f"↑{best_improvement} positions")
    
    with col2:
        # Most declined
        if improvements:
            worst_team, worst_improvement = min(improvements, key=lambda x: x[1])
            st.metric("🔻 Most Declined", worst_team, f"↓{-worst_improvement} positions")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Consistent performers
        consistency = []
        for team in bumpy_df["Team"].unique():
            team_data = bumpy_df[bumpy_df["Team"] == team].sort_values("Season")
            if len(team_data) >= 2:
                positions = team_data["Position"].values
                variance = positions.var() if len(positions[positions > 0]) > 0 else 999
                consistency.append((team, variance))
        
        if consistency:
            most_consistent = min(consistency, key=lambda x: x[1])
            st.metric("⭐ Most Consistent", most_consistent[0], f"Low variance")

with tab2:
    st.subheader("🔥 Heat Map")
    st.info("📝 Coming soon: Heat maps for player activity and shot maps")
    st.markdown("""
    **What it shows:**
    - Player movement density on the pitch
    - Touch map for specific players or teams
    - Positional heat analysis
    """)
    st.write("*Note: Add heat map implementation here*")

with tab3:
    st.subheader("🔗 Pass Map")
    st.info("📝 Coming soon: Pass network and passing sequence maps")
    st.markdown("""
    **What it shows:**
    - Pass network between players
    - Player connections and frequency
    - Ball progression patterns
    """)
    st.write("*Note: Add pass map implementation here*")

with tab4:
    st.subheader("🎯 Shot Map")
    st.info("📝 Coming soon: Shot maps with expected goals (xG)")
    st.markdown("""
    **What it shows:**
    - Shot location and outcome
    - Expected goals (xG) visualization
    - Team and player shooting efficiency
    """)
    st.write("*Note: Add shot map implementation here*")

with tab5:
    st.subheader("📊 Radar Chart")
    st.info("📝 Coming soon: Player and team radar comparisons")
    st.markdown("""
    **What it shows:**
    - Player attribute comparison (skills, stats)
    - Team performance metrics radar
    - Multi-player or team comparison
    """)
    st.write("*Note: Add radar chart implementation here*")

with tab6:
    st.subheader("🍕 Pizza Chart")
    st.info("📝 Coming soon: Pizza charts for tactical analysis")
    st.markdown("""
    **What it shows:**
    - Player role and strengths visualization
    - Positional profile comparison
    - Attribute distribution (like a pizza slice)
    """)
    st.write("*Note: Add pizza chart implementation here*")

st.markdown("---")
st.markdown("""
### About MPLSoccer
[MPLSoccer](https://mplsoccer.readthedocs.io/) is a Python library for advanced football analytics and visualization.
These charts will provide deeper insights into team tactics, player performance, and match events.
""")


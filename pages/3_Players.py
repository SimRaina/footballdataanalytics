import streamlit as st
import plotly.express as px
from utils.loader import load_data

teams, players, matches, seasons, teams_socials = load_data()
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
st.title("👤 Players")

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    team_filter = st.selectbox("Filter by Team", ["All"] + list(players["team"].unique()))

with col2:
    position_filter = st.selectbox("Filter by Position", ["All"] + list(players["position"].unique()))

with col3:
    nationality_filter = st.selectbox("Filter by Nationality", ["All"] + list(players["nationality"].unique()))

with col4:
    # Get unique ages and sort them
    unique_ages = sorted([int(age) for age in players["age"].dropna().unique() if str(age).replace('.', '').isdigit()])
    age_filter = st.selectbox("Filter by Age", ["All"] + unique_ages)

# Apply filters
filtered_players = players.copy()

if team_filter != "All":
    filtered_players = filtered_players[filtered_players["team"] == team_filter]

if position_filter != "All":
    filtered_players = filtered_players[filtered_players["position"] == position_filter]

if nationality_filter != "All":
    filtered_players = filtered_players[filtered_players["nationality"] == nationality_filter]

if age_filter != "All":
    filtered_players = filtered_players[filtered_players["age"] == age_filter]

# Display player stats
st.subheader("Player Statistics")
display_players = filtered_players[[
    "name", "team", "position", "nationality", "goals", "assists", "minutes"
]].copy()
display_players.columns = ["Player", "Team", "Position", "Nationality", "Goals", "Assists", "Minutes"]

st.dataframe(display_players, use_container_width=True, hide_index=True)



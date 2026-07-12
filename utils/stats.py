import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def get_top_scorers(players_df, limit=10):
    """Get top scorers ranked by goals."""
    return players_df.nlargest(limit, "goals")[["name", "team", "position", "goals", "minutes"]]


@st.cache_data
def get_top_assists(players_df, limit=10):
    """Get top assists providers ranked by assists."""
    return players_df.nlargest(limit, "assists")[["name", "team", "position", "assists", "minutes"]]


@st.cache_data
def get_efficiency_stats(players_df, limit=10):
    """Calculate goals per 90 minutes for players with sufficient minutes."""
    players = players_df.copy()
    
    # Filter players with at least 500 minutes
    players = players[players["minutes"] >= 500].copy()

    # Ensure minutes > 0 and compute per-90 safely
    players["minutes"] = pd.to_numeric(players["minutes"], errors="coerce").fillna(0)
    players["goals"] = pd.to_numeric(players["goals"], errors="coerce").fillna(0)
    players["goals_per_90"] = np.where(
        players["minutes"] > 0,
        (players["goals"] / (players["minutes"] / 90)).round(2),
        0,
    )

    return players.nlargest(limit, "goals_per_90")[
        ["name", "team", "position", "goals", "minutes", "goals_per_90"]
    ]


@st.cache_data
def get_assists_per_90(players_df, limit=10):
    """Calculate assists per 90 minutes for players with sufficient minutes."""
    players = players_df.copy()
    
    # Filter players with at least 500 minutes
    players = players[players["minutes"] >= 500].copy()

    players["minutes"] = pd.to_numeric(players["minutes"], errors="coerce").fillna(0)
    players["assists"] = pd.to_numeric(players["assists"], errors="coerce").fillna(0)
    players["assists_per_90"] = np.where(
        players["minutes"] > 0,
        (players["assists"] / (players["minutes"] / 90)).round(2),
        0,
    )

    return players.nlargest(limit, "assists_per_90")[
        ["name", "team", "position", "assists", "minutes", "assists_per_90"]
    ]


@st.cache_data
def get_recent_form(matches_df, team_name, limit=5):
    """Get recent match results for a team."""
    matches = matches_df[matches_df["match_status"] == "completed"].copy()
    
    home_matches = matches[matches["home_team"] == team_name].copy()
    away_matches = matches[matches["away_team"] == team_name].copy()
    
    # Prepare home matches
    home_matches["opponent"] = home_matches["away_team"]
    home_matches["for"] = home_matches["home_goals"]
    home_matches["against"] = home_matches["away_goals"]
    home_matches["location"] = "Home"
    
    # Prepare away matches
    away_matches["opponent"] = away_matches["home_team"]
    away_matches["for"] = away_matches["away_goals"]
    away_matches["against"] = away_matches["home_goals"]
    away_matches["location"] = "Away"
    
    # Combine and sort by date
    recent = pd.concat([home_matches, away_matches], ignore_index=True)
    recent = recent.sort_values("date", ascending=False).head(limit)
    
    # Determine result
    recent["result"] = recent.apply(
        lambda row: "W" if row["for"] > row["against"] else ("D" if row["for"] == row["against"] else "L"),
        axis=1
    )
    
    return recent[["date", "opponent", "location", "for", "against", "result"]]


@st.cache_data
def get_head_to_head(matches_df, team1, team2):
    """Get head-to-head stats between two teams."""
    matches = matches_df[matches_df["match_status"] == "completed"].copy()
    
    h2h = matches[
        ((matches["home_team"] == team1) & (matches["away_team"] == team2)) |
        ((matches["home_team"] == team2) & (matches["away_team"] == team1))
    ].copy()
    
    if len(h2h) == 0:
        return None, "No matches played between these teams yet."
    
    team1_wins = 0
    team2_wins = 0
    draws = 0
    team1_goals = 0
    team2_goals = 0
    
    for _, match in h2h.iterrows():
        if match["home_team"] == team1:
            team1_goals += match["home_goals"]
            team2_goals += match["away_goals"]
            if match["home_goals"] > match["away_goals"]:
                team1_wins += 1
            elif match["home_goals"] < match["away_goals"]:
                team2_wins += 1
            else:
                draws += 1
        else:
            team1_goals += match["away_goals"]
            team2_goals += match["home_goals"]
            if match["away_goals"] > match["home_goals"]:
                team1_wins += 1
            elif match["away_goals"] < match["home_goals"]:
                team2_wins += 1
            else:
                draws += 1
    
    stats = {
        "matches_played": len(h2h),
        f"{team1}_wins": team1_wins,
        f"{team2}_wins": team2_wins,
        "draws": draws,
        f"{team1}_goals": team1_goals,
        f"{team2}_goals": team2_goals,
    }
    
    return h2h.sort_values("date", ascending=False), stats


@st.cache_data
def get_goalkeeper_stats(players_df, matches_df, teams_df):
    """Calculate goalkeeper stats including goals conceded and clean sheets."""
    goalkeepers = players_df[players_df["position"] == "Goalkeeper"].copy()

    # Get completed matches
    completed_matches = matches_df[matches_df["match_status"] == "completed"].copy()

    if completed_matches.empty or goalkeepers.empty:
        return pd.DataFrame()

    # For home matches, team = home_team, conceded = away_goals, clean_sheet when away_goals==0
    home = completed_matches[["home_team", "away_goals"]].copy()
    home.columns = ["team", "goals_conceded"]
    home["clean_sheet"] = home["goals_conceded"] == 0

    # For away matches, team = away_team, conceded = home_goals
    away = completed_matches[["away_team", "home_goals"]].copy()
    away.columns = ["team", "goals_conceded"]
    away["clean_sheet"] = away["goals_conceded"] == 0

    all_team_matches = pd.concat([home, away], ignore_index=True)

    team_agg = all_team_matches.groupby("team").agg(
        Matches=("goals_conceded", "count"),
        Goals_Conceded=("goals_conceded", "sum"),
        Clean_Sheets=("clean_sheet", "sum"),
    )

    # Merge with goalkeepers by team; one goalkeeper per row will get team aggregates
    merged = goalkeepers.merge(team_agg.reset_index(), left_on="team", right_on="team", how="left")
    merged = merged.fillna({"Matches": 0, "Goals_Conceded": 0, "Clean_Sheets": 0})

    # Compute averages
    merged["Matches"] = merged["Matches"].astype(int)
    merged["Goals_Conceded"] = merged["Goals_Conceded"].astype(int)
    merged["Clean_Sheets"] = merged["Clean_Sheets"].astype(int)
    merged["Avg Goals/Match"] = merged.apply(
        lambda r: round(r["Goals_Conceded"] / r["Matches"], 2) if r["Matches"] > 0 else 0.0,
        axis=1,
    )

    gk_stats = merged[["name", "team", "Matches", "Goals_Conceded", "Clean_Sheets", "Avg Goals/Match"]].copy()
    gk_stats = gk_stats.rename(columns={
        "Goals_Conceded": "Goals Conceded",
        "Clean_Sheets": "Clean Sheets",
    })
    gk_stats["Goals_Conceded"] = gk_stats["Goals Conceded"]
    gk_stats["Clean_Sheets"] = gk_stats["Clean Sheets"]

    return gk_stats.reset_index(drop=True)

import pandas as pd
import streamlit as st


@st.cache_data
def calculate_standings(matches_df, teams_df, season=None):
    """
    Vectorized calculation of league standings.

    Returns the same columns as the previous implementation but uses
    groupby/aggregation for performance on larger datasets.
    """
    if season:
        matches = matches_df[matches_df["season"] == season].copy()
    else:
        matches = matches_df.copy()

    # Filter only completed matches
    matches = matches[matches["match_status"] == "completed"]

    if matches.empty:
        # Return empty standings based on teams_df structure
        df = pd.DataFrame(
            {
                "position": [],
                "team_name": [],
                "city": [],
                "matches_played": [],
                "wins": [],
                "draws": [],
                "losses": [],
                "goals_for": [],
                "goals_against": [],
                "goal_difference": [],
                "points": [],
            }
        )
        return df

    # Home side aggregations
    home = matches.groupby("home_team").agg(
        matches_home=("home_team", "count"),
        goals_for_home=("home_goals", "sum"),
        goals_against_home=("away_goals", "sum"),
        wins_home=("home_goals", lambda s: (s > matches.loc[s.index, "away_goals"]).sum()),
        draws_home=("home_goals", lambda s: (s == matches.loc[s.index, "away_goals"]).sum()),
        losses_home=("home_goals", lambda s: (s < matches.loc[s.index, "away_goals"]).sum()),
    )

    # Away side aggregations
    away = matches.groupby("away_team").agg(
        matches_away=("away_team", "count"),
        goals_for_away=("away_goals", "sum"),
        goals_against_away=("home_goals", "sum"),
        wins_away=("away_goals", lambda s: (s > matches.loc[s.index, "home_goals"]).sum()),
        draws_away=("away_goals", lambda s: (s == matches.loc[s.index, "home_goals"]).sum()),
        losses_away=("away_goals", lambda s: (s < matches.loc[s.index, "home_goals"]).sum()),
    )

    # Combine home/away
    home.index.name = "team_name"
    away.index.name = "team_name"
    agg = pd.concat([home, away], axis=1).fillna(0)

    # Sum totals
    agg["matches_played"] = agg["matches_home"] + agg["matches_away"]
    agg["wins"] = agg["wins_home"] + agg["wins_away"]
    agg["draws"] = agg["draws_home"] + agg["draws_away"]
    agg["losses"] = agg["losses_home"] + agg["losses_away"]
    agg["goals_for"] = agg["goals_for_home"] + agg["goals_for_away"]
    agg["goals_against"] = agg["goals_against_home"] + agg["goals_against_away"]

    # Points and goal difference
    agg["points"] = agg["wins"] * 3 + agg["draws"]
    agg["goal_difference"] = agg["goals_for"] - agg["goals_against"]

    # Merge to preserve team metadata and ensure all teams included.
    # Convert merge keys to string to avoid categorical fillna issues.
    teams_meta = teams_df[["team_id", "team_name", "city"]].copy()
    teams_meta["team_name"] = teams_meta["team_name"].astype(str)
    agg_df = agg.reset_index()
    agg_df["team_name"] = agg_df["team_name"].astype(str)

    standings_df = teams_meta.merge(agg_df, on="team_name", how="left")

    # Fill numeric columns only
    numeric_cols = [
        c for c in standings_df.columns if standings_df[c].dtype.kind in "biufc"
    ]
    standings_df[numeric_cols] = standings_df[numeric_cols].fillna(0)

    # Sort and assign position
    standings_df = standings_df.sort_values(
        by=["points", "goal_difference", "goals_for"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    standings_df["position"] = range(1, len(standings_df) + 1)

    column_order = [
        "position",
        "team_name",
        "city",
        "matches_played",
        "wins",
        "draws",
        "losses",
        "goals_for",
        "goals_against",
        "goal_difference",
        "points",
    ]

    return standings_df[column_order]


@st.cache_data
def get_team_stats(matches_df, teams_df, team_name, season=None):
    """Get detailed stats for a specific team."""
    if season:
        matches = matches_df[matches_df["season"] == season].copy()
    else:
        matches = matches_df.copy()
    
    matches = matches[matches["match_status"] == "completed"]
    
    home_matches = matches[matches["home_team"] == team_name]
    away_matches = matches[matches["away_team"] == team_name]
    
    home_wins = len(home_matches[home_matches["home_goals"] > home_matches["away_goals"]])
    away_wins = len(away_matches[away_matches["away_goals"] > away_matches["home_goals"]])
    
    home_losses = len(home_matches[home_matches["home_goals"] < home_matches["away_goals"]])
    away_losses = len(away_matches[away_matches["away_goals"] < away_matches["home_goals"]])
    
    home_draws = len(home_matches[home_matches["home_goals"] == home_matches["away_goals"]])
    away_draws = len(away_matches[away_matches["away_goals"] == away_matches["home_goals"]])
    
    return {
        "home_wins": home_wins,
        "away_wins": away_wins,
        "home_losses": home_losses,
        "away_losses": away_losses,
        "home_draws": home_draws,
        "away_draws": away_draws,
        "total_wins": home_wins + away_wins,
        "total_losses": home_losses + away_losses,
        "total_draws": home_draws + away_draws,
    }


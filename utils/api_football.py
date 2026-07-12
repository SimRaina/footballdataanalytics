"""
API Football data fetcher utility
Handles all api-football.com API interactions with caching and error handling
Free tier: 100 requests per day
ISL League ID: 323 (confirmed)
"""

import requests
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional, Dict, List, Any


class APIFootballError(Exception):
    """Custom exception for API Football errors"""
    pass


# ISL League ID - confirmed working (323)
ISL_LEAGUE_ID = 323

def get_isl_league_id() -> int:
    """
    Get ISL league ID - returns confirmed ID: 323
    """
    return ISL_LEAGUE_ID


@st.cache_data(ttl=43200)
def get_isl_standings(season: int = 2025) -> Optional[pd.DataFrame]:
    """
    Fetch ISL standings for a given season
    """
    try:
        headers = {
            "x-apisports-key": st.secrets["API_FOOTBALL_KEY"]
        }
        
        response = requests.get(
            f"{st.secrets['API_FOOTBALL_BASE_URL']}/standings",
            params={"league": ISL_LEAGUE_ID, "season": season},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("response") and len(data["response"]) > 0:
            standings_data = []
            for group in data["response"]:
                # Standings are at group["league"]["standings"] - a list of groups
                league_standings = group.get("league", {}).get("standings", [])
                for standings_group in league_standings:
                    for team_standing in standings_group:
                        standings_data.append({
                            "Position": team_standing["rank"],
                            "Team": team_standing["team"]["name"],
                            "Played": team_standing["all"]["played"],
                            "Won": team_standing["all"]["win"],
                            "Draw": team_standing["all"]["draw"],
                            "Lost": team_standing["all"]["lose"],
                            "Goals For": team_standing["all"]["goals"]["for"],
                            "Goals Against": team_standing["all"]["goals"]["against"],
                            "Goal Difference": team_standing["goalsDiff"],
                            "Points": team_standing["points"]
                        })
            
            if standings_data:
                return pd.DataFrame(standings_data)
        
        return None
        
    except Exception as e:
        st.warning(f"⚠️ Could not fetch standings: {str(e)}")
        return None


@st.cache_data(ttl=43200)
def get_isl_teams(season: int = 2022) -> Optional[pd.DataFrame]:
    """
    Fetch all ISL teams for a given season
    """
    try:
        headers = {
            "x-apisports-key": st.secrets["API_FOOTBALL_KEY"]
        }
        
        response = requests.get(
            f"{st.secrets['API_FOOTBALL_BASE_URL']}/teams",
            params={"league": ISL_LEAGUE_ID, "season": season},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("response"):
            teams_data = []
            for team in data["response"]:
                teams_data.append({
                    "Team": team["team"]["name"],
                    "Founded": team["team"].get("founded", "N/A"),
                    "Country": team["team"].get("country", "N/A"),
                    "Venue": team["venue"].get("name", "N/A") if team.get("venue") else "N/A",
                    "Capacity": team["venue"].get("capacity", "N/A") if team.get("venue") else "N/A"
                })
            
            if teams_data:
                return pd.DataFrame(teams_data)
        
        return None
        
    except Exception as e:
        st.warning(f"⚠️ Could not fetch teams: {str(e)}")
        return None


@st.cache_data(ttl=43200)
def get_isl_fixtures(season: int = 2022) -> Optional[pd.DataFrame]:
    """
    Fetch all ISL fixtures for a season
    Note: Free tier doesn't support 'last' or 'next' parameters
    """
    try:
        headers = {
            "x-apisports-key": st.secrets["API_FOOTBALL_KEY"]
        }
        
        response = requests.get(
            f"{st.secrets['API_FOOTBALL_BASE_URL']}/fixtures",
            params={"league": ISL_LEAGUE_ID, "season": season},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("response"):
            fixtures_data = []
            for fixture in data["response"]:
                fixtures_data.append({
                    "Date": fixture["fixture"]["date"],
                    "Home Team": fixture["teams"]["home"]["name"],
                    "Away Team": fixture["teams"]["away"]["name"],
                    "Home Score": fixture["goals"]["home"] or "-",
                    "Away Score": fixture["goals"]["away"] or "-",
                    "Status": fixture["fixture"]["status"]["short"]
                })
            
            if fixtures_data:
                return pd.DataFrame(fixtures_data)
        
        return None
        
    except Exception as e:
        st.warning(f"⚠️ Could not fetch fixtures: {str(e)}")
        return None


@st.cache_data(ttl=43200)
def get_isl_top_scorers(season: int = 2022) -> Optional[pd.DataFrame]:
    """
    Fetch top scorers for ISL season
    """
    try:
        headers = {
            "x-apisports-key": st.secrets["API_FOOTBALL_KEY"]
        }
        
        response = requests.get(
            f"{st.secrets['API_FOOTBALL_BASE_URL']}/players/topscorers",
            params={"league": ISL_LEAGUE_ID, "season": season},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("response"):
            scorers_data = []
            for player in data["response"]:
                stats = player.get("statistics", [{}])[0]
                goals = stats.get("goals", {})
                
                # Extract total goals
                if isinstance(goals, dict):
                    total_goals = goals.get("total", 0)
                else:
                    total_goals = 0
                
                # Extract assists 
                assists = stats.get("goals", {})
                if isinstance(assists, dict):
                    total_assists = assists.get("assists", 0)
                else:
                    total_assists = 0
                
                scorers_data.append({
                    "Player": player.get("player", {}).get("name", "N/A"),
                    "Team": stats.get("team", {}).get("name", "N/A"),
                    "Goals": total_goals,
                    "Assists": total_assists,
                })
            
            if scorers_data:
                return pd.DataFrame(scorers_data)
        
        return None
        
    except Exception as e:
        st.warning(f"⚠️ Could not fetch top scorers: {str(e)}")
        return None


def get_api_quota_info() -> Dict[str, Any]:
    """
    Get current API quota information
    Note: This endpoint might require additional call
    """
    try:
        headers = {
            "x-apisports-key": st.secrets["API_FOOTBALL_KEY"]
        }
        
        response = requests.get(
            f"{st.secrets['API_FOOTBALL_BASE_URL']}/status",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        return response.json().get("response", {})
        
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=43200)
def get_isl_top_assists(season: int = 2022) -> Optional[pd.DataFrame]:
    """
    Fetch top assists for ISL season
    """
    try:
        headers = {
            "x-apisports-key": st.secrets["API_FOOTBALL_KEY"]
        }
        
        response = requests.get(
            f"{st.secrets['API_FOOTBALL_BASE_URL']}/players/topassists",
            params={"league": ISL_LEAGUE_ID, "season": season},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("response"):
            assists_data = []
            for player in data["response"]:
                stats = player.get("statistics", [{}])[0]
                assists_value = stats.get("goals", {})
                
                if isinstance(assists_value, dict):
                    assists_count = assists_value.get("assists", 0)
                else:
                    assists_count = 0
                
                assists_data.append({
                    "Player": player.get("player", {}).get("name", "N/A"),
                    "Team": stats.get("team", {}).get("name", "N/A"),
                    "Assists": assists_count,
                })
            
            if assists_data:
                return pd.DataFrame(assists_data).sort_values("Assists", ascending=False)
        
        return None
        
    except Exception as e:
        st.warning(f"⚠️ Could not fetch top assists: {str(e)}")
        return None


@st.cache_data(ttl=43200)
def get_isl_all_players(season: int = 2022) -> Optional[pd.DataFrame]:
    """
    Fetch all players in ISL season
    """
    try:
        headers = {
            "x-apisports-key": st.secrets["API_FOOTBALL_KEY"]
        }
        
        response = requests.get(
            f"{st.secrets['API_FOOTBALL_BASE_URL']}/players",
            params={"league": ISL_LEAGUE_ID, "season": season},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("response"):
            players_data = []
            for player in data["response"]:
                stats = player.get("statistics", [{}])[0]
                player_info = player.get("player", {})
                
                players_data.append({
                    "Player": player_info.get("name", "N/A"),
                    "Team": stats.get("team", {}).get("name", "N/A"),
                    "Age": player_info.get("age", "N/A"),
                    "Position": stats.get("position", "N/A"),
                    "Goals": stats.get("goals", {}).get("total", 0) if isinstance(stats.get("goals"), dict) else 0,
                    "Assists": stats.get("goals", {}).get("assists", 0) if isinstance(stats.get("goals"), dict) else 0,
                    "Appearances": stats.get("games", {}).get("appearances", 0) if isinstance(stats.get("games"), dict) else 0,
                })
            
            if players_data:
                return pd.DataFrame(players_data)
        
        return None
        
    except Exception as e:
        st.warning(f"⚠️ Could not fetch players: {str(e)}")
        return None


@st.cache_data(ttl=43200)
def get_isl_league_info() -> Optional[Dict[str, Any]]:
    """
    Fetch ISL league information
    """
    try:
        headers = {
            "x-apisports-key": st.secrets["API_FOOTBALL_KEY"]
        }
        
        response = requests.get(
            f"{st.secrets['API_FOOTBALL_BASE_URL']}/leagues",
            params={"id": ISL_LEAGUE_ID},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("response") and len(data["response"]) > 0:
            return data["response"][0]
        
        return None
        
    except Exception as e:
        st.warning(f"⚠️ Could not fetch league info: {str(e)}")
        return None

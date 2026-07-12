"""
Centralized styling for ISL Dashboard
Provides consistent theming across all pages
"""
import streamlit as st

# Color constants
THEME = {
    "bg_dark": "#0e1117",
    "bg_card": "#1c1f26",
    "accent_green": "#228B22",
    "accent_green_light": "rgba(34, 139, 34, 0.2)",
    "text_white": "white",
    "text_light_gray": "#c9d1d9",
}

def apply_dark_theme():
    """Apply consistent dark theme styling across all pages."""
    st.markdown(f"""
        <style>
        body {{
            background-color: {THEME['bg_dark']};
            color: {THEME['text_white']};
        }}
        .stMetric {{
            background-color: {THEME['bg_card']};
            padding: 10px;
            border-radius: 10px;
        }}
        .stDataFrame {{
            background-color: {THEME['bg_dark']};
        }}
        </style>
    """, unsafe_allow_html=True)

def get_theme_color(key):
    """Get a specific theme color by key."""
    return THEME.get(key, "#FFFFFF")


def apply_league_theme(league_config=None):
    """Apply league-specific branding colors and optional logo display."""
    if league_config is None:
        league_config = {}

    accent_color = (league_config.get("metadata") or {}).get("accent_color") or THEME["accent_green"]
    light_accent = (league_config.get("metadata") or {}).get("accent_color_light") or "rgba(34, 139, 34, 0.2)"
    logo_path = (league_config.get("metadata") or {}).get("logo")

    st.markdown(f"""
        <style>
        body {{
            background-color: {THEME['bg_dark']};
            color: {THEME['text_white']};
        }}
        .stMetric {{
            background-color: {THEME['bg_card']};
            padding: 10px;
            border-radius: 10px;
        }}
        .stDataFrame {{
            background-color: {THEME['bg_dark']};
        }}
        .league-accent {{
            color: {accent_color};
            font-weight: 700;
        }}
        .league-pill {{
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            background-color: {light_accent};
            color: {accent_color};
            margin-bottom: 0.75rem;
        }}
        </style>
    """, unsafe_allow_html=True)

    if logo_path:
        try:
            st.image(logo_path, width=120)
        except Exception:
            pass

    return accent_color


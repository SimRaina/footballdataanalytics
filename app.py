import streamlit as st
from utils.loader import load_data, get_current_season

st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
)

# ── Landing page content ────────────────────────────────────────────────
st.title("⚽ Football Data Analytics Dashboard")
st.markdown(
    "### Welcome to the Indian Super League Analytics Platform!"
)
st.info("Use the sidebar to navigate between pages. All data is for the Indian Super League (ISL).")


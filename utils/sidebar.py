import streamlit as st

def render_sidebar_info():
    """
    Display ISL branding in the sidebar.
    """
    with st.sidebar:
        st.markdown("## ⚽ Indian Super League")
        st.success("🏆 **League:** ISL")
        st.divider()
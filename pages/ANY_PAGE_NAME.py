# pages/ANY_PAGE_NAME.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

# Page config
st.set_page_config(
    page_title="Page Title - TechWokx",
    page_icon="📄",
    layout="wide"
)

# Import and apply theme
from modules.ui_theme import apply_theme, sidebar_navigation
apply_theme()

# Render sidebar (optional - if you want sidebar on this page)
current_page = sidebar_navigation()

# Page title
st.markdown('<div class="section-header">📄 Page Title</div>', unsafe_allow_html=True)

# Your page content here
st.markdown("""
<div class="data-card">
    <h4>Content Section</h4>
    <p>Your page content goes here...</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Ghana")

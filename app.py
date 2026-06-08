# app.py (Root directory - Main entry point)
import streamlit as st

# Set page config FIRST (must be the first Streamlit command)
st.set_page_config(
    page_title="TechWokx Lead Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple navigation without importing modules
st.markdown("# TechWokx Lead Intelligence")
st.markdown("## AI-Powered Company Research & Lead Scoring")

st.markdown("---")

st.markdown("""
### Welcome to the Lead Intelligence Platform

This platform helps you research companies, score leads, and generate proposals.

**Available Features:**
- 🔍 **Company Research** - Research any company in seconds
- 📊 **Dashboard** - View your lead pipeline  
- 👥 **CRM** - Manage your contacts
- 📄 **Proposal Generator** - Create professional proposals
- 🧠 **Lead Intelligence** - AI-powered insights
- 🌐 **Website Audit** - Security and SSL checks

**Quick Start:**
1. Go to **Company Research** from the sidebar
2. Enter a company name or website
3. View detailed analysis and lead score
4. Generate a proposal for hot leads
""")

# Sidebar navigation
st.sidebar.markdown("# Navigation")
st.sidebar.markdown("---")

# Navigation buttons
pages = {
    "🔍 Company Research": "pages/company_research.py",
    "📊 Dashboard": "pages/Dashboard.py",
    "👥 CRM": "pages/CRM.py",
    "📄 Proposal Generator": "pages/Proposal_Generator.py",
    "🧠 Lead Intelligence": "pages/Lead_Intelligence.py",
    "📊 Bulk Research": "pages/Bulk_Research.py",
    "🌐 Website Audit": "pages/Website_Audit.py",
}

for page_name, page_path in pages.items():
    if st.sidebar.button(page_name, use_container_width=True, key=page_name):
        try:
            st.switch_page(page_path)
        except Exception as e:
            st.sidebar.error(f"Could not load {page_name}")
            st.sidebar.caption(str(e)[:50])

st.sidebar.markdown("---")
st.sidebar.caption("TechWokx Lead Intelligence v1.0")

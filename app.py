# app.py - Main Dashboard
import streamlit as st
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page config MUST be first
st.set_page_config(
    page_title="TechWokx Lead Intelligence Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import and apply theme
from modules.ui_theme import apply_theme, sidebar_navigation
apply_theme()

# Initialize session state
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Emran"

# Render sidebar navigation
current_page = sidebar_navigation()

# Main content area
st.markdown("""
<div class="welcome-card">
    <h2>Welcome back, Emran!</h2>
    <p>Here's what's happening with your leads today.</p>
</div>
""", unsafe_allow_html=True)

# Page routing
if current_page == "dashboard":
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Leads", "2,438", "↑ 18%")
    with col2:
        st.metric("Hot Leads", "184", "↑ 12%")
    with col3:
        st.metric("Pipeline Value", "$32.5K", "↑ 22%")
    with col4:
        st.metric("Conversion Rate", "72%", "↑ 8%")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Lead Distribution</div>', unsafe_allow_html=True)
        distribution = {"Hot (90-100)": 7.5, "Warm (70-89)": 32.1, "Cold (40-69)": 45.3, "Very Cold (20-39)": 10.2, "Bad (0-19)": 4.9}
        for cat, pct in distribution.items():
            st.markdown(f"""
            <div style="margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between;">
                    <span>{cat}</span>
                    <span>{pct}%</span>
                </div>
                <div style="background: #e2e8f0; border-radius: 10px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #fbbf24, #f59e0b); width: {pct}%; height: 6px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">📝 Recent Activity</div>', unsafe_allow_html=True)
        activities = ["Airside Hotel audited", "Proposal for Ecobank Ghana", "DNS audit for XYZ Logistics", "Lead moved: Melcom Ltd"]
        for act in activities:
            st.markdown(f'<div class="activity-item"><div class="activity-action">{act}</div><div class="activity-time">Recently</div></div>', unsafe_allow_html=True)

elif current_page == "company_search":
    try:
        from pages.company_research import *
    except ImportError:
        st.info("🔍 Company Search - Coming Soon")

elif current_page == "bulk_research":
    st.info("📊 Bulk Research - Coming Soon")

elif current_page == "dns_audit":
    st.info("🌐 DNS Audit - Coming Soon")

elif current_page == "website_audit":
    st.info("🔒 Website Audit - Coming Soon")

elif current_page == "email_security":
    st.info("📧 Email Security - Coming Soon")

elif current_page == "ai_intelligence":
    st.info("🤖 AI Intelligence - Coming Soon")

elif current_page == "proposals":
    st.info("📄 Proposals - Coming Soon")

elif current_page == "crm":
    st.info("👥 CRM - Coming Soon")

elif current_page == "reports":
    st.info("📈 Reports - Coming Soon")

elif current_page == "settings":
    st.info("⚙️ Settings - Coming Soon")

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption(f"© 2024 TechWokx Ghana • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

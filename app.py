# app.py - Main Dashboard
import streamlit as st
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page config MUST be first
st.set_page_config(
    page_title="TechWokx Lead Intelligence Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional UI
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg, .stSidebar {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    /* Welcome card */
    .welcome-card {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.05));
        border: 1px solid rgba(251, 191, 36, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(251, 191, 36, 0.3);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #fbbf24;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.5rem;
    }
    
    /* Section headers */
    .section-header {
        color: #fbbf24;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        border-left: 3px solid #fbbf24;
        padding-left: 1rem;
    }
    
    /* Activity items */
    .activity-item {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #fbbf24;
    }
    
    /* Quick action buttons */
    .quick-action {
        background: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.2);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quick-action:hover {
        background: rgba(251, 191, 36, 0.2);
        transform: translateY(-3px);
    }
    
    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #fbbf24, transparent);
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Emran"

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🔍 TechWokx")
    st.markdown("#### Lead Intelligence Engine")
    st.markdown("---")
    
    # Navigation sections
    st.markdown("**Dashboard**")
    
    # Main navigation
    nav_options = {
        "🏠 Dashboard": "dashboard",
        "🔍 Company Search": "company_search",
        "📊 Bulk Research": "bulk_research",
        "---": "divider1",
        "**AUDITS**": "audits_header",
        "🌐 DNS Audit": "dns_audit",
        "🔒 Website Audit": "website_audit",
        "📧 Email Security": "email_security",
        "---": "divider2",
        "**INTELLIGENCE**": "intelligence_header",
        "🧠 AI Intelligence": "ai_intelligence",
        "---": "divider3",
        "**OUTREACH**": "outreach_header",
        "📄 Proposals": "proposals",
        "👥 CRM": "crm",
        "📈 Leads Pipeline": "leads_pipeline",
        "📊 Reports": "reports",
        "---": "divider4",
        "⚙️ Settings": "settings"
    }
    
    selected_page = None
    
    for label, page_id in nav_options.items():
        if label == "---":
            st.markdown("---")
        elif label.startswith("**"):
            st.markdown(f"<small>{label}</small>", unsafe_allow_html=True)
        else:
            if st.button(label, key=page_id, use_container_width=True):
                selected_page = page_id
                st.session_state.current_page = page_id
    
    st.markdown("---")
    st.caption("© 2024 TechWokx Ghana")
    st.caption("v2.0.0")

# Main content area
st.markdown(f'<div class="welcome-card">', unsafe_allow_html=True)
st.markdown(f"## Welcome back, {st.session_state.user_name}!")
st.markdown("Here's what's happening with your leads today.")
st.markdown('</div>', unsafe_allow_html=True)

# Get current page or default to dashboard
current_page = st.session_state.get('current_page', 'dashboard')

# Page routing
if current_page == "dashboard":
    # Dashboard content
    col1, col2, col3, col4 = st.columns(4)
    
    # Mock data - replace with real data from database
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">47</div>
            <div class="metric-label">Total Leads</div>
            <small style="color:#22c55e">↑ 23%</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">18</div>
            <div class="metric-label">Hot Leads</div>
            <small style="color:#22c55e">↑ 12%</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">₵47.5K</div>
            <div class="metric-label">Pipeline Value</div>
            <small style="color:#22c55e">↑ ₵12K</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">72%</div>
            <div class="metric-label">Conversion Rate</div>
            <small style="color:#22c55e">↑ 8%</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Lead Distribution</div>', unsafe_allow_html=True)
        
        # Simple bar chart data
        chart_data = {
            "Hot Leads (70+)": 18,
            "Warm Leads (50-69)": 15,
            "Cold Leads (<50)": 14
        }
        
        st.bar_chart(chart_data)
    
    with col2:
        st.markdown('<div class="section-header">Recent Activity</div>', unsafe_allow_html=True)
        
        activities = [
            {"time": "2 hours ago", "action": "New lead: Nyaho Medical Centre", "score": 85},
            {"time": "5 hours ago", "action": "Email sent to MTN Ghana", "score": None},
            {"time": "1 day ago", "action": "New lead: GCB Bank", "score": 72},
            {"time": "2 days ago", "action": "Proposal sent to Kasapreko", "score": None},
        ]
        
        for act in activities:
            score_badge = f'<span style="background:#22c55e; padding:2px 8px; border-radius:12px; font-size:11px;">Score: {act["score"]}</span>' if act["score"] else ""
            st.markdown(f"""
            <div class="activity-item">
                <small style="color:#94a3b8">{act['time']}</small>
                <div style="color:#e2e8f0">{act['action']}</div>
                {score_badge}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Quick actions
    st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 New Search", use_container_width=True):
            st.session_state.current_page = "company_search"
            st.rerun()
    
    with col2:
        if st.button("📊 Bulk Research", use_container_width=True):
            st.session_state.current_page = "bulk_research"
            st.rerun()
    
    with col3:
        if st.button("📄 Create Proposal", use_container_width=True):
            st.session_state.current_page = "proposals"
            st.rerun()
    
    with col4:
        if st.button("👥 View CRM", use_container_width=True):
            st.session_state.current_page = "crm"
            st.rerun()

elif current_page == "company_search":
    # Import and run company research page
    try:
        from pages.company_research import *
    except ImportError:
        st.info("🔍 Company Research Page")
        st.markdown("Search for companies to analyze and score leads.")
        
        col1, col2 = st.columns(2)
        with col1:
            company_input = st.text_input("Company Name")
        with col2:
            website_input = st.text_input("Website")
        
        if st.button("Research", type="primary"):
            st.info(f"Researching: {company_input or website_input}")

elif current_page == "bulk_research":
    try:
        from pages.Bulk_Research import *
    except ImportError:
        st.info("📊 Bulk Research Page")
        st.markdown("Research multiple companies at once.")

elif current_page == "dns_audit":
    try:
        from pages.Website_Audit import *
    except ImportError:
        st.info("🌐 DNS Audit Page")
        st.markdown("Check DNS records and email security.")

elif current_page == "website_audit":
    try:
        from pages.Website_Audit import *
    except ImportError:
        st.info("🔒 Website Audit Page")
        st.markdown("Comprehensive website security audit.")

elif current_page == "email_security":
    st.info("📧 Email Security Audit")
    st.markdown("Check SPF, DKIM, and DMARC records for your domain.")
    
    domain = st.text_input("Enter Domain", placeholder="example.com")
    if st.button("Check Email Security"):
        st.info(f"Checking email security for {domain}...")

elif current_page == "ai_intelligence":
    st.info("🧠 AI Intelligence")
    st.markdown("AI-powered lead scoring and insights.")
    
    if st.button("Generate AI Insights"):
        st.info("AI analysis would appear here")

elif current_page == "proposals":
    try:
        from pages.Proposal_Generator import *
    except ImportError:
        st.info("📄 Proposal Generator")
        st.markdown("Create professional proposals for your leads.")

elif current_page == "crm":
    try:
        from pages.CRM import *
    except ImportError:
        st.info("👥 CRM Dashboard")
        st.markdown("Manage your leads and customers.")

elif current_page == "leads_pipeline":
    st.info("📈 Leads Pipeline")
    st.markdown("Track your leads through the sales pipeline.")
    
    # Pipeline stages
    stages = ["New Leads", "Contacted", "Qualified", "Proposal Sent", "Negotiation", "Closed Won", "Closed Lost"]
    
    for stage in stages:
        col1, col2 = st.columns([2, 3])
        with col1:
            st.write(f"**{stage}**")
        with col2:
            st.progress(0.3)
            st.caption("3 leads")

elif current_page == "reports":
    st.info("📊 Reports")
    st.markdown("Generate detailed reports on your lead intelligence.")
    
    report_type = st.selectbox("Report Type", ["Lead Summary", "Conversion Report", "Activity Report", "Revenue Report"])
    
    if st.button("Generate Report"):
        st.success(f"Generating {report_type}...")

elif current_page == "settings":
    try:
        from pages.Settings import *
    except ImportError:
        st.info("⚙️ Settings")
        st.markdown("Configure API keys and system settings.")

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

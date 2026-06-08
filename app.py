# app.py - Main Dashboard with All Text Visible
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

# Custom CSS - All text properly visible
st.markdown("""
<style>
    /* Main container - Light background for readability */
    .stApp {
        background: #f8fafc;
    }
    
    /* Sidebar - Dark only */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(251, 191, 36, 0.2);
    }
    
    /* Sidebar text - All visible */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar small text */
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] .caption,
    [data-testid="stSidebar"] .stCaption {
        color: #94a3b8 !important;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton button {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24 !important;
        border: 1px solid rgba(251, 191, 36, 0.3);
        text-align: left;
        justify-content: flex-start;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(251, 191, 36, 0.3);
        color: #fbbf24 !important;
        border-color: #fbbf24;
    }
    
    /* Sidebar headers */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #fbbf24 !important;
    }
    
    /* Main content area */
    .main .block-container {
        background: #f8fafc;
        padding: 2rem;
    }
    
    /* Main content text - ALL TEXT VISIBLE */
    .main .stMarkdown,
    .main p,
    .main li,
    .main span,
    .main div,
    .main label,
    .main .stText,
    .main .stCaption,
    .main small,
    .main .stMarkdown p {
        color: #1e293b !important;
    }
    
    /* Headers in main content */
    .main h1, .main h2, .main h3, .main h4 {
        color: #0f172a !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #fbbf24;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.7rem;
        color: #10b981;
        margin-top: 0.25rem;
    }
    
    /* Welcome card */
    .welcome-card {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border: none;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .welcome-card h2 {
        color: #0f172a !important;
    }
    
    .welcome-card p {
        color: #334155 !important;
    }
    
    /* Section headers */
    .section-header {
        color: #0f172a;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        border-left: 3px solid #fbbf24;
        padding-left: 1rem;
    }
    
    /* Activity items */
    .activity-item {
        background: white;
        border-radius: 12px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #fbbf24;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .activity-time {
        font-size: 0.7rem;
        color: #94a3b8 !important;
    }
    
    .activity-action {
        color: #1e293b !important;
        font-weight: 500;
    }
    
    /* Pipeline item */
    .pipeline-item {
        background: white;
        border-radius: 10px;
        padding: 0.6rem;
        margin-bottom: 0.5rem;
        border: 1px solid #e2e8f0;
    }
    
    .pipeline-stage {
        font-weight: 600;
        color: #0f172a;
    }
    
    .pipeline-count {
        color: #64748b;
        font-size: 0.85rem;
    }
    
    /* Table styling */
    .data-table {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    
    .data-table th {
        background: #f1f5f9;
        color: #0f172a !important;
        padding: 0.75rem;
        font-weight: 600;
    }
    
    .data-table td {
        padding: 0.75rem;
        border-top: 1px solid #e2e8f0;
        color: #334155 !important;
    }
    
    /* Score badges */
    .score-badge-hot {
        background: #dc2626;
        color: white !important;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .score-badge-warm {
        background: #f97316;
        color: white !important;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .score-badge-good {
        background: #22c55e;
        color: white !important;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, #e2e8f0, #fbbf24, #e2e8f0);
        margin: 1.5rem 0;
    }
    
    /* Plan badge */
    .plan-badge {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: #0f172a !important;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        text-align: center;
    }
    
    .plan-badge small {
        color: #0f172a !important;
    }
    
    .plan-badge a {
        color: #0f172a !important;
        text-decoration: underline;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: #0f172a !important;
        font-weight: 600;
        border: none;
        border-radius: 8px;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white !important;
    }
    
    /* Metric styling - Override Streamlit defaults */
    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 0.85rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #10b981 !important;
        font-size: 0.7rem !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        background: white;
        border-radius: 12px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        color: #1e293b !important;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #64748b !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #fbbf24 !important;
        background-color: #0f172a;
    }
    
    /* Info/Warning/Success boxes */
    .stAlert {
        background-color: white !important;
        border-left: 4px solid #fbbf24 !important;
    }
    
    .stAlert p {
        color: #1e293b !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    /* Selectbox */
    .stSelectbox label {
        color: #1e293b !important;
    }
    
    /* Number input */
    .stNumberInput label {
        color: #1e293b !important;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #1e293b !important;
    }
    
    /* Radio */
    .stRadio label {
        color: #1e293b !important;
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
    nav_items = {
        "Dashboard": "dashboard",
        "Research": "research_header",
        "🔍 Company Search": "company_search",
        "📊 Bulk Research": "bulk_research",
        "Audits": "audits_header",
        "🌐 DNS Audit": "dns_audit",
        "🔒 Website Audit": "website_audit",
        "📧 Email Security": "email_security",
        "Intelligence": "intelligence_header",
        "🤖 AI Intelligence": "ai_intelligence",
        "Outreach": "outreach_header",
        "📄 Proposals": "proposals",
        "👥 CRM": "crm",
        "📈 Reports": "reports",
        "⚙️ Settings": "settings"
    }
    
    for label, page_id in nav_items.items():
        if label in ["Research", "Audits", "Intelligence", "Outreach"]:
            st.markdown(f"<small style='color:#94a3b8; font-size:0.7rem;'>{label}</small>", unsafe_allow_html=True)
        elif st.button(label, key=page_id, use_container_width=True):
            st.session_state.current_page = page_id
            st.rerun()
    
    st.markdown("---")
    
    # Plan info
    st.markdown("""
    <div class="plan-badge">
        🚀 You're on Pro Plan<br>
        <small>Unlimited leads & audits</small><br>
        <a href="#">Upgrade Plan →</a>
    </div>
    """, unsafe_allow_html=True)

# Main content area
st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
st.markdown("## Welcome back, Emran!")
st.markdown("Here's what's happening with your leads today.")
st.markdown('</div>', unsafe_allow_html=True)

# Get current page or default to dashboard
current_page = st.session_state.get('current_page', 'dashboard')

# Dashboard content
if current_page == "dashboard":
    # Metrics row using Streamlit metrics (properly styled)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Leads",
            value="47",
            delta="23%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="Hot Leads",
            value="18",
            delta="12%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="Pipeline Value",
            value="€47.5K",
            delta="€12K",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="Conversion Rate",
            value="72%",
            delta="8%",
            delta_color="normal"
        )
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">📊 Lead Distribution</div>', unsafe_allow_html=True)
        
        # Lead distribution data
        distribution = {
            "Hot Leads (90-100)": 7.5,
            "Warm Leads (70-89)": 32.1,
            "Cold Leads (40-69)": 45.3,
            "Very Cold (20-39)": 10.2,
            "Bad (0-19)": 4.9
        }
        
        for category, percentage in distribution.items():
            st.markdown(f"""
            <div class="pipeline-item">
                <div style="display: flex; justify-content: space-between;">
                    <span class="pipeline-stage">{category}</span>
                    <span class="pipeline-count">{percentage}%</span>
                </div>
                <div style="background: #e2e8f0; border-radius: 10px; margin-top: 5px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #fbbf24, #f59e0b); width: {percentage}%; height: 6px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">📝 Recent Activity</div>', unsafe_allow_html=True)
        
        activities = [
            {"action": "Airside Hotel audited", "time": "2 minutes ago"},
            {"action": "Proposal generated for Ecobank Ghana", "time": "1 hour ago"},
            {"action": "DNS audit completed for XYZ Logistics", "time": "2 hours ago"},
            {"action": "Lead moved to Negotiation: Melcom Ltd", "time": "3 hours ago"},
            {"action": "Email security audit completed", "time": "3 hours ago"},
        ]
        
        for act in activities:
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-action">{act['action']}</div>
                <div class="activity-time">{act['time']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("📋 View all activity →", use_container_width=True):
            st.info("Viewing all activities")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Top Opportunities Table
    st.markdown('<div class="section-header">🏆 Top Opportunities</div>', unsafe_allow_html=True)
    
    # Create DataFrame for display
    opportunities = [
        {"Company": "Airside Hotel", "Lead Score": 92, "Opportunity Value": "$5,000 - $10,000"},
        {"Company": "Ecobank Ghana", "Lead Score": 87, "Opportunity Value": "$3,000 - $7,000"},
        {"Company": "XYZ Logistics", "Lead Score": 85, "Opportunity Value": "$2,500 - $5,000"},
        {"Company": "Melcom Ltd", "Lead Score": 81, "Opportunity Value": "$1,500 - $3,000"},
        {"Company": "Sunrise Logistics", "Lead Score": 78, "Opportunity Value": "$1,000 - $2,500"},
    ]
    
    # Display as interactive table
    for opp in opportunities:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.write(f"**{opp['Company']}**")
        with col2:
            score = opp['Lead Score']
            if score >= 90:
                st.markdown(f'<span class="score-badge-hot">{score}</span>', unsafe_allow_html=True)
            elif score >= 80:
                st.markdown(f'<span class="score-badge-warm">{score}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="score-badge-good">{score}</span>', unsafe_allow_html=True)
        with col3:
            st.write(opp['Opportunity Value'])
        st.markdown("---")

elif current_page == "company_search":
    try:
        from pages.company_research import *
    except ImportError:
        st.info("🔍 Company Search")
        st.markdown("Search for companies to analyze and score leads.")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", placeholder="e.g. Nyaho Medical Centre")
        with col2:
            website = st.text_input("Website", placeholder="e.g. nyahoclinic.com")
        
        if st.button("🔍 Research", type="primary"):
            st.success(f"Researching: {company_name or website}")

elif current_page == "bulk_research":
    st.info("📊 Bulk Research")
    st.markdown("Research multiple companies at once.")
    
    companies = st.text_area("Enter company names (one per line)", height=150, placeholder="Nyaho Medical Centre\nMTN Ghana\nGCB Bank")
    if st.button("Start Bulk Research", type="primary"):
        st.success("Bulk research started!")

elif current_page == "dns_audit":
    st.info("🌐 DNS Audit")
    st.markdown("Check DNS records and email security.")
    
    domain = st.text_input("Enter Domain", placeholder="example.com")
    if st.button("Run DNS Audit", type="primary"):
        st.info(f"Auditing {domain}...")

elif current_page == "website_audit":
    st.info("🔒 Website Audit")
    st.markdown("Comprehensive website security audit.")
    
    url = st.text_input("Website URL", placeholder="https://example.com")
    if st.button("Audit Website", type="primary"):
        st.info(f"Auditing {url}...")

elif current_page == "email_security":
    st.info("📧 Email Security Audit")
    st.markdown("Check SPF, DKIM, and DMARC records.")
    
    domain = st.text_input("Domain", placeholder="example.com")
    if st.button("Check Email Security", type="primary"):
        st.info(f"Checking email security for {domain}...")

elif current_page == "ai_intelligence":
    st.info("🤖 AI Intelligence")
    st.markdown("AI-powered lead scoring and insights.")
    
    if st.button("Generate AI Insights", type="primary"):
        st.info("AI analysis would appear here")

elif current_page == "proposals":
    st.info("📄 Proposals")
    st.markdown("Create professional proposals for your leads.")

elif current_page == "crm":
    st.info("👥 CRM Dashboard")
    st.markdown("Manage your leads and customers.")

elif current_page == "reports":
    st.info("📈 Reports")
    st.markdown("Generate detailed reports on your lead intelligence.")
    
    report_type = st.selectbox("Report Type", ["Lead Summary", "Conversion Report", "Activity Report"])
    if st.button("Generate Report", type="primary"):
        st.success(f"Generating {report_type}...")

elif current_page == "settings":
    st.info("⚙️ Settings")
    st.markdown("Configure API keys and system settings.")

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption(f"© 2024 TechWokx Ghana • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

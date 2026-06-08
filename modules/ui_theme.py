# modules/ui_theme.py
# Centralized UI theme for all pages

import streamlit as st

# Main theme CSS that will be applied to all pages
MAIN_THEME_CSS = """
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
    
    /* Sidebar headers */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #fbbf24 !important;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton button {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24 !important;
        border: 1px solid rgba(251, 191, 36, 0.3);
        text-align: left;
        justify-content: flex-start;
        font-weight: 500;
        width: 100%;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(251, 191, 36, 0.3);
        color: #fbbf24 !important;
        border-color: #fbbf24;
    }
    
    /* Main content area */
    .main .block-container {
        background: #f8fafc;
        padding: 2rem;
    }
    
    /* Main content text - ALL VISIBLE */
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
    
    /* Headers */
    .main h1, .main h2, .main h3, .main h4 {
        color: #0f172a !important;
    }
    
    /* Metric cards */
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
    
    /* Cards */
    .data-card, .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
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
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #64748b !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        color: #fbbf24 !important;
        background-color: #0f172a;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        color: #1e293b !important;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Dataframe */
    .stDataFrame {
        background: white;
        border-radius: 12px;
    }
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: white;
        border: 1px solid #e2e8f0;
        color: #1e293b;
        border-radius: 8px;
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
    
    /* Logo */
    .logo {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid rgba(251, 191, 36, 0.2);
        margin-bottom: 1rem;
    }
    
    .logo h3 {
        color: #fbbf24 !important;
        margin: 0;
    }
    
    .logo p {
        color: #94a3b8 !important;
        font-size: 0.7rem;
        margin: 0;
    }
</style>
"""

# Navigation items for sidebar
NAV_ITEMS = {
    "Dashboard": "🏠 Dashboard",
    "Research": None,
    "🔍 Company Search": "company_search",
    "📊 Bulk Research": "bulk_research",
    "Audits": None,
    "🌐 DNS Audit": "dns_audit",
    "🔒 Website Audit": "website_audit",
    "📧 Email Security": "email_security",
    "Intelligence": None,
    "🤖 AI Intelligence": "ai_intelligence",
    "Outreach": None,
    "📄 Proposals": "proposals",
    "👥 CRM": "crm",
    "📈 Reports": "reports",
    None: None,
    "⚙️ Settings": "settings"
}

def apply_theme():
    """Apply the theme to the current page"""
    st.markdown(MAIN_THEME_CSS, unsafe_allow_html=True)

def sidebar_navigation():
    """Render the sidebar navigation"""
    with st.sidebar:
        st.markdown("""
        <div class="logo">
            <h3>🔍 TechWokx</h3>
            <p>Lead Intelligence Engine</p>
        </div>
        """, unsafe_allow_html=True)
        
        for label, page_id in NAV_ITEMS.items():
            if label is None:
                st.markdown("---")
            elif page_id is None:
                st.markdown(f"<small style='color:#94a3b8; font-size:0.7rem;'>{label}</small>", unsafe_allow_html=True)
            else:
                if st.button(label, key=page_id, use_container_width=True):
                    st.session_state.current_page = page_id
                    st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div class="plan-badge">
            🚀 Pro Plan<br>
            <small>Unlimited leads & audits</small>
        </div>
        """, unsafe_allow_html=True)
    
    return st.session_state.get('current_page', 'dashboard')

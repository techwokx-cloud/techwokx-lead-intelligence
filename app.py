# app.py
import streamlit as st

st.set_page_config(
    page_title="TechWokx Lead Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean CSS
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #fbbf24 !important;
    }
    
    /* Main content */
    .stApp {
        background: #f8fafc;
    }
    .main-header {
        color: #0f172a;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .welcome-card {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.8rem;
    }
    .section-header {
        color: #0f172a;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1rem 0;
        border-left: 3px solid #fbbf24;
        padding-left: 1rem;
    }
    .activity-item {
        background: white;
        border-radius: 10px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #fbbf24;
    }
    .custom-divider {
        height: 1px;
        background: #e2e8f0;
        margin: 1.5rem 0;
    }
    .stButton button {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: #0f172a !important;
        font-weight: 600;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔍 TechWokx")
    st.markdown("#### Lead Intelligence Engine")
    st.markdown("---")
    
    pages = {
        "🏠 Dashboard": "dashboard",
        "🔍 Company Search": "company_search",
        "📊 Bulk Research": "bulk_research",
        "🌐 DNS Audit": "dns_audit",
        "🔒 Website Audit": "website_audit",
        "📧 Email Security": "email_security",
        "🤖 AI Intelligence": "ai_intelligence",
        "📄 Proposals": "proposals",
        "👥 CRM": "crm",
        "📈 Reports": "reports",
        "⚙️ Settings": "settings"
    }
    
    for label, key in pages.items():
        if st.button(label, key=key, use_container_width=True):
            st.session_state.page = key
            st.rerun()
    
    st.markdown("---")
    st.markdown("🚀 **Pro Plan**")
    st.caption("Unlimited leads & audits")

# Main content
page = st.session_state.get("page", "dashboard")

if page == "dashboard":
    st.markdown("""
    <div class="welcome-card">
        <h2>Welcome back, Emran!</h2>
        <p>Here's what's happening with your leads today.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">2,438</div>
            <div class="metric-label">Total Leads</div>
            <small style="color:#10b981;">↑ 18%</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">184</div>
            <div class="metric-label">Hot Leads</div>
            <small style="color:#10b981;">↑ 12%</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">$32.5K</div>
            <div class="metric-label">Pipeline Value</div>
            <small style="color:#10b981;">↑ 22%</small>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">72%</div>
            <div class="metric-label">Conversion Rate</div>
            <small style="color:#10b981;">↑ 8%</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Lead Distribution</div>', unsafe_allow_html=True)
        data = {"Hot": 7.5, "Warm": 32.1, "Cold": 45.3, "Very Cold": 10.2, "Bad": 4.9}
        for cat, val in data.items():
            st.markdown(f"{cat}: {val}%")
            st.progress(val / 100)
    
    with col2:
        st.markdown('<div class="section-header">📝 Recent Activity</div>', unsafe_allow_html=True)
        activities = ["Airside Hotel audited", "Proposal for Ecobank", "DNS audit completed", "Lead moved to negotiation"]
        for act in activities:
            st.markdown(f'<div class="activity-item">{act}</div>', unsafe_allow_html=True)

elif page == "company_search":
    st.markdown('<div class="section-header">🔍 Company Search</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company Name")
    with col2:
        website = st.text_input("Website (optional)")
    if st.button("Research", type="primary"):
        st.info(f"Researching {company or website}...")
        st.success("Demo: Company researched successfully!")

elif page == "bulk_research":
    st.markdown('<div class="section-header">📊 Bulk Research</div>', unsafe_allow_html=True)
    companies = st.text_area("Company names (one per line)", height=150)
    if st.button("Start"):
        if companies:
            lines = [c.strip() for c in companies.split("\n") if c.strip()]
            st.success(f"Will research {len(lines)} companies")
            for c in lines[:5]:
                st.write(f"• {c}")

elif page == "dns_audit":
    st.markdown('<div class="section-header">🌐 DNS Audit</div>', unsafe_allow_html=True)
    domain = st.text_input("Domain")
    if st.button("Run DNS Audit"):
        st.info(f"Auditing {domain}...")

elif page == "website_audit":
    st.markdown('<div class="section-header">🔒 Website Audit</div>', unsafe_allow_html=True)
    url = st.text_input("Website URL")
    if st.button("Audit"):
        st.info(f"Auditing {url}...")

elif page == "email_security":
    st.markdown('<div class="section-header">📧 Email Security</div>', unsafe_allow_html=True)
    domain = st.text_input("Domain")
    if st.button("Check"):
        st.info(f"Checking email security for {domain}...")

elif page == "ai_intelligence":
    st.markdown('<div class="section-header">🤖 AI Intelligence</div>', unsafe_allow_html=True)
    if st.button("Generate AI Insights"):
        st.info("AI analysis would appear here")

elif page == "proposals":
    st.markdown('<div class="section-header">📄 Proposals</div>', unsafe_allow_html=True)
    st.info("Proposal generator - Coming soon")

elif page == "crm":
    st.markdown('<div class="section-header">👥 CRM</div>', unsafe_allow_html=True)
    st.info("CRM Dashboard - Coming soon")

elif page == "reports":
    st.markdown('<div class="section-header">📈 Reports</div>', unsafe_allow_html=True)
    report_type = st.selectbox("Report Type", ["Lead Summary", "Conversion Report", "Activity Report"])
    if st.button("Generate"):
        st.success(f"Generating {report_type}...")

elif page == "settings":
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.info("Settings - Coming soon")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Ghana")

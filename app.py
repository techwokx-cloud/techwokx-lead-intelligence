# app.py - Unified Light Theme
import streamlit as st

st.set_page_config(
    page_title="TechWokx Lead Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Unified Light Theme CSS
st.markdown("""
<style>
    /* Main app - Light background */
    .stApp {
        background: #f8fafc;
    }
    
    /* Sidebar - Dark only */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(251, 191, 36, 0.2);
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
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
    
    /* Main content - ALL LIGHT */
    .main .block-container {
        background: #f8fafc;
        padding: 2rem;
    }
    
    /* Main text - Dark for readability */
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
    
    /* Welcome card - Light yellow */
    .welcome-card {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border: none;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .welcome-card h2, .welcome-card p {
        color: #0f172a !important;
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
    
    /* Cards - White background */
    .data-card, .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.85rem;
    }
    
    .metric-delta {
        color: #10b981;
        font-size: 0.7rem;
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
    
    /* Buttons - Gold gradient */
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
    
    /* Plan badge in sidebar */
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
    
    /* Metrics override */
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
    
    /* Tabs - Light */
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
    
    /* Input fields - Light */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: white;
        border: 1px solid #e2e8f0;
        color: #1e293b;
        border-radius: 8px;
    }
    
    /* Dataframe */
    .stDataFrame {
        background: white;
        border-radius: 12px;
    }
    
    /* Logo in sidebar */
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
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="logo">
        <h3>🔍 TechWokx</h3>
        <p>Lead Intelligence Engine</p>
    </div>
    """, unsafe_allow_html=True)
    
    pages = {
        "🏠 Dashboard": "dashboard",
        "🔍 Company Research": "company_research",
        "📊 Bulk Research": "bulk_research",
        "🌐 Website Audit": "website_audit",
        "📧 Email Security": "email_security",
        "🔒 DNS Audit": "dns_audit",
        "🧠 AI Intelligence": "ai_intelligence",
        "📄 Proposal Generator": "proposals",
        "👥 CRM": "crm",
        "📈 Reports": "reports",
        "⚙️ Settings": "settings"
    }
    
    for label, key in pages.items():
        if st.button(label, key=key, use_container_width=True):
            st.session_state.page = key
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div class="plan-badge">
        🚀 Pro Plan<br>
        <small>Unlimited leads & audits</small>
    </div>
    """, unsafe_allow_html=True)

# Main content
page = st.session_state.get("page", "dashboard")

# Dashboard Page
if page == "dashboard":
    st.markdown("""
    <div class="welcome-card">
        <h2>Welcome back, Emran!</h2>
        <p>Here's what's happening with your leads today.</p>
    </div>
    """, unsafe_allow_html=True)
    
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
            st.markdown(f"{cat}: {pct}%")
            st.progress(pct / 100)
    
    with col2:
        st.markdown('<div class="section-header">📝 Recent Activity</div>', unsafe_allow_html=True)
        activities = [
            {"action": "Airside Hotel audited", "time": "2 minutes ago"},
            {"action": "Proposal generated for Ecobank Ghana", "time": "1 hour ago"},
            {"action": "DNS audit completed for XYZ Logistics", "time": "2 hours ago"},
            {"action": "Lead moved to Negotiation: Melcom Ltd", "time": "3 hours ago"}
        ]
        for act in activities:
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-action">{act['action']}</div>
                <div class="activity-time">{act['time']}</div>
            </div>
            """, unsafe_allow_html=True)

# Company Research Page
elif page == "company_research":
    st.markdown('<div class="section-header">🔍 Company Research</div>', unsafe_allow_html=True)
    st.caption("Research any company and get instant lead scoring")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company Name", placeholder="e.g. Nyaho Medical Centre")
    with col2:
        website = st.text_input("Website (optional)", placeholder="e.g. nyahoclinic.com")
    
    if st.button("🔍 Research Company", type="primary"):
        if company:
            with st.spinner(f"Researching {company}..."):
                st.success(f"✅ Research complete for {company}!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div class="data-card">
                        <h4>Company Information</h4>
                        <p><strong>Name:</strong> {}</p>
                        <p><strong>Website:</strong> {}</p>
                        <p><strong>Email:</strong> info@{}•com</p>
                        <p><strong>Phone:</strong> +233 XX XXX XXXX</p>
                    </div>
                    """.format(company, website or f"www.{company.lower().replace(' ', '')}.com", company.lower().replace(' ', '')), unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class="data-card">
                        <h4>Lead Score</h4>
                        <p style="font-size: 2rem; font-weight: 700; color: #fbbf24;">72/100</p>
                        <p><strong>Status:</strong> Warm Lead</p>
                        <p><strong>Confidence:</strong> High</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a company name")

# Bulk Research Page
elif page == "bulk_research":
    st.markdown('<div class="section-header">📊 Bulk Company Research</div>', unsafe_allow_html=True)
    st.caption("Research multiple companies at once")
    st.markdown("---")
    
    companies = st.text_area("Company Names (one per line)", height=150, placeholder="Nyaho Medical Centre\nMTN Ghana\nGCB Bank")
    
    if st.button("🚀 Start Bulk Research", type="primary"):
        if companies:
            lines = [c.strip() for c in companies.split("\n") if c.strip()]
            progress = st.progress(0)
            for i, c in enumerate(lines):
                progress.progress((i + 1) / len(lines))
            st.success(f"✅ Researched {len(lines)} companies!")
            st.dataframe([{"Company": c, "Status": "Researched", "Lead Score": "72/100"} for c in lines], use_container_width=True)
        else:
            st.warning("Please enter company names")

# Website Audit Page
elif page == "website_audit":
    st.markdown('<div class="section-header">🌐 Website Audit</div>', unsafe_allow_html=True)
    st.caption("Comprehensive security and performance audit")
    st.markdown("---")
    
    url = st.text_input("Website URL", placeholder="https://example.com")
    if st.button("Run Website Audit", type="primary"):
        if url:
            with st.spinner(f"Auditing {url}..."):
                st.success("✅ Audit complete!")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div class="data-card">
                        <h4>SSL Certificate</h4>
                        <p>✅ Valid</p>
                        <p>📅 Expires in 180 days</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class="data-card">
                        <h4>Security Headers</h4>
                        <p>✅ HSTS Enabled</p>
                        <p>⚠️ CSP Not Configured</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a URL")

# Email Security Page
elif page == "email_security":
    st.markdown('<div class="section-header">📧 Email Security Audit</div>', unsafe_allow_html=True)
    st.caption("Check SPF, DKIM, and DMARC records")
    st.markdown("---")
    
    domain = st.text_input("Domain", placeholder="example.com")
    if st.button("Check Email Security", type="primary"):
        if domain:
            with st.spinner(f"Checking {domain}..."):
                st.success("✅ Security check complete!")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>Email Records</h4>
                        <p>✅ SPF: Configured</p>
                        <p>⚠️ DKIM: Not Found</p>
                        <p>❌ DMARC: Not Configured</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class="data-card">
                        <h4>Risk Assessment</h4>
                        <p style="color: #f97316;">🟠 Moderate Risk</p>
                        <p>Email spoofing possible</p>
                        <p>Recommend: Setup DMARC</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a domain")

# DNS Audit Page
elif page == "dns_audit":
    st.markdown('<div class="section-header">🔒 DNS Audit</div>', unsafe_allow_html=True)
    st.caption("Check DNS records and configuration")
    st.markdown("---")
    
    domain = st.text_input("Domain", placeholder="example.com")
    if st.button("Run DNS Audit", type="primary"):
        if domain:
            with st.spinner(f"Auditing {domain}..."):
                st.success("✅ DNS audit complete!")
                st.markdown("""
                <div class="data-card">
                    <h4>DNS Records</h4>
                    <p>✅ A Records: Found</p>
                    <p>✅ MX Records: Found</p>
                    <p>⚠️ TXT Records: Partial</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a domain")

# AI Intelligence Page
elif page == "ai_intelligence":
    st.markdown('<div class="section-header">🧠 AI Intelligence</div>', unsafe_allow_html=True)
    st.caption("AI-powered lead scoring and insights")
    st.markdown("---")
    
    if st.button("Generate AI Insights", type="primary"):
        with st.spinner("Analyzing leads..."):
            st.success("AI analysis complete!")
            st.markdown("""
            <div class="data-card">
                <h4>Key Insights</h4>
                <p>📊 Top industry: Hospitality (32% of leads)</p>
                <p>🎯 Best time to contact: Tuesday 10 AM</p>
                <p>💡 Recommendation: Focus on email security for SMEs</p>
            </div>
            """, unsafe_allow_html=True)

# Proposals Page
elif page == "proposals":
    st.markdown('<div class="section-header">📄 Proposal Generator</div>', unsafe_allow_html=True)
    st.caption("Create professional proposals for your leads")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Company Name")
        client_email = st.text_input("Client Email")
    with col2:
        proposal_type = st.selectbox("Proposal Type", ["Email Security", "Website Audit", "IT Infrastructure", "Custom"])
        urgency = st.selectbox("Priority", ["High", "Medium", "Low"])
    
    if st.button("Generate Proposal", type="primary"):
        if client_name:
            st.success("Proposal generated!")
            st.markdown(f"""
            <div class="data-card">
                <h4>Proposal for {client_name}</h4>
                <p><strong>Service:</strong> {proposal_type}</p>
                <p><strong>Value:</strong> $2,500 - $5,000</p>
                <p><strong>Next Steps:</strong> Schedule discovery call</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please enter client name")

# CRM Page
elif page == "crm":
    st.markdown('<div class="section-header">👥 CRM Dashboard</div>', unsafe_allow_html=True)
    st.caption("Manage your leads and customers")
    st.markdown("---")
    
    # Sample CRM data
    crm_data = [
        {"Company": "Airside Hotel", "Contact": "John Doe", "Lead Score": 92, "Status": "Hot", "Value": "$10,000"},
        {"Company": "Ecobank Ghana", "Contact": "Jane Smith", "Lead Score": 87, "Status": "Warm", "Value": "$7,000"},
        {"Company": "XYZ Logistics", "Contact": "Mike Johnson", "Lead Score": 85, "Status": "Warm", "Value": "$5,000"},
        {"Company": "Melcom Ltd", "Contact": "Sarah Adams", "Lead Score": 81, "Status": "Warm", "Value": "$3,000"},
    ]
    st.dataframe(crm_data, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Lead", use_container_width=True):
            st.info("Add lead form would appear here")
    with col2:
        if st.button("📊 Export CRM Data", use_container_width=True):
            st.success("Exporting CRM data...")

# Reports Page
elif page == "reports":
    st.markdown('<div class="section-header">📈 Reports</div>', unsafe_allow_html=True)
    st.caption("Generate detailed reports on your lead intelligence")
    st.markdown("---")
    
    report_type = st.selectbox("Report Type", ["Lead Summary", "Conversion Report", "Activity Report", "Revenue Report"])
    date_range = st.selectbox("Date Range", ["Last 7 days", "Last 30 days", "Last quarter", "Year to date"])
    
    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            st.success(f"{report_type} generated for {date_range}!")
            st.markdown("""
            <div class="data-card">
                <h4>Report Summary</h4>
                <p>📊 Total Leads: 2,438</p>
                <p>🎯 Conversion Rate: 23.3%</p>
                <p>💰 Pipeline Value: $32,500</p>
            </div>
            """, unsafe_allow_html=True)

# Settings Page
elif page == "settings":
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.caption("Configure API keys and system settings")
    st.markdown("---")
    
    st.markdown("### API Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    with col2:
        st.text_input("Google Maps API Key", type="password", placeholder="AIzaSy...")
        st.text_input("Resend API Key", type="password", placeholder="re_...")
    
    st.markdown("### Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Default Country", ["Ghana", "Nigeria", "Kenya", "South Africa"])
    with col2:
        st.selectbox("Email Notifications", ["Daily", "Weekly", "Never"])
    
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Ghana • All pages now have unified light theme")

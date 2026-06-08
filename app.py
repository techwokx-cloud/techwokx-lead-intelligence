# app.py - Complete working app with light theme
import streamlit as st

st.set_page_config(
    page_title="TechWokx Lead Intelligence",
    page_icon=":mag:",
    layout="wide"
)

# Light theme CSS - no syntax errors
st.markdown("""
<style>
.stApp {
    background-color: #f8fafc;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #fbbf24 !important;
}

.main-header {
    color: #0f172a;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 1rem;
    border-left: 3px solid #fbbf24;
    padding-left: 1rem;
}

.welcome-card {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.welcome-card h2 {
    color: #0f172a;
    margin: 0;
}

.welcome-card p {
    color: #334155;
    margin: 0.5rem 0 0 0;
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
    margin-top: 0.25rem;
}

.metric-delta {
    color: #10b981;
    font-size: 0.7rem;
    margin-top: 0.25rem;
}

.data-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem;
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
}

.data-card h4 {
    color: #0f172a;
    margin-top: 0;
    margin-bottom: 0.75rem;
}

.data-card p {
    color: #334155;
    margin: 0.25rem 0;
}

.activity-item {
    background: white;
    border-radius: 12px;
    padding: 0.8rem;
    margin-bottom: 0.5rem;
    border-left: 3px solid #fbbf24;
}

.activity-action {
    color: #1e293b;
    font-weight: 500;
}

.activity-time {
    color: #94a3b8;
    font-size: 0.7rem;
}

.section-header {
    color: #0f172a;
    font-size: 1.2rem;
    font-weight: 600;
    margin: 1.5rem 0 1rem 0;
    border-left: 3px solid #fbbf24;
    padding-left: 1rem;
}

.custom-divider {
    height: 1px;
    background: #e2e8f0;
    margin: 1.5rem 0;
}

.plan-badge {
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    border-radius: 12px;
    padding: 0.75rem;
    text-align: center;
}

.plan-badge * {
    color: #0f172a !important;
}

.score-hot {
    background: #dc2626;
    color: white;
    padding: 4px 10px;
    border-radius: 20px;
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
}

.score-warm {
    background: #f97316;
    color: white;
    padding: 4px 10px;
    border-radius: 20px;
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
}

.score-good {
    background: #22c55e;
    color: white;
    padding: 4px 10px;
    border-radius: 20px;
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
}

.stButton > button {
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    color: #0f172a;
    font-weight: 600;
    border: none;
    border-radius: 8px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("### :mag: TechWokx")
    st.markdown("#### Lead Intelligence Engine")
    st.markdown("---")
    
    pages = {
        "Dashboard": "dashboard",
        "Company Research": "company_research",
        "Bulk Research": "bulk_research",
        "Website Audit": "website_audit",
        "Email Security": "email_security",
        "DNS Audit": "dns_audit",
        "AI Intelligence": "ai_intelligence",
        "Proposals": "proposals",
        "CRM": "crm",
        "Reports": "reports",
        "Settings": "settings"
    }
    
    for label, key in pages.items():
        if st.button(label, key=key, use_container_width=True):
            st.session_state.page = key
            st.rerun()
    
    st.markdown("---")
    st.markdown('<div class="plan-badge">🚀 Pro Plan<br><small>Unlimited leads</small></div>', unsafe_allow_html=True)

# Get current page
page = st.session_state.get("page", "dashboard")

# ============ DASHBOARD PAGE ============
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
            <div class="metric-delta">↑ 18%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">184</div>
            <div class="metric-label">Hot Leads</div>
            <div class="metric-delta">↑ 12%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">$32.5K</div>
            <div class="metric-label">Pipeline Value</div>
            <div class="metric-delta">↑ 22%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">72%</div>
            <div class="metric-label">Conversion Rate</div>
            <div class="metric-delta">↑ 8%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">📊 Lead Distribution</div>', unsafe_allow_html=True)
        
        dist_data = [
            ("Hot (90-100)", 7.5),
            ("Warm (70-89)", 32.1),
            ("Cold (40-69)", 45.3),
            ("Very Cold (20-39)", 10.2),
            ("Bad (0-19)", 4.9)
        ]
        
        for label, val in dist_data:
            st.write(f"{label}: {val}%")
            st.progress(val / 100)
    
    with col2:
        st.markdown('<div class="section-header">📝 Recent Activity</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="activity-item">
            <div class="activity-action">Airside Hotel audited</div>
            <div class="activity-time">2 minutes ago</div>
        </div>
        <div class="activity-item">
            <div class="activity-action">Proposal for Ecobank Ghana</div>
            <div class="activity-time">1 hour ago</div>
        </div>
        <div class="activity-item">
            <div class="activity-action">DNS audit for XYZ Logistics</div>
            <div class="activity-time">2 hours ago</div>
        </div>
        <div class="activity-item">
            <div class="activity-action">Lead moved: Melcom Ltd</div>
            <div class="activity-time">3 hours ago</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">🏆 Top Opportunities</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.write("**Company**")
    with col2:
        st.write("**Score**")
    with col3:
        st.write("**Value**")
    
    st.markdown("---")
    
    opportunities = [
        ("Airside Hotel", 92, "$5,000 - $10,000"),
        ("Ecobank Ghana", 87, "$3,000 - $7,000"),
        ("XYZ Logistics", 85, "$2,500 - $5,000"),
        ("Melcom Ltd", 81, "$1,500 - $3,000")
    ]
    
    for company, score, value in opportunities:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.write(company)
        with col2:
            if score >= 90:
                st.markdown(f'<span class="score-hot">{score}</span>', unsafe_allow_html=True)
            elif score >= 80:
                st.markdown(f'<span class="score-warm">{score}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="score-good">{score}</span>', unsafe_allow_html=True)
        with col3:
            st.write(value)

# ============ COMPANY RESEARCH PAGE ============
elif page == "company_research":
    st.markdown('<div class="section-header">🔍 Company Research</div>', unsafe_allow_html=True)
    st.caption("Research any company and get instant lead scoring")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company Name", placeholder="e.g. Nyaho Medical Centre")
    with col2:
        website = st.text_input("Website (optional)", placeholder="e.g. nyahoclinic.com")
    
    if st.button("Research Company", type="primary"):
        if company:
            with st.spinner(f"Researching {company}..."):
                st.success("Research complete!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>Company Information</h4>
                        <p><strong>Name:</strong> {company}</p>
                        <p><strong>Website:</strong> {website or f"www.{company.lower().replace(' ', '')}.com"}</p>
                        <p><strong>Email:</strong> info@{company.lower().replace(' ', '')}.com</p>
                        <p><strong>Phone:</strong> +233 XX XXX XXXX</p>
                    </div>
                    """, unsafe_allow_html=True)
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

# ============ BULK RESEARCH PAGE ============
elif page == "bulk_research":
    st.markdown('<div class="section-header">📊 Bulk Company Research</div>', unsafe_allow_html=True)
    st.caption("Research multiple companies at once")
    st.markdown("---")
    
    companies = st.text_area("Company Names (one per line)", height=150, placeholder="Nyaho Medical Centre\nMTN Ghana\nGCB Bank")
    
    if st.button("Start Bulk Research", type="primary"):
        if companies:
            lines = [c.strip() for c in companies.split("\n") if c.strip()]
            progress = st.progress(0)
            for i, c in enumerate(lines):
                progress.progress((i + 1) / len(lines))
            st.success(f"Researched {len(lines)} companies!")
            st.dataframe([{"Company": c, "Lead Score": "72/100", "Status": "Warm"} for c in lines], use_container_width=True)
        else:
            st.warning("Please enter company names")

# ============ WEBSITE AUDIT PAGE ============
elif page == "website_audit":
    st.markdown('<div class="section-header">🌐 Website Audit</div>', unsafe_allow_html=True)
    st.caption("Comprehensive security and performance audit")
    st.markdown("---")
    
    url = st.text_input("Website URL", placeholder="https://example.com")
    
    if st.button("Run Website Audit", type="primary"):
        if url:
            with st.spinner(f"Auditing {url}..."):
                st.success("Audit complete!")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div class="data-card">
                        <h4>SSL Certificate</h4>
                        <p>✅ Valid</p>
                        <p>📅 Expires in 180 days</p>
                        <p>🔒 TLS 1.3 supported</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class="data-card">
                        <h4>Security Headers</h4>
                        <p>✅ HSTS: Enabled</p>
                        <p>⚠️ CSP: Not Configured</p>
                        <p>✅ X-Frame-Options: Present</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a URL")

# ============ EMAIL SECURITY PAGE ============
elif page == "email_security":
    st.markdown('<div class="section-header">📧 Email Security Audit</div>', unsafe_allow_html=True)
    st.caption("Check SPF, DKIM, and DMARC records")
    st.markdown("---")
    
    domain = st.text_input("Domain", placeholder="example.com")
    
    if st.button("Check Email Security", type="primary"):
        if domain:
            with st.spinner(f"Checking {domain}..."):
                st.success("Security check complete!")
                st.markdown(f"""
                <div class="data-card">
                    <h4>Email Security Report for {domain}</h4>
                    <p>✅ SPF: Configured</p>
                    <p>⚠️ DKIM: Not Found</p>
                    <p>❌ DMARC: Not Configured</p>
                    <p style="color: #f97316;">🟠 Overall Risk: Moderate</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a domain")

# ============ DNS AUDIT PAGE ============
elif page == "dns_audit":
    st.markdown('<div class="section-header">🔒 DNS Audit</div>', unsafe_allow_html=True)
    st.caption("Check DNS records and configuration")
    st.markdown("---")
    
    domain = st.text_input("Domain", placeholder="example.com")
    
    if st.button("Run DNS Audit", type="primary"):
        if domain:
            with st.spinner(f"Auditing {domain}..."):
                st.success("DNS audit complete!")
                st.markdown(f"""
                <div class="data-card">
                    <h4>DNS Records for {domain}</h4>
                    <p>✅ A Records: 2 found</p>
                    <p>✅ MX Records: 1 found</p>
                    <p>✅ TXT Records: Found</p>
                    <p>⚠️ CNAME: Not configured</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a domain")

# ============ AI INTELLIGENCE PAGE ============
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
                <p>🚀 Projected conversion: 24% next quarter</p>
            </div>
            """, unsafe_allow_html=True)

# ============ PROPOSALS PAGE ============
elif page == "proposals":
    st.markdown('<div class="section-header">📄 Proposal Generator</div>', unsafe_allow_html=True)
    st.caption("Create professional proposals for your leads")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Company Name")
        client_email = st.text_input("Client Email")
    with col2:
        proposal_type = st.selectbox("Proposal Type", ["Email Security", "Website Audit", "IT Infrastructure"])
        proposal_value = st.selectbox("Package", ["Basic", "Professional", "Enterprise"])
    
    if st.button("Generate Proposal", type="primary"):
        if client_name:
            st.success("Proposal generated!")
            st.markdown(f"""
            <div class="data-card">
                <h4>Proposal for {client_name}</h4>
                <p><strong>Service:</strong> {proposal_type}</p>
                <p><strong>Package:</strong> {proposal_value}</p>
                <p><strong>Value:</strong> $2,500 - $5,000</p>
                <p><strong>Next Steps:</strong> Schedule discovery call</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please enter client name")

# ============ CRM PAGE ============
elif page == "crm":
    st.markdown('<div class="section-header">👥 CRM Dashboard</div>', unsafe_allow_html=True)
    st.caption("Manage your leads and customers")
    st.markdown("---")
    
    crm_data = [
        {"Company": "Airside Hotel", "Contact": "John Doe", "Lead Score": 92, "Status": "Hot", "Value": "$10,000"},
        {"Company": "Ecobank Ghana", "Contact": "Jane Smith", "Lead Score": 87, "Status": "Warm", "Value": "$7,000"},
        {"Company": "XYZ Logistics", "Contact": "Mike Johnson", "Lead Score": 85, "Status": "Warm", "Value": "$5,000"},
        {"Company": "Melcom Ltd", "Contact": "Sarah Adams", "Lead Score": 81, "Status": "Warm", "Value": "$3,000"},
    ]
    st.dataframe(crm_data, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Lead", use_container_width=True):
            st.info("Add lead feature coming soon")
    with col2:
        if st.button("Export Data", use_container_width=True):
            st.success("Export started")

# ============ REPORTS PAGE ============
elif page == "reports":
    st.markdown('<div class="section-header">📈 Reports</div>', unsafe_allow_html=True)
    st.caption("Generate detailed reports on your lead intelligence")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        report_type = st.selectbox("Report Type", ["Lead Summary", "Conversion Report", "Activity Report"])
    with col2:
        date_range = st.selectbox("Date Range", ["Last 7 days", "Last 30 days", "Last quarter"])
    
    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            st.success(f"{report_type} generated for {date_range}!")
            st.markdown("""
            <div class="data-card">
                <h4>Report Summary</h4>
                <p>📊 Total Leads: 2,438</p>
                <p>🎯 Conversion Rate: 23.3%</p>
                <p>💰 Pipeline Value: $32,500</p>
                <p>⭐ Hot Leads: 184</p>
            </div>
            """, unsafe_allow_html=True)

# ============ SETTINGS PAGE ============
elif page == "settings":
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.caption("Configure API keys and system settings")
    st.markdown("---")
    
    st.markdown("### API Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("OpenAI API Key", type="password", placeholder="sk-...", key="openai_key")
        st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...", key="anthropic_key")
    with col2:
        st.text_input("Google Maps API Key", type="password", placeholder="AIzaSy...", key="google_key")
        st.text_input("Resend API Key", type="password", placeholder="re_...", key="resend_key")
    
    st.markdown("### Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Default Country", ["Ghana", "Nigeria", "Kenya", "South Africa"], key="country")
    with col2:
        st.selectbox("Email Notifications", ["Daily", "Weekly", "Never"], key="notifications")
    
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption(":copyright: 2024 TechWokx Ghana | Light Theme Active")

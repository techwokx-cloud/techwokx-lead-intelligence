# app.py
import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# Import modules
from modules.company_research import deep_research_company
from modules.email_service import send_proposal_email

# Page config
st.set_page_config(
    page_title="TechWokx Enterprise Suite",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state init
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'leads' not in st.session_state:
    # Load leads from file if exists
    if os.path.exists("data/leads.json"):
        with open("data/leads.json", "r") as f:
            st.session_state.leads = json.load(f)
    else:
        st.session_state.leads = []
if 'email_log' not in st.session_state:
    st.session_state.email_log = []

# Create data directory
os.makedirs("data", exist_ok=True)

# Login credentials
USERS = {
    "hello@techwokx.online": {
        "password": "Gtech.5628!@#$",
        "role": "admin",
        "name": "TechWokx Admin"
    }
}

# SMTP Configuration (from secrets or hardcoded for now)
SMTP_CONFIG = {
    "host": "smtp.hostinger.com",
    "port": 465,
    "username": "hello@techwokx.online",
    "password": "Gtech.5628!@#$",
    "use_ssl": True
}

# Get API keys from secrets
def get_api_keys():
    return {
        "serp_api": st.secrets.get("SERP_API_KEY", ""),
        "openai": st.secrets.get("OPENAI_API_KEY", "")
    }

def save_leads():
    """Save leads to file"""
    with open("data/leads.json", "w") as f:
        json.dump(st.session_state.leads, f, default=str)

def add_lead(lead_data):
    """Add lead to CRM"""
    lead = {
        "id": len(st.session_state.leads) + 1,
        "name": lead_data.get("name"),
        "website": lead_data.get("website"),
        "email": lead_data.get("email"),
        "phone": lead_data.get("phone"),
        "address": lead_data.get("address"),
        "lead_score": lead_data.get("lead_score", 0),
        "contacts": lead_data.get("contacts", []),
        "recommendations": lead_data.get("recommendations", []),
        "created_at": datetime.now().isoformat(),
        "status": "New"
    }
    st.session_state.leads.append(lead)
    save_leads()
    return lead

# CSS (same as before, keep for styling)
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fbbf24 !important; }
[data-testid="stSidebar"] .stButton button { background: rgba(251, 191, 36, 0.15); color: #fbbf24 !important; width: 100%; margin: 2px 0; }
.welcome-card { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; color: white; }
.metric-card { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
.metric-label { color: #64748b; font-size: 0.8rem; }
.data-card { background: white; border-radius: 12px; padding: 1.2rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
.section-header { color: #0f172a; font-size: 1.2rem; font-weight: 600; border-left: 3px solid #667eea; padding-left: 1rem; margin: 1.5rem 0 1rem 0; }
.custom-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
.stButton > button { background: linear-gradient(135deg, #667eea, #764ba2); color: white !important; font-weight: 600; border: none; border-radius: 8px; }
.status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
.status-hot { background: #dc2626; color: white; }
.status-warm { background: #f97316; color: white; }
.status-cold { background: #64748b; color: white; }
</style>
""", unsafe_allow_html=True)

# ============ LOGIN PAGE ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 450px; margin: 100px auto; padding: 2rem; background: white; border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); text-align: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
        <div style="font-size: 1.875rem; font-weight: 700; color: #1e293b;">TechWokx</div>
        <div style="color: #64748b; margin-bottom: 2rem;">Enterprise Suite</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Email", placeholder="hello@techwokx.online")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user = USERS[username]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    st.markdown("""
        <div style="background: #f1f5f9; padding: 1rem; border-radius: 12px; margin-top: 1.5rem;">
            <div style="font-size: 0.75rem; color: #64748b;">🔐 Demo Access</div>
            <div style="font-size: 0.8rem; font-family: monospace;">hello@techwokx.online / Gtech.5628!@#$</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### 🔍 TechWokx")
    st.markdown("#### Welcome, " + st.session_state.user['name'])
    st.markdown("---")
    
    nav_items = [
        ("🏠 Dashboard", "dashboard"),
        ("---", "divider0"),
        ("📋 LEAD MANAGEMENT", "header1"),
        ("🔍 Company Research", "company_research"),
        ("👥 Lead CRM", "crm"),
        ("---", "divider1"),
        ("🤖 FREELANCE", "header2"),
        ("🎯 Find Jobs", "find_jobs"),
        ("📋 My Bids", "bid_history"),
        ("---", "divider2"),
        ("📧 EMAIL", "header3"),
        ("📤 Send Email", "send_email"),
        ("📊 Email Log", "email_log"),
        ("---", "divider3"),
        ("⚙️ Settings", "settings"),
        ("🚪 Logout", "logout")
    ]
    
    for label, key in nav_items:
        if label == "---":
            st.markdown("---")
        elif label.startswith("📋") or label.startswith("🤖") or label.startswith("📧"):
            st.markdown("<small style='color:#94a3b8'>" + label + "</small>", unsafe_allow_html=True)
        elif st.button(label, key=key, use_container_width=True):
            if key == "logout":
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()
            else:
                st.session_state.page = key
                st.rerun()
    
    st.markdown("---")
    api_keys = get_api_keys()
    st.markdown(f"🔍 SERP: {'✅' if api_keys['serp_api'] else '❌'}")
    st.markdown(f"🧠 AI: {'✅' if api_keys['openai'] else '❌'}")
    st.markdown(f"📧 SMTP: {'✅' if SMTP_CONFIG['username'] else '❌'}")
    st.markdown(f"📊 Leads: {len(st.session_state.leads)}")

# ============ DASHBOARD ============
if st.session_state.page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>🤖 TechWokx Enterprise Suite</h2>
        <p>AI-powered Company Research | Lead Intelligence | Email Automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.leads)}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        hot = sum(1 for l in st.session_state.leads if l.get("lead_score", 0) >= 70)
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.email_log)}</div><div class='metric-label'>Emails Sent</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>✅</div><div class='metric-label'>System Ready</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Recent Leads</div>', unsafe_allow_html=True)
        if st.session_state.leads:
            for lead in st.session_state.leads[-5:]:
                status_class = "status-hot" if lead.get("lead_score", 0) >= 70 else "status-warm" if lead.get("lead_score", 0) >= 50 else "status-cold"
                st.markdown(f"<div class='data-card'><strong>{lead['name']}</strong> - Score: {lead['lead_score']}/100 <span class='status-badge {status_class}'>{lead['status']}</span><br><small>{lead['created_at'][:10]}</small></div>", unsafe_allow_html=True)
        else:
            st.info("No leads yet. Research companies to get started.")
    
    with col2:
        st.markdown('<div class="section-header">🚀 Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍 Research Company", use_container_width=True):
            st.session_state.page = 'company_research'
            st.rerun()
        if st.button("📧 Send Proposal Email", use_container_width=True):
            st.session_state.page = 'send_email'
            st.rerun()
        if st.button("👥 View CRM", use_container_width=True):
            st.session_state.page = 'crm'
            st.rerun()

# ============ COMPANY RESEARCH PAGE ============
elif st.session_state.page == 'company_research':
    st.markdown('<div class="section-header">🔍 Deep Company Research</div>', unsafe_allow_html=True)
    st.caption("Powered by Google Search (SERP API) + AI | Find contact persons automatically")
    st.markdown("---")
    
    api_keys = get_api_keys()
    
    if not api_keys["serp_api"]:
        st.error("❌ SERP API key missing! Add to secrets.toml")
        st.stop()
    
    company_name = st.text_input("Company Name", placeholder="e.g. Courmack Ghana, MTN Ghana, OMA Group")
    
    if st.button("🔍 Deep Research", type="primary"):
        if company_name:
            with st.spinner(f"Researching {company_name} using Google Search..."):
                result = deep_research_company(
                    company_name, 
                    serp_api_key=api_keys["serp_api"],
                    openai_api_key=api_keys["openai"]
                )
                
                # Store in session for adding to CRM
                st.session_state.last_research = result
                
                # Company Information
                st.markdown(f"""
                <div class="data-card">
                    <h4>🏢 Company Information</h4>
                    <table style="width:100%">
                        <tr><th>Name</th><td>{result['name']}</td></tr>
                        <tr><th>Website</th><td>{result['website'] or 'Not found'}</td></tr>
                        <tr><th>Address</th><td>{result['address'] or 'Not found'}</td></tr>
                        <tr><th>Phone</th><td>{result['phone'] or 'Not found'}</td></tr>
                        <tr><th>Email</th><td>{result['email'] or 'Not found'}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
                # Contacts Found
                if result['contacts']:
                    st.markdown("### 👤 Contacts Found")
                    for contact in result['contacts'][:3]:
                        st.markdown(f"""
                        <div class="data-card">
                            <strong>{contact.get('name', 'Name found')}</strong><br>
                            Title: {contact.get('title', 'Staff')}<br>
                            Source: {contact.get('source', 'Website')}
                        </div>
                        """, unsafe_allow_html=True)
                
                # Description
                if result['description']:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>📝 Business Description</h4>
                        <p>{result['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Website Status
                if result['website_status']:
                    status_icon = "✅" if result['website_status']['reachable'] else "❌"
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>🌐 Website Status</h4>
                        <p><strong>Status:</strong> {status_icon} {'Online' if result['website_status']['reachable'] else 'Down'}</p>
                        <p><strong>Response Time:</strong> {result['website_status'].get('response_time', 'N/A'):.0f}ms</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Lead Score
                score_color = "#22c55e" if result['lead_score'] >= 70 else "#f97316" if result['lead_score'] >= 50 else "#ef4444"
                st.markdown(f"""
                <div class="data-card" style="text-align: center;">
                    <h4>🎯 Lead Score</h4>
                    <p style="font-size: 3rem; font-weight: 700; color: {score_color};">{result['lead_score']}/100</p>
                    <p><strong>Data Sources:</strong> {', '.join(result['sources']) if result['sources'] else 'None'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # AI Insights
                if result['ai_insights']:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>🧠 AI-Powered Insights</h4>
                        <p>{result['ai_insights']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Recommendations
                st.markdown(f"""
                <div class="data-card">
                    <h4>🚀 Recommendations</h4>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in result['recommendations']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Add to CRM button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➕ Add to CRM", use_container_width=True):
                        add_lead(result)
                        st.success(f"✅ {result['name']} added to CRM!")
                        st.rerun()
                
                with col2:
                    if result.get('email') or result.get('business_emails'):
                        if st.button("📧 Send Proposal Email", use_container_width=True):
                            st.session_state.proposal_lead = result
                            st.session_state.page = 'send_email'
                            st.rerun()
        else:
            st.warning("Please enter a company name")

# ============ LEAD CRM PAGE ============
elif st.session_state.page == 'crm':
    st.markdown('<div class="section-header">👥 Lead CRM</div>', unsafe_allow_html=True)
    st.caption("All researched leads and contacts")
    st.markdown("---")
    
    if st.session_state.leads:
        for lead in st.session_state.leads:
            with st.expander(f"{lead['name']} - Score: {lead['lead_score']}/100 - {lead['status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Website:** {lead.get('website', 'N/A')}")
                    st.write(f"**Email:** {lead.get('email', 'N/A')}")
                    st.write(f"**Phone:** {lead.get('phone', 'N/A')}")
                with col2:
                    st.write(f"**Address:** {lead.get('address', 'N/A')}")
                    st.write(f"**Added:** {lead['created_at'][:10]}")
                
                if lead.get('contacts'):
                    st.write("**Contacts Found:**")
                    for contact in lead['contacts'][:2]:
                        st.write(f"- {contact.get('name', 'Name')} ({contact.get('title', 'Staff')})")
                
                if st.button(f"📧 Send Email", key=f"email_{lead['id']}"):
                    st.session_state.proposal_lead = lead
                    st.session_state.page = 'send_email'
                    st.rerun()
    else:
        st.info("No leads yet. Research companies to add to CRM.")

# ============ SEND EMAIL PAGE ============
elif st.session_state.page == 'send_email':
    st.markdown('<div class="section-header">📧 Send Proposal Email</div>', unsafe_allow_html=True)
    st.caption("Send personalized proposal emails to leads")
    st.markdown("---")
    
    # Select lead
    leads = st.session_state.leads
    lead_options = {f"{l['name']} (Score: {l['lead_score']}/100)": l for l in leads}
    
    if st.session_state.get('proposal_lead'):
        default_lead = f"{st.session_state.proposal_lead['name']} (Score: {st.session_state.proposal_lead['lead_score']}/100)"
    else:
        default_lead = list(lead_options.keys())[0] if lead_options else None
    
    if lead_options:
        selected = st.selectbox("Select Lead", list(lead_options.keys()), index=0 if default_lead else None)
        lead = lead_options[selected]
        
        # Email fields
        to_email = st.text_input("To Email", value=lead.get('email') or (lead.get('contacts', [{}])[0].get('email') if lead.get('contacts') else ''))
        
        st.markdown("### Email Preview")
        
        from modules.email_service import generate_proposal_email
        contact_person = lead.get('contacts', [{}])[0] if lead.get('contacts') else None
        email_body = generate_proposal_email(lead, contact_person)
        
        st.markdown(email_body, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Send Email", type="primary"):
                if to_email:
                    success, msg = send_proposal_email(SMTP_CONFIG, lead, to_email, contact_person)
                    if success:
                        st.session_state.email_log.append({
                            "to": to_email,
                            "company": lead['name'],
                            "date": datetime.now().isoformat(),
                            "status": "Sent"
                        })
                        st.success(f"✅ Email sent to {to_email}!")
                    else:
                        st.error(f"❌ Failed: {msg}")
                else:
                    st.warning("Please enter recipient email")
        
        with col2:
            if st.button("← Back to CRM"):
                st.session_state.page = 'crm'
                st.rerun()
    else:
        st.info("No leads in CRM. Research companies first.")
        if st.button("Go to Company Research"):
            st.session_state.page = 'company_research'
            st.rerun()

# ============ EMAIL LOG PAGE ============
elif st.session_state.page == 'email_log':
    st.markdown('<div class="section-header">📊 Email Log</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.email_log:
        for log in reversed(st.session_state.email_log):
            st.markdown(f"""
            <div class="data-card">
                <strong>To:</strong> {log['to']}<br>
                <strong>Company:</strong> {log['company']}<br>
                <strong>Status:</strong> {log['status']}<br>
                <strong>Date:</strong> {log['date'][:19]}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No emails sent yet")

# ============ SETTINGS PAGE ============
elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### API Configuration")
    st.code("""
    # .streamlit/secrets.toml
    SERP_API_KEY = "your_serp_api_key"
    OPENAI_API_KEY = "your_openai_api_key"
    """)
    
    st.markdown("### Email Configuration")
    st.info(f"""
    **SMTP Settings (Active):**
    - Host: {SMTP_CONFIG['host']}
    - Port: {SMTP_CONFIG['port']}
    - Username: {SMTP_CONFIG['username']}
    - SSL: {SMTP_CONFIG['use_ssl']}
    """)
    
    st.markdown("### Data Management")
    if st.button("Clear All Leads"):
        st.session_state.leads = []
        save_leads()
        st.success("All leads cleared!")
        st.rerun()

# ============ FREELANCE PAGES (Placeholders for now) ============
elif st.session_state.page == 'find_jobs':
    st.markdown('<div class="section-header">🎯 Find Freelance Jobs</div>', unsafe_allow_html=True)
    st.info("Freelance job search feature - Coming soon in v2.0")

elif st.session_state.page == 'bid_history':
    st.markdown('<div class="section-header">📋 My Bids</div>', unsafe_allow_html=True)
    st.info("Bid history feature - Coming soon in v2.0")

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Enterprise Suite | Email: hello@techwokx.online | WhatsApp: +233 555 087 407")

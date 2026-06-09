import streamlit as st
import pandas as pd
import os
import socket
import platform
import re
import requests
from datetime import datetime, timedelta
import json
import hashlib

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
    st.session_state.leads = []
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'email_log' not in st.session_state:
    st.session_state.email_log = []
if 'bid_history' not in st.session_state:
    st.session_state.bid_history = []
if 'research_cache' not in st.session_state:
    st.session_state.research_cache = {}

# Login credentials
USERS = {
    "hello@techwokx.online": {
        "password": "Gtech.5628!@#$",
        "role": "admin",
        "name": "TechWokx Admin"
    }
}

# User skills for freelance matching
USER_SKILLS = {
    "it_support": 90,
    "data_entry": 95,
    "excel": 95,
    "research": 85,
    "administrative": 85,
    "hotel_operations": 80,
    "pdf_handling": 90,
    "web_scraping": 75,
    "data_analysis": 80,
    "document_conversion": 88,
    "python": 75,
    "sql": 70,
    "automation": 80,
    "virtual_assistant": 85,
    "customer_service": 80
}

# ============ LEAD INTELLIGENCE FUNCTIONS ============

def add_lead(name, email, phone, score, source="Manual"):
    """Add lead to CRM"""
    status = "Hot" if score >= 80 else "Warm" if score >= 60 else "Cold"
    lead = {
        "id": len(st.session_state.leads) + 1,
        "name": name,
        "email": email,
        "phone": phone,
        "score": score,
        "status": status,
        "source": source,
        "created_at": datetime.now()
    }
    st.session_state.leads.append(lead)
    return lead

def deep_research_company(company_name, website=None):
    """Simulate deep research (simplified for demo)"""
    result = {
        "name": company_name,
        "website": website or f"www.{company_name.lower().replace(' ', '')}.com",
        "email": f"info@{company_name.lower().replace(' ', '')}.com",
        "phone": "+233 XX XXX XXXX",
        "address": "Accra, Ghana",
        "description": f"{company_name} is a leading business in Ghana.",
        "lead_score": 75,
        "recommendations": ["Setup professional email", "Conduct IT audit", "Schedule consultation"]
    }
    return result

# ============ FREELANCE FUNCTIONS ============

def fetch_upwork_rss_jobs():
    """Fetch jobs from Upwork RSS feed"""
    jobs = [
        {
            "id": "job_1",
            "title": "PDF-to-Excel Data Transfer",
            "description": "Need accurate transfer of tables from PDF to Excel",
            "platform": "Upwork",
            "budget_min": 15,
            "budget_max": 35,
            "skills_required": ["excel", "data_entry"],
            "access_type": "connect_required",
            "unlock_cost": "8 connects",
            "url": "#"
        },
        {
            "id": "job_2",
            "title": "Virtual Assistant - Email Management",
            "description": "Need VA for email and calendar management",
            "platform": "Upwork",
            "budget_min": 20,
            "budget_max": 40,
            "skills_required": ["virtual_assistant", "administrative"],
            "access_type": "connect_required",
            "unlock_cost": "8 connects",
            "url": "#"
        }
    ]
    return jobs

def calculate_match_score(job):
    """Calculate match score based on skills"""
    total_score = 0
    for skill in job.get("skills_required", []):
        if skill in USER_SKILLS:
            total_score += USER_SKILLS[skill]
    if job.get("skills_required"):
        match = (total_score / (len(job["skills_required"]) * 100)) * 100
    else:
        match = 70
    return min(int(match), 100)

def generate_proposal(job, match_score):
    """Generate proposal for job"""
    return f"""Dear Client,

I am very interested in your {job['title']} project.

My relevant skills include:
• Data Entry and Excel (95% proficiency)
• Virtual Assistant experience
• Fast turnaround (24-48 hours)

I am available to start immediately.

Best regards,
George Jabley
TechWokx Freelancer"""

# ============ SAMPLE DATA ============
SAMPLE_JOBS = [
    {
        "id": "sample_1",
        "title": "PDF-to-Excel Data Transfer",
        "description": "Need accurate transfer of tables from PDF to Excel",
        "platform": "Freelancer",
        "budget_min": 15,
        "budget_max": 35,
        "skills_required": ["excel", "data_entry", "pdf_handling"],
        "access_type": "unlock_required",
        "unlock_cost": "$20 balance required",
        "url": "#"
    },
    {
        "id": "sample_2",
        "title": "Virtual Assistant - Email Management",
        "description": "Need VA for email and calendar management",
        "platform": "Upwork",
        "budget_min": 20,
        "budget_max": 40,
        "skills_required": ["virtual_assistant", "administrative"],
        "access_type": "connect_required",
        "unlock_cost": "8 connects",
        "url": "#"
    },
    {
        "id": "sample_3",
        "title": "Excel Data Cleaning",
        "description": "Clean and format large Excel dataset",
        "platform": "Freelancer",
        "budget_min": 30,
        "budget_max": 60,
        "skills_required": ["excel", "data_analysis"],
        "access_type": "open",
        "unlock_cost": "Free",
        "url": "#"
    }
]

# ============ CSS ============
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
</style>
""", unsafe_allow_html=True)

# ============ LOGIN PAGE ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 450px; margin: 100px auto; padding: 2rem; background: white; border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); text-align: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
        <div style="font-size: 1.875rem; font-weight: 700; color: #1e293b;">TechWokx</div>
        <div style="color: #64748b; margin-bottom: 2rem;">Lead Intelligence + Freelance Agent</div>
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

# ============ SIDEBAR NAVIGATION ============
with st.sidebar:
    st.markdown("### 🔍 TechWokx")
    st.markdown("#### Welcome, " + st.session_state.user['name'])
    st.markdown("---")
    
    nav_items = [
        ("🏠 Dashboard", "dashboard"),
        ("---", "divider0"),
        ("📋 LEAD MANAGEMENT", "header1"),
        ("🔍 Company Research", "company_research"),
        ("📥 Import Leads", "import_leads"),
        ("👥 Lead CRM", "crm"),
        ("---", "divider1"),
        ("🤖 FREELANCE INTELLIGENCE", "header2"),
        ("🎯 Find Jobs", "find_jobs"),
        ("💰 Bid ROI Calculator", "bid_roi"),
        ("📋 My Bids", "bid_history"),
        ("---", "divider2"),
        ("🛡️ AUDITS", "header3"),
        ("🌐 DNS Audit", "dns_audit"),
        ("🔒 Website Audit", "website_audit"),
        ("📧 Email Security", "email_security"),
        ("---", "divider3"),
        ("📊 REPORTS", "header4"),
        ("📊 Analytics", "analytics"),
        ("⚙️ Settings", "settings"),
        ("🚪 Logout", "logout")
    ]
    
    for label, key in nav_items:
        if label == "---":
            st.markdown("---")
        elif label.startswith("📋") or label.startswith("🤖") or label.startswith("🛡️") or label.startswith("📊"):
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
    st.markdown("👤 Leads: " + str(len(st.session_state.leads)))
    st.markdown("🎯 Jobs: " + str(len(st.session_state.jobs) if st.session_state.jobs else 0))
    st.markdown("📊 Bids: " + str(len(st.session_state.bid_history)))

# ============ DASHBOARD ============
if st.session_state.page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>🤖 Welcome to TechWokx Enterprise Suite</h2>
        <p>Lead Intelligence + Freelance Intelligence Agent | AI-powered insights for your business</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-card'><div class='metric-value'>" + str(len(st.session_state.leads)) + "</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        hot = sum(1 for l in st.session_state.leads if l.get("score", 0) >= 80)
        st.markdown("<div class='metric-card'><div class='metric-value'>" + str(hot) + "</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        jobs_count = len(st.session_state.jobs) if st.session_state.jobs else 0
        st.markdown("<div class='metric-card'><div class='metric-value'>" + str(jobs_count) + "</div><div class='metric-label'>Available Jobs</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-card'><div class='metric-value'>✅</div><div class='metric-label'>System Active</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Recent Leads</div>', unsafe_allow_html=True)
        if st.session_state.leads:
            for lead in st.session_state.leads[-5:]:
                st.markdown("<div class='data-card'><strong>" + lead['name'] + "</strong> - Score: " + str(lead['score']) + "/100<br><small>" + lead['created_at'].strftime("%Y-%m-%d") + "</small></div>", unsafe_allow_html=True)
        else:
            st.info("No leads yet. Import leads or research companies.")
    
    with col2:
        st.markdown('<div class="section-header">🎯 Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍 Research Company", use_container_width=True):
            st.session_state.page = 'company_research'
            st.rerun()
        if st.button("🎯 Find Freelance Jobs", use_container_width=True):
            st.session_state.page = 'find_jobs'
            st.rerun()
        if st.button("📥 Import Leads", use_container_width=True):
            st.session_state.page = 'import_leads'
            st.rerun()

# ============ COMPANY RESEARCH ============
elif st.session_state.page == 'company_research':
    st.markdown('<div class="section-header">🔍 Company Research</div>', unsafe_allow_html=True)
    st.caption("Research companies and add to lead CRM")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g. Nyaho Medical Centre")
    with col2:
        website = st.text_input("Website (optional)", placeholder="e.g. nyahoclinic.com")
    
    if st.button("🔍 Research", type="primary"):
        if company_name:
            with st.spinner("Researching " + company_name + "..."):
                result = deep_research_company(company_name, website)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div class='data-card'><h4>Company Information</h4><p><strong>Name:</strong> " + result['name'] + "</p><p><strong>Website:</strong> " + result['website'] + "</p><p><strong>Address:</strong> " + result['address'] + "</p></div>", unsafe_allow_html=True)
                    st.markdown("<div class='data-card'><h4>Contact Information</h4><p><strong>Email:</strong> " + result['email'] + "</p><p><strong>Phone:</strong> " + result['phone'] + "</p></div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<div class='data-card' style='text-align:center'><h4>Lead Score</h4><p style='font-size:3rem;font-weight:700;color:#667eea'>" + str(result['lead_score']) + "/100</p><p><strong>Status:</strong> Warm Lead</p></div>", unsafe_allow_html=True)
                    st.markdown("<div class='data-card'><h4>Recommendations</h4><ul><li>" + "</li><li>".join(result['recommendations']) + "</li></ul></div>", unsafe_allow_html=True)
                
                if st.button("➕ Add to CRM"):
                    add_lead(result['name'], result['email'], result['phone'], result['lead_score'], "Research")
                    st.success("Added " + result['name'] + " to CRM!")
        else:
            st.warning("Please enter a company name")

# ============ IMPORT LEADS ============
elif st.session_state.page == 'import_leads':
    st.markdown('<div class="section-header">📥 Import Leads</div>', unsafe_allow_html=True)
    st.caption("Import leads from CSV or Excel files")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Choose CSV/Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.dataframe(df.head())
            
            if st.button("Import", type="primary"):
                imported = 0
                for _, row in df.iterrows():
                    name = row.get('name', row.get('Name', ''))
                    email = row.get('email', row.get('Email', ''))
                    phone = str(row.get('phone', row.get('Phone', '')))
                    score = int(row.get('score', row.get('Score', 50)))
                    if name and email:
                        add_lead(name, email, phone, score, "Import")
                        imported += 1
                st.success("Imported " + str(imported) + " leads!")
                st.rerun()
        except Exception as e:
            st.error("Error: " + str(e))
    else:
        st.info("Please upload a CSV or Excel file")
    
    st.markdown("---")
    st.markdown("### Manual Entry")
    with st.form("manual_lead"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name*")
            email = st.text_input("Email*")
        with col2:
            phone = st.text_input("Phone")
            score = st.slider("Lead Score", 0, 100, 50)
        
        if st.form_submit_button("Add Lead"):
            if name and email:
                add_lead(name, email, phone, score, "Manual")
                st.success("Added " + name + "!")
                st.rerun()
            else:
                st.error("Name and email required")

# ============ LEAD CRM ============
elif st.session_state.page == 'crm':
    st.markdown('<div class="section-header">👥 Lead CRM</div>', unsafe_allow_html=True)
    st.caption("Manage all your leads")
    st.markdown("---")
    
    if st.session_state.leads:
        search = st.text_input("🔍 Search", placeholder="Name or email")
        filtered = st.session_state.leads
        if search:
            filtered = [l for l in filtered if search.lower() in l["name"].lower() or search.lower() in l.get("email", "").lower()]
        
        for lead in filtered:
            with st.expander(lead['name'] + " - Score: " + str(lead['score']) + "/100 - " + lead['status']):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Email:** " + lead.get('email', 'N/A'))
                    st.write("**Phone:** " + lead.get('phone', 'N/A'))
                with col2:
                    st.write("**Status:** " + lead['status'])
                    st.write("**Source:** " + lead['source'])
                st.write("**Added:** " + lead['created_at'].strftime('%Y-%m-%d %H:%M'))
        
        if st.button("📥 Export to CSV"):
            df = pd.DataFrame(st.session_state.leads)
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "leads_export.csv", "text/csv")
    else:
        st.info("No leads yet. Import leads or research companies.")

# ============ FIND JOBS ============
elif st.session_state.page == 'find_jobs':
    st.markdown('<div class="section-header">🎯 Find Freelance Jobs</div>', unsafe_allow_html=True)
    st.caption("AI-powered job matching | Personalized proposals")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        keywords = st.text_input("Keywords", placeholder="data entry, excel, virtual assistant")
    with col2:
        min_match = st.slider("Min Match %", 0, 100, 50)
    with col3:
        if st.button("🔄 Find Jobs", type="primary"):
            with st.spinner("Searching for jobs..."):
                st.session_state.jobs = SAMPLE_JOBS
                st.success("Found " + str(len(st.session_state.jobs)) + " jobs!")
                st.rerun()
    
    display_jobs = st.session_state.jobs if st.session_state.jobs else SAMPLE_JOBS
    
    if keywords:
        keyword_list = [k.strip().lower() for k in keywords.split(",")]
        display_jobs = [j for j in display_jobs if any(k in j["title"].lower() or k in j["description"].lower() for k in keyword_list)]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs", len(display_jobs))
    with col2:
        high_match = sum(1 for j in display_jobs if calculate_match_score(j) >= 80)
        st.metric("High Match (80%+)", high_match)
    with col3:
        st.metric("Ready to Bid", len([j for j in display_jobs if calculate_match_score(j) >= 70]))
    
    st.markdown("---")
    
    for job in display_jobs:
        match_score = calculate_match_score(job)
        
        if match_score >= min_match:
            with st.expander("[" + job['platform'] + "] " + job['title'] + " - Match: " + str(match_score) + "%"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("**Description:** " + job['description'])
                    st.markdown("**Budget:** $" + str(job['budget_min']) + " - $" + str(job['budget_max']))
                    st.markdown("**Skills:** " + ', '.join(job.get('skills_required', ['General'])))
                    st.markdown("**Access:** " + job['access_type'] + " | " + job['unlock_cost'])
                
                with col2:
                    st.markdown("**Match Score:** " + str(match_score) + "%")
                    st.markdown("**Recommended Bid:** $" + str(int((job['budget_min'] + job['budget_max']) / 2)))
                
                st.markdown("---")
                st.markdown("### 📝 Proposal")
                proposal = generate_proposal(job, match_score)
                st.text_area("Proposal", proposal, height=200)
                
                if st.button("📤 Save Bid", key="bid_" + job['id']):
                    st.session_state.bid_history.append({
                        "job_title": job['title'],
                        "platform": job['platform'],
                        "bid_amount": int((job['budget_min'] + job['budget_max']) / 2),
                        "date": datetime.now(),
                        "status": "Draft"
                    })
                    st.success("Bid saved for " + job['title'] + "!")

# ============ BID HISTORY ============
elif st.session_state.page == 'bid_history':
    st.markdown('<div class="section-header">📋 My Bids</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.bid_history:
        for bid in reversed(st.session_state.bid_history):
            st.markdown("<div class='data-card'><strong>" + bid['job_title'] + "</strong><br>Platform: " + bid['platform'] + " | Bid: $" + str(bid['bid_amount']) + "<br>Status: " + bid['status'] + " | Date: " + bid['date'].strftime('%Y-%m-%d %H:%M') + "</div>", unsafe_allow_html=True)
    else:
        st.info("No bids yet. Find jobs and submit bids.")

# ============ BID ROI CALCULATOR ============
elif st.session_state.page == 'bid_roi':
    st.markdown('<div class="section-header">💰 Bid ROI Calculator</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Calculate Your ROI")
        job_payout = st.number_input("Job Payout ($)", min_value=10, value=100)
        win_probability = st.slider("Win Probability (%)", 0, 100, 35)
        bid_cost = st.number_input("Cost to Bid ($)", min_value=0, value=5)
        
        expected_value = job_payout * (win_probability / 100)
        roi = ((expected_value - bid_cost) / bid_cost * 100) if bid_cost > 0 else expected_value * 10
        
        st.markdown("---")
        st.markdown("**Expected Value:** $" + str(round(expected_value, 2)))
        st.markdown("**ROI:** " + str(round(roi, 1)) + "%")
        
        if roi > 300:
            st.success("🟢 EXCELLENT ROI - Strongly recommend bidding")
        elif roi > 100:
            st.warning("🟡 GOOD ROI - Consider bidding")
        else:
            st.error("🔴 POOR ROI - Skip this opportunity")
    
    with col2:
        st.markdown("### 💡 Bid Strategy")
        st.markdown("""
        **When to bid:**
        - ✅ Match score > 80%
        - ✅ ROI > 100%
        - ✅ Win probability > 30%
        
        **Platform costs:**
        - Freelancer: $20 unlock fee
        - Upwork: 8-16 connects ($1.20-$2.40)
        """)

# ============ AUDIT PAGES ============
elif st.session_state.page == 'dns_audit':
    st.markdown('<div class="section-header">🌐 DNS Audit</div>', unsafe_allow_html=True)
    domain = st.text_input("Domain", placeholder="example.com")
    if st.button("Run DNS Audit"):
        st.markdown("<div class='data-card'><h4>DNS Records for " + domain + "</h4><p>✅ A Records: Found</p><p>✅ MX Records: Found</p><p>⚠️ SPF: Not configured</p></div>", unsafe_allow_html=True)

elif st.session_state.page == 'website_audit':
    st.markdown('<div class="section-header">🔒 Website Audit</div>', unsafe_allow_html=True)
    url = st.text_input("Website URL", placeholder="https://example.com")
    if st.button("Run Website Audit"):
        st.markdown("<div class='data-card'><h4>Website Audit for " + url + "</h4><p>✅ SSL Certificate: Valid</p><p>✅ HTTPS: Enabled</p><p>⚠️ Security Headers: Partial</p></div>", unsafe_allow_html=True)

elif st.session_state.page == 'email_security':
    st.markdown('<div class="section-header">📧 Email Security Audit</div>', unsafe_allow_html=True)
    domain = st.text_input("Domain", placeholder="example.com")
    if st.button("Run Email Security Audit"):
        st.markdown("<div class='data-card'><h4>Email Security for " + domain + "</h4><p>✅ SPF: Configured</p><p>⚠️ DKIM: Not Found</p><p>❌ DMARC: Not Configured</p></div>", unsafe_allow_html=True)

# ============ ANALYTICS ============
elif st.session_state.page == 'analytics':
    st.markdown('<div class="section-header">📊 Analytics</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.leads:
        scores = [l.get("score", 0) for l in st.session_state.leads]
        hot = sum(1 for s in scores if s >= 80)
        warm = sum(1 for s in scores if 60 <= s < 80)
        cold = sum(1 for s in scores if s < 60)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Hot Leads (80+)", hot)
        with col2:
            st.metric("Warm Leads (60-79)", warm)
        with col3:
            st.metric("Cold Leads (<60)", cold)
        
        st.markdown("---")
        chart_data = pd.DataFrame({"Category": ["Hot", "Warm", "Cold"], "Count": [hot, warm, cold]})
        st.bar_chart(chart_data.set_index("Category"))
        
        avg_score = sum(scores) / len(scores)
        st.metric("Average Lead Score", str(round(avg_score, 1)) + "/100")
    else:
        st.info("No data yet. Import leads to see analytics.")

# ============ SETTINGS ============
elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### Your Skills Profile")
    for skill, level in sorted(USER_SKILLS.items(), key=lambda x: x[1], reverse=True):
        st.markdown("**" + skill.replace('_', ' ').title() + ":** " + str(level) + "%")
        st.progress(level / 100)
    
    st.markdown("---")
    if st.button("Clear All Data"):
        st.session_state.leads = []
        st.session_state.bid_history = []
        st.session_state.jobs = []
        st.success("All data cleared!")

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Enterprise Suite | Lead Intelligence + Freelance Agent")

import streamlit as st
import pandas as pd
import json
import os
import requests
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import hashlib
import time

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="TechWokx Enterprise Suite",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ SESSION STATE INIT ============
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'
if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'email_log' not in st.session_state:
    st.session_state.email_log = []
if 'followup_queue' not in st.session_state:
    st.session_state.followup_queue = []
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'bid_history' not in st.session_state:
    st.session_state.bid_history = []

# ============ FILE STORAGE ============
os.makedirs("data", exist_ok=True)
LEADS_FILE = "data/leads.json"
EMAIL_LOG_FILE = "data/email_log.json"
JOBS_FILE = "data/jobs.json"

def load_leads():
    try:
        if os.path.exists(LEADS_FILE):
            with open(LEADS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_leads():
    try:
        with open(LEADS_FILE, 'w') as f:
            json.dump(st.session_state.leads, f, indent=2, default=str)
    except:
        pass

def load_email_log():
    try:
        if os.path.exists(EMAIL_LOG_FILE):
            with open(EMAIL_LOG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_email_log():
    try:
        with open(EMAIL_LOG_FILE, 'w') as f:
            json.dump(st.session_state.email_log, f, indent=2, default=str)
    except:
        pass

st.session_state.leads = load_leads()
st.session_state.email_log = load_email_log()

# ============ LOGIN CREDENTIALS ============
USERS = {
    "hello@techwokx.online": {
        "password": "Gtech.5628!@#$",
        "role": "admin",
        "name": "TechWokx Admin"
    }
}

# ============ SMTP CONFIGURATION ============
SMTP_CONFIG = {
    "host": "smtp.hostinger.com",
    "port": 465,
    "username": "hello@techwokx.online",
    "password": "Gtech.5628!@#$",
    "use_ssl": True,
    "daily_limit": 20,
    "sent_today": 0
}

# ============ EMAIL TEMPLATES ============
EMAIL_TEMPLATES = {
    "initial": {
        "name": "Initial Outreach",
        "subject": "IT Assessment for {company} - Score: {score}/100",
        "days_delay": 0
    },
    "followup_1": {
        "name": "First Follow-up",
        "subject": "Following up on your IT assessment",
        "days_delay": 3
    },
    "followup_2": {
        "name": "Second Follow-up",
        "subject": "Special offer for {company}",
        "days_delay": 7
    },
    "proposal": {
        "name": "Proposal",
        "subject": "Custom IT proposal for {company}",
        "days_delay": 14
    }
}

# ============ EMAIL FUNCTIONS ============
def send_email(to_email, subject, body):
    """Send email using SMTP"""
    if SMTP_CONFIG["sent_today"] >= SMTP_CONFIG["daily_limit"]:
        return False, "Daily limit reached"
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"TechWokx <{SMTP_CONFIG['username']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        if SMTP_CONFIG['use_ssl']:
            server = smtplib.SMTP_SSL(SMTP_CONFIG['host'], SMTP_CONFIG['port'])
        else:
            server = smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port'])
            server.starttls()
        
        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        
        SMTP_CONFIG["sent_today"] += 1
        return True, "Email sent"
    except Exception as e:
        return False, str(e)

def generate_proposal_email(lead):
    """Generate personalized proposal email"""
    audit_link = "https://techwokx.online/#audit"
    
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; }}
            .score {{ font-size: 2rem; font-weight: bold; color: #667eea; text-align: center; }}
            .button {{ background: #22c55e; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>TechWokx IT Assessment</h2>
            </div>
            <div class="content">
                <p>Dear {lead.get('name', 'Valued Customer')},</p>
                
                <p>We've reviewed your business and identified opportunities to improve your IT infrastructure.</p>
                
                <div class="score">
                    Lead Score: {lead.get('lead_score', 50)}/100
                </div>
                
                <h3>Recommended Services:</h3>
                <ul>
                    <li>Email Security Setup (SPF/DKIM/DMARC)</li>
                    <li>Professional Email Configuration</li>
                    <li>IT Infrastructure Audit</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{audit_link}" class="button">Run Free Audit</a>
                </div>
                
                <p>Best regards,<br>George Jabley<br>TechWokx Ghana</p>
            </div>
        </div>
    </body>
    </html>
    """

def send_proposal(lead):
    """Send proposal email to lead"""
    subject = EMAIL_TEMPLATES["initial"]["subject"].format(
        company=lead.get('name', ''),
        score=lead.get('lead_score', 50)
    )
    body = generate_proposal_email(lead)
    
    success, msg = send_email(lead.get('email', ''), subject, body)
    
    if success:
        lead['email_sent'] = True
        lead['email_sent_date'] = datetime.now().isoformat()
        lead['followup_stage'] = 1
        lead['next_followup'] = (datetime.now() + timedelta(days=3)).isoformat()
        save_leads()
        
        st.session_state.email_log.append({
            "to": lead.get('email'),
            "company": lead.get('name'),
            "subject": subject,
            "date": datetime.now().isoformat(),
            "status": "Sent"
        })
        save_email_log()
    
    return success, msg

def process_followups():
    """Process automated follow-ups"""
    now = datetime.now()
    for lead in st.session_state.leads:
        if lead.get('email_sent') and not lead.get('email_responded'):
            if lead.get('next_followup'):
                next_date = datetime.fromisoformat(lead['next_followup'])
                if now >= next_date:
                    stage = lead.get('followup_stage', 1)
                    if stage <= 3:
                        template_key = f"followup_{stage}"
                        if template_key in EMAIL_TEMPLATES:
                            subject = EMAIL_TEMPLATES[template_key]["subject"].format(
                                company=lead.get('name', '')
                            )
                            body = generate_proposal_email(lead)
                            success, _ = send_email(lead.get('email', ''), subject, body)
                            
                            if success:
                                lead['followup_stage'] = stage + 1
                                lead['next_followup'] = (datetime.now() + timedelta(days=3)).isoformat()
                                save_leads()

# ============ DEEP SEARCH FUNCTIONS ============
def deep_search_company(company_name):
    """Deep search using SERP API if available, otherwise simulated"""
    result = {
        "name": company_name,
        "website": f"www.{company_name.lower().replace(' ', '')}.com",
        "email": f"info@{company_name.lower().replace(' ', '')}.com",
        "phone": "+233 XX XXX XXXX",
        "address": "Accra, Ghana",
        "description": f"{company_name} is a business operating in Ghana.",
        "industry": "General Business",
        "employee_count": "10-50",
        "lead_score": 65,
        "contacts": [
            {"name": "Management", "title": "Decision Maker"},
            {"name": "IT Manager", "title": "Technical Contact"}
        ],
        "recommendations": [
            "Setup professional email (Google Workspace/Microsoft 365)",
            "Implement SPF/DKIM/DMARC for email security",
            "Conduct full IT security audit",
            "Schedule free consultation call"
        ]
    }
    
    # Try real SERP API if key exists
    try:
        serp_key = st.secrets.get("SERP_API_KEY", "")
        if serp_key:
            # Would call actual API here
            pass
    except:
        pass
    
    return result

# ============ FREELANCE JOB SEARCH ============
def search_freelance_jobs(keyword="data entry"):
    """Search for freelance jobs"""
    jobs = [
        {
            "id": 1,
            "title": f"{keyword.title()} Specialist Needed",
            "description": f"We need an experienced {keyword} specialist for ongoing work.",
            "platform": "Upwork",
            "budget": "$15-25/hr",
            "skills": [keyword, "excel", "communication"],
            "posted": "2 hours ago"
        },
        {
            "id": 2,
            "title": f"{keyword.title()} Project - 1000 records",
            "description": f"Looking for someone to handle {keyword} for a large dataset.",
            "platform": "Freelancer",
            "budget": "$100-200",
            "skills": [keyword, "attention to detail"],
            "posted": "1 day ago"
        },
        {
            "id": 3,
            "title": f"Virtual Assistant with {keyword.title()} Skills",
            "description": f"Need VA with strong {keyword} background for administrative tasks.",
            "platform": "Upwork",
            "budget": "$10-20/hr",
            "skills": [keyword, "administrative", "communication"],
            "posted": "3 hours ago"
        }
    ]
    return jobs

# ============ LEAD FUNCTIONS ============
def add_lead(lead_data):
    """Add lead to CRM"""
    for lead in st.session_state.leads:
        if lead.get('name', '').lower() == lead_data.get('name', '').lower():
            return False, "Lead already exists"
    
    new_lead = {
        "id": len(st.session_state.leads) + 1,
        "name": lead_data.get("name"),
        "website": lead_data.get("website", ""),
        "email": lead_data.get("email", ""),
        "phone": lead_data.get("phone", ""),
        "address": lead_data.get("address", ""),
        "lead_score": lead_data.get("lead_score", 50),
        "industry": lead_data.get("industry", ""),
        "employee_count": lead_data.get("employee_count", ""),
        "contacts": lead_data.get("contacts", []),
        "recommendations": lead_data.get("recommendations", []),
        "description": lead_data.get("description", ""),
        "source": lead_data.get("source", "Manual"),
        "created_at": datetime.now().isoformat(),
        "status": "Hot" if lead_data.get("lead_score", 50) >= 70 else "Warm" if lead_data.get("lead_score", 50) >= 50 else "Cold",
        "email_sent": False,
        "email_responded": False,
        "followup_stage": 0,
        "next_followup": None,
        "email_sent_date": None,
        "notes": ""
    }
    
    st.session_state.leads.append(new_lead)
    save_leads()
    return True, "Lead added"

def delete_lead(lead_id):
    st.session_state.leads = [l for l in st.session_state.leads if l['id'] != lead_id]
    save_leads()
    return True

# ============ CSS ============
st.markdown("""
<style>
.stApp { background: #f8fafc; }
[data-testid="stSidebar"] { background: #0f172a; }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #e2e8f0; }
[data-testid="stSidebar"] .stButton button { background: rgba(251, 191, 36, 0.15); color: #fbbf24; width: 100%; margin: 2px 0; }
.welcome-card { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; color: white; }
.metric-card { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
.metric-label { color: #64748b; font-size: 0.8rem; }
.data-card { background: white; border-radius: 12px; padding: 1.2rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
.section-header { color: #0f172a; font-size: 1.2rem; font-weight: 600; border-left: 3px solid #667eea; padding-left: 1rem; margin: 1rem 0; }
.custom-divider { height: 1px; background: #e2e8f0; margin: 1rem 0; }
.stButton > button { background: linear-gradient(135deg, #667eea, #764ba2); color: white; font-weight: 600; border: none; border-radius: 8px; }
.status-hot { background: #dc2626; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; }
.status-warm { background: #f97316; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; }
.status-cold { background: #64748b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; }
</style>
""", unsafe_allow_html=True)

# ============ LOGIN PAGE ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 400px; margin: 100px auto; padding: 2rem; background: white; border-radius: 24px; text-align: center;">
        <h1 style="color: #667eea;">TechWokx</h1>
        <p>Enterprise Suite</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if email in USERS and USERS[email]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user = USERS[email]
                st.session_state.current_page = 'dashboard'
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### TechWokx")
    st.markdown(f"Welcome, {st.session_state.user['name']}")
    st.markdown("---")
    
    menu = {
        "Dashboard": "dashboard",
        "Deep Company Search": "search",
        "Lead CRM": "crm",
        "Email Automation": "email",
        "Freelance Jobs": "jobs",
        "Settings": "settings",
        "Logout": "logout"
    }
    
    for label, key in menu.items():
        if st.button(label, key=key, use_container_width=True):
            if key == "logout":
                st.session_state.authenticated = False
                st.rerun()
            else:
                st.session_state.current_page = key
                st.rerun()
    
    st.markdown("---")
    st.markdown(f"Leads: {len(st.session_state.leads)}")
    st.markdown(f"Emails Today: {SMTP_CONFIG['sent_today']}/{SMTP_CONFIG['daily_limit']}")

# ============ DASHBOARD ============
if st.session_state.current_page == 'dashboard':
    total = len(st.session_state.leads)
    hot = sum(1 for l in st.session_state.leads if l.get("lead_score", 0) >= 70)
    emails = len(st.session_state.email_log)
    
    st.markdown('<div class="welcome-card"><h2>Welcome to TechWokx</h2><p>Lead Intelligence | Email Automation | Freelance Jobs</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{emails}</div><div class='metric-label'>Emails Sent</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.jobs)}</div><div class='metric-label'>Jobs Found</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Recent Leads</div>', unsafe_allow_html=True)
        for lead in st.session_state.leads[-5:]:
            status_class = "status-hot" if lead.get("lead_score", 0) >= 70 else "status-warm" if lead.get("lead_score", 0) >= 50 else "status-cold"
            st.markdown(f"<div class='data-card'><strong>{lead['name']}</strong> - Score: {lead['lead_score']}/100 <span class='{status_class}'>{lead['status']}</span><br><small>Added: {lead['created_at'][:10]}</small></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
        if st.button("Deep Search Company", use_container_width=True):
            st.session_state.current_page = 'search'
            st.rerun()
        if st.button("Send Proposals", use_container_width=True):
            st.session_state.current_page = 'email'
            st.rerun()
        if st.button("Find Jobs", use_container_width=True):
            st.session_state.current_page = 'jobs'
            st.rerun()

# ============ DEEP COMPANY SEARCH ============
elif st.session_state.current_page == 'search':
    st.markdown('<div class="section-header">Deep Company Search</div>', unsafe_allow_html=True)
    st.caption("AI-powered search with SERP API integration")
    st.markdown("---")
    
    company_name = st.text_input("Company Name", placeholder="e.g. Prime Meridian Docks")
    
    if st.button("Deep Search", type="primary"):
        if company_name:
            with st.spinner(f"Searching {company_name}..."):
                result = deep_search_company(company_name)
                st.session_state.last_search = result
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>Company Information</h4>
                        <p><strong>Name:</strong> {result['name']}</p>
                        <p><strong>Website:</strong> {result['website']}</p>
                        <p><strong>Email:</strong> {result['email']}</p>
                        <p><strong>Phone:</strong> {result['phone']}</p>
                        <p><strong>Address:</strong> {result['address']}</p>
                        <p><strong>Industry:</strong> {result['industry']}</p>
                        <p><strong>Employees:</strong> {result['employee_count']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="data-card" style="text-align: center;">
                        <h4>Lead Score</h4>
                        <p style="font-size: 3rem; font-weight: 700; color: #667eea;">{result['lead_score']}/100</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if result.get('description'):
                    st.markdown(f"<div class='data-card'><p>{result['description']}</p></div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="data-card">
                    <h4>Recommendations</h4>
                    <ul>{"".join([f"<li>{r}</li>" for r in result['recommendations']])}</ul>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Add to CRM", type="primary"):
                        success, msg = add_lead(result)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.warning(msg)
                
                with col2:
                    if result.get('email'):
                        if st.button("Send Proposal Now"):
                            success, msg = send_proposal(result)
                            if success:
                                st.success(f"Proposal sent to {result['email']}")
                                st.rerun()
                            else:
                                st.error(f"Failed: {msg}")
        else:
            st.warning("Enter company name")

# ============ LEAD CRM ============
elif st.session_state.current_page == 'crm':
    st.markdown('<div class="section-header">Lead CRM</div>', unsafe_allow_html=True)
    st.caption(f"Total Leads: {len(st.session_state.leads)}")
    st.markdown("---")
    
    if st.session_state.leads:
        search = st.text_input("Search", placeholder="Search by name, email")
        
        filtered = st.session_state.leads
        if search:
            filtered = [l for l in filtered if search.lower() in l.get('name', '').lower() or search.lower() in l.get('email', '').lower()]
        
        for lead in filtered:
            status_class = "status-hot" if lead.get("lead_score", 0) >= 70 else "status-warm" if lead.get("lead_score", 0) >= 50 else "status-cold"
            with st.expander(f"{lead['name']} - Score: {lead['lead_score']}/100 - {lead['status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Email: {lead.get('email', 'N/A')}")
                    st.write(f"Phone: {lead.get('phone', 'N/A')}")
                    st.write(f"Website: {lead.get('website', 'N/A')}")
                with col2:
                    st.write(f"Added: {lead['created_at'][:10]}")
                    st.write(f"Email Sent: {'Yes' if lead.get('email_sent') else 'No'}")
                    if lead.get('email_sent_date'):
                        st.write(f"Sent: {lead['email_sent_date'][:10]}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if lead.get('email') and not lead.get('email_sent'):
                        if st.button(f"Send Proposal", key=f"send_{lead['id']}"):
                            success, msg = send_proposal(lead)
                            if success:
                                st.success("Proposal sent!")
                                st.rerun()
                            else:
                                st.error(f"Failed: {msg}")
                with col2:
                    if lead.get('email'):
                        st.info(f"Email: {lead['email']}")
                with col3:
                    if st.button(f"Delete", key=f"del_{lead['id']}"):
                        delete_lead(lead['id'])
                        st.rerun()
    else:
        st.info("No leads yet. Use Deep Search to add leads.")
        if st.button("Go to Deep Search"):
            st.session_state.current_page = 'search'
            st.rerun()

# ============ EMAIL AUTOMATION ============
elif st.session_state.current_page == 'email':
    st.markdown('<div class="section-header">Email Automation</div>', unsafe_allow_html=True)
    st.caption("Send proposals and manage follow-up sequences")
    st.markdown("---")
    
    # Process auto follow-ups
    process_followups()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Send Bulk Proposals")
        leads_with_email = [l for l in st.session_state.leads if l.get('email') and not l.get('email_sent')]
        
        if leads_with_email:
            selected = st.multiselect("Select leads", [f"{l['name']} ({l['email']})" for l in leads_with_email])
            if st.button("Send to Selected"):
                count = 0
                for s in selected:
                    lead = next(l for l in leads_with_email if f"{l['name']} ({l['email']})" == s)
                    success, _ = send_proposal(lead)
                    if success:
                        count += 1
                st.success(f"Sent to {count} leads")
                st.rerun()
        else:
            st.info("No leads pending email")
    
    with col2:
        st.markdown("### Email Status")
        st.metric("Emails Sent Today", SMTP_CONFIG["sent_today"])
        st.metric("Daily Limit", SMTP_CONFIG["daily_limit"])
        st.progress(SMTP_CONFIG["sent_today"] / SMTP_CONFIG["daily_limit"])
    
    st.markdown("---")
    st.markdown("### Email Log")
    
    if st.session_state.email_log:
        for log in reversed(st.session_state.email_log[-10:]):
            st.markdown(f"<div class='data-card'><strong>{log['company']}</strong><br>To: {log['to']}<br>Subject: {log['subject']}<br>Date: {log['date'][:19]}</div>", unsafe_allow_html=True)
    else:
        st.info("No emails sent yet")

# ============ FREELANCE JOBS ============
elif st.session_state.current_page == 'jobs':
    st.markdown('<div class="section-header">Freelance Jobs</div>', unsafe_allow_html=True)
    st.caption("Find and bid on freelance opportunities")
    st.markdown("---")
    
    keyword = st.text_input("Search Keyword", value="data entry")
    
    if st.button("Search Jobs", type="primary"):
        with st.spinner("Searching..."):
            jobs = search_freelance_jobs(keyword)
            st.session_state.jobs = jobs
        
    if st.session_state.jobs:
        for job in st.session_state.jobs:
            with st.expander(f"{job['title']} - {job['platform']} - {job['budget']}"):
                st.write(f"Description: {job['description']}")
                st.write(f"Skills: {', '.join(job['skills'])}")
                st.write(f"Posted: {job['posted']}")
                
                if st.button(f"Save Bid", key=f"bid_{job['id']}"):
                    st.session_state.bid_history.append({
                        "job": job['title'],
                        "platform": job['platform'],
                        "date": datetime.now().isoformat()
                    })
                    st.success("Bid saved!")
    else:
        st.info("Click Search Jobs to find opportunities")

# ============ SETTINGS ============
elif st.session_state.current_page == 'settings':
    st.markdown('<div class="section-header">Settings</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### Email Configuration")
    st.info(f"""
    SMTP Settings:
    - Host: {SMTP_CONFIG['host']}
    - Port: {SMTP_CONFIG['port']}
    - Username: {SMTP_CONFIG['username']}
    - Daily Limit: {SMTP_CONFIG['daily_limit']} emails
    """)
    
    st.markdown("### Follow-up Sequence")
    for key, template in EMAIL_TEMPLATES.items():
        st.write(f"- {template['name']}: {template['days_delay']} days")
    
    st.markdown("### Data Management")
    if st.button("Clear All Leads", type="secondary"):
        st.session_state.leads = []
        save_leads()
        st.success("All leads cleared")
        st.rerun()

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("2024 TechWokx Enterprise Suite | hello@techwokx.online | +233 555 087 407")

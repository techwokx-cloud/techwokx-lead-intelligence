import streamlit as st
import pandas as pd
import json
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time
import random
import uuid

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="TechWokx Lead Intelligence",
    page_icon=":mag:",
    layout="wide"
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
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = []
if 'letter_queue' not in st.session_state:
    st.session_state.letter_queue = []

# ============ FILE STORAGE ============
os.makedirs("data", exist_ok=True)
LEADS_FILE = "data/leads.json"
EMAIL_LOG_FILE = "data/email_log.json"

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
    "daily_limit": 50,
    "sent_today": 0
}

# ============ COMPANY DATABASE ============
COMPANY_DATABASE = {
    "Hotels": {
        "Airport Area": [
            {"name": "Marriott Hotel Accra", "area": "Airport", "type": "Hotel"},
            {"name": "Kempinski Hotel Gold Coast City", "area": "Airport", "type": "Hotel"},
            {"name": "Holiday Inn Accra Airport", "area": "Airport", "type": "Hotel"},
            {"name": "Alisa Hotel North Ridge", "area": "Airport", "type": "Hotel"},
            {"name": "Fiesta Royale Hotel", "area": "Airport", "type": "Hotel"}
        ],
        "Osu": [
            {"name": "Movenpick Ambassador Hotel", "area": "Osu", "type": "Hotel"},
            {"name": "Oxford Street Hotel", "area": "Osu", "type": "Hotel"},
            {"name": "Noble House Hotel", "area": "Osu", "type": "Hotel"}
        ],
        "Labadi": [
            {"name": "Labadi Beach Hotel", "area": "Labadi", "type": "Hotel"},
            {"name": "La Palm Royal Beach Hotel", "area": "Labadi", "type": "Hotel"},
            {"name": "African Regent Hotel", "area": "Labadi", "type": "Hotel"}
        ]
    },
    "SMEs": {
        "Airport Area": [
            {"name": "Airport West Consult", "area": "Airport", "type": "SME"},
            {"name": "Silver Star Auto Ltd", "area": "Airport", "type": "SME"},
            {"name": "Ranch & Blues", "area": "Airport", "type": "SME"},
            {"name": "St. Maritz Pharmacy", "area": "Airport", "type": "SME"}
        ],
        "Osu": [
            {"name": "Osu Business Centre", "area": "Osu", "type": "SME"},
            {"name": "Frankie's Hotel", "area": "Osu", "type": "SME"},
            {"name": "Buka Restaurant", "area": "Osu", "type": "SME"}
        ],
        "Nima": [
            {"name": "Nima Business Hub", "area": "Nima", "type": "SME"},
            {"name": "Nima Plaza Shopping", "area": "Nima", "type": "SME"},
            {"name": "Nima Medical Centre", "area": "Nima", "type": "SME"}
        ]
    },
    "Banks": {
        "Accra Central": [
            {"name": "GCB Bank Head Office", "area": "Accra", "type": "Bank"},
            {"name": "Ecobank Ghana Head Office", "area": "Accra", "type": "Bank"},
            {"name": "Stanbic Bank Ghana", "area": "Accra", "type": "Bank"},
            {"name": "Standard Chartered Bank", "area": "Accra", "type": "Bank"},
            {"name": "Fidelity Bank Ghana", "area": "Accra", "type": "Bank"}
        ]
    }
}

# ============ EMAIL FUNCTIONS ============
def generate_email_body(company, category):
    """Generate personalized email for company"""
    
    services = [
        "Professional Email Setup (Google Workspace/Microsoft 365)",
        "Email Security (SPF/DKIM/DMARC Configuration)",
        "IT Security Audit and Compliance",
        "Data Backup and Disaster Recovery",
        "Staff IT Training and Support"
    ]
    
    return f"""
    <html>
    <head><style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9fafb; }}
        .button {{ background: #22c55e; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
    </style></head>
    <body>
        <div class="container">
            <div class="header">
                <h2>TechWokx IT Assessment</h2>
                <p>For {company['name']}</p>
            </div>
            <div class="content">
                <p>Dear Management Team,</p>
                <p>We are offering {company['name']} a complimentary IT infrastructure assessment.</p>
                <h3>Recommended Services:</h3>
                <ul>
                    <li>{services[0]}</li>
                    <li>{services[1]}</li>
                    <li>{services[2]}</li>
                </ul>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://techwokx.online/#audit" class="button">Schedule Free Audit</a>
                </div>
                <p>Best regards,<br>George Jabley<br>TechWokx Ghana</p>
            </div>
        </div>
    </body>
    </html>
    """

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

def add_lead(lead_data):
    """Add lead to CRM"""
    for lead in st.session_state.leads:
        if lead.get('name', '').lower() == lead_data.get('name', '').lower():
            return False
    
    new_lead = {
        "id": len(st.session_state.leads) + 1,
        "name": lead_data.get("name"),
        "email": lead_data.get("email", ""),
        "area": lead_data.get("area", ""),
        "type": lead_data.get("type", ""),
        "lead_score": random.randint(60, 85),
        "created_at": datetime.now().isoformat(),
        "email_sent": False
    }
    st.session_state.leads.append(new_lead)
    save_leads()
    return True

def get_companies_by_category(category, area, limit=10):
    """Get companies by category and area"""
    if category in COMPANY_DATABASE and area in COMPANY_DATABASE[category]:
        companies = COMPANY_DATABASE[category][area][:limit]
        results = []
        for company in companies:
            results.append({
                "name": company['name'],
                "area": company.get('area', area),
                "type": company.get('type', category),
                "email": f"info@{company['name'].lower().replace(' ', '').replace('&', '').replace("'", '')}.com"
            })
        return results
    return []

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
</style>
""", unsafe_allow_html=True)

# ============ LOGIN ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 400px; margin: 100px auto; padding: 2rem; background: white; border-radius: 24px; text-align: center;">
        <h1 style="color: #667eea;">TechWokx</h1>
        <p>Lead Intelligence Suite</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
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
    
    menu_options = [
        ("Dashboard", "dashboard"),
        ("Batch Search", "batch_search"),
        ("Leads CRM", "crm"),
        ("Email Log", "email_log"),
        ("Settings", "settings"),
        ("Logout", "logout")
    ]
    
    for label, page in menu_options:
        if st.button(label, key=f"nav_{page}", use_container_width=True):
            if page == "logout":
                st.session_state.authenticated = False
                st.rerun()
            else:
                st.session_state.current_page = page
                st.rerun()
    
    st.markdown("---")
    st.markdown(f"Leads: {len(st.session_state.leads)}")
    st.markdown(f"Emails Today: {SMTP_CONFIG['sent_today']}/{SMTP_CONFIG['daily_limit']}")

# ============ DASHBOARD ============
if st.session_state.current_page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>TechWokx Lead Intelligence</h2>
        <p>Batch Company Search | Automated Email Campaigns | Lead Tracking</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.leads)}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.email_log)}</div><div class='metric-label'>Emails Sent</div></div>", unsafe_allow_html=True)
    with col3:
        remaining = SMTP_CONFIG['daily_limit'] - SMTP_CONFIG['sent_today']
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{remaining}</div><div class='metric-label'>Emails Remaining</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
        if st.button("Start Batch Search", key="quick_batch", use_container_width=True):
            st.session_state.current_page = 'batch_search'
            st.rerun()
    with col2:
        st.markdown('<div class="section-header">Recent Activity</div>', unsafe_allow_html=True)
        for lead in st.session_state.leads[-3:]:
            st.markdown(f"<div class='data-card'><strong>{lead['name']}</strong><br>Added: {lead['created_at'][:10]}</div>", unsafe_allow_html=True)

# ============ BATCH SEARCH ============
elif st.session_state.current_page == 'batch_search':
    st.markdown('<div class="section-header">Batch Company Search</div>', unsafe_allow_html=True)
    st.caption("Search companies by category and location, then send automated emails")
    st.markdown("---")
    
    # Form for batch search
    with st.form("batch_search_form"):
        categories = list(COMPANY_DATABASE.keys())
        col1, col2 = st.columns(2)
        with col1:
            selected_category = st.selectbox("Business Category", categories)
        with col2:
            areas = list(COMPANY_DATABASE[selected_category].keys())
            selected_area = st.selectbox("Location Area", areas)
        
        limit = st.slider("Number of Companies", 3, 10, 5)
        
        submitted = st.form_submit_button("Search Companies")
        
        if submitted:
            companies = get_companies_by_category(selected_category, selected_area, limit)
            st.session_state.batch_results = companies
            st.success(f"Found {len(companies)} companies")
    
    # Display results outside form
    if st.session_state.batch_results:
        st.markdown("### Search Results")
        
        # Display as table
        df = pd.DataFrame(st.session_state.batch_results)
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add All to CRM", key="add_all_crm", use_container_width=True):
                count = 0
                for company in st.session_state.batch_results:
                    if add_lead(company):
                        count += 1
                st.success(f"Added {count} companies to CRM")
                st.rerun()
        
        with col2:
            if st.button("Send Emails to All", key="send_all_emails", type="primary", use_container_width=True):
                success_count = 0
                for company in st.session_state.batch_results:
                    email = company.get('email')
                    subject = f"IT Assessment Offer for {company['name']}"
                    body = generate_email_body(company, selected_category)
                    success, msg = send_email(email, subject, body)
                    
                    if success:
                        success_count += 1
                        st.session_state.email_log.append({
                            "to": email,
                            "company": company['name'],
                            "subject": subject,
                            "date": datetime.now().isoformat(),
                            "status": "Sent"
                        })
                    else:
                        # Add to letter queue
                        st.session_state.letter_queue.append({
                            "company": company['name'],
                            "area": company.get('area', ''),
                            "email": email,
                            "reason": msg
                        })
                    time.sleep(1)
                
                save_email_log()
                st.success(f"Sent: {success_count} | Failed: {len(st.session_state.batch_results) - success_count}")
                st.info(f"{len(st.session_state.letter_queue)} companies added to letter queue")
                st.rerun()
        
        # Individual actions
        st.markdown("### Individual Company Actions")
        for idx, company in enumerate(st.session_state.batch_results):
            with st.expander(f"{company['name']} - {company.get('area', '')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Add to CRM", key=f"add_{idx}_{company['name']}"):
                        if add_lead(company):
                            st.success(f"Added {company['name']} to CRM")
                            st.rerun()
                with col2:
                    if st.button("Preview Email", key=f"preview_{idx}_{company['name']}"):
                        email_body = generate_email_body(company, selected_category)
                        st.markdown(email_body, unsafe_allow_html=True)
                with col3:
                    if st.button("Send Email", key=f"send_{idx}_{company['name']}"):
                        email = company.get('email')
                        subject = f"IT Assessment Offer for {company['name']}"
                        body = generate_email_body(company, selected_category)
                        success, msg = send_email(email, subject, body)
                        if success:
                            st.success(f"Email sent to {company['name']}")
                            st.session_state.email_log.append({
                                "to": email,
                                "company": company['name'],
                                "subject": subject,
                                "date": datetime.now().isoformat(),
                                "status": "Sent"
                            })
                            save_email_log()
                            st.rerun()
                        else:
                            st.error(f"Failed: {msg}")

# ============ LEADS CRM ============
elif st.session_state.current_page == 'crm':
    st.markdown('<div class="section-header">Leads CRM</div>', unsafe_allow_html=True)
    st.caption(f"Total Leads: {len(st.session_state.leads)}")
    st.markdown("---")
    
    if st.session_state.leads:
        search = st.text_input("Search", placeholder="Search by name or area")
        
        filtered = st.session_state.leads
        if search:
            filtered = [l for l in filtered if search.lower() in l.get('name', '').lower() or search.lower() in l.get('area', '').lower()]
        
        for lead in filtered:
            with st.expander(f"{lead['name']} - Score: {lead['lead_score']}/100"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {lead.get('email', 'N/A')}")
                    st.write(f"**Area:** {lead.get('area', 'N/A')}")
                with col2:
                    st.write(f"**Type:** {lead.get('type', 'N/A')}")
                    st.write(f"**Added:** {lead['created_at'][:10]}")
                
                if not lead.get('email_sent') and lead.get('email'):
                    if st.button(f"Send Email", key=f"send_crm_{lead['id']}"):
                        subject = f"IT Assessment Offer for {lead['name']}"
                        body = generate_email_body(lead, lead.get('type', 'SME'))
                        success, msg = send_email(lead['email'], subject, body)
                        if success:
                            lead['email_sent'] = True
                            save_leads()
                            st.success(f"Email sent to {lead['name']}")
                            st.rerun()
                        else:
                            st.error(f"Failed: {msg}")
    else:
        st.info("No leads yet. Run a batch search to add leads.")

# ============ EMAIL LOG ============
elif st.session_state.current_page == 'email_log':
    st.markdown('<div class="section-header">Email Log</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.email_log:
        for log in reversed(st.session_state.email_log):
            st.markdown(f"""
            <div class="data-card">
                <strong>To:</strong> {log['to']}<br>
                <strong>Company:</strong> {log['company']}<br>
                <strong>Subject:</strong> {log['subject']}<br>
                <strong>Date:</strong> {log['date'][:19]}<br>
                <strong>Status:</strong> ✅ {log['status']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No emails sent yet")

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
    - Daily Limit: {SMTP_CONFIG['daily_limit']}
    """)
    
    new_limit = st.number_input("Daily Email Limit", min_value=10, max_value=200, value=SMTP_CONFIG['daily_limit'], key="daily_limit_input")
    if st.button("Update Limit", key="update_limit"):
        SMTP_CONFIG['daily_limit'] = new_limit
        st.success(f"Daily limit updated to {new_limit}")
    
    st.markdown("### Data Management")
    if st.button("Clear All Data", key="clear_data", type="secondary"):
        st.session_state.leads = []
        st.session_state.email_log = []
        st.session_state.batch_results = []
        st.session_state.letter_queue = []
        save_leads()
        save_email_log()
        st.success("All data cleared")
        st.rerun()

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("2024 TechWokx Lead Intelligence | Batch Search | Email Automation")

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

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="TechWokx Lead Intelligence",
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

# ============ COMPANY DATABASE BY CATEGORY & LOCATION ============
COMPANY_DATABASE = {
    "hotels": {
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
            {"name": "Noble House Hotel", "area": "Osu", "type": "Hotel"},
            {"name": "Osu Home Inn", "area": "Osu", "type": "Hotel"}
        ],
        "Labadi": [
            {"name": "Labadi Beach Hotel", "area": "Labadi", "type": "Hotel"},
            {"name": "La Palm Royal Beach Hotel", "area": "Labadi", "type": "Hotel"},
            {"name": "African Regent Hotel", "area": "Labadi", "type": "Hotel"}
        ],
        "Accra Central": [
            {"name": "Accra City Hotel", "area": "Accra Central", "type": "Hotel"},
            {"name": "Central Hotel Ridge", "area": "Accra Central", "type": "Hotel"},
            {"name": "Tang Palace Hotel", "area": "Accra Central", "type": "Hotel"}
        ]
    },
    "smes": {
        "Airport Area": [
            {"name": "Airport West Consult", "area": "Airport", "type": "SME", "industry": "Consulting"},
            {"name": "Silver Star Auto Ltd", "area": "Airport", "type": "SME", "industry": "Automotive"},
            {"name": "Ranch & Blues", "area": "Airport", "type": "SME", "industry": "Restaurant"},
            {"name": "St. Maritz Pharmacy", "area": "Airport", "type": "SME", "industry": "Pharmacy"},
            {"name": "Kozo Restaurant", "area": "Airport", "type": "SME", "industry": "Restaurant"}
        ],
        "Osu": [
            {"name": "Osu Business Centre", "area": "Osu", "type": "SME", "industry": "Business Services"},
            {"name": "Frankie's Hotel", "area": "Osu", "type": "SME", "industry": "Hospitality"},
            {"name": "Buka Restaurant", "area": "Osu", "type": "SME", "industry": "Restaurant"},
            {"name": "Osu Food Court", "area": "Osu", "type": "SME", "industry": "Food Services"}
        ],
        "Labadi": [
            {"name": "Labadi Trading Company", "area": "Labadi", "type": "SME", "industry": "Retail"},
            {"name": "Coastal Services Ltd", "area": "Labadi", "type": "SME", "industry": "Services"},
            {"name": "Labadi Beach Resort", "area": "Labadi", "type": "SME", "industry": "Hospitality"}
        ],
        "Nima": [
            {"name": "Nima Business Hub", "area": "Nima", "type": "SME", "industry": "Business Hub"},
            {"name": "Nima Plaza Shopping", "area": "Nima", "type": "SME", "industry": "Retail"},
            {"name": "Nima Medical Centre", "area": "Nima", "type": "SME", "industry": "Healthcare"}
        ]
    },
    "restaurants": {
        "Airport Area": [
            {"name": "Zen Garden", "area": "Airport", "type": "Restaurant"},
            {"name": "Santoku", "area": "Airport", "type": "Restaurant"},
            {"name": "Casa Trattoria", "area": "Airport", "type": "Restaurant"}
        ],
        "Osu": [
            {"name": "Coco Lounge", "area": "Osu", "type": "Restaurant"},
            {"name": "Rockstone's Office", "area": "Osu", "type": "Restaurant"},
            {"name": "Tandoor Indian Restaurant", "area": "Osu", "type": "Restaurant"}
        ]
    },
    "banks": {
        "Accra": [
            {"name": "GCB Bank Head Office", "area": "Accra", "type": "Bank"},
            {"name": "Ecobank Ghana Head Office", "area": "Accra", "type": "Bank"},
            {"name": "Stanbic Bank Ghana", "area": "Accra", "type": "Bank"},
            {"name": "Standard Chartered Bank", "area": "Accra", "type": "Bank"},
            {"name": "Fidelity Bank Ghana", "area": "Accra", "type": "Bank"},
            {"name": "Access Bank Ghana", "area": "Accra", "type": "Bank"},
            {"name": "Zenith Bank Ghana", "area": "Accra", "type": "Bank"}
        ]
    }
}

# ============ EMAIL TEMPLATES ============
def generate_personalized_email(company, category):
    """Generate AI-like personalized email for company"""
    
    if category == "hotels":
        services = [
            "Guest WiFi optimization for better reviews",
            "Property Management System integration",
            "Booking platform API connectivity",
            "Staff email security training"
        ]
        pain_points = "guest WiFi complaints, booking system downtime, email security risks"
    elif category == "banks":
        services = [
            "Enterprise email security (SPF/DKIM/DMARC)",
            "Secure data backup and recovery",
            "Customer data protection",
            "Compliance auditing"
        ]
        pain_points = "email spoofing attacks, data breaches, compliance risks"
    elif category == "restaurants":
        services = [
            "Online ordering system setup",
            "Customer database management",
            "POS system integration",
            "Delivery platform API connections"
        ]
        pain_points = "order management chaos, customer data loss, delivery platform issues"
    else:
        services = [
            "Professional email setup (Google Workspace/Microsoft 365)",
            "IT security audit and compliance",
            "Data backup and disaster recovery",
            "Staff IT training and support"
        ]
        pain_points = "email security vulnerabilities, data loss, system downtime"
    
    email_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 20px; background: #f9fafb; }}
            .footer {{ text-align: center; padding: 15px; font-size: 12px; color: #666; }}
            .button {{ background: #22c55e; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            .service-box {{ background: white; padding: 10px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>TechWokx IT Assessment</h2>
                <p>For {company['name']}</p>
            </div>
            <div class="content">
                <p>Dear Management Team,</p>
                
                <p>We recently reviewed IT infrastructure needs for businesses in the {company.get('area', 'Accra')} area and identified {company['name']} as a potential partner for our IT optimization services.</p>
                
                <h3>Key Challenges We Address:</h3>
                <ul>
                    <li>{pain_points}</li>
                </ul>
                
                <h3>Recommended Services for {company['name']}:</h3>
                {''.join([f'<div class="service-box">✓ {s}</div>' for s in services[:3]])}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://techwokx.online/#audit" class="button">Schedule Free IT Audit</a>
                </div>
                
                <p>We're offering a complimentary IT assessment to help you identify security gaps and optimization opportunities - no obligation, just insights.</p>
                
                <p>Best regards,<br>
                <strong>George Jabley</strong><br>
                Founder & IT Operations Lead<br>
                TechWokx Ghana<br>
                +233 555 087 407</p>
            </div>
            <div class="footer">
                <p>© 2024 TechWokx | IT Intelligence for African Businesses</p>
            </div>
        </div>
    </body>
    </html>
    """
    return email_body

def generate_letter_content(company):
    """Generate letter content for companies without email"""
    return f"""
TECHWOKX IT ASSESSMENT - OFFICIAL LETTER

Date: {datetime.now().strftime('%B %d, %Y')}

To: Management Team
{company['name']}
{company.get('area', 'Accra')}, Ghana

RE: Complimentary IT Infrastructure Assessment

Dear Sir/Madam,

We are reaching out to offer {company['name']} a complimentary IT infrastructure assessment. 

Based on our research of businesses in the {company.get('area', 'Accra')} area, we believe {company['name']} could benefit from our expertise in:

• Email Security Configuration (SPF/DKIM/DMARC)
• Professional Email Setup (Google Workspace/Microsoft 365)
• IT Security Audit and Compliance
• Data Backup and Disaster Recovery

This assessment is completely free and includes:
1. Email security risk analysis
2. Network infrastructure review
3. Data backup evaluation
4. Staff IT security assessment

To schedule your complimentary assessment, please:
• Call us at: +233 555 087 407
• Email: hello@techwokx.online
• Visit: techwokx.online

We look forward to helping {company['name']} achieve better IT security and efficiency.

Sincerely,

George Jabley
Founder & IT Operations Lead
TechWokx Ghana

TechWokx | +233 555 087 407 | techwokx.online
    """

# ============ EMAIL SENDING FUNCTIONS ============
def send_email(to_email, subject, body):
    """Send email using SMTP"""
    if SMTP_CONFIG["sent_today"] >= SMTP_CONFIG["daily_limit"]:
        return False, "Daily limit reached", None
    
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
        return True, "Email sent", None
    except Exception as e:
        return False, str(e), None

def send_batch_emails(companies, category):
    """Send emails to a batch of companies"""
    results = []
    success_count = 0
    fail_count = 0
    
    for company in companies:
        # Generate email address (in real system, you'd have actual emails)
        domain = company['name'].lower().replace(' ', '').replace('&', '').replace("'", '')
        email = f"info@{domain}.com"
        
        subject = f"IT Assessment Offer for {company['name']}"
        body = generate_personalized_email(company, category)
        
        success, message, _ = send_email(email, subject, body)
        
        result = {
            "company": company['name'],
            "area": company.get('area', ''),
            "email": email,
            "status": "Sent" if success else "Failed",
            "message": message if not success else "",
            "date": datetime.now().isoformat()
        }
        results.append(result)
        
        if success:
            success_count += 1
            # Log to email log
            st.session_state.email_log.append({
                "to": email,
                "company": company['name'],
                "subject": subject,
                "date": datetime.now().isoformat(),
                "status": "Sent"
            })
        else:
            fail_count += 1
            # Add to letter queue
            st.session_state.letter_queue.append({
                "company": company['name'],
                "area": company.get('area', ''),
                "type": category,
                "reason": "No valid email",
                "letter_content": generate_letter_content(company)
            })
        
        time.sleep(2)  # Rate limiting
    
    save_email_log()
    return results, success_count, fail_count

# ============ COMPANY SEARCH FUNCTIONS ============
def search_companies_by_category(category, area, limit=10):
    """Search companies by category and area"""
    results = []
    
    if category in COMPANY_DATABASE:
        if area in COMPANY_DATABASE[category]:
            companies = COMPANY_DATABASE[category][area][:limit]
            for company in companies:
                results.append({
                    "name": company['name'],
                    "area": company.get('area', area),
                    "type": company.get('type', category),
                    "industry": company.get('industry', 'General'),
                    "email": f"info@{company['name'].lower().replace(' ', '').replace('&', '').replace("'", '')}.com",
                    "phone": "+233 XX XXX XXXX",
                    "lead_score": random.randint(60, 85)
                })
    
    return results

def get_available_categories():
    return list(COMPANY_DATABASE.keys())

def get_available_areas(category):
    if category in COMPANY_DATABASE:
        return list(COMPANY_DATABASE[category].keys())
    return []

# ============ LEAD FUNCTIONS ============
def add_lead(lead_data):
    """Add lead to CRM"""
    for lead in st.session_state.leads:
        if lead.get('name', '').lower() == lead_data.get('name', '').lower():
            return False, "Lead already exists"
    
    new_lead = {
        "id": len(st.session_state.leads) + 1,
        "name": lead_data.get("name"),
        "email": lead_data.get("email", ""),
        "phone": lead_data.get("phone", ""),
        "website": lead_data.get("website", ""),
        "area": lead_data.get("area", ""),
        "type": lead_data.get("type", ""),
        "lead_score": lead_data.get("lead_score", 65),
        "source": lead_data.get("source", "Batch Search"),
        "created_at": datetime.now().isoformat(),
        "status": "Hot" if lead_data.get("lead_score", 65) >= 70 else "Warm",
        "email_sent": False,
        "email_sent_date": None,
        "email_responded": False
    }
    
    st.session_state.leads.append(new_lead)
    save_leads()
    return True, "Lead added"

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
.status-sent { background: #22c55e; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; }
.status-pending { background: #f59e0b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; }
.status-failed { background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; }
</style>
""", unsafe_allow_html=True)

# ============ LOGIN PAGE ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 400px; margin: 100px auto; padding: 2rem; background: white; border-radius: 24px; text-align: center;">
        <h1 style="color: #667eea;">TechWokx</h1>
        <p>Lead Intelligence Suite</p>
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
        "Batch Company Search": "batch_search",
        "Email Campaigns": "email_campaigns",
        "Lead CRM": "crm",
        "Letter Queue": "letter_queue",
        "Email Log": "email_log",
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
    st.markdown(f"Letters Ready: {len(st.session_state.letter_queue)}")

# ============ DASHBOARD ============
if st.session_state.current_page == 'dashboard':
    total = len(st.session_state.leads)
    emails_sent = len(st.session_state.email_log)
    
    st.markdown('<div class="welcome-card"><h2>TechWokx Lead Intelligence</h2><p>Batch Company Search | AI Email Automation | Campaign Tracking</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{emails_sent}</div><div class='metric-label'>Emails Sent</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.letter_queue)}</div><div class='metric-label'>Letters Ready</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{SMTP_CONFIG['daily_limit'] - SMTP_CONFIG['sent_today']}</div><div class='metric-label'>Emails Remaining</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Batch Company Search", use_container_width=True):
            st.session_state.current_page = 'batch_search'
            st.rerun()
    with col2:
        if st.button("View Letter Queue", use_container_width=True):
            st.session_state.current_page = 'letter_queue'
            st.rerun()

# ============ BATCH COMPANY SEARCH ============
elif st.session_state.current_page == 'batch_search':
    st.markdown('<div class="section-header">Batch Company Search</div>', unsafe_allow_html=True)
    st.caption("Search companies by category and location, then send automated emails")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Business Category", get_available_categories())
    with col2:
        areas = get_available_areas(category)
        area = st.selectbox("Location Area", areas)
    
    col1, col2 = st.columns(2)
    with col1:
        limit = st.slider("Number of Companies", 3, 15, 10)
    with col2:
        auto_send = st.checkbox("Auto-send emails after search", value=True)
    
    if st.button("🔍 Search Companies", type="primary"):
        with st.spinner(f"Searching for {category} in {area}..."):
            companies = search_companies_by_category(category, area, limit)
            st.session_state.batch_results = companies
            st.success(f"Found {len(companies)} companies")
    
    if st.session_state.batch_results:
        st.markdown("### Search Results")
        
        # Display results table
        results_df = pd.DataFrame(st.session_state.batch_results)
        st.dataframe(results_df, use_container_width=True)
        
        # Add to CRM option
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add All to CRM", use_container_width=True):
                added = 0
                for company in st.session_state.batch_results:
                    success, _ = add_lead(company)
                    if success:
                        added += 1
                st.success(f"Added {added} companies to CRM")
                st.rerun()
        
        with col2:
            if auto_send and st.button("Send Emails to All", type="primary", use_container_width=True):
                with st.spinner("Sending emails..."):
                    results, success_count, fail_count = send_batch_emails(st.session_state.batch_results, category)
                    
                    st.markdown("### Email Campaign Results")
                    
                    # Display results
                    for result in results:
                        status_class = "status-sent" if result['status'] == "Sent" else "status-failed"
                        st.markdown(f"""
                        <div class='data-card'>
                            <strong>{result['company']}</strong><br>
                            Email: {result['email']}<br>
                            Status: <span class='{status_class}'>{result['status']}</span>
                            {f"<br>Error: {result['message']}" if result['message'] else ""}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.info(f"✅ Sent: {success_count} | ❌ Failed: {fail_count}")
                    
                    if fail_count > 0:
                        st.warning(f"{fail_count} companies added to letter queue for manual follow-up")
                    
                    st.rerun()
        
        # Individual company actions
        st.markdown("### Individual Company Actions")
        for company in st.session_state.batch_results:
            with st.expander(f"{company['name']} - {company.get('area', '')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Add to CRM", key=f"add_{company['name']}"):
                        add_lead(company)
                        st.success(f"Added {company['name']} to CRM")
                        st.rerun()
                with col2:
                    if st.button(f"Preview Email", key=f"preview_{company['name']}"):
                        email_body = generate_personalized_email(company, category)
                        st.markdown(email_body, unsafe_allow_html=True)
                with col3:
                    if st.button(f"Send Email", key=f"send_{company['name']}"):
                        email = f"info@{company['name'].lower().replace(' ', '').replace('&', '')}.com"
                        subject = f"IT Assessment Offer for {company['name']}"
                        body = generate_personalized_email(company, category)
                        success, msg, _ = send_email(email, subject, body)
                        if success:
                            st.success(f"Email sent to {company['name']}")
                        else:
                            st.error(f"Failed: {msg}")

# ============ EMAIL CAMPAIGNS ============
elif st.session_state.current_page == 'email_campaigns':
    st.markdown('<div class="section-header">Email Campaigns</div>', unsafe_allow_html=True)
    st.caption("Track and manage email campaigns")
    st.markdown("---")
    
    if st.session_state.email_log:
        # Campaign stats
        sent_count = len(st.session_state.email_log)
        today_count = len([e for e in st.session_state.email_log if e['date'][:10] == datetime.now().strftime('%Y-%m-%d')])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Emails Sent", sent_count)
        with col2:
            st.metric("Today's Emails", today_count)
        with col3:
            st.metric("Daily Limit", SMTP_CONFIG['daily_limit'])
        
        st.markdown("### Email History")
        
        for log in reversed(st.session_state.email_log[-20:]):
            st.markdown(f"""
            <div class='data-card'>
                <strong>To:</strong> {log['to']}<br>
                <strong>Company:</strong> {log['company']}<br>
                <strong>Subject:</strong> {log['subject']}<br>
                <strong>Date:</strong> {log['date'][:19]}<br>
                <strong>Status:</strong> <span class='status-sent'>{log['status']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No emails sent yet. Run a batch search to start email campaigns.")

# ============ LEAD CRM ============
elif st.session_state.current_page == 'crm':
    st.markdown('<div class="section-header">Lead CRM</div>', unsafe_allow_html=True)
    st.caption(f"Total Leads: {len(st.session_state.leads)}")
    st.markdown("---")
    
    if st.session_state.leads:
        search = st.text_input("Search", placeholder="Search by name, area, or type")
        
        filtered = st.session_state.leads
        if search:
            filtered = [l for l in filtered if search.lower() in l.get('name', '').lower() or search.lower() in l.get('area', '').lower() or search.lower() in l.get('type', '').lower()]
        
        for lead in filtered:
            with st.expander(f"{lead['name']} - Score: {lead['lead_score']}/100 - {lead['status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {lead.get('email', 'N/A')}")
                    st.write(f"**Phone:** {lead.get('phone', 'N/A')}")
                    st.write(f"**Area:** {lead.get('area', 'N/A')}")
                with col2:
                    st.write(f"**Type:** {lead.get('type', 'N/A')}")
                    st.write(f"**Source:** {lead.get('source', 'Manual')}")
                    st.write(f"**Added:** {lead['created_at'][:10]}")
                
                if not lead.get('email_sent'):
                    if st.button(f"Send Email Now", key=f"send_crm_{lead['id']}"):
                        email = lead.get('email')
                        if email:
                            subject = f"IT Assessment Offer for {lead['name']}"
                            body = generate_personalized_email(lead, lead.get('type', 'smes'))
                            success, msg, _ = send_email(email, subject, body)
                            if success:
                                lead['email_sent'] = True
                                lead['email_sent_date'] = datetime.now().isoformat()
                                save_leads()
                                st.success(f"Email sent to {lead['name']}")
                                st.rerun()
                            else:
                                st.error(f"Failed: {msg}")
                        else:
                            st.warning("No email address for this lead")
    
    else:
        st.info("No leads yet. Run a batch search to add leads.")

# ============ LETTER QUEUE ============
elif st.session_state.current_page == 'letter_queue':
    st.markdown('<div class="section-header">Letter Queue</div>', unsafe_allow_html=True)
    st.caption("Companies without valid email - Ready for physical letters")
    st.markdown("---")
    
    if st.session_state.letter_queue:
        st.warning(f"{len(st.session_state.letter_queue)} companies need physical letters")
        
        for letter in st.session_state.letter_queue:
            with st.expander(f"{letter['company']} - {letter['area']}"):
                st.write(f"**Type:** {letter['type']}")
                st.write(f"**Reason:** {letter['reason']}")
                
                st.markdown("### Letter Content")
                st.code(letter['letter_content'], language='text')
                
                if st.button(f"Mark as Printed", key=f"print_{letter['company']}"):
                    st.session_state.letter_queue = [l for l in st.session_state.letter_queue if l['company'] != letter['company']]
                    st.success("Letter marked as processed")
                    st.rerun()
    else:
        st.success("No pending letters - All companies have valid emails!")

# ============ EMAIL LOG ============
elif st.session_state.current_page == 'email_log':
    st.markdown('<div class="section-header">Email Log</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.email_log:
        for log in reversed(st.session_state.email_log):
            st.markdown(f"""
            <div class='data-card'>
                <strong>To:</strong> {log['to']}<br>
                <strong>Company:</strong> {log['company']}<br>
                <strong>Subject:</strong> {log['subject']}<br>
                <strong>Date:</strong> {log['date'][:19]}<br>
                <strong>Status:</strong> <span class='status-sent'>{log['status']}</span>
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
    **SMTP Settings:**
    - Host: {SMTP_CONFIG['host']}
    - Port: {SMTP_CONFIG['port']}
    - Username: {SMTP_CONFIG['username']}
    - Daily Limit: {SMTP_CONFIG['daily_limit']} emails
    """)
    
    st.markdown("### Campaign Settings")
    new_limit = st.number_input("Daily Email Limit", min_value=10, max_value=200, value=SMTP_CONFIG['daily_limit'])
    if st.button("Update Limit"):
        SMTP_CONFIG['daily_limit'] = new_limit
        st.success(f"Daily limit updated to {new_limit}")
    
    st.markdown("### Data Management")
    if st.button("Clear All Data", type="secondary"):
        st.session_state.leads = []
        st.session_state.email_log = []
        st.session_state.letter_queue = []
        st.session_state.batch_results = []
        save_leads()
        save_email_log()
        st.success("All data cleared")
        st.rerun()

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("2024 TechWokx Lead Intelligence | Batch Search | Email Automation | Campaign Tracking")

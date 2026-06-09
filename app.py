import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
if 'email_log' not in st.session_state:
    st.session_state.email_log = []
if 'last_research' not in st.session_state:
    st.session_state.last_research = None

# Create data directory and ensure leads.json exists
os.makedirs("data", exist_ok=True)

# Load leads from file if exists
leads_file = "data/leads.json"
if os.path.exists(leads_file):
    try:
        with open(leads_file, "r") as f:
            loaded_leads = json.load(f)
            if loaded_leads:
                st.session_state.leads = loaded_leads
    except Exception as e:
        print(f"Error loading leads: {e}")

# Email log file
email_log_file = "data/email_log.json"
if os.path.exists(email_log_file):
    try:
        with open(email_log_file, "r") as f:
            loaded_log = json.load(f)
            if loaded_log:
                st.session_state.email_log = loaded_log
    except Exception as e:
        print(f"Error loading email log: {e}")

# Login credentials
USERS = {
    "hello@techwokx.online": {
        "password": "Gtech.5628!@#$",
        "role": "admin",
        "name": "TechWokx Admin"
    }
}

# SMTP Configuration
SMTP_CONFIG = {
    "host": "smtp.hostinger.com",
    "port": 465,
    "username": "hello@techwokx.online",
    "password": "Gtech.5628!@#$",
    "use_ssl": True
}

def save_leads():
    """Save leads to file"""
    try:
        with open("data/leads.json", "w") as f:
            json.dump(st.session_state.leads, f, default=str, indent=2)
        return True
    except Exception as e:
        print(f"Error saving leads: {e}")
        return False

def save_email_log():
    """Save email log to file"""
    try:
        with open("data/email_log.json", "w") as f:
            json.dump(st.session_state.email_log, f, default=str, indent=2)
    except Exception as e:
        print(f"Error saving email log: {e}")

def add_lead(lead_data):
    """Add lead to CRM with notification"""
    # Check if lead already exists (by name or website)
    existing = False
    existing_lead = None
    for lead in st.session_state.leads:
        if lead.get('name') == lead_data.get('name') or lead.get('website') == lead_data.get('website'):
            existing = True
            existing_lead = lead
            break
    
    if existing:
        st.warning(f"⚠️ {lead_data.get('name')} already exists in CRM!")
        st.info(f"View existing lead in the CRM tab")
        return None
    
    # Create new lead
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
        "description": lead_data.get("description", ""),
        "linkedin_search_url": lead_data.get("linkedin_search_url", ""),
        "created_at": datetime.now().isoformat(),
        "status": "New",
        "email_sent": False,
        "email_sent_date": None,
        "email_opened": False,
        "email_responded": False,
        "followup_date": None,
        "followup_count": 0
    }
    
    st.session_state.leads.append(lead)
    save_success = save_leads()
    
    if save_success:
        st.success(f"✅ {lead_data.get('name')} added to CRM successfully!")
        st.balloons()
    else:
        st.error("⚠️ Lead added to memory but file save failed. Check file permissions.")
    
    return lead

def update_lead_email_status(lead_id, action):
    """Update email status for a lead"""
    for lead in st.session_state.leads:
        if lead['id'] == lead_id:
            if action == "sent":
                lead['email_sent'] = True
                lead['email_sent_date'] = datetime.now().isoformat()
                lead['followup_date'] = (datetime.now() + timedelta(days=3)).isoformat()
                lead['followup_count'] = 1
            elif action == "opened":
                lead['email_opened'] = True
            elif action == "responded":
                lead['email_responded'] = True
            save_leads()
            return True
    return False

def get_leads_needing_followup():
    """Get leads that need follow-up"""
    now = datetime.now()
    needs_followup = []
    for lead in st.session_state.leads:
        if lead.get('email_sent') and not lead.get('email_responded'):
            if lead.get('followup_date'):
                try:
                    followup_date = datetime.fromisoformat(lead['followup_date'])
                    if now >= followup_date:
                        needs_followup.append(lead)
                except:
                    pass
    return needs_followup

# Get API keys from secrets
def get_api_keys():
    try:
        return {
            "serp_api": st.secrets.get("SERP_API_KEY", ""),
            "openai": st.secrets.get("OPENAI_API_KEY", "")
        }
    except:
        return {"serp_api": "", "openai": ""}

# ============ COMPANY RESEARCH FUNCTIONS ============

def search_google_serp(api_key, business_name, location="Ghana"):
    """Search Google SERP for business information"""
    if not api_key:
        return None
    
    try:
        url = "https://serpapi.com/search"
        params = {
            "api_key": api_key,
            "q": f"{business_name} {location}",
            "location": location,
            "engine": "google"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        result = {
            "name": business_name,
            "website": None,
            "description": None,
            "address": None,
            "phone": None,
            "linkedin_url": None
        }
        
        if "knowledge_graph" in data:
            kg = data["knowledge_graph"]
            result["name"] = kg.get("title", result["name"])
            result["website"] = kg.get("website", "")
            result["description"] = kg.get("description", "")
            result["address"] = kg.get("address", "")
            result["phone"] = kg.get("phone", "")
        
        if "organic_results" in data and not result["description"]:
            for org in data["organic_results"][:2]:
                if org.get("snippet"):
                    result["description"] = org.get("snippet")
                    break
        
        return result
    except Exception as e:
        return None

def crawl_website_for_emails(website):
    """Deep crawl website to find emails"""
    if not website:
        return {"all_emails": [], "primary_email": None}
    
    all_emails = []
    try:
        if not website.startswith("http"):
            website = "https://" + website
        
        pages_to_check = [website, website + "/contact", website + "/about", website + "/team"]
        
        for page_url in pages_to_check[:3]:
            try:
                response = requests.get(page_url, timeout=10, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, response.text)
                
                exclude = ['example', 'test', 'noreply', 'placeholder', 'jpg', 'png', 'css', 'js']
                valid_emails = [e for e in emails if not any(x in e.lower() for x in exclude)]
                all_emails.extend(valid_emails)
            except:
                continue
        
        all_emails = list(set(all_emails))
        
        business_keywords = ['info', 'contact', 'hello', 'support', 'sales', 'admin', 'enquiries']
        business_emails = [e for e in all_emails if any(kw in e.lower() for kw in business_keywords)]
        
        return {
            "all_emails": all_emails[:5],
            "primary_email": business_emails[0] if business_emails else (all_emails[0] if all_emails else None)
        }
    except Exception as e:
        return {"all_emails": [], "primary_email": None}

def find_contact_person(website):
    """Try to find contact person from website"""
    if not website:
        return []
    
    contacts = []
    try:
        if not website.startswith("http"):
            website = "https://" + website
        
        response = requests.get(website, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        about_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if 'about' in href or 'team' in href or 'management' in href:
                full_url = urljoin(website, link.get('href'))
                about_links.append(full_url)
        
        if about_links:
            try:
                about_response = requests.get(about_links[0], timeout=10)
                
                titles = ['CEO', 'Managing Director', 'General Manager', 'Founder', 'Director', 'Manager', 'IT Manager', 'CTO']
                for title in titles:
                    pattern = rf'([A-Z][a-z]+ [A-Z][a-z]+).*?{title}'
                    matches = re.findall(pattern, about_response.text, re.IGNORECASE)
                    for match in matches[:1]:
                        contacts.append({"name": match, "title": title, "source": "About Page"})
            except:
                pass
        
        return contacts[:2]
    except Exception as e:
        return []

def check_website_status(url):
    """Check if website is accessible"""
    if not url:
        return {"reachable": False, "error": "No website"}
    
    try:
        if not url.startswith("http"):
            url = "https://" + url
        
        start_time = datetime.now()
        response = requests.get(url, timeout=10, verify=True)
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "reachable": response.status_code == 200,
            "status_code": response.status_code,
            "response_time": response_time,
            "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
        }
    except Exception as e:
        return {"reachable": False, "error": str(e)[:50], "response_time": None}

def deep_research_company(company_name, serp_api_key=None, openai_api_key=None):
    """Perform deep research using Google Search"""
    
    result = {
        "name": company_name,
        "website": None,
        "email": None,
        "phone": None,
        "address": None,
        "description": None,
        "contacts": [],
        "linkedin_search_url": f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace(' ', '%20')}",
        "website_status": None,
        "ai_insights": None,
        "lead_score": 0,
        "recommendations": [],
        "sources": []
    }
    
    # Step 1: Google Search via SERP API
    if serp_api_key:
        serp_data = search_google_serp(serp_api_key, company_name)
        if serp_data:
            result["name"] = serp_data.get("name", result["name"])
            result["website"] = serp_data.get("website")
            result["address"] = serp_data.get("address")
            result["phone"] = serp_data.get("phone")
            result["description"] = serp_data.get("description")
            result["sources"].append("Google Search")
    
    # Step 2: Check website status
    if result["website"]:
        result["website_status"] = check_website_status(result["website"])
        
        # Step 3: Crawl website for emails
        email_data = crawl_website_for_emails(result["website"])
        if email_data and email_data.get("primary_email"):
            result["email"] = email_data["primary_email"]
            result["sources"].append("Website Crawl")
        
        # Step 4: Find contact persons
        contacts = find_contact_person(result["website"])
        if contacts:
            result["contacts"] = contacts
            result["sources"].append("Website")
    
    # Calculate lead score
    score = 0
    if result["website"]:
        score += 20
        if result["website_status"] and result["website_status"].get("reachable"):
            score += 15
    if result["address"]:
        score += 10
    if result["phone"]:
        score += 10
    if result["email"]:
        score += 25
    if result["contacts"]:
        score += 15
    if result["description"]:
        score += 5
    result["lead_score"] = min(score, 100)
    
    # Generate recommendations
    recs = []
    if result["phone"]:
        recs.append(f"📞 Call {result['phone']} - Ask for IT decision maker")
    if not result["email"]:
        recs.append("📧 No email found - Try deep crawl button")
    if not result["contacts"]:
        recs.append("👤 Find decision maker - Use LinkedIn search above")
    recs.append("📊 Schedule free IT consultation")
    result["recommendations"] = recs[:4]
    
    return result

# ============ EMAIL FUNCTIONS ============

def send_email(to_email, subject, body):
    """Send email using SMTP"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
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
        
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

def generate_proposal_email(company_data, contact_person=None):
    """Generate personalized proposal email with audit link"""
    
    audit_link = "https://techwokx.online/#audit"
    
    if contact_person and contact_person.get('name'):
        salutation = f"Dear {contact_person['name']}"
    elif company_data.get('contacts') and company_data['contacts'][0].get('name'):
        salutation = f"Dear {company_data['contacts'][0]['name']}"
    else:
        salutation = "Dear Management Team"
    
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; }}
            .score {{ font-size: 2rem; font-weight: bold; color: #667eea; text-align: center; }}
            .audit-box {{ background: #f0fdf4; border: 2px solid #22c55e; border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0; }}
            .button {{ background: #22c55e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🔍 TechWokx IT Assessment</h2>
            </div>
            <div class="content">
                {salutation},<br><br>
                
                <p>I recently reviewed <strong>{company_data['name']}</strong>'s online presence and identified opportunities to improve your IT infrastructure.</p>
                
                <div class="score">
                    Lead Score: {company_data['lead_score']}/100
                </div>
                
                <h3>📊 Key Findings:</h3>
                <ul>
                    <li><strong>Website:</strong> {company_data.get('website', 'Not found')}</li>
                    <li><strong>Email:</strong> {'Configured' if company_data.get('email') else 'Not configured'}</li>
                    <li><strong>Contact Info:</strong> {'Complete' if company_data.get('phone') else 'Missing'}</li>
                </ul>
                
                <div class="audit-box">
                    <h3>📋 Free Email Security Audit</h3>
                    <a href="{audit_link}" class="button">🚀 Run Free Audit →</a>
                    <p style="font-size: 12px; margin-top: 10px;">or visit: {audit_link}</p>
                </div>
                
                <h3>🚀 Recommended Next Steps:</h3>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in company_data.get('recommendations', [])[:3]])}
                </ul>
                
                <p>Best regards,<br>
                <strong>George Jabley</strong><br>
                TechWokx Ghana<br>
                <a href="https://techwokx.online">techwokx.online</a> | +233 555 087 407
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return body

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
    </div>
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
        ("📧 COMMUNICATIONS", "header2"),
        ("📤 Send Email", "send_email"),
        ("📊 Email Log", "email_log"),
        ("🔄 Follow-ups", "followups"),
        ("---", "divider2"),
        ("⚙️ Settings", "settings"),
        ("🚪 Logout", "logout")
    ]
    
    for label, key in nav_items:
        if label == "---":
            st.markdown("---")
        elif label.startswith("📋") or label.startswith("📧"):
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
    st.markdown(f"📧 SMTP: ✅")
    st.markdown(f"📊 Leads: {len(st.session_state.leads)}")
    
    needs_followup = get_leads_needing_followup()
    if needs_followup:
        st.markdown(f"⚠️ {len(needs_followup)} need follow-up")

# ============ DASHBOARD ============
if st.session_state.page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>🤖 TechWokx Enterprise Suite</h2>
        <p>AI-powered Company Research | Lead Intelligence | Email Automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    total_leads = len(st.session_state.leads)
    hot_leads = sum(1 for l in st.session_state.leads if l.get("lead_score", 0) >= 70)
    emails_sent = len(st.session_state.email_log)
    need_followup = len(get_leads_needing_followup())
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_leads}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot_leads}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{emails_sent}</div><div class='metric-label'>Emails Sent</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{need_followup}</div><div class='metric-label'>Need Follow-up</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Recent Leads</div>', unsafe_allow_html=True)
        if st.session_state.leads:
            for lead in st.session_state.leads[-5:]:
                status_class = "status-hot" if lead.get("lead_score", 0) >= 70 else "status-warm" if lead.get("lead_score", 0) >= 50 else "status-cold"
                st.markdown(f"<div class='data-card'><strong>{lead['name']}</strong> - Score: {lead['lead_score']}/100 <span class='status-badge {status_class}'>{lead['status']}</span><br><small>Added: {lead['created_at'][:10]}</small></div>", unsafe_allow_html=True)
        else:
            st.info("No leads yet. Research companies to get started.")
    
    with col2:
        st.markdown('<div class="section-header">🚀 Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍 Research Company", use_container_width=True):
            st.session_state.page = 'company_research'
            st.rerun()
        if st.button("📧 Send Email", use_container_width=True):
            st.session_state.page = 'send_email'
            st.rerun()
        if st.button("👥 View CRM", use_container_width=True):
            st.session_state.page = 'crm'
            st.rerun()

# ============ COMPANY RESEARCH PAGE ============
elif st.session_state.page == 'company_research':
    st.markdown('<div class="section-header">🔍 Deep Company Research</div>', unsafe_allow_html=True)
    st.caption("Powered by Google Search - Finds real company data with website crawling")
    st.markdown("---")
    
    api_keys = get_api_keys()
    
    if not api_keys["serp_api"]:
        st.warning("⚠️ SERP API key missing. Add to .streamlit/secrets.toml")
        st.info("Get your key from https://serpapi.com/")
    
    company_name = st.text_input("Company Name", placeholder="e.g. Prime Meridian Docks, MTN Ghana")
    
    if st.button("🔍 Deep Research", type="primary"):
        if company_name:
            with st.spinner(f"Researching {company_name}..."):
                result = deep_research_company(
                    company_name, 
                    serp_api_key=api_keys["serp_api"],
                    openai_api_key=api_keys["openai"]
                )
                
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
                
                # Deep crawl button
                if result['website'] and not result['email']:
                    if st.button("🔄 Deep Crawl Website for Email"):
                        with st.spinner(f"Deep crawling {result['website']}..."):
                            email_data = crawl_website_for_emails(result['website'])
                            if email_data and email_data.get('primary_email'):
                                result['email'] = email_data['primary_email']
                                st.success(f"✅ Found email: {result['email']}")
                                st.rerun()
                            else:
                                st.warning("No email found after deep crawl")
                
                # Contacts Found
                if result['contacts']:
                    st.markdown("### 👤 Contacts Found")
                    for contact in result['contacts']:
                        st.markdown(f"""
                        <div class="data-card">
                            <strong>{contact.get('name', 'Name found')}</strong><br>
                            Title: {contact.get('title', 'Staff')}<br>
                            Source: {contact.get('source', 'Website')}
                        </div>
                        """, unsafe_allow_html=True)
                
                # LinkedIn Search
                st.markdown(f"""
                <div class="data-card">
                    <h4>🔗 LinkedIn Search</h4>
                    <a href="{result['linkedin_search_url']}" target="_blank">Search LinkedIn for {result['name']} →</a>
                </div>
                """, unsafe_allow_html=True)
                
                # Description
                if result['description']:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>📝 Business Description</h4>
                        <p>{result['description'][:500]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Website Status
                if result['website_status']:
                    status_icon = "✅" if result['website_status'].get('reachable') else "❌"
                    status_text = "Online" if result['website_status'].get('reachable') else "Down"
                    response_time = result['website_status'].get('response_time')
                    response_display = f"{response_time:.0f}ms" if response_time and isinstance(response_time, (int, float)) else "N/A"
                    
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>🌐 Website Status</h4>
                        <p><strong>Status:</strong> {status_icon} {status_text}</p>
                        <p><strong>Response Time:</strong> {response_display}</p>
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
                
                # Recommendations
                st.markdown(f"""
                <div class="data-card">
                    <h4>🚀 Recommendations</h4>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in result['recommendations']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➕ Add to CRM", use_container_width=True, type="primary"):
                        add_lead(result)
                        st.rerun()
                
                with col2:
                    if result.get('email'):
                        if st.button("📧 Send Email", use_container_width=True):
                            st.session_state.proposal_lead = result
                            st.session_state.page = 'send_email'
                            st.rerun()
        else:
            st.warning("Please enter a company name")

# ============ LEAD CRM PAGE ============
elif st.session_state.page == 'crm':
    st.markdown('<div class="section-header">👥 Lead CRM</div>', unsafe_allow_html=True)
    st.caption("All researched leads")
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
                    for contact in lead['contacts']:
                        st.write(f"- {contact.get('name', 'Name')} ({contact.get('title', 'Staff')})")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📧 Send Email", key=f"email_{lead['id']}"):
                        st.session_state.proposal_lead = lead
                        st.session_state.page = 'send_email'
                        st.rerun()
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_{lead['id']}"):
                        st.session_state.leads = [l for l in st.session_state.leads if l['id'] != lead['id']]
                        save_leads()
                        st.success(f"Deleted {lead['name']}")
                        st.rerun()
    else:
        st.info("No leads yet. Research companies to add to CRM.")
        if st.button("Go to Company Research"):
            st.session_state.page = 'company_research'
            st.rerun()

# ============ SEND EMAIL PAGE ============
elif st.session_state.page == 'send_email':
    st.markdown('<div class="section-header">📧 Send Email</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    leads = st.session_state.leads
    if leads:
        lead_options = {f"{l['name']} (Score: {l['lead_score']}/100)": l for l in leads}
        
        if st.session_state.get('proposal_lead'):
            default_lead = f"{st.session_state.proposal_lead['name']} (Score: {st.session_state.proposal_lead['lead_score']}/100)"
        else:
            default_lead = list(lead_options.keys())[0] if lead_options else None
        
        selected = st.selectbox("Select Lead", list(lead_options.keys()), index=0 if default_lead else None)
        lead = lead_options[selected]
        
        recipient_email = lead.get('email', '')
        to_email = st.text_input("To Email", value=recipient_email)
        
        if to_email:
            st.markdown("### Email Preview")
            contact_person = lead.get('contacts', [{}])[0] if lead.get('contacts') else None
            email_body = generate_proposal_email(lead, contact_person)
            st.markdown(email_body, unsafe_allow_html=True)
            
            if st.button("📤 Send Email", type="primary"):
                subject = f"IT Assessment for {lead['name']} - Score: {lead['lead_score']}/100"
                success, msg = send_email(to_email, subject, email_body)
                if success:
                    update_lead_email_status(lead['id'], "sent")
                    st.session_state.email_log.append({
                        "to": to_email,
                        "company": lead['name'],
                        "date": datetime.now().isoformat(),
                        "status": "Sent"
                    })
                    save_email_log()
                    st.success(f"✅ Email sent to {to_email}!")
                else:
                    st.error(f"❌ Failed: {msg}")
        else:
            st.warning("No email address for this lead. Add email or use LinkedIn search.")
    else:
        st.info("No leads in CRM. Research companies first.")

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

# ============ FOLLOW-UPS PAGE ============
elif st.session_state.page == 'followups':
    st.markdown('<div class="section-header">🔄 Follow-up Management</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    needs_followup = get_leads_needing_followup()
    
    if needs_followup:
        st.warning(f"⚠️ {len(needs_followup)} leads need follow-up")
        for lead in needs_followup:
            with st.expander(f"{lead['name']} - Email sent on {lead.get('email_sent_date', '')[:10]}"):
                st.write(f"**Email:** {lead.get('email', 'N/A')}")
                st.write(f"**Phone:** {lead.get('phone', 'N/A')}")
                if st.button(f"📧 Send Follow-up", key=f"followup_{lead['id']}"):
                    st.session_state.proposal_lead = lead
                    st.session_state.page = 'send_email'
                    st.rerun()
    else:
        st.success("✅ No leads need follow-up at this time")

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
    
    st.markdown("### Data Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear All Leads", type="secondary"):
            st.session_state.leads = []
            save_leads()
            st.success("All leads cleared!")
            st.rerun()
    with col2:
        if st.button("Export Leads to CSV"):
            if st.session_state.leads:
                df = pd.DataFrame(st.session_state.leads)
                csv = df.to_csv(index=False)
                st.download_button("Download CSV", csv, "leads_export.csv", "text/csv")
            else:
                st.warning("No leads to export")

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Enterprise Suite | Email: hello@techwokx.online")

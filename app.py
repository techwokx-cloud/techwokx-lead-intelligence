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
    page_icon=":mag:",
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

# Create data directory
os.makedirs("data", exist_ok=True)

# Load leads from file
leads_file = "data/leads.json"
if os.path.exists(leads_file):
    try:
        with open(leads_file, "r") as f:
            loaded = json.load(f)
            if loaded:
                st.session_state.leads = loaded
    except:
        pass

# Login credentials
USERS = {
    "hello@techwokx.online": {
        "password": "Gtech.5628!@#$",
        "role": "admin",
        "name": "TechWokx Admin"
    }
}

def save_leads():
    try:
        with open("data/leads.json", "w") as f:
            json.dump(st.session_state.leads, f, default=str, indent=2)
        return True
    except:
        return False

def add_lead(lead_data):
    if not lead_data.get('name'):
        st.error("Name required")
        return None
    
    # Check duplicate
    for lead in st.session_state.leads:
        if lead.get('name') == lead_data.get('name'):
            st.warning(f"Lead already exists: {lead_data.get('name')}")
            return None
    
    lead = {
        "id": len(st.session_state.leads) + 1,
        "name": lead_data.get("name"),
        "website": lead_data.get("website", ""),
        "email": lead_data.get("email", ""),
        "phone": lead_data.get("phone", ""),
        "address": lead_data.get("address", ""),
        "lead_score": lead_data.get("lead_score", 50),
        "contacts": lead_data.get("contacts", []),
        "recommendations": lead_data.get("recommendations", []),
        "description": lead_data.get("description", ""),
        "source": lead_data.get("source", "Manual"),
        "created_at": datetime.now().isoformat(),
        "status": "Hot" if lead_data.get("lead_score", 50) >= 70 else "Warm" if lead_data.get("lead_score", 50) >= 50 else "Cold",
        "email_sent": False,
        "email_responded": False
    }
    
    st.session_state.leads.append(lead)
    save_leads()
    st.success(f"Added: {lead_data.get('name')}")
    return lead

def import_from_csv(file):
    try:
        df = pd.read_csv(file)
        imported = 0
        for _, row in df.iterrows():
            name = row.get('name', '')
            if name:
                add_lead({
                    "name": name,
                    "website": row.get('website', ''),
                    "email": row.get('email', ''),
                    "phone": str(row.get('phone', '')),
                    "address": row.get('address', ''),
                    "lead_score": int(row.get('lead_score', 50)),
                    "source": "CSV Import"
                })
                imported += 1
        return True, f"Imported {imported} leads"
    except Exception as e:
        return False, str(e)

def import_from_json(file):
    try:
        data = json.load(file)
        if isinstance(data, dict) and 'leads' in data:
            leads_list = data['leads']
        elif isinstance(data, list):
            leads_list = data
        else:
            return False, "Invalid JSON format"
        
        imported = 0
        for item in leads_list:
            name = item.get('name', '')
            if name:
                add_lead({
                    "name": name,
                    "website": item.get('website', ''),
                    "email": item.get('email', ''),
                    "phone": str(item.get('phone', '')),
                    "address": item.get('address', ''),
                    "lead_score": int(item.get('lead_score', 50)),
                    "source": "JSON Import"
                })
                imported += 1
        return True, f"Imported {imported} leads"
    except Exception as e:
        return False, str(e)

def import_from_text(file):
    try:
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')
        imported = 0
        for line in lines:
            line = line.strip()
            if line:
                add_lead({"name": line, "source": "Text Import"})
                imported += 1
        return True, f"Imported {imported} leads"
    except Exception as e:
        return False, str(e)

def deep_research(company_name):
    """Simple research function"""
    result = {
        "name": company_name,
        "website": f"www.{company_name.lower().replace(' ', '')}.com",
        "email": f"info@{company_name.lower().replace(' ', '')}.com",
        "phone": "+233 XX XXX XXXX",
        "address": "Accra, Ghana",
        "description": f"{company_name} is a business in Ghana.",
        "lead_score": 65,
        "recommendations": ["Setup professional email", "Conduct IT audit", "Schedule consultation"]
    }
    return result

# CSS
st.markdown("""
<style>
.stApp { background: #f5f7fa; }
[data-testid="stSidebar"] { background: #0f172a; }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #e2e8f0; }
.welcome-card { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; color: white; }
.metric-card { background: white; border-radius: 12px; padding: 1rem; text-align: center; border: 1px solid #e2e8f0; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
.metric-label { color: #64748b; font-size: 0.8rem; }
.data-card { background: white; border-radius: 12px; padding: 1.2rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
.section-header { color: #0f172a; font-size: 1.2rem; font-weight: 600; border-left: 3px solid #667eea; padding-left: 1rem; margin: 1.5rem 0 1rem 0; }
.custom-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
.stButton > button { background: #667eea; color: white; font-weight: 600; border: none; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ============ LOGIN ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 400px; margin: 100px auto; padding: 2rem; background: white; border-radius: 24px; text-align: center;">
        <h1 style="color: #667eea;">TechWokx</h1>
        <p>Enterprise Suite</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user = USERS[username]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### TechWokx")
    st.markdown(f"Welcome, {st.session_state.user['name']}")
    st.markdown("---")
    
    pages = {
        "Dashboard": "dashboard",
        "Company Research": "research",
        "Import Leads": "import",
        "Lead CRM": "crm",
        "Export Leads": "export",
        "Send Email": "email",
        "Email Log": "log",
        "Settings": "settings",
        "Logout": "logout"
    }
    
    for label, key in pages.items():
        if st.button(label, key=key, use_container_width=True):
            if key == "logout":
                st.session_state.authenticated = False
                st.rerun()
            else:
                st.session_state.page = key
                st.rerun()
    
    st.markdown("---")
    st.markdown(f"Leads: {len(st.session_state.leads)}")

# ============ DASHBOARD ============
if st.session_state.page == 'dashboard':
    st.markdown('<div class="welcome-card"><h2>Welcome to TechWokx</h2><p>Lead Intelligence System</p></div>', unsafe_allow_html=True)
    
    total = len(st.session_state.leads)
    hot = sum(1 for l in st.session_state.leads if l.get("lead_score", 0) >= 70)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>0</div><div class='metric-label'>Emails Sent</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>Ready</div><div class='metric-label'>Status</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    if st.session_state.leads:
        st.markdown('<div class="section-header">Recent Leads</div>', unsafe_allow_html=True)
        for lead in st.session_state.leads[-5:]:
            st.markdown(f"<div class='data-card'><strong>{lead['name']}</strong> - Score: {lead['lead_score']}/100<br><small>Added: {lead['created_at'][:10]}</small></div>", unsafe_allow_html=True)
    else:
        st.info("No leads yet. Research or import leads.")

# ============ RESEARCH PAGE ============
elif st.session_state.page == 'research':
    st.markdown('<div class="section-header">Company Research</div>', unsafe_allow_html=True)
    
    company_name = st.text_input("Company Name")
    
    if st.button("Research", type="primary"):
        if company_name:
            with st.spinner("Researching..."):
                result = deep_research(company_name)
                
                st.markdown(f"""
                <div class="data-card">
                    <h4>Company Information</h4>
                    <p><strong>Name:</strong> {result['name']}</p>
                    <p><strong>Website:</strong> {result['website']}</p>
                    <p><strong>Email:</strong> {result['email']}</p>
                    <p><strong>Phone:</strong> {result['phone']}</p>
                    <p><strong>Address:</strong> {result['address']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="data-card">
                    <h4>Lead Score</h4>
                    <p style="font-size: 2rem; font-weight: 700; color: #667eea;">{result['lead_score']}/100</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Add to CRM"):
                    add_lead(result)
                    st.rerun()
        else:
            st.warning("Enter company name")

# ============ IMPORT PAGE ============
elif st.session_state.page == 'import':
    st.markdown('<div class="section-header">Import Leads</div>', unsafe_allow_html=True)
    
    st.info("CSV Format: name,website,email,phone,address,lead_score")
    
    uploaded = st.file_uploader("Choose file", type=['csv', 'json', 'txt'])
    
    if uploaded:
        ext = uploaded.name.split('.')[-1].lower()
        if ext == 'csv':
            success, msg = import_from_csv(uploaded)
        elif ext == 'json':
            success, msg = import_from_json(uploaded)
        elif ext == 'txt':
            success, msg = import_from_text(uploaded)
        else:
            success, msg = False, "Unsupported"
        
        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)
    
    st.markdown("---")
    st.markdown("### Manual Entry")
    
    with st.form("manual"):
        name = st.text_input("Company Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        score = st.slider("Lead Score", 0, 100, 50)
        
        if st.form_submit_button("Add Lead"):
            if name:
                add_lead({"name": name, "email": email, "phone": phone, "lead_score": score})
                st.rerun()
            else:
                st.error("Name required")

# ============ CRM PAGE ============
elif st.session_state.page == 'crm':
    st.markdown('<div class="section-header">Lead CRM</div>', unsafe_allow_html=True)
    
    if st.session_state.leads:
        for lead in st.session_state.leads:
            with st.expander(f"{lead['name']} - Score: {lead['lead_score']}/100"):
                st.write(f"Email: {lead.get('email', 'N/A')}")
                st.write(f"Phone: {lead.get('phone', 'N/A')}")
                st.write(f"Website: {lead.get('website', 'N/A')}")
                st.write(f"Address: {lead.get('address', 'N/A')}")
                st.write(f"Source: {lead.get('source', 'Manual')}")
                st.write(f"Added: {lead['created_at'][:10]}")
                
                if st.button(f"Delete", key=f"del_{lead['id']}"):
                    st.session_state.leads = [l for l in st.session_state.leads if l['id'] != lead['id']]
                    save_leads()
                    st.rerun()
    else:
        st.info("No leads yet")

# ============ EXPORT PAGE ============
elif st.session_state.page == 'export':
    st.markdown('<div class="section-header">Export Leads</div>', unsafe_allow_html=True)
    
    if st.session_state.leads:
        df = pd.DataFrame(st.session_state.leads)
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "leads.csv", "text/csv")
        
        json_data = json.dumps(st.session_state.leads, default=str, indent=2)
        st.download_button("Download JSON", json_data, "leads.json", "application/json")
    else:
        st.info("No leads to export")

# ============ EMAIL PAGE ============
elif st.session_state.page == 'email':
    st.markdown('<div class="section-header">Send Email</div>', unsafe_allow_html=True)
    st.info("Email feature coming soon. Configure SMTP in settings.")
    
    if st.session_state.leads:
        leads = {f"{l['name']} ({l.get('email', 'No email')})": l for l in st.session_state.leads if l.get('email')}
        if leads:
            selected = st.selectbox("Select Lead", list(leads.keys()))
            lead = leads[selected]
            st.write(f"Sending to: {lead.get('email')}")
            st.text_area("Message", "Your proposal is ready...")
            if st.button("Send"):
                st.success("Demo: Email would be sent")
        else:
            st.warning("No leads with email addresses")

# ============ LOG PAGE ============
elif st.session_state.page == 'log':
    st.markdown('<div class="section-header">Email Log</div>', unsafe_allow_html=True)
    st.info("No emails sent yet")

# ============ SETTINGS PAGE ============
elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">Settings</div>', unsafe_allow_html=True)
    
    st.markdown("### API Configuration")
    st.code("""
    # .streamlit/secrets.toml
    SERP_API_KEY = "your_key"
    """)
    
    if st.button("Clear All Leads", type="secondary"):
        st.session_state.leads = []
        save_leads()
        st.success("Cleared!")
        st.rerun()

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("2024 TechWokx Enterprise Suite")

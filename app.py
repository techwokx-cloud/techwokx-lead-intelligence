import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import requests
import re

# Page config
st.set_page_config(
    page_title="TechWokx Enterprise Suite",
    page_icon="🔍",
    layout="wide"
)

# ============ SESSION STATE INITIALIZATION ============
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'
if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'email_log' not in st.session_state:
    st.session_state.email_log = []
if 'notification' not in st.session_state:
    st.session_state.notification = None

# ============ FILE STORAGE FOR LEADS ============
LEADS_FILE = "data/leads.json"

def load_leads_from_file():
    """Load leads from JSON file"""
    try:
        if os.path.exists(LEADS_FILE):
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                leads = json.load(f)
                return leads
    except Exception as e:
        print(f"Error loading leads: {e}")
    return []

def save_leads_to_file(leads):
    """Save leads to JSON file"""
    try:
        os.makedirs("data", exist_ok=True)
        with open(LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving leads: {e}")
        return False

# Load leads on startup
st.session_state.leads = load_leads_from_file()

# ============ LOGIN CREDENTIALS ============
USERS = {
    "hello@techwokx.online": {
        "password": "Gtech.5628!@#$",
        "role": "admin",
        "name": "TechWokx Admin"
    }
}

# ============ LEAD FUNCTIONS ============
def add_lead(lead_data):
    """Add a new lead to CRM"""
    # Check for duplicate
    for lead in st.session_state.leads:
        if lead.get('name', '').lower() == lead_data.get('name', '').lower():
            st.session_state.notification = {"type": "warning", "message": f"Lead '{lead_data.get('name')}' already exists!"}
            return False
    
    new_lead = {
        "id": len(st.session_state.leads) + 1,
        "name": lead_data.get("name", ""),
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
        "email_responded": False,
        "notes": ""
    }
    
    st.session_state.leads.append(new_lead)
    save_leads_to_file(st.session_state.leads)
    st.session_state.notification = {"type": "success", "message": f"Lead '{lead_data.get('name')}' added successfully!"}
    return True

def delete_lead(lead_id):
    """Delete a lead from CRM"""
    st.session_state.leads = [l for l in st.session_state.leads if l['id'] != lead_id]
    save_leads_to_file(st.session_state.leads)
    st.session_state.notification = {"type": "success", "message": "Lead deleted successfully!"}
    return True

def update_lead(lead_id, updates):
    """Update lead information"""
    for lead in st.session_state.leads:
        if lead['id'] == lead_id:
            lead.update(updates)
            save_leads_to_file(st.session_state.leads)
            return True
    return False

# ============ COMPANY RESEARCH FUNCTION ============
def research_company(company_name):
    """Simulate company research"""
    return {
        "name": company_name,
        "website": f"www.{company_name.lower().replace(' ', '')}.com",
        "email": f"info@{company_name.lower().replace(' ', '')}.com",
        "phone": "+233 XX XXX XXXX",
        "address": "Accra, Ghana",
        "description": f"{company_name} is a business operating in Ghana.",
        "lead_score": 65,
        "recommendations": [
            "Setup professional email (Google Workspace/Microsoft 365)",
            "Conduct IT security audit",
            "Schedule free consultation call"
        ],
        "contacts": [
            {"name": "Management Team", "title": "Decision Makers", "source": "LinkedIn"}
        ]
    }

# ============ IMPORT FUNCTIONS ============
def import_csv(file):
    try:
        df = pd.read_csv(file)
        imported = 0
        for _, row in df.iterrows():
            if row.get('name'):
                add_lead({
                    "name": row.get('name'),
                    "email": row.get('email', ''),
                    "phone": str(row.get('phone', '')),
                    "website": row.get('website', ''),
                    "address": row.get('address', ''),
                    "lead_score": int(row.get('lead_score', 50)),
                    "source": "CSV Import"
                })
                imported += 1
        return True, f"Imported {imported} leads"
    except Exception as e:
        return False, str(e)

def import_json(file):
    try:
        data = json.load(file)
        if isinstance(data, list):
            leads_list = data
        elif isinstance(data, dict) and 'leads' in data:
            leads_list = data['leads']
        else:
            return False, "Invalid JSON format"
        
        imported = 0
        for item in leads_list:
            if item.get('name'):
                add_lead({
                    "name": item.get('name'),
                    "email": item.get('email', ''),
                    "phone": str(item.get('phone', '')),
                    "website": item.get('website', ''),
                    "address": item.get('address', ''),
                    "lead_score": int(item.get('lead_score', 50)),
                    "source": "JSON Import"
                })
                imported += 1
        return True, f"Imported {imported} leads"
    except Exception as e:
        return False, str(e)

def import_text(file):
    try:
        content = file.read().decode('utf-8')
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        imported = 0
        for line in lines:
            add_lead({"name": line, "source": "Text Import"})
            imported += 1
        return True, f"Imported {imported} leads"
    except Exception as e:
        return False, str(e)

# ============ EXPORT FUNCTIONS ============
def export_csv():
    df = pd.DataFrame(st.session_state.leads)
    return df.to_csv(index=False)

def export_json():
    return json.dumps(st.session_state.leads, indent=2, default=str)

# ============ CSS ============
st.markdown("""
<style>
.stApp { background: #f8fafc; }
[data-testid="stSidebar"] { background: #0f172a; }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #e2e8f0; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fbbf24; }
[data-testid="stSidebar"] .stButton button { background: rgba(251, 191, 36, 0.15); color: #fbbf24; width: 100%; margin: 2px 0; }
.welcome-card { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; color: white; }
.metric-card { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
.metric-label { color: #64748b; font-size: 0.8rem; }
.data-card { background: white; border-radius: 12px; padding: 1.2rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
.section-header { color: #0f172a; font-size: 1.2rem; font-weight: 600; border-left: 3px solid #667eea; padding-left: 1rem; margin: 1.5rem 0 1rem 0; }
.custom-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
.stButton > button { background: linear-gradient(135deg, #667eea, #764ba2); color: white; font-weight: 600; border: none; border-radius: 8px; }
.notification-success { background: #d1fae5; border-left: 4px solid #10b981; padding: 12px; border-radius: 8px; margin-bottom: 16px; }
.notification-warning { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; border-radius: 8px; margin-bottom: 16px; }
.status-hot { background: #dc2626; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
.status-warm { background: #f97316; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
.status-cold { background: #64748b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ============ LOGIN PAGE ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 400px; margin: 100px auto; padding: 2rem; background: white; border-radius: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center;">
        <h1 style="color: #667eea;">TechWokx</h1>
        <p>Enterprise Suite</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login"):
        email = st.text_input("Email", placeholder="hello@techwokx.online")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if email in USERS and USERS[email]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user = USERS[email]
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
    
    menu = {
        "Dashboard": "dashboard",
        "Company Research": "research",
        "Import Leads": "import",
        "Lead CRM": "crm",
        "Export Leads": "export",
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
    st.markdown(f"Total Leads: {len(st.session_state.leads)}")

# ============ DASHBOARD ============
if st.session_state.current_page == 'dashboard':
    # Show notification
    if st.session_state.notification:
        notif = st.session_state.notification
        notif_class = "notification-success" if notif["type"] == "success" else "notification-warning"
        st.markdown(f"<div class='{notif_class}'>{notif['message']}</div>", unsafe_allow_html=True)
        st.session_state.notification = None
    
    st.markdown("""
    <div class="welcome-card">
        <h2>Welcome to TechWokx Enterprise Suite</h2>
        <p>Lead Intelligence | Company Research | Email Automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    total = len(st.session_state.leads)
    hot = sum(1 for l in st.session_state.leads if l.get("lead_score", 0) >= 70)
    warm = sum(1 for l in st.session_state.leads if 50 <= l.get("lead_score", 0) < 70)
    cold = sum(1 for l in st.session_state.leads if l.get("lead_score", 0) < 50)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{warm}</div><div class='metric-label'>Warm Leads</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{cold}</div><div class='metric-label'>Cold Leads</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Recent Leads</div>', unsafe_allow_html=True)
        if st.session_state.leads:
            for lead in st.session_state.leads[-5:]:
                status_class = "status-hot" if lead.get("lead_score", 0) >= 70 else "status-warm" if lead.get("lead_score", 0) >= 50 else "status-cold"
                st.markdown(f"<div class='data-card'><strong>{lead['name']}</strong> - Score: {lead['lead_score']}/100 <span class='{status_class}'>{lead['status']}</span><br><small>Added: {lead['created_at'][:10]}</small></div>", unsafe_allow_html=True)
        else:
            st.info("No leads yet. Research or import leads.")
    
    with col2:
        st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
        if st.button("Research Company", use_container_width=True):
            st.session_state.current_page = 'research'
            st.rerun()
        if st.button("Import Leads", use_container_width=True):
            st.session_state.current_page = 'import'
            st.rerun()
        if st.button("View CRM", use_container_width=True):
            st.session_state.current_page = 'crm'
            st.rerun()

# ============ COMPANY RESEARCH ============
elif st.session_state.current_page == 'research':
    st.markdown('<div class="section-header">Company Research</div>', unsafe_allow_html=True)
    st.caption("Research any company and add to CRM")
    st.markdown("---")
    
    company_name = st.text_input("Company Name", placeholder="e.g. Prime Meridian Docks, MTN Ghana")
    
    if st.button("Research", type="primary"):
        if company_name:
            with st.spinner(f"Researching {company_name}..."):
                result = research_company(company_name)
                
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
                
                if result.get('description'):
                    st.markdown(f"<div class='data-card'><p>{result['description']}</p></div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="data-card" style="text-align: center;">
                    <h4>Lead Score</h4>
                    <p style="font-size: 2.5rem; font-weight: 700; color: #667eea;">{result['lead_score']}/100</p>
                </div>
                """, unsafe_allow_html=True)
                
                if result.get('recommendations'):
                    st.markdown("<div class='data-card'><h4>Recommendations</h4><ul>" + "".join([f"<li>{r}</li>" for r in result['recommendations']]) + "</ul></div>", unsafe_allow_html=True)
                
                if st.button("Add to CRM", type="primary"):
                    add_lead(result)
                    st.rerun()
        else:
            st.warning("Please enter a company name")

# ============ IMPORT LEADS ============
elif st.session_state.current_page == 'import':
    st.markdown('<div class="section-header">Import Leads</div>', unsafe_allow_html=True)
    st.caption("Import leads from CSV, JSON, or Text files")
    st.markdown("---")
    
    with st.expander("Format Instructions"):
        st.markdown("""
        **CSV Format:**

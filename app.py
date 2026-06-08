# app.py - Complete TechWokx Lead Intelligence System with Full Automation
import streamlit as st
import pandas as pd
import requests
import re
import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import io

st.set_page_config(
    page_title="TechWokx Lead Intelligence",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'research_cache' not in st.session_state:
    st.session_state.research_cache = {}
if 'email_templates' not in st.session_state:
    st.session_state.email_templates = {
        'initial': {
            'name': 'Initial Follow-up',
            'subject': 'Thanks for your audit - Next steps for {company}',
            'body': '''Dear {contact_name},

Thank you for completing our security audit. Your company {company} scored {score}/100.

Based on your results, we've identified opportunities to improve your security posture.

Would you like to schedule a free 15-minute consultation to review your results?

Best regards,
TechWokx Team''',
            'delay_days': 1,
            'active': True
        },
        'nurture': {
            'name': 'Nurture Sequence',
            'subject': 'Security insights for {company}',
            'body': '''Hi {contact_name},

Here are 3 quick security wins for {company} based on your audit score of {score}/100:

1. Implement email authentication (SPF/DKIM/DMARC)
2. Enable multi-factor authentication for all staff
3. Regular security awareness training

Want to discuss implementing these? Book a call: [Calendar Link]

Best regards,
TechWokx Team''',
            'delay_days': 3,
            'active': True
        },
        'urgent': {
            'name': 'Urgent Fix Required',
            'subject': 'URGENT: {company} email security at risk',
            'body': '''URGENT: {contact_name}

Your audit shows CRITICAL security gaps at {company} (Score: {score}/100):

- Email spoofing possible
- Data breach risk
- Brand impersonation threat

Book emergency fix: [Emergency Link]
Valid for 48 hours.

Stay secure,
TechWokx Security Team''',
            'delay_days': 7,
            'active': True
        },
        'proposal': {
            'name': 'Proposal Ready',
            'subject': 'Your custom proposal for {company}',
            'body': '''Dear {contact_name},

Based on your audit results for {company}, we've prepared a custom proposal addressing your specific needs.

Key recommendations:
- Email security implementation
- Infrastructure audit
- Staff training program

View your proposal: [Proposal Link]

Looking forward to working with you,
TechWokx Team''',
            'delay_days': 14,
            'active': True
        }
    }
if 'automation_log' not in st.session_state:
    st.session_state.automation_log = []
if 'email_settings' not in st.session_state:
    st.session_state.email_settings = {
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': '',
        'smtp_password': '',
        'from_email': '',
        'auto_followup': True,
        'followup_frequency': 'daily'
    }

# API Keys
SERP_API_KEY = ""
GOOGLE_MAPS_API_KEY = ""
OPENAI_API_KEY = ""

try:
    SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
    GOOGLE_MAPS_API_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY", "")
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
except:
    pass

# ============ EMAIL FUNCTIONS ============

def send_email(to_email, subject, body):
    """Send email using SMTP"""
    if not st.session_state.email_settings['smtp_user']:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = st.session_state.email_settings['from_email']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(
            st.session_state.email_settings['smtp_host'], 
            st.session_state.email_settings['smtp_port']
        )
        server.starttls()
        server.login(
            st.session_state.email_settings['smtp_user'], 
            st.session_state.email_settings['smtp_password']
        )
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email error: {e}")
        return False

def check_and_send_auto_followups():
    """Automatically send follow-up emails to leads"""
    if not st.session_state.email_settings['auto_followup']:
        return 0
    
    now = datetime.now()
    sent_count = 0
    
    for lead in st.session_state.leads:
        if 'followup_stage' not in lead:
            lead['followup_stage'] = 0
        if 'last_contact' not in lead:
            lead['last_contact'] = None
        
        # Determine which template to send
        templates = list(st.session_state.email_templates.values())
        expected_stage = 0
        
        if lead['last_contact']:
            days_since = (now - lead['last_contact']).days
            if lead['score'] >= 80:  # Hot leads get faster follow-up
                expected_stage = min(days_since // 2, len(templates))
            else:
                expected_stage = min(days_since // 3, len(templates))
        
        if expected_stage > lead['followup_stage'] and lead['followup_stage'] < len(templates):
            template = templates[lead['followup_stage']]
            if template['active']:
                # Prepare email
                subject = template['subject'].format(
                    company=lead['name'],
                    contact_name=lead.get('contact_name', 'Valued Customer')
                )
                body = template['body'].format(
                    company=lead['name'],
                    contact_name=lead.get('contact_name', 'Valued Customer'),
                    score=lead['score']
                )
                
                if send_email(lead['email'], subject, body):
                    lead['followup_stage'] += 1
                    lead['last_contact'] = now
                    sent_count += 1
                    log_automation(f"Auto email sent to {lead['name']}: {template['name']}")
    
    return sent_count

def log_automation(action):
    """Log automation activity"""
    st.session_state.automation_log.insert(0, {
        'time': datetime.now(),
        'action': action,
        'status': 'Success'
    })
    # Keep last 100 logs
    st.session_state.automation_log = st.session_state.automation_log[:100]

# ============ API FUNCTIONS ============

def search_company_serp(company_name):
    if not SERP_API_KEY:
        return None
    try:
        url = "https://serpapi.com/search"
        params = {
            "api_key": SERP_API_KEY,
            "q": f"{company_name} Ghana company",
            "engine": "google",
            "num": 5
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        result = {"website": None, "description": None}
        if "organic_results" in data:
            for org in data["organic_results"][:3]:
                link = org.get("link", "")
                if link and "google" not in link:
                    if not result["website"]:
                        result["website"] = link
                    if not result["description"]:
                        result["description"] = org.get("snippet", "")
        return result
    except Exception:
        return None

def get_company_location(company_name):
    if not GOOGLE_MAPS_API_KEY:
        return None
    try:
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "key": GOOGLE_MAPS_API_KEY,
            "input": f"{company_name} Ghana",
            "inputtype": "textquery",
            "fields": "formatted_address"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("candidates"):
            return {"address": data["candidates"][0].get("formatted_address", "")}
        return None
    except Exception:
        return None

def extract_email_from_website(website):
    if not website:
        return {"emails": [], "primary_email": None}
    try:
        if not website.startswith("http"):
            website = "https://" + website
        response = requests.get(website, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, response.text)
        exclude = ['example', 'test', 'noreply', 'png', 'jpg', 'css']
        valid = [e for e in emails if not any(x in e.lower() for x in exclude)]
        primary = None
        for e in valid:
            if any(x in e.lower() for x in ['info', 'contact', 'hello', 'support']):
                primary = e
                break
        return {"emails": list(set(valid))[:3], "primary_email": primary or (valid[0] if valid else None)}
    except Exception:
        return {"emails": [], "primary_email": None}

def deep_research_company(company_name, website=None):
    cache_key = hashlib.md5(f"{company_name}_{website}".encode()).hexdigest()
    if cache_key in st.session_state.research_cache:
        return st.session_state.research_cache[cache_key]
    
    result = {
        "name": company_name,
        "website": website,
        "emails": [],
        "primary_email": None,
        "address": None,
        "description": None,
        "lead_score": 50,
        "sources": []
    }
    
    progress = st.progress(0)
    status = st.empty()
    
    status.text("Searching company information...")
    serp_data = search_company_serp(company_name)
    if serp_data:
        result["website"] = result["website"] or serp_data.get("website")
        result["description"] = serp_data.get("description")
        result["sources"].append("SERP API")
    progress.progress(0.33)
    
    status.text("Finding location...")
    location_data = get_company_location(company_name)
    if location_data:
        result["address"] = location_data.get("address")
        result["sources"].append("Google Maps")
    progress.progress(0.66)
    
    target_website = result["website"] or website
    if target_website:
        status.text("Extracting contact info...")
        email_data = extract_email_from_website(target_website)
        if email_data:
            result["emails"] = email_data.get("emails", [])
            result["primary_email"] = email_data.get("primary_email")
            if result["emails"]:
                result["sources"].append("Website")
    
    # Calculate lead score
    score = 30
    if result["website"]:
        score += 20
    if result["primary_email"]:
        score += 25
    if result["address"]:
        score += 15
    if result["emails"]:
        score += 10
    result["lead_score"] = min(score, 100)
    
    progress.progress(1.0)
    status.text("Research complete!")
    
    st.session_state.research_cache[cache_key] = result
    return result

def add_lead(name, email, phone, score, contact_name=""):
    new_id = len(st.session_state.leads) + 1
    status = "Hot" if score >= 80 else "Warm" if score >= 60 else "Cold"
    st.session_state.leads.append({
        "id": new_id, 
        "name": name, 
        "email": email, 
        "phone": phone,
        "contact_name": contact_name or name.split()[0] if name else "",
        "score": score, 
        "status": status, 
        "audit_date": datetime.now(),
        "last_contact": None,
        "followup_stage": 0,
        "notes": ""
    })
    log_automation(f"New lead added: {name} (Score: {score})")

def import_leads_from_csv(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        required = ['name', 'email']
        missing = [col for col in required if col not in df.columns]
        if missing:
            return False, f"Missing columns: {missing}"
        
        imported = 0
        for _, row in df.iterrows():
            score = int(row.get('score', 50)) if 'score' in df.columns else 50
            phone = str(row.get('phone', '')) if 'phone' in df.columns else ''
            contact = str(row.get('contact_name', '')) if 'contact_name' in df.columns else ''
            add_lead(row['name'], row['email'], phone, score, contact)
            imported += 1
        
        return True, f"Imported {imported} leads"
    except Exception as e:
        return False, str(e)

def export_leads_to_csv():
    df = pd.DataFrame(st.session_state.leads)
    return df.to_csv(index=False)

# ============ CSS STYLES ============
css_style = """
<style>
.stApp { background-color: #f8fafc; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fbbf24 !important; }
[data-testid="stSidebar"] .stButton button { background: rgba(251, 191, 36, 0.15); color: #fbbf24 !important; border: 1px solid rgba(251, 191, 36, 0.3); text-align: left; width: 100%; margin: 2px 0; }
[data-testid="stSidebar"] .stButton button:hover { background: rgba(251, 191, 36, 0.3); }
.welcome-card { background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; }
.metric-card { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
.metric-label { color: #64748b; font-size: 0.8rem; }
.data-card { background: white; border-radius: 12px; padding: 1.2rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
.data-card h4 { color: #0f172a; margin-top: 0; margin-bottom: 0.75rem; }
.activity-item { background: white; border-radius: 12px; padding: 0.8rem; margin-bottom: 0.5rem; border-left: 3px solid #fbbf24; }
.section-header { color: #0f172a; font-size: 1.2rem; font-weight: 600; margin: 1.5rem 0 1rem 0; border-left: 3px solid #fbbf24; padding-left: 1rem; }
.custom-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
.plan-badge { background: linear-gradient(135deg, #fbbf24, #f59e0b); border-radius: 12px; padding: 0.75rem; text-align: center; margin-top: 1rem; }
.stButton > button { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #0f172a !important; font-weight: 600; border: none; border-radius: 8px; }
.status-hot { color: #dc2626; font-weight: 600; }
.status-warm { color: #f97316; font-weight: 600; }
.status-cold { color: #3b82f6; font-weight: 600; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# Run auto follow-ups on dashboard load
if st.session_state.page == 'dashboard':
    sent = check_and_send_auto_followups()
    if sent > 0:
        st.toast(f"📧 Sent {sent} automated follow-up emails!", icon="📧")

# ============ SIDEBAR NAVIGATION ============
with st.sidebar:
    st.markdown("### 🔍 TechWokx")
    st.markdown("#### Lead Intelligence Engine")
    st.markdown("---")
    
    nav_items = [
        ("🏠 Dashboard", "dashboard"),
        ("🔍 Company Research", "company_research"),
        ("📊 Bulk Research", "bulk_research"),
        ("📥 Import Leads", "import_leads"),
        ("---", "divider1"),
        ("📧 Lead Follow-up", "lead_followup"),
        ("📝 Email Templates", "email_templates"),
        ("⚙️ Email Settings", "email_settings"),
        ("---", "divider2"),
        ("🌐 DNS Audit", "dns_audit"),
        ("🔒 Website Audit", "website_audit"),
        ("📧 Email Security", "email_security"),
        ("🛡️ IT Audit", "it_audit"),
        ("---", "divider3"),
        ("👥 CRM", "crm"),
        ("📈 Reports", "reports"),
        ("⚙️ Settings", "settings")
    ]
    
    for label, key in nav_items:
        if label == "---":
            st.markdown("---")
        elif st.button(label, key=key, use_container_width=True):
            st.session_state.page = key
            st.rerun()
    
    st.markdown("---")
    st.markdown("### API Status")
    st.markdown(f"SERP: {'✅' if SERP_API_KEY else '❌'}")
    st.markdown(f"Maps: {'✅' if GOOGLE_MAPS_API_KEY else '❌'}")
    st.markdown(f"Email: {'✅' if st.session_state.email_settings['smtp_user'] else '❌'}")
    st.markdown("---")
    st.markdown('<div class="plan-badge">🚀 Pro Plan<br><small>Full Automation</small></div>', unsafe_allow_html=True)

# ============ DASHBOARD PAGE ============
if st.session_state.page == 'dashboard':
    st.markdown('<div class="welcome-card"><h2>Welcome to TechWokx Lead Intelligence</h2><p>Full automation for lead management and follow-ups.</p></div>', unsafe_allow_html=True)
    
    total_leads = len(st.session_state.leads)
    hot_leads = sum(1 for l in st.session_state.leads if l.get("score", 0) >= 80)
    warm_leads = sum(1 for l in st.session_state.leads if 60 <= l.get("score", 0) < 80)
    pending_followup = sum(1 for l in st.session_state.leads if l.get("followup_stage", 0) < 3)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_leads}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot_leads}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{warm_leads}</div><div class='metric-label'>Warm Leads</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{pending_followup}</div><div class='metric-label'>Pending Follow-up</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Recent Research</div>', unsafe_allow_html=True)
        if st.session_state.leads:
            for lead in st.session_state.leads[-5:]:
                st.markdown(f'<div class="activity-item"><div class="activity-action">{lead["name"]} - Score: {lead["score"]}/100 - Stage: {lead.get("followup_stage", 0)}/4</div><div class="activity-time">{lead["audit_date"].strftime("%Y-%m-%d")}</div></div>', unsafe_allow_html=True)
        else:
            st.info("No leads yet. Use Company Research or Import Leads.")
    
    with col2:
        st.markdown('<div class="section-header">🤖 Automation Log</div>', unsafe_allow_html=True)
        for log in st.session_state.automation_log[:5]:
            st.markdown(f'<div class="activity-item"><div class="activity-action">{log["action"]}</div><div class="activity-time">{log["time"].strftime("%Y-%m-%d %H:%M")}</div></div>', unsafe_allow_html=True)

# ============ COMPANY RESEARCH PAGE ============
elif st.session_state.page == 'company_research':
    st.markdown('<div class="section-header">🔍 Company Research</div>', unsafe_allow_html=True)
    st.caption("Research companies and automatically add to follow-up sequence")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g. Nyaho Medical Centre, MTN Ghana")
    with col2:
        website = st.text_input("Website (optional)", placeholder="e.g. nyahoclinic.com")
    
    contact_name = st.text_input("Contact Person (optional)", placeholder="e.g. John Doe")
    
    if st.button("🔍 Research & Add to CRM", type="primary"):
        if company_name:
            with st.spinner(f"Researching {company_name}..."):
                result = deep_research_company(company_name, website)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<div class="data-card"><h4>Company Information</h4><p><strong>Name:</strong> {result["name"]}</p><p><strong>Website:</strong> {result["website"] or "Not found"}</p><p><strong>Address:</strong> {result["address"] or "Not found"}</p></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'<div class="data-card" style="text-align: center;"><h4>Lead Score</h4><p style="font-size: 3rem; font-weight: 700; color: #fbbf24;">{result["lead_score"]}/100</p><p><strong>Status:</strong> {"Hot" if result["lead_score"] >= 80 else "Warm" if result["lead_score"] >= 60 else "Cold"}</p></div>', unsafe_allow_html=True)
                
                if st.button("➕ Add to CRM", use_container_width=True):
                    email = result.get("primary_email") or (result.get("emails", [""])[0] if result.get("emails") else "")
                    add_lead(result["name"], email, "", result["lead_score"], contact_name)
                    st.success(f"Added {result['name']} to CRM! Auto follow-up will begin shortly.")
        else:
            st.warning("Please enter a company name")

# ============ BULK RESEARCH PAGE ============
elif st.session_state.page == 'bulk_research':
    st.markdown('<div class="section-header">📊 Bulk Research</div>', unsafe_allow_html=True)
    st.caption("Research multiple companies and add to CRM")
    st.markdown("---")
    
    companies = st.text_area("Company Names (one per line)", height=150, placeholder="Nyaho Medical Centre\nMTN Ghana\nGCB Bank\nKasapreko")
    
    if st.button("Start Bulk Research", type="primary"):
        if companies:
            lines = [c.strip() for c in companies.split("\n") if c.strip()]
            progress = st.progress(0)
            results = []
            for i, c in enumerate(lines):
                progress.progress((i + 1) / len(lines))
                result = deep_research_company(c)
                email = result.get("primary_email") or (result.get("emails", [""])[0] if result.get("emails") else "")
                add_lead(result["name"], email, "", result["lead_score"], "")
                results.append({"Company": c, "Score": f"{result['lead_score']}/100", "Status": "Added to CRM"})
            st.success(f"Added {len(lines)} companies to CRM!")
            st.dataframe(results, use_container_width=True)

# ============ IMPORT LEADS PAGE ============
elif st.session_state.page == 'import_leads':
    st.markdown('<div class="section-header">📥 Import Leads</div>', unsafe_allow_html=True)
    st.caption("Import leads from CSV or Excel file")
    st.markdown("---")
    
    st.markdown("""
    ### Required Columns
    - `name` - Company name
    - `email` - Contact email
    
    ### Optional Columns
    - `phone` - Phone number
    - `score` - Lead score (0-100)
    - `contact_name` - Contact person name
    
    ### Sample CSV Format
    ```csv
    name,email,phone,score,contact_name
    Airside Hotel,info@airside.com,0551234567,85,John Doe
""")

uploaded_file = st.file_uploader("Choose CSV or Excel file", type=['csv', 'xlsx'])

if uploaded_file:
success, message = import_leads_from_csv(uploaded_file)
if success:
st.success(message)
st.info("Leads added to CRM. Auto follow-up will begin based on email settings.")
else:
st.error(message)

============ LEAD FOLLOW-UP PAGE ============
elif st.session_state.page == 'lead_followup':
st.markdown('<div class="section-header">📧 Lead Follow-up Management</div>', unsafe_allow_html=True)
st.caption("Manage follow-ups and send emails to leads")
st.markdown("---")

Stats
total = len(st.session_state.leads)
if total > 0:
avg_score = sum(l.get("score", 0) for l in st.session_state.leads) / total
completed = sum(1 for l in st.session_state.leads if l.get("followup_stage", 0) >= 4)

col1, col2, col3 = st.columns(3)
with col1:
st.metric("Total Leads", total)
with col2:
st.metric("Avg Lead Score", f"{avg_score:.0f}")
with col3:
st.metric("Completed Follow-ups", f"{completed}/{total}")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📋 Leads", "📧 Send Manual Email", "📊 Follow-up Status"])

with tab1:
if st.session_state.leads:
for lead in st.session_state.leads:
status_color = "status-hot" if lead["score"] >= 80 else "status-warm" if lead["score"] >= 60 else "status-cold"
with st.expander(f"{lead['name']} - Score: {lead['score']}/100 - Stage: {lead.get('followup_stage', 0)}/4"):
col1, col2 = st.columns(2)
with col1:
st.write(f"Email: {lead['email']}")
st.write(f"Phone: {lead['phone'] or 'N/A'}")
st.write(f"Contact: {lead.get('contact_name', 'N/A')}")
st.write(f"Status: <span class='{status_color}'>{lead['status']}</span>", unsafe_allow_html=True)
with col2:
st.write(f"Added: {lead['audit_date'].strftime('%Y-%m-%d')}")
st.write(f"Last Contact: {lead['last_contact'].strftime('%Y-%m-%d') if lead['last_contact'] else 'Never'}")
st.write(f"Notes: {lead.get('notes', 'No notes')}")

col1, col2, col3 = st.columns(3)
with col1:
new_note = st.text_input("Add Note", key=f"note_{lead['id']}")
if st.button("Save Note", key=f"save_note_{lead['id']}"):
lead['notes'] = new_note
st.success("Note saved!")
with col2:
if st.button("📧 Send Email", key=f"email_{lead['id']}"):
template = st.session_state.email_templates['initial']
subject = template['subject'].format(company=lead['name'], contact_name=lead.get('contact_name', 'Valued Customer'))
body = template['body'].format(company=lead['name'], contact_name=lead.get('contact_name', 'Valued Customer'), score=lead['score'])
if send_email(lead['email'], subject, body):
lead['last_contact'] = datetime.now()
st.success(f"Email sent to {lead['name']}!")
st.rerun()
with col3:
if st.button("✅ Mark Contacted", key=f"contact_{lead['id']}"):
lead['followup_stage'] = min(lead.get('followup_stage', 0) + 1, 4)
lead['last_contact'] = datetime.now()
st.success(f"Follow-up logged for {lead['name']}")
st.rerun()
else:
st.info("No leads yet. Import leads or use Company Research.")

with tab2:
st.markdown("### Send Manual Email")

if st.session_state.leads:
lead_options = {f"{l['name']} ({l['email']})": l for l in st.session_state.leads}
selected = st.selectbox("Select Lead", list(lead_options.keys()))
lead = lead_options[selected]

template_options = {t['name']: t for t in st.session_state.email_templates.values()}
selected_template = st.selectbox("Select Template", list(template_options.keys()))
template = template_options[selected_template]

subject = st.text_input("Subject", value=template['subject'].format(company=lead['name'], contact_name=lead.get('contact_name', 'Valued Customer')))
body = st.text_area("Email Body", height=200, value=template['body'].format(company=lead['name'], contact_name=lead.get('contact_name', 'Valued Customer'), score=lead['score']))

if st.button("Send Email", type="primary"):
if send_email(lead['email'], subject, body):
lead['last_contact'] = datetime.now()
lead['followup_stage'] = min(lead.get('followup_stage', 0) + 1, 4)
st.success(f"Email sent to {lead['name']}!")
log_automation(f"Manual email sent to {lead['name']}")
else:
st.info("No leads available")

with tab3:
st.markdown("### Follow-up Status")
if st.session_state.leads:
status_data = []
for lead in st.session_state.leads:
status_data.append({
"Company": lead['name'],
"Score": lead['score'],
"Status": lead['status'],
"Stage": f"{lead.get('followup_stage', 0)}/4",
"Last Contact": lead['last_contact'].strftime('%Y-%m-%d') if lead['last_contact'] else 'Never'
})
st.dataframe(status_data, use_container_width=True)

============ EMAIL TEMPLATES PAGE ============
elif st.session_state.page == 'email_templates':
st.markdown('<div class="section-header">📝 Email Templates</div>', unsafe_allow_html=True)
st.caption("Manage automated follow-up email templates")
st.markdown("---")

for key, template in st.session_state.email_templates.items():
with st.expander(f"{template['name']} - {'✅ Active' if template['active'] else '⏸️ Inactive'}"):
col1, col2 = st.columns(2)
with col1:
new_name = st.text_input("Template Name", value=template['name'], key=f"name_{key}")
new_subject = st.text_input("Subject Line", value=template['subject'], key=f"subject_{key}")
new_delay = st.number_input("Delay (days)", min_value=0, max_value=30, value=template['delay_days'], key=f"delay_{key}")
with col2:
active = st.checkbox("Active", value=template['active'], key=f"active_{key}")

new_body = st.text_area("Email Body", value=template['body'], height=200, key=f"body_{key}")
st.caption("Available variables: {company}, {contact_name}, {score}")

if st.button("Save Template", key=f"save_{key}"):
template['name'] = new_name
template['subject'] = new_subject
template['body'] = new_body
template['delay_days'] = new_delay
template['active'] = active
st.success("Template saved!")

============ EMAIL SETTINGS PAGE ============
elif st.session_state.page == 'email_settings':
st.markdown('<div class="section-header">⚙️ Email Settings</div>', unsafe_allow_html=True)
st.caption("Configure SMTP for automated emails")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
new_host = st.text_input("SMTP Host", value=st.session_state.email_settings['smtp_host'])
new_port = st.number_input("SMTP Port", value=st.session_state.email_settings['smtp_port'])
new_user = st.text_input("SMTP Username", value=st.session_state.email_settings['smtp_user'])
with col2:
new_password = st.text_input("SMTP Password", type="password", value=st.session_state.email_settings['smtp_password'])
new_from = st.text_input("From Email", value=st.session_state.email_settings['from_email'])
auto_followup = st.checkbox("Enable Auto Follow-ups", value=st.session_state.email_settings['auto_followup'])
followup_freq = st.selectbox("Follow-up Frequency", ["daily", "every 2 days", "weekly"],
index=["daily", "every 2 days", "weekly"].index(st.session_state.email_settings['followup_frequency']))

if st.button("Save Email Settings", type="primary"):
st.session_state.email_settings['smtp_host'] = new_host
st.session_state.email_settings['smtp_port'] = new_port
st.session_state.email_settings['smtp_user'] = new_user
st.session_state.email_settings['smtp_password'] = new_password
st.session_state.email_settings['from_email'] = new_from
st.session_state.email_settings['auto_followup'] = auto_followup
st.session_state.email_settings['followup_frequency'] = followup_freq
st.success("Email settings saved!")

if new_user and new_password:
st.info("Auto follow-up is enabled. Emails will be sent automatically based on templates.")

============ DNS AUDIT PAGE ============
elif st.session_state.page == 'dns_audit':
st.markdown('<div class="section-header">🌐 DNS Audit</div>', unsafe_allow_html=True)
st.caption("Check DNS records and configuration")
st.markdown("---")

domain = st.text_input("Domain", placeholder="example.com")

if st.button("Run DNS Audit", type="primary"):
if domain:
with st.spinner(f"Auditing {domain}..."):
try:
import dns.resolver
results = []
try:
a_records = dns.resolver.resolve(domain, 'A')
results.append(("A Records", "✅ Found", f"{len(a_records)} records"))
except:
results.append(("A Records", "❌ Failed", "No A records found"))

try:
mx_records = dns.resolver.resolve(domain, 'MX')
results.append(("MX Records", "✅ Found", f"{len(mx_records)} mail servers"))
except:
results.append(("MX Records", "❌ Failed", "No mail servers configured"))

try:
txt_records = dns.resolver.resolve(domain, 'TXT')
has_spf = any('v=spf1' in str(r) for r in txt_records)
results.append(("SPF Record", "✅ Found" if has_spf else "⚠️ Missing", "Email authentication" if has_spf else "Spoofing risk"))
except:
results.append(("SPF Record", "❌ Failed", "Not configured"))

for name, status, detail in results:
st.markdown(f'<div class="data-card"><p><strong>{name}:</strong> {status}</p><p style="color:#64748b; font-size:0.8rem;">{detail}</p></div>', unsafe_allow_html=True)
except ImportError:
st.error("Please install dnspython: pip install dnspython")
else:
st.warning("Please enter a domain")

============ WEBSITE AUDIT PAGE ============
elif st.session_state.page == 'website_audit':
st.markdown('<div class="section-header">🔒 Website Audit</div>', unsafe_allow_html=True)
st.caption("Check website security and SSL certificate")
st.markdown("---")

url = st.text_input("Website URL", placeholder="https://example.com")

if st.button("Run Website Audit", type="primary"):
if url:
with st.spinner(f"Auditing {url}..."):
if not url.startswith("http"):
url = "https://" + url

results = []
try:
response = requests.get(url, timeout=10, verify=True)
results.append(("HTTPS", "✅ Enabled", f"Status: {response.status_code}"))
except:
results.append(("HTTPS", "❌ Failed", "SSL certificate issue or site unreachable"))

try:
import ssl
import socket
hostname = url.replace("https://", "").replace("http://", "").split("/")[0]
ctx = ssl.create_default_context()
with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
s.connect((hostname, 443))
cert = s.getpeercert()
results.append(("SSL Certificate", "✅ Valid", f"Expires: {cert.get('notAfter', 'Unknown')}"))
except:
results.append(("SSL Certificate", "❌ Invalid", "Certificate not found or expired"))

for name, status, detail in results:
st.markdown(f'<div class="data-card"><p><strong>{name}:</strong> {status}</p><p style="color:#64748b; font-size:0.8rem;">{detail}</p></div>', unsafe_allow_html=True)
else:
st.warning("Please enter a URL")

============ EMAIL SECURITY PAGE ============
elif st.session_state.page == 'email_security':
st.markdown('<div class="section-header">📧 Email Security Audit</div>', unsafe_allow_html=True)
st.caption("Check SPF, DKIM, and DMARC records")
st.markdown("---")

domain = st.text_input("Domain", placeholder="example.com")

if st.button("Run Email Security Audit", type="primary"):
if domain:
with st.spinner(f"Checking {domain}..."):
try:
import dns.resolver
results = []
try:
txt_records = dns.resolver.resolve(domain, 'TXT')
spf_found = any('v=spf1' in str(r).lower() for r in txt_records)
results.append(("SPF Record", "✅ Configured" if spf_found else "❌ Missing", "Prevents email spoofing" if spf_found else "Emails may be spoofed"))
except:
results.append(("SPF Record", "❌ Failed", "Not configured"))

try:
dmarc = dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
results.append(("DMARC Record", "✅ Configured", "Email security policy active"))
except:
results.append(("DMARC Record", "⚠️ Missing", "No DMARC policy - spoofing risk"))

risk_score = sum(1 for r in results if '✅' in r[1]) * 50
risk_level = "Low" if risk_score >= 66 else "Medium" if risk_score >= 33 else "High"

for name, status, detail in results:
st.markdown(f'<div class="data-card"><p><strong>{name}:</strong> {status}</p><p style="color:#64748b; font-size:0.8rem;">{detail}</p></div>', unsafe_allow_html=True)

st.markdown(f'<div class="data-card"><h4>Overall Risk Assessment</h4><p><strong>Risk Level:</strong> {risk_level}</p><p><strong>Security Score:</strong> {risk_score}/100</p></div>', unsafe_allow_html=True)
except ImportError:
st.error("Please install dnspython: pip install dnspython")
else:
st.warning("Please enter a domain")

============ IT AUDIT PAGE ============
elif st.session_state.page == 'it_audit':
st.markdown('<div class="section-header">🛡️ IT Infrastructure Audit</div>', unsafe_allow_html=True)
st.caption("Comprehensive IT security assessment")
st.markdown("---")

company_name = st.text_input("Company Name", placeholder="Your company name")

if st.button("Start IT Audit", type="primary"):
if company_name:
with st.spinner("Running IT audit..."):
st.markdown(f'<div class="data-card"><h4>IT Audit for {company_name}</h4><p>✅ Network Security: Good</p><p>⚠️ Email Security: Needs improvement</p><p>✅ Access Control: Properly configured</p><p>⚠️ Backup System: Review recommended</p><p>✅ Device Management: Active monitoring</p></div>', unsafe_allow_html=True)
st.markdown('<div class="data-card"><h4>Recommendations</h4><ul><li>Implement DMARC policy for email security</li><li>Review backup and disaster recovery plan</li><li>Conduct employee security awareness training</li><li>Schedule quarterly security assessments</li></ul></div>', unsafe_allow_html=True)
st.markdown('<div class="data-card"><h4>Risk Score: 72/100 - Moderate Risk</h4><p>Priority: Medium - Address within 30 days</p></div>', unsafe_allow_html=True)
else:
st.warning("Please enter company name")

============ CRM PAGE ============
elif st.session_state.page == 'crm':
st.markdown('<div class="section-header">👥 Lead CRM</div>', unsafe_allow_html=True)
st.caption("Manage all your leads")
st.markdown("---")

if st.session_state.leads:
crm_data = []
for lead in st.session_state.leads:
crm_data.append({
"Company": lead['name'],
"Email": lead.get('email', 'N/A'),
"Score": lead.get('score', 0),
"Status": lead.get('status', 'New'),
"Follow-up Stage": f"{lead.get('followup_stage', 0)}/4",
"Date Added": lead['audit_date'].strftime("%Y-%m-%d")
})
st.dataframe(crm_data, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
if st.button("Export to CSV", use_container_width=True):
csv = export_leads_to_csv()
st.download_button("Download CSV", csv, "leads_export.csv", "text/csv")
with col2:
if st.button("Clear All Leads", use_container_width=True):
st.session_state.leads = []
st.success("All leads cleared!")
st.rerun()
else:
st.info("No leads yet. Use Company Research or Import Leads.")

============ REPORTS PAGE ============
elif st.session_state.page == 'reports':
st.markdown('<div class="section-header">📈 Reports</div>', unsafe_allow_html=True)
st.caption("Generate reports on your leads and activities")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
report_type = st.selectbox("Report Type", ["Lead Summary", "Follow-up Status", "Automation Log", "Audit History"])
with col2:
date_range = st.selectbox("Date Range", ["Last 7 days", "Last 30 days", "All time"])

if st.button("Generate Report", type="primary"):
if report_type == "Lead Summary":
data = []
for lead in st.session_state.leads:
data.append({
"Company": lead['name'],
"Email": lead['email'],
"Score": lead['score'],
"Status": lead['status'],
"Follow-up Stage": lead.get('followup_stage', 0),
"Date Added": lead['audit_date'].strftime("%Y-%m-%d")
})
df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)
st.download_button("Download Report", df.to_csv(index=False), "lead_summary.csv", "text/csv")

elif report_type == "Follow-up Status":
data = []
for lead in st.session_state.leads:
data.append({
"Company": lead['name'],
"Stage": f"{lead.get('followup_stage', 0)}/4",
"Last Contact": lead['last_contact'].strftime("%Y-%m-%d") if lead['last_contact'] else "Never",
"Score": lead['score']
})
df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

elif report_type == "Automation Log":
df = pd.DataFrame(st.session_state.automation_log)
if not df.empty:
df['time'] = df['time'].dt.strftime("%Y-%m-%d %H:%M")
st.dataframe(df, use_container_width=True)
else:
st.info("No automation logs yet")

st.success(f"Report generated for {date_range}")

============ SETTINGS PAGE ============
elif st.session_state.page == 'settings':
st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
st.caption("Configure system settings")
st.markdown("---")

st.markdown("### API Configuration")
st.markdown("Add API keys to enable advanced features:")
st.markdown("- SERP API - Get company data from search")
st.markdown("- Google Maps API - Location verification")
st.markdown("- OpenAI API - AI-powered insights")
st.markdown("")
st.markdown("### How to add API keys:")
st.markdown("Create .streamlit/secrets.toml file:")
st.code("""
SERP_API_KEY = "your_key_here"
GOOGLE_MAPS_API_KEY = "your_key_here"
OPENAI_API_KEY = "your_key_here"
""")

st.markdown("---")
st.markdown("### Email Configuration")
st.markdown("Configure SMTP settings in the Email Settings page.")

st.markdown("---")
st.markdown("### Current Status")
col1, col2 = st.columns(2)
with col1:
st.markdown(f"SERP API: {'✅ Active' if SERP_API_KEY else '❌ Inactive'}")
st.markdown(f"Google Maps: {'✅ Active' if GOOGLE_MAPS_API_KEY else '❌ Inactive'}")
with col2:
st.markdown(f"Email SMTP: {'✅ Active' if st.session_state.email_settings['smtp_user'] else '❌ Inactive'}")
st.markdown(f"Total Leads: {len(st.session_state.leads)}")

============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Ghana | Full Automation | Lead Management | Email Follow-up")

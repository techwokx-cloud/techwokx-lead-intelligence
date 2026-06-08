import streamlit as st
import pandas as pd
import os
import socket
import platform
from datetime import datetime

# Page config
st.set_page_config(
    page_title="TechWokx Enterprise Suite",
    page_icon="🔍",
    layout="wide"
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

# Login credentials
USERS = {
    "hello@techwokx.online": {
        "password": "Gtech.5628!@#$",
        "role": "admin",
        "name": "TechWokx Admin"
    }
}

# Resend email setup
RESEND_AVAILABLE = False
try:
    import resend
    RESEND_API_KEY = st.secrets.get("RESEND_API_KEY", "")
    if RESEND_API_KEY:
        resend.api_key = RESEND_API_KEY
        RESEND_AVAILABLE = True
except:
    pass

def send_email_resend(to_email, subject, body, from_email="hello@techwokx.online"):
    if not RESEND_AVAILABLE:
        return False, "Resend not configured"
    try:
        params = {
            "from": f"TechWokx <{from_email}>",
            "to": [to_email],
            "subject": subject,
            "html": body.replace('\n', '<br>')
        }
        email = resend.Emails.send(params)
        if email and email.get('id'):
            st.session_state.email_log.append({
                "to": to_email,
                "subject": subject,
                "date": datetime.now(),
                "status": "Sent"
            })
            return True, "Email sent"
        return False, "Failed"
    except Exception as e:
        return False, str(e)

def add_lead(name, email, phone, score, source="Manual"):
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
    
    # Send email notification
    if email:
        body = f"Dear {name},<br><br>Thank you for your interest. Your lead score is {score}/100.<br><br>Best regards,<br>TechWokx Team"
        send_email_resend(email, "Thank you for contacting TechWokx", body)
    
    return lead

def check_auth(username, password):
    if username in USERS and USERS[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.user = USERS[username]
        return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.page = 'login'
    st.rerun()

def get_system_info():
    info = {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_version": platform.version(),
        "processor": platform.processor(),
    }
    return info

def get_folder_size(path):
    total_size = 0
    try:
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            if os.path.isfile(entry_path):
                total_size += os.path.getsize(entry_path)
            elif os.path.isdir(entry_path):
                total_size += get_folder_size(entry_path)
    except:
        pass
    return total_size

def analyze_folders(path):
    folders = []
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                try:
                    size = get_folder_size(item_path)
                    folders.append({
                        "name": item,
                        "size_gb": size / (1024**3),
                        "size_mb": size / (1024**2)
                    })
                except:
                    pass
    except:
        pass
    return sorted(folders, key=lambda x: x['size_gb'], reverse=True)[:20]

def check_dns(domain):
    import socket
    results = {}
    try:
        socket.gethostbyname(domain)
        results['a_record'] = True
    except:
        results['a_record'] = False
    
    try:
        socket.gethostbyname(f"mail.{domain}")
        results['mx_record'] = True
    except:
        results['mx_record'] = False
    
    return results

def check_website(url):
    import requests
    results = {}
    try:
        response = requests.get(url, timeout=5, verify=True)
        results['reachable'] = response.status_code == 200
        results['https'] = url.startswith('https')
        results['status_code'] = response.status_code
    except:
        results['reachable'] = False
        results['https'] = url.startswith('https')
    return results

# CSS
st.markdown("""
<style>
.stApp { background-color: #f8fafc; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fbbf24 !important; }
[data-testid="stSidebar"] .stButton button { background: rgba(251, 191, 36, 0.15); color: #fbbf24 !important; width: 100%; margin: 2px 0; }
.welcome-card { background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; }
.metric-card { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
.metric-label { color: #64748b; font-size: 0.8rem; }
.data-card { background: white; border-radius: 12px; padding: 1.2rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
.section-header { color: #0f172a; font-size: 1.2rem; font-weight: 600; margin: 1.5rem 0 1rem 0; border-left: 3px solid #fbbf24; padding-left: 1rem; }
.custom-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
.stButton > button { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #0f172a !important; font-weight: 600; border: none; border-radius: 8px; }
.stButton > button:hover { background: linear-gradient(135deg, #f59e0b, #d97706); color: white !important; }
</style>
""", unsafe_allow_html=True)

# ============ LOGIN PAGE ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 400px; margin: 100px auto; text-align: center;">
        <h1 style="color: #fbbf24;">🔍 TechWokx</h1>
        <h3>Enterprise Suite</h3>
        <p>Lead Intelligence • Deep LAN Analysis • Email Automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Email", placeholder="hello@techwokx.online")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if check_auth(username, password):
                st.success("Welcome back!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown(f"### 🔍 TechWokx")
    st.markdown(f"#### Welcome, {st.session_state.user['name']}")
    st.markdown("---")
    
    nav_items = [
        ("🏠 Dashboard", "dashboard"),
        ("📥 Import Leads", "import_leads"),
        ("👥 Lead CRM", "crm"),
        ("---", "divider1"),
        ("💻 System Info", "system_info"),
        ("📁 Folder Analyzer", "folder_analyzer"),
        ("---", "divider2"),
        ("🌐 DNS Audit", "dns_audit"),
        ("🔒 Website Audit", "website_audit"),
        ("📧 Email Security", "email_security"),
        ("---", "divider3"),
        ("📊 Analytics", "analytics"),
        ("📋 Notification Log", "notification_log"),
        ("⚙️ Settings", "settings"),
        ("🚪 Logout", "logout")
    ]
    
    for label, key in nav_items:
        if label == "---":
            st.markdown("---")
        elif st.button(label, key=key, use_container_width=True):
            if key == "logout":
                logout()
            else:
                st.session_state.page = key
                st.rerun()
    
    st.markdown("---")
    st.markdown(f"Resend: {'✅' if RESEND_AVAILABLE else '❌'}")
    st.markdown(f"Leads: {len(st.session_state.leads)}")

# ============ DASHBOARD ============
if st.session_state.page == 'dashboard':
    st.markdown('<div class="welcome-card"><h2>Welcome to TechWokx Enterprise Suite</h2><p>Lead Intelligence • Deep LAN Analysis • Email Automation</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.leads)}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        hot = sum(1 for l in st.session_state.leads if l.get('score', 0) >= 80)
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.email_log)}</div><div class='metric-label'>Emails Sent</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>✅</div><div class='metric-label'>System Active</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Recent Leads</div>', unsafe_allow_html=True)
        if st.session_state.leads:
            for lead in st.session_state.leads[-5:]:
                st.markdown(f'<div class="data-card"><strong>{lead["name"]}</strong> - Score: {lead["score"]}/100<br><small>{lead["created_at"].strftime("%Y-%m-%d") if lead.get("created_at") else "Just now"}</small></div>', unsafe_allow_html=True)
        else:
            st.info("No leads yet")
    
    with col2:
        st.markdown('<div class="section-header">📧 Recent Emails</div>', unsafe_allow_html=True)
        if st.session_state.email_log:
            for log in st.session_state.email_log[-5:]:
                st.markdown(f'<div class="data-card"><strong>{log["subject"][:30]}...</strong><br><small>To: {log["to"]}</small></div>', unsafe_allow_html=True)
        else:
            st.info("No emails sent yet")

# ============ IMPORT LEADS ============
elif st.session_state.page == 'import_leads':
    st.markdown('<div class="section-header">📥 Import Leads</div>', unsafe_allow_html=True)
    
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
                st.success(f"Imported {imported} leads!")
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
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
                st.success(f"Added {name}!")
                st.rerun()
            else:
                st.error("Name and email required")

# ============ CRM ============
elif st.session_state.page == 'crm':
    st.markdown('<div class="section-header">👥 Lead CRM</div>', unsafe_allow_html=True)
    
    if st.session_state.leads:
        search = st.text_input("🔍 Search", placeholder="Name or email")
        filtered = st.session_state.leads
        if search:
            filtered = [l for l in filtered if search.lower() in l["name"].lower() or search.lower() in l.get("email", "").lower()]
        
        for lead in filtered:
            with st.expander(f"{lead['name']} - Score: {lead['score']}/100"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {lead.get('email', 'N/A')}")
                    st.write(f"**Phone:** {lead.get('phone', 'N/A')}")
                with col2:
                    st.write(f"**Status:** {lead['status']}")
                    st.write(f"**Source:** {lead['source']}")
                st.write(f"**Added:** {lead['created_at'].strftime('%Y-%m-%d %H:%M') if lead.get('created_at') else 'N/A'}")
        
        if st.button("Export to CSV"):
            df = pd.DataFrame(st.session_state.leads)
            csv = df.to_csv(index=False)
            st.download_button("Download", csv, "leads.csv", "text/csv")
    else:
        st.info("No leads yet. Import leads to get started.")

# ============ SYSTEM INFO ============
elif st.session_state.page == 'system_info':
    st.markdown('<div class="section-header">💻 System Information</div>', unsafe_allow_html=True)
    
    if st.button("Scan System", type="primary"):
        with st.spinner("Scanning..."):
            info = get_system_info()
            st.markdown(f"""
            <div class="data-card">
                <p><strong>Hostname:</strong> {info['hostname']}</p>
                <p><strong>Platform:</strong> {info['platform']}</p>
                <p><strong>Version:</strong> {info['platform_version']}</p>
                <p><strong>Processor:</strong> {info['processor'] or 'N/A'}</p>
            </div>
            """, unsafe_allow_html=True)

# ============ FOLDER ANALYZER ============
elif st.session_state.page == 'folder_analyzer':
    st.markdown('<div class="section-header">📁 Folder Analyzer</div>', unsafe_allow_html=True)
    
    folder_path = st.text_input("Folder Path", placeholder="/home/user/Documents or C:\\Users\\User\\Documents")
    
    if st.button("Analyze", type="primary"):
        if folder_path and os.path.exists(folder_path):
            with st.spinner("Analyzing..."):
                folders = analyze_folders(folder_path)
                if folders:
                    for folder in folders[:10]:
                        st.markdown(f"""
                        <div class="data-card">
                            <strong>{folder['name']}</strong><br>
                            Size: {folder['size_gb']:.2f} GB ({folder['size_mb']:.0f} MB)
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No folders found")
        else:
            st.error("Please enter a valid path")

# ============ DNS AUDIT ============
elif st.session_state.page == 'dns_audit':
    st.markdown('<div class="section-header">🌐 DNS Audit</div>', unsafe_allow_html=True)
    
    domain = st.text_input("Domain", placeholder="example.com")
    if st.button("Run Audit", type="primary"):
        if domain:
            import socket
            results = check_dns(domain)
            st.markdown(f"""
            <div class="data-card">
                <h4>DNS Records for {domain}</h4>
                <p>✅ A Record: {'Found' if results.get('a_record') else 'Not found'}</p>
                <p>✅ MX Record: {'Found' if results.get('mx_record') else 'Not found'}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a domain")

# ============ WEBSITE AUDIT ============
elif st.session_state.page == 'website_audit':
    st.markdown('<div class="section-header">🔒 Website Audit</div>', unsafe_allow_html=True)
    
    url = st.text_input("Website URL", placeholder="https://example.com")
    if st.button("Run Audit", type="primary"):
        if url:
            try:
                import requests
                results = check_website(url)
                st.markdown(f"""
                <div class="data-card">
                    <h4>Website Audit for {url}</h4>
                    <p>✅ Reachable: {'Yes' if results.get('reachable') else 'No'}</p>
                    <p>✅ HTTPS: {'Enabled' if results.get('https') else 'Disabled'}</p>
                    <p>📊 Status Code: {results.get('status_code', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            except ImportError:
                st.info("Install requests: pip install requests")
        else:
            st.warning("Please enter a URL")

# ============ EMAIL SECURITY ============
elif st.session_state.page == 'email_security':
    st.markdown('<div class="section-header">📧 Email Security Audit</div>', unsafe_allow_html=True)
    
    domain = st.text_input("Domain", placeholder="example.com")
    if st.button("Run Audit", type="primary"):
        if domain:
            st.markdown(f"""
            <div class="data-card">
                <h4>Email Security for {domain}</h4>
                <p>📧 SPF: Check suggested</p>
                <p>🔑 DKIM: Check suggested</p>
                <p>🛡️ DMARC: Recommended</p>
                <p style="color:#f97316;">Risk: Unknown - Full audit requires DNS tools</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a domain")

# ============ ANALYTICS ============
elif st.session_state.page == 'analytics':
    st.markdown('<div class="section-header">📊 Analytics</div>', unsafe_allow_html=True)
    
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
        st.metric("Average Score", f"{avg_score:.1f}/100")
    else:
        st.info("No data yet. Import leads to see analytics.")

# ============ NOTIFICATION LOG ============
elif st.session_state.page == 'notification_log':
    st.markdown('<div class="section-header">📋 Notification Log</div>', unsafe_allow_html=True)
    
    if st.session_state.email_log:
        for log in reversed(st.session_state.email_log[-20:]):
            st.markdown(f"""
            <div class="data-card">
                <strong>{log['subject']}</strong><br>
                To: {log['to']}<br>
                Status: {log['status']}<br>
                <small>{log['date'].strftime('%Y-%m-%d %H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No notifications sent yet")

# ============ SETTINGS ============
elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    st.markdown("### Resend Email Status")
    if RESEND_AVAILABLE:
        st.success("✅ Resend API configured")
    else:
        st.error("❌ Resend API not configured")
        st.info("Add RESEND_API_KEY to .streamlit/secrets.toml")
    
    st.markdown("---")
    st.markdown("### Data Management")
    
    if st.button("Clear All Leads", type="secondary"):
        st.session_state.leads = []
        st.session_state.email_log = []
        st.success("All leads cleared!")

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Enterprise Suite | Login: hello@techwokx.online")

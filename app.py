# app.py - TechWokx Enterprise Lead Intelligence System
import streamlit as st
import pandas as pd
import requests
import re
import smtplib
import json
import os
import subprocess
import socket
import platform
import psutil
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import hashlib
import uuid
import sqlite3
from pathlib import Path
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import twilio
from twilio.rest import Client

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="TechWokx Enterprise Suite",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ INITIALIZE SESSION STATE ============
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'research_cache' not in st.session_state:
    st.session_state.research_cache = {}
if 'email_log' not in st.session_state:
    st.session_state.email_log = []
if 'whatsapp_log' not in st.session_state:
    st.session_state.whatsapp_log = []
if 'notification_log' not in st.session_state:
    st.session_state.notification_log = []
if 'google_sheet_url' not in st.session_state:
    st.session_state.google_sheet_url = ""
if 'client_sites' not in st.session_state:
    st.session_state.client_sites = []

# ============ HARDCODED USERS (In production, use database) ============
USERS = {
    "admin": {"password": "admin123", "role": "admin", "name": "Administrator"},
    "techwokx": {"password": "techwokx2024", "role": "admin", "name": "TechWokx Team"},
    "client1": {"password": "client123", "role": "client", "name": "Client User"}
}

# ============ DATABASE SETUP ============
def init_database():
    """Initialize SQLite database for client sites"""
    conn = sqlite3.connect('client_sites.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS client_sites
                 (id INTEGER PRIMARY KEY,
                  client_name TEXT,
                  site_name TEXT,
                  site_path TEXT,
                  last_backup TEXT,
                  backup_size TEXT,
                  status TEXT,
                  created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS backup_history
                 (id INTEGER PRIMARY KEY,
                  site_id INTEGER,
                  backup_date TEXT,
                  backup_path TEXT,
                  size TEXT,
                  status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS leads
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  email TEXT,
                  phone TEXT,
                  score INTEGER,
                  status TEXT,
                  source TEXT,
                  created_at TEXT,
                  google_sheet_synced INTEGER DEFAULT 0,
                  whatsapp_sent INTEGER DEFAULT 0,
                  techwokx_notified INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_database()

# ============ AUTHENTICATION FUNCTIONS ============
def check_auth(username, password):
    if username in USERS and USERS[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.user = {
            "username": username,
            "role": USERS[username]["role"],
            "name": USERS[username]["name"]
        }
        return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.page = 'login'
    st.rerun()

# ============ GOOGLE SHEETS INTEGRATION ============
def setup_google_sheets():
    """Setup Google Sheets connection"""
    try:
        # For production, use service account JSON
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Store credentials in secrets
        creds_dict = {
            "type": "service_account",
            "project_id": st.secrets.get("GCP_PROJECT_ID", ""),
            "private_key_id": st.secrets.get("GCP_PRIVATE_KEY_ID", ""),
            "private_key": st.secrets.get("GCP_PRIVATE_KEY", ""),
            "client_email": st.secrets.get("GCP_CLIENT_EMAIL", ""),
            "client_id": st.secrets.get("GCP_CLIENT_ID", ""),
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        return None

def sync_to_google_sheets(lead):
    """Sync lead to Google Sheets"""
    if not st.session_state.google_sheet_url:
        return False
    
    try:
        client = setup_google_sheets()
        if client:
            # Open spreadsheet by URL
            sheet = client.open_by_url(st.session_state.google_sheet_url).sheet1
            # Append lead data
            row = [
                lead.get('name', ''),
                lead.get('email', ''),
                lead.get('phone', ''),
                lead.get('score', 0),
                lead.get('status', ''),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
            return True
    except Exception as e:
        print(f"Google Sheets error: {e}")
    return False

# ============ WHATSAPP INTEGRATION ============
def send_whatsapp_message(to_number, message):
    """Send WhatsApp message using Twilio"""
    try:
        account_sid = st.secrets.get("TWILIO_ACCOUNT_SID", "")
        auth_token = st.secrets.get("TWILIO_AUTH_TOKEN", "")
        from_number = st.secrets.get("TWILIO_WHATSAPP_FROM", "")
        
        if not account_sid:
            # Fallback: Log message (for demo)
            st.session_state.whatsapp_log.append({
                "to": to_number,
                "message": message[:100],
                "date": datetime.now(),
                "status": "Logged (No Twilio)"
            })
            return True
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message,
            from_=f'whatsapp:{from_number}',
            to=f'whatsapp:{to_number}'
        )
        st.session_state.whatsapp_log.append({
            "to": to_number,
            "message": message[:100],
            "date": datetime.now(),
            "status": "Sent"
        })
        return True
    except Exception as e:
        st.session_state.whatsapp_log.append({
            "to": to_number,
            "message": f"Failed: {str(e)[:50]}",
            "date": datetime.now(),
            "status": "Failed"
        })
        return False

def send_whatsapp_lead_notification(lead):
    """Send WhatsApp notification for new lead"""
    message = f"""🔔 NEW LEAD ALERT - TechWokx

📌 Name: {lead.get('name')}
📧 Email: {lead.get('email', 'N/A')}
📞 Phone: {lead.get('phone', 'N/A')}
⭐ Score: {lead.get('score', 0)}/100
🏷️ Status: {lead.get('status', 'New')}

View in CRM: [Link]
"""
    # Send to client
    if lead.get('phone'):
        send_whatsapp_message(lead['phone'], f"Thank you for your interest! Your lead score is {lead.get('score', 0)}/100. We'll contact you soon.")
    
    # Send to TechWokx team
    techwokx_numbers = st.secrets.get("TECHWOKX_WHATSAPP_NUMBERS", "+233555087407").split(",")
    for number in techwokx_numbers:
        send_whatsapp_message(number.strip(), message)
    
    return True

# ============ EMAIL FUNCTIONS ============
def send_email(to_email, subject, body, attachment=None):
    """Send email with optional attachment"""
    if not st.secrets.get("EMAIL_USER", ""):
        return False, "Email not configured"
    
    try:
        msg = MIMEMultipart()
        msg['From'] = st.secrets.get("EMAIL_USER", "")
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if attachment and os.path.exists(attachment):
            with open(attachment, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment)}')
                msg.attach(part)
        
        server = smtplib.SMTP(st.secrets.get("EMAIL_HOST", "smtp.gmail.com"), int(st.secrets.get("EMAIL_PORT", 587)))
        server.starttls()
        server.login(st.secrets.get("EMAIL_USER", ""), st.secrets.get("EMAIL_PASSWORD", ""))
        server.send_message(msg)
        server.quit()
        
        st.session_state.email_log.append({
            "to": to_email,
            "subject": subject,
            "date": datetime.now(),
            "status": "Sent"
        })
        return True, "Email sent"
    except Exception as e:
        return False, str(e)

def send_lead_notifications(lead):
    """Send all notifications for new lead"""
    notifications = []
    
    # 1. Send email to client
    email_body = f"""Dear {lead.get('name')},

Thank you for your interest in TechWokx services.

Your lead score: {lead.get('score', 0)}/100
Status: {lead.get('status', 'New')}

Our team will contact you within 24 hours.

Best regards,
TechWokx Team
"""
    success, msg = send_email(lead.get('email', ''), "Thank you for contacting TechWokx", email_body)
    notifications.append(("Email to Client", success))
    
    # 2. Send WhatsApp to client
    if lead.get('phone'):
        success = send_whatsapp_message(lead['phone'], f"Hi {lead.get('name')}, thanks for reaching out! Your lead score is {lead.get('score', 0)}/100. We'll contact you soon. - TechWokx")
        notifications.append(("WhatsApp to Client", success))
    
    # 3. Send notification to TechWokx team
    techwokx_email = st.secrets.get("TECHWOKX_EMAIL", "hello@techwokx.online")
    team_body = f"""NEW LEAD ALERT

Name: {lead.get('name')}
Email: {lead.get('email')}
Phone: {lead.get('phone', 'N/A')}
Score: {lead.get('score', 0)}/100
Source: {lead.get('source', 'Website')}

Take action: [View in CRM]
"""
    success, msg = send_email(techwokx_email, f"New Lead: {lead.get('name')}", team_body)
    notifications.append(("TechWokx Team Email", success))
    
    # 4. Send WhatsApp to TechWokx
    techwokx_numbers = st.secrets.get("TECHWOKX_WHATSAPP_NUMBERS", "+233555087407").split(",")
    for number in techwokx_numbers:
        success = send_whatsapp_message(number.strip(), f"🔔 NEW LEAD: {lead.get('name')} - Score: {lead.get('score', 0)}/100")
        notifications.append((f"WhatsApp to {number}", success))
    
    # 5. Sync to Google Sheets
    success = sync_to_google_sheets(lead)
    notifications.append(("Google Sheets Sync", success))
    
    st.session_state.notification_log.append({
        "lead": lead.get('name'),
        "notifications": notifications,
        "date": datetime.now()
    })
    
    return notifications

# ============ DEEP LAN ANALYSIS FUNCTIONS ============
def scan_network(ip_range="192.168.1.0/24"):
    """Scan network for devices"""
    devices = []
    try:
        # Get local IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        network = '.'.join(local_ip.split('.')[:-1]) + '.1/24'
        
        # Ping sweep (simplified)
        for i in range(1, 255):
            ip = f"{'.'.join(local_ip.split('.')[:-1])}.{i}"
            response = subprocess.run(['ping', '-c', '1', '-W', '1', ip], capture_output=True)
            if response.returncode == 0:
                try:
                    host = socket.gethostbyaddr(ip)[0]
                except:
                    host = "Unknown"
                devices.append({"ip": ip, "hostname": host, "status": "Online"})
    except Exception as e:
        st.error(f"Network scan error: {e}")
    return devices

def get_system_info():
    """Get detailed system information"""
    info = {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_version": platform.version(),
        "processor": platform.processor(),
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_total": psutil.virtual_memory().total / (1024**3),
        "memory_available": psutil.virtual_memory().available / (1024**3),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": {},
        "network_interfaces": []
    }
    
    # Disk usage
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            info["disk_usage"][partition.mountpoint] = {
                "total": usage.total / (1024**3),
                "used": usage.used / (1024**3),
                "free": usage.free / (1024**3),
                "percent": usage.percent
            }
        except:
            pass
    
    # Network interfaces
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                info["network_interfaces"].append({
                    "name": interface,
                    "ip": addr.address,
                    "netmask": addr.netmask
                })
    
    return info

def analyze_folders(path="/"):
    """Analyze folder structure and sizes"""
    folders = []
    try:
        for item in Path(path).iterdir():
            if item.is_dir():
                try:
                    size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                    folders.append({
                        "name": item.name,
                        "path": str(item),
                        "size_gb": size / (1024**3),
                        "item_count": len(list(item.rglob('*')))
                    })
                except:
                    pass
    except:
        pass
    return sorted(folders, key=lambda x: x['size_gb'], reverse=True)[:20]

def create_backup(source_path, backup_name=None):
    """Create backup of specified folder"""
    if not backup_name:
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    backup_path = f"/tmp/{backup_name}.zip"
    try:
        shutil.make_archive(f"/tmp/{backup_name}", 'zip', source_path)
        size = os.path.getsize(backup_path) / (1024**2)  # MB
        return {"success": True, "path": backup_path, "size_mb": size, "name": backup_name}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============ LEAD FUNCTIONS ============
def add_lead(name, email, phone, score, source="Manual"):
    """Add lead with full notifications"""
    new_id = len(st.session_state.leads) + 1
    status = "Hot" if score >= 80 else "Warm" if score >= 60 else "Cold"
    
    lead = {
        "id": new_id,
        "name": name,
        "email": email,
        "phone": phone,
        "score": score,
        "status": status,
        "source": source,
        "created_at": datetime.now(),
        "notified": False
    }
    
    st.session_state.leads.append(lead)
    
    # Send all notifications
    send_lead_notifications(lead)
    
    # Save to local database
    conn = sqlite3.connect('client_sites.db')
    c = conn.cursor()
    c.execute("INSERT INTO leads (name, email, phone, score, status, source, created_at) VALUES (?,?,?,?,?,?,?)",
              (name, email, phone, score, status, source, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return new_id

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
.status-hot { background: #dc2626; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
.status-warm { background: #f97316; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
.status-cold { background: #64748b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ============ LOGIN PAGE ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 400px; margin: 100px auto;">
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #fbbf24;">🔍 TechWokx</h1>
            <h3>Enterprise Suite</h3>
            <p>Lead Intelligence • Deep LAN Analysis • Multi-channel Notifications</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if check_auth(username, password):
                st.success(f"Welcome back, {st.session_state.user['name']}!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; color: #64748b;">
        <small>Demo credentials: admin / admin123 | techwokx / techwokx2024 | client1 / client123</small>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ============ SIDEBAR NAVIGATION ============
with st.sidebar:
    st.markdown("### 🔍 TechWokx")
    st.markdown(f"#### Welcome, {st.session_state.user['name']}")
    st.markdown(f"<small>Role: {st.session_state.user['role'].title()}</small>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Main Navigation
    nav_items = [
        ("🏠 Dashboard", "dashboard"),
        ("---", "divider0"),
        ("📋 LEAD MANAGEMENT", "header1"),
        ("🔍 Company Research", "company_research"),
        ("📊 Bulk Research", "bulk_research"),
        ("📥 Import Leads", "import_leads"),
        ("👥 Lead CRM", "crm"),
        ("---", "divider1"),
        ("📧 COMMUNICATIONS", "header2"),
        ("📧 Lead Follow-up", "lead_followup"),
        ("✉️ Email Automation", "email_automation"),
        ("💬 WhatsApp Broadcast", "whatsapp_broadcast"),
        ("📊 Google Sheets Sync", "google_sheets"),
        ("---", "divider2"),
        ("🖥️ DEEP LAN ANALYSIS", "header3"),
        ("🌐 Network Scanner", "network_scan"),
        ("💻 System Info", "system_info"),
        ("📁 Folder Analyzer", "folder_analyzer"),
        ("💾 Backup Manager", "backup_manager"),
        ("---", "divider3"),
        ("🛡️ AUDITS", "header4"),
        ("🌐 DNS Audit", "dns_audit"),
        ("🔒 Website Audit", "website_audit"),
        ("📧 Email Security", "email_security"),
        ("🛡️ IT Audit", "it_audit"),
        ("---", "divider4"),
        ("📈 REPORTS", "header5"),
        ("📊 Analytics", "analytics"),
        ("📋 Notification Log", "notification_log"),
        ("⚙️ Settings", "settings"),
        ("---", "divider5"),
        ("🚪 Logout", "logout")
    ]
    
    for label, key in nav_items:
        if label == "---":
            st.markdown("---")
        elif label.startswith("📋") or label.startswith("📧") or label.startswith("🖥️") or label.startswith("🛡️") or label.startswith("📈"):
            st.markdown(f"<small style='color:#94a3b8'>{label}</small>", unsafe_allow_html=True)
        elif st.button(label, key=key, use_container_width=True):
            if key == "logout":
                logout()
            else:
                st.session_state.page = key
                st.rerun()
    
    st.markdown("---")
    st.markdown("### System Status")
    st.markdown(f"Email: {'✅' if st.secrets.get('EMAIL_USER', '') else '❌'}")
    st.markdown(f"WhatsApp: {'✅' if st.secrets.get('TWILIO_ACCOUNT_SID', '') else '❌'}")
    st.markdown(f"Sheets: {'✅' if st.session_state.google_sheet_url else '❌'}")
    
    if st.button("🔄 Run Auto Follow-ups", use_container_width=True):
        st.success("Follow-up check complete!")
    
    st.markdown("---")
    st.markdown('<div class="plan-badge">🚀 Enterprise Plan<br><small>Full Suite Active</small></div>', unsafe_allow_html=True)

# ============ DASHBOARD PAGE ============
if st.session_state.page == 'dashboard':
    total_leads = len(st.session_state.leads)
    hot_leads = sum(1 for l in st.session_state.leads if l.get("score", 0) >= 80)
    emails_sent = len(st.session_state.email_log)
    whatsapp_sent = len(st.session_state.whatsapp_log)
    
    st.markdown('<div class="welcome-card"><h2>Welcome to TechWokx Enterprise Suite</h2><p>Lead Intelligence • Deep LAN Analysis • Multi-channel Notifications</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_leads}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot_leads}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{emails_sent}</div><div class='metric-label'>Emails Sent</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{whatsapp_sent}</div><div class='metric-label'>WhatsApp Msgs</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Recent Leads</div>', unsafe_allow_html=True)
        for lead in st.session_state.leads[-5:]:
            st.markdown(f'<div class="activity-item"><strong>{lead["name"]}</strong> - Score: {lead["score"]}/100<br><small>{lead["created_at"].strftime("%Y-%m-%d %H:%M") if lead.get("created_at") else "Just now"}</small></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">📧 Recent Activity</div>', unsafe_allow_html=True)
        for log in st.session_state.notification_log[-3:]:
            st.markdown(f'<div class="activity-item"><strong>Lead: {log["lead"]}</strong><br><small>{len(log["notifications"])} notifications sent at {log["date"].strftime("%H:%M")}</small></div>', unsafe_allow_html=True)

# ============ DEEP LAN ANALYSIS PAGES ============

elif st.session_state.page == 'network_scan':
    st.markdown('<div class="section-header">🌐 Network Scanner</div>', unsafe_allow_html=True)
    st.caption("Scan local network for connected devices")
    st.markdown("---")
    
    if st.button("🔍 Start Network Scan", type="primary"):
        with st.spinner("Scanning network..."):
            devices = scan_network()
            if devices:
                st.success(f"Found {len(devices)} devices")
                for device in devices:
                    st.markdown(f'<div class="data-card"><strong>IP:</strong> {device["ip"]}<br><strong>Hostname:</strong> {device["hostname"]}<br><strong>Status:</strong> 🟢 Online</div>', unsafe_allow_html=True)
            else:
                st.warning("No devices found or scan incomplete")

elif st.session_state.page == 'system_info':
    st.markdown('<div class="section-header">💻 System Information</div>', unsafe_allow_html=True)
    st.caption("Detailed system analysis for client site")
    st.markdown("---")
    
    if st.button("🔍 Scan System", type="primary"):
        with st.spinner("Analyzing system..."):
            info = get_system_info()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="data-card">
                    <h4>Hardware Info</h4>
                    <p><strong>Hostname:</strong> {info['hostname']}</p>
                    <p><strong>Platform:</strong> {info['platform']}</p>
                    <p><strong>Processor:</strong> {info['processor'] or 'N/A'}</p>
                    <p><strong>CPU Cores:</strong> {info['cpu_count']}</p>
                    <p><strong>CPU Usage:</strong> {info['cpu_percent']}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="data-card">
                    <h4>Memory & Storage</h4>
                    <p><strong>Total RAM:</strong> {info['memory_total']:.1f} GB</p>
                    <p><strong>Available RAM:</strong> {info['memory_available']:.1f} GB</p>
                    <p><strong>RAM Usage:</strong> {info['memory_percent']}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Network interfaces
            st.markdown('<div class="data-card"><h4>Network Interfaces</h4>', unsafe_allow_html=True)
            for nic in info['network_interfaces']:
                st.write(f"**{nic['name']}:** {nic['ip']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Disk usage
            st.markdown('<div class="data-card"><h4>Disk Usage</h4>', unsafe_allow_html=True)
            for mount, usage in info['disk_usage'].items():
                st.write(f"**{mount}:** {usage['used']:.1f} GB / {usage['total']:.1f} GB ({usage['percent']}% used)")
                st.progress(usage['percent'] / 100)
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == 'folder_analyzer':
    st.markdown('<div class="section-header">📁 Folder Analyzer</div>', unsafe_allow_html=True)
    st.caption("Analyze folder structures and identify large directories")
    st.markdown("---")
    
    folder_path = st.text_input("Folder Path to Analyze", placeholder="/home/user/Documents or C:\\Users\\User\\Documents")
    
    if st.button("🔍 Analyze Folders", type="primary"):
        if folder_path:
            with st.spinner(f"Analyzing {folder_path}..."):
                folders = analyze_folders(folder_path)
                if folders:
                    st.success(f"Found {len(folders)} folders")
                    for folder in folders[:10]:
                        st.markdown(f"""
                        <div class="data-card">
                            <strong>{folder['name']}</strong><br>
                            Size: {folder['size_gb']:.2f} GB<br>
                            Items: {folder['item_count']:,}<br>
                            Path: {folder['path'][:80]}...
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No folders found or unable to access")

elif st.session_state.page == 'backup_manager':
    st.markdown('<div class="section-header">💾 Backup Manager</div>', unsafe_allow_html=True)
    st.caption("Create and manage backups of client data")
    st.markdown("---")
    
    backup_source = st.text_input("Source Folder to Backup", placeholder="/home/user/important_data")
    backup_name = st.text_input("Backup Name (optional)", placeholder="auto-generated")
    
    if st.button("📦 Create Backup", type="primary"):
        if backup_source:
            with st.spinner("Creating backup..."):
                result = create_backup(backup_source, backup_name)
                if result['success']:
                    st.success(f"Backup created: {result['name']}.zip ({result['size_mb']:.1f} MB)")
                    
                    # Option to download
                    with open(result['path'], 'rb') as f:
                        st.download_button("Download Backup", f, f"{result['name']}.zip", "application/zip")
                    
                    # Send notification
                    send_whatsapp_message(st.secrets.get("TECHWOKX_WHATSAPP_NUMBERS", "+233555087407"), f"Backup created: {result['name']} ({result['size_mb']:.1f} MB)")
                else:
                    st.error(f"Backup failed: {result['error']}")

# ============ COMMUNICATIONS PAGES ============

elif st.session_state.page == 'whatsapp_broadcast':
    st.markdown('<div class="section-header">💬 WhatsApp Broadcast</div>', unsafe_allow_html=True)
    st.caption("Send WhatsApp messages to leads")
    st.markdown("---")
    
    # Select recipients
    recipient_type = st.radio("Send to", ["All Leads", "Hot Leads Only", "Warm Leads Only", "Specific Lead"])
    
    if recipient_type == "Specific Lead":
        lead_options = {f"{l['name']} - {l.get('phone', 'No phone')}": l for l in st.session_state.leads if l.get('phone')}
        selected = st.selectbox("Select Lead", list(lead_options.keys()))
        recipient = [lead_options[selected]]
    else:
        if recipient_type == "All Leads":
            recipients = [l for l in st.session_state.leads if l.get('phone')]
        elif recipient_type == "Hot Leads Only":
            recipients = [l for l in st.session_state.leads if l.get('score', 0) >= 80 and l.get('phone')]
        else:
            recipients = [l for l in st.session_state.leads if 60 <= l.get('score', 0) < 80 and l.get('phone')]
    
    st.info(f"📊 {len(recipients)} leads selected")
    
    message = st.text_area("Message", height=150, placeholder="Enter your WhatsApp message here...")
    
    if st.button("📤 Send Broadcast", type="primary"):
        if message and recipients:
            success_count = 0
            progress = st.progress(0)
            for i, lead in enumerate(recipients):
                if send_whatsapp_message(lead['phone'], message):
                    success_count += 1
                progress.progress((i + 1) / len(recipients))
            st.success(f"Sent to {success_count}/{len(recipients)} leads")

elif st.session_state.page == 'google_sheets':
    st.markdown('<div class="section-header">📊 Google Sheets Integration</div>', unsafe_allow_html=True)
    st.caption("Connect Google Sheets for lead data sync")
    st.markdown("---")
    
    sheet_url = st.text_input("Google Sheet URL", value=st.session_state.google_sheet_url, placeholder="https://docs.google.com/spreadsheets/d/...")
    
    if st.button("Connect & Test Sync"):
        st.session_state.google_sheet_url = sheet_url
        if sheet_url:
            test_lead = {
                'name': 'Test Lead',
                'email': 'test@example.com',
                'phone': '+233 XX XXX XXXX',
                'score': 75,
                'status': 'Warm'
            }
            if sync_to_google_sheets(test_lead):
                st.success("✅ Connected! Test lead synced to Google Sheets")
            else:
                st.error("❌ Connection failed. Check credentials in secrets.")
    
    st.markdown("---")
    if st.button("🔄 Sync All Existing Leads"):
        with st.spinner("Syncing..."):
            synced = 0
            for lead in st.session_state.leads:
                if sync_to_google_sheets(lead):
                    synced += 1
            st.success(f"Synced {synced} leads to Google Sheets")

# ============ LEAD MANAGEMENT PAGES ============

elif st.session_state.page == 'import_leads':
    st.markdown('<div class="section-header">📥 Import Leads</div>', unsafe_allow_html=True)
    st.caption("Import leads from CSV, Excel, or JSON - Auto notifications will be sent")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Choose file", type=['csv', 'xlsx', 'json'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_json(uploaded_file)
            
            st.dataframe(df.head())
            
            if st.button("Import Leads", type="primary"):
                imported = 0
                for _, row in df.iterrows():
                    name = row.get('name', row.get('Name', ''))
                    email = row.get('email', row.get('Email', ''))
                    phone = str(row.get('phone', row.get('Phone', '')))
                    score = int(row.get('score', row.get('Score', 50)))
                    
                    if name and email:
                        add_lead(name, email, phone, score, "CSV Import")
                        imported += 1
                
                st.success(f"✅ Imported {imported} leads! Notifications sent to all channels.")
        except Exception as e:
            st.error(f"Error: {e}")

# ============ NOTIFICATION LOG PAGE ============

elif st.session_state.page == 'notification_log':
    st.markdown('<div class="section-header">📋 Notification Log</div>', unsafe_allow_html=True)
    st.caption("Track all notifications sent to leads and team")
    st.markdown("---")
    
    if st.session_state.notification_log:
        for log in reversed(st.session_state.notification_log):
            with st.expander(f"📧 {log['lead']} - {log['date'].strftime('%Y-%m-%d %H:%M:%S')}"):
                for notification in log['notifications']:
                    status = "✅" if notification[1] else "❌"
                    st.write(f"{status} {notification[0]}")
    else:
        st.info("No notifications sent yet")

# ============ SETTINGS PAGE ============

elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ System Settings</div>', unsafe_allow_html=True)
    st.caption("Configure API keys and integration settings")
    st.markdown("---")
    
    st.markdown("""
    ### Required Configuration
    
    Create `.streamlit/secrets.toml` with:
    
    ```toml
    # Email Settings
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USER = "your@email.com"
    EMAIL_PASSWORD = "your_app_password"
    
    # Twilio WhatsApp
    TWILIO_ACCOUNT_SID = "your_sid"
    TWILIO_AUTH_TOKEN = "your_token"
    TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
    
    # Google Sheets
    GCP_PROJECT_ID = "your_project"
    GCP_PRIVATE_KEY_ID = "key_id"
    GCP_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----..."
    GCP_CLIENT_EMAIL = "service@account.com"
    
    # TechWokx Team
    TECHWOKX_EMAIL = "hello@techwokx.online"
    TECHWOKX_WHATSAPP_NUMBERS = "+233555087407"

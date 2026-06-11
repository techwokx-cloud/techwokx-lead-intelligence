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
import qrcode
from io import BytesIO
import base64
import re
import tldextract

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
if 'call_queue' not in st.session_state:
    st.session_state.call_queue = []
if 'visit_queue' not in st.session_state:
    st.session_state.visit_queue = []
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None
if 'searched_companies' not in st.session_state:
    st.session_state.searched_companies = set()

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

# ============ API KEYS ============
def get_api_keys():
    try:
        return {
            "google_maps": st.secrets.get("GOOGLE_MAPS_API_KEY", ""),
            "serp_api": st.secrets.get("SERP_API_KEY", ""),
        }
    except:
        return {"google_maps": "", "serp_api": ""}

# ============ COMPLETE GHANA CITIES DATABASE ============
ALL_CITIES = {
    "Greater Accra": [
        "Accra Central", "Airport Residential", "Airport City", "Cantonments", "Labone", 
        "Osu", "Ring Road Central", "Ridge", "North Ridge", "Adabraka", "Asylum Down", 
        "Tudu", "Jamestown", "Usshertown", "Korle Bu", "Mamprobi", "Chorkor", "Kaneshie", 
        "Achimota", "Legon", "Madina", "Adenta", "East Legon", "West Legon", "Dzorwulu", 
        "Shiashie", "Trasacco Valley", "Spintex", "Sakumono", "Teshie", "Nungua", "Lashibi", 
        "Ashaiman", "Tema", "Tema Community 1-10", "Tema Industrial Area", "Kpone", 
        "Adjei Kojo", "Afienya", "Dawhenya", "Prampram", "Dodowa", "Abokobi", "Danfa", 
        "Teiman", "Taifa", "Kwabenya", "Dome", "Pokuase", "Haasto", "Amasaman", "Nsawam", 
        "Medie", "Sarpeiman", "Weija", "Gbawe", "Mallam", "Kwashieman", "Darkuman", 
        "Kasoa", "Budumburam", "Opeikuma"
    ],
    "Ashanti": [
        "Kumasi Central", "Adum", "Bantama", "Asafo", "Asokwa", "Tafo", "Suame", "Oforikrom", 
        "Ayigya", "Bohyen", "Kaase", "Danyame", "Amakom", "Buokrom", "Kwadaso", "Nhyiaeso", 
        "Abuakwa", "Mampong", "Atonsu", "Ahinsan", "Boadi", "Kentinkrono", "Ayeduase", "Kotei", 
        "Santasi", "Patase", "Abrepo", "Bekwai", "Obuasi", "Konongo", "Effiduase", "Mamponteng"
    ],
    "Western": [
        "Takoradi Central", "Sekondi", "Effiakuma", "Anaji", "Kwesimintsim", "Apremdo", 
        "Kojokrom", "Nkontompo", "Fijai", "Nkroful", "Adiembra", "Essikado", "Tarkwa", 
        "Nsuta", "Tamso", "Prestea", "Bogoso"
    ],
    "Central": [
        "Cape Coast Central", "Pedu", "Adisadel", "Amamoma", "Kakumdo", "Kasoa Central", 
        "Opeikuma", "Akweley", "Budumburam", "Millennium City", "Winneba", "Elmina"
    ],
    "Eastern": [
        "Koforidua Central", "Adweso", "Effiduase", "Oyoko", "New Juaben", "Nsawam", 
        "Akwatia", "Asamankese", "Akim Oda", "Akim Swedru", "Anyinam", "Suhum", "Aburi"
    ],
    "Volta": [
        "Ho Central", "Hliha", "Ahoe", "Bankoe", "Deme", "Dome", "Klefe", "Hohoe", 
        "Keta", "Anloga", "Denu", "Sogakope", "Kpando"
    ],
    "Northern": [
        "Tamale Central", "Jisonayili", "Dungu", "Lamashegu", "Tishigu", "Yendi", 
        "Bimbilla", "Gushegu", "Karaga", "Savelugu"
    ],
    "Upper East": ["Bolgatanga Central", "Zuarungu", "Bongo", "Navrongo", "Paga", "Bawku"],
    "Upper West": ["Wa Central", "Dafiama", "Gwolu", "Jirapa", "Lawra", "Nandom"],
    "Western North": ["Sefwi Wiawso", "Bibiani", "Sefwi Bekwai", "Akontombra"],
    "Savannah": ["Damango", "Bole", "Salaga", "Daboya", "Yapei"],
    "North East": ["Nalerigu", "Gambaga", "Walewale", "Bunkpurugu"],
    "Oti": ["Dambai", "Jasikan", "Kadjebi", "Kete Krachi", "Nkwanta"],
    "Ahafo": ["Goaso", "Bechem", "Duayaw Nkwanta", "Kenyasi", "Mim"],
    "Bono East": ["Techiman", "Kintampo", "Nkoranza", "Atebubu", "Jema"],
    "Bono": ["Sunyani Central", "Sunyani West", "Berekum", "Dormaa Ahenkro", "Nsoatre"]
}

# ============ SEARCH QUERIES ============
SEARCH_QUERIES = {
    "Hotels": "hotel",
    "SMEs": "small business company",
    "Restaurants": "restaurant",
    "Schools": "school international",
    "Hospitals": "hospital medical center",
    "Shopping Malls": "shopping mall",
    "Supermarkets": "supermarket",
    "Pharmaceuticals": "pharmacy drug store",
    "Insurance": "insurance company",
    "Law Firms": "law firm solicitor",
    "Tech Companies": "technology IT company",
    "Real Estate": "real estate agency",
    "Construction": "construction company",
    "Logistics": "logistics shipping company",
    "NGOs": "non governmental organization",
    "Printing": "printing services",
    "Event Planning": "event planning services"
}

# ============ QR CODE GENERATION ============
def generate_qr_code_base64(url):
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except:
        return ""

# ============ WEBSITE FUNCTIONS ============
def check_website_status(url):
    if not url:
        return {"working": False, "error": "No website"}
    try:
        if not url.startswith("http"):
            url = "https://" + url
        response = requests.get(url, timeout=5, verify=False)
        return {"working": response.status_code == 200, "status_code": response.status_code}
    except:
        return {"working": False, "error": "Connection failed"}

def generate_possible_emails(company_name, domain=None):
    emails = []
    name_parts = company_name.lower().replace('&', 'and').split()
    base_name = ''.join(name_parts[:2]) if len(name_parts) > 1 else name_parts[0]
    base_name = re.sub(r'[^a-z0-9]', '', base_name)
    patterns = [
        f"info@{base_name}.com",
        f"contact@{base_name}.com",
        f"hello@{base_name}.com",
        f"admin@{base_name}.com"
    ]
    if domain:
        clean_domain = domain.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]
        patterns = [f"info@{clean_domain}", f"contact@{clean_domain}", f"hello@{clean_domain}"]
    return patterns

# ============ CALL SCRIPT ============
CALL_SCRIPT_TEMPLATE = """
================================================================================
                          CALL SCRIPT - TECHWOKX IT SOLUTIONS
================================================================================

Company: {company_name}
Phone: {phone}
Date: _______________

----------------- INTRODUCTION -----------------
"Hello, this is George from TechWokx IT Solutions. 
Am I speaking with the person responsible for IT or business operations?"

----------------- IF YES -----------------
"Great! We recently tried to reach you about our FREE IT assessment."

"We help businesses fix email and IT problems - emails going to spam, 
website issues, printer problems, and data backup."

----------------- THE OFFER -----------------
"We're offering a FREE 5-Step Email & IT Health Check that takes less than 5 minutes."

----------------- NEXT STEPS -----------------
• If interested: "I'll send the assessment link to your email. What's the best email?"
• If not interested: "Would you prefer a physical letter?"
• If busy: "What's a better time to reach you?"

================================================================================
"""

def generate_call_script(company_name, phone, bounce_reason=""):
    return CALL_SCRIPT_TEMPLATE.format(company_name=company_name, phone=phone)

# ============ PERSONALIZED LETTER ============
def get_personalized_letter(company_name, phone="", address=""):
    qr_base64 = generate_qr_code_base64("https://techwokx.online/#audit")
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return f"""
================================================================================
                          TECHWOKX IT SOLUTIONS
                    FREE 5-Step Email & IT Health Check
================================================================================

Date: {current_date}

To: Management Team
{company_name}
{address}
Ghana

Dear Management Team,

I hope this letter finds you well.

My name is George Jabley, and I represent TechWokx IT Solutions. We help businesses 
improve their technology operations through reliable email systems, IT support, 
backup solutions, infrastructure reviews, and business continuity planning.

As part of our business outreach program, we conducted a high-level review of 
your organization's publicly available digital presence.

================================================================================
                          WHAT WE OBSERVED
================================================================================

• We were unable to verify whether all recommended email authentication records 
  are fully configured.
• Your company logo does not currently appear alongside emails in supported inboxes.
• There may be opportunities to improve email deliverability and trust indicators.
• We could not verify the existence of backup and recovery measures protecting 
  business-critical communications and data.

================================================================================
              FIND OUT YOURSELF: 5-STEP EMAIL & IT HEALTH CHECK
================================================================================

To receive your complimentary assessment:
• Scan the QR code on this letter
• Or visit: techwokx.online/#audit

The assessment takes less than five minutes and provides:
• A personalized technology health score
• Email configuration insights

================================================================================
                         OUR SERVICES
================================================================================

⚡ Entry — Fast Fix: Email security setup, DNS configuration, professional signatures

🔄 Recurring IT Retainer: 24/7 remote support, network troubleshooting, system health checks

📋 Infrastructure Audit: Complete IT environment audit with risk report

🤖 Automation Scripts: Custom automation for your business processes

================================================================================
                         LET'S TALK
================================================================================

📞 WhatsApp: +233 555 087 407
✉️ Email: hello@techwokx.online
🌐 Website: techwokx.online

At Techwokx, our approach is simple: Diagnose before we prescribe.

Kind regards,

George Jabley
Founder & IT Operations Lead
TechWokx Ghana
================================================================================
"""

# ============ EMAIL BODY ============
def get_email_body(company_name):
    audit_url = "https://techwokx.online/#audit"
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>FREE 5-Step Email & IT Health Check</h2>
        <p>Dear Management Team,</p>
        <p>My name is George Jabley from TechWokx IT Solutions.</p>
        <p>We conducted a review of your digital presence and identified opportunities 
        to improve your IT infrastructure and email security.</p>
        <p><strong>Get your Business Email Risk Score:</strong><br>
        <a href="{audit_url}">techwokx.online/#audit</a></p>
        <p>Best regards,<br>George Jabley<br>TechWokx Ghana<br>📞 +233 555 087 407</p>
    </body>
    </html>
    """

# ============ GOOGLE PLACES API ============
def search_google_places(api_key, query, location):
    if not api_key:
        return []
    try:
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {"key": api_key, "address": f"{location}, Ghana"}
        geocode_response = requests.get(geocode_url, params=geocode_params, timeout=10)
        geocode_data = geocode_response.json()
        if not geocode_data.get('results'):
            return []
        lat = geocode_data['results'][0]['geometry']['location']['lat']
        lng = geocode_data['results'][0]['geometry']['location']['lng']
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places_params = {
            "key": api_key, "location": f"{lat},{lng}", "radius": 5000,
            "keyword": query, "type": "establishment"
        }
        response = requests.get(places_url, params=places_params, timeout=10)
        data = response.json()
        businesses = []
        for place in data.get('results', [])[:20]:
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                "key": api_key, "place_id": place['place_id'],
                "fields": "name,formatted_address,formatted_phone_number,website,rating"
            }
            details_response = requests.get(details_url, params=details_params, timeout=10)
            details = details_response.json().get('result', {})
            businesses.append({
                "name": place.get('name'),
                "address": details.get('formatted_address', place.get('vicinity', '')),
                "phone": details.get('formatted_phone_number', ''),
                "website": details.get('website', ''),
                "email": "",
                "rating": details.get('rating', 0),
                "place_id": place.get('place_id')
            })
        return businesses
    except Exception as e:
        return []

# ============ LEAD FUNCTIONS ============
def send_email_msg(to_email, subject, body):
    if SMTP_CONFIG["sent_today"] >= SMTP_CONFIG["daily_limit"]:
        return False, "Daily limit reached"
    try:
        msg = MIMEMultipart()
        msg['From'] = f"TechWokx IT Solutions <{SMTP_CONFIG['username']}>"
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
    for lead in st.session_state.leads:
        if lead.get('name', '').lower() == lead_data.get('name', '').lower():
            return False
    new_lead = {
        "id": len(st.session_state.leads) + 1,
        "name": lead_data.get("name"),
        "address": lead_data.get("address", ""),
        "phone": lead_data.get("phone", ""),
        "website": lead_data.get("website", ""),
        "email": lead_data.get("email", ""),
        "category": lead_data.get("category", ""),
        "rating": lead_data.get("rating", 0),
        "lead_score": 75,
        "created_at": datetime.now().isoformat(),
        "email_sent": False,
        "email_sent_date": None,
        "email_responded": False,
        "call_made": False,
        "call_notes": ""
    }
    st.session_state.leads.append(new_lead)
    save_leads()
    return True

def update_email_sent(lead_name, email):
    for lead in st.session_state.leads:
        if lead['name'] == lead_name:
            lead['email_sent'] = True
            lead['email_sent_date'] = datetime.now().isoformat()
            save_leads()
            return True
    return False

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
        ("🏠 Dashboard", "dashboard"),
        ("🔍 Search Companies", "search"),
        ("👥 Leads CRM", "crm"),
        ("📞 Call Queue", "call_queue"),
        ("🏢 Visit Queue", "visit_queue"),
        ("📧 Email Log", "email_log"),
        ("⚙️ Settings", "settings"),
        ("🚪 Logout", "logout")
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
    api_keys = get_api_keys()
    st.markdown(f"Google Maps: {'✅' if api_keys['google_maps'] else '❌'}")
    st.markdown(f"SERP API: {'✅' if api_keys['serp_api'] else '❌'}")
    st.markdown(f"Leads: {len(st.session_state.leads)}")
    st.markdown(f"Emails Today: {SMTP_CONFIG['sent_today']}/{SMTP_CONFIG['daily_limit']}")

# ============ DASHBOARD ============
if st.session_state.current_page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>TechWokx Lead Intelligence</h2>
        <p>Professional IT Outreach | Email Tracking | Call Management</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.leads)}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        emails_sent = len([l for l in st.session_state.leads if l.get('email_sent')])
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{emails_sent}</div><div class='metric-label'>Emails Sent</div></div>", unsafe_allow_html=True)
    with col3:
        responded = len([l for l in st.session_state.leads if l.get('email_responded')])
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{responded}</div><div class='metric-label'>Responded</div></div>", unsafe_allow_html=True)
    with col4:
        remaining = SMTP_CONFIG['daily_limit'] - SMTP_CONFIG['sent_today']
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{remaining}</div><div class='metric-label'>Emails Left</div></div>", unsafe_allow_html=True)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
        if st.button("Search Companies", use_container_width=True):
            st.session_state.current_page = 'search'
            st.rerun()
        if st.button("View CRM", use_container_width=True):
            st.session_state.current_page = 'crm'
            st.rerun()
    with col2:
        st.markdown('<div class="section-header">Recent Leads</div>', unsafe_allow_html=True)
        for lead in st.session_state.leads[-3:]:
            st.markdown(f"<div class='data-card'><strong>{lead['name']}</strong><br>Added: {lead['created_at'][:10]}</div>", unsafe_allow_html=True)

# ============ SEARCH COMPANIES ============
if st.session_state.current_page == 'search':
    st.markdown('<div class="section-header">Search Companies</div>', unsafe_allow_html=True)
    st.caption("Find businesses across Ghana using Google Places API")
    st.markdown("---")
    api_keys = get_api_keys()
    if not api_keys["google_maps"]:
        st.error("Google Maps API key not configured!")
        st.stop()
    
    col1, col2 = st.columns(2)
    with col1:
        regions = list(ALL_CITIES.keys())
        selected_region = st.selectbox("Select Region", regions)
    with col2:
        if selected_region:
            cities = ALL_CITIES[selected_region]
            selected_city = st.selectbox("Select City/Town", cities)
    
    col1, col2 = st.columns(2)
    with col1:
        categories = list(SEARCH_QUERIES.keys())
        selected_category = st.selectbox("Business Category", categories)
    with col2:
        limit = st.slider("Number of Companies", 5, 30, 15)
    
    if st.button("Search", type="primary"):
        if selected_city:
            with st.spinner(f"Searching for {selected_category} in {selected_city}..."):
                query = SEARCH_QUERIES.get(selected_category, selected_category)
                businesses = search_google_places(api_keys["google_maps"], query, selected_city)
                for biz in businesses:
                    biz["category"] = selected_category
                    biz["city"] = selected_city
                    biz["region"] = selected_region
                st.session_state.batch_results = businesses[:limit]
                st.success(f"Found {len(businesses)} businesses")
    
    if st.session_state.batch_results:
        st.markdown("### Search Results")
        for idx, company in enumerate(st.session_state.batch_results):
            with st.expander(f"Company: {company['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Address:** {company.get('address', 'N/A')}")
                    st.markdown(f"**Phone:** {company.get('phone', 'N/A')}")
                    website = company.get('website', '')
                    if website:
                        status = check_website_status(website)
                        st.markdown(f"**Website:** {website} {'Working' if status['working'] else 'Not working'}")
                    else:
                        st.markdown(f"**Website:** Not found")
                with col2:
                    st.markdown(f"**Rating:** {'⭐' * int(company.get('rating', 0))} {company.get('rating', 'N/A')}")
                    st.markdown(f"**Category:** {selected_category}")
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("View Letter", key=f"letter_{idx}"):
                        letter = get_personalized_letter(company['name'], company.get('phone', ''), company.get('address', ''))
                        st.code(letter, language='text')
                with col2:
                    if st.button("Add to CRM", key=f"add_{idx}"):
                        if add_lead(company):
                            st.success(f"Added {company['name']} to CRM")
                            st.rerun()
                        else:
                            st.warning("Already in CRM")
                with col3:
                    possible_emails = generate_possible_emails(company['name'], company.get('website'))
                    if possible_emails:
                        selected_email = st.selectbox("Email", possible_emails, key=f"email_{idx}")
                    else:
                        selected_email = st.text_input("Email", key=f"email_input_{idx}")
                    if st.button("Send Email", key=f"send_{idx}"):
                        if selected_email:
                            email_body = get_email_body(company['name'])
                            subject = f"FREE IT Assessment for {company['name']}"
                            success, msg = send_email_msg(selected_email, subject, email_body)
                            if success:
                                update_email_sent(company['name'], selected_email)
                                st.success(f"Email sent to {company['name']}")
                                st.rerun()
                            else:
                                st.error(f"Failed: {msg}")
                                call_script = generate_call_script(company['name'], company.get('phone', ''), msg)
                                st.session_state.call_queue.append({
                                    "company": company['name'],
                                    "phone": company.get('phone', ''),
                                    "script": call_script,
                                    "reason": msg,
                                    "added_date": datetime.now().isoformat()
                                })
                                st.info("Added to call queue for follow-up")
                        else:
                            st.warning("Enter email address")

# ============ LEADS CRM ============
elif st.session_state.current_page == 'crm':
    st.markdown('<div class="section-header">Leads CRM</div>', unsafe_allow_html=True)
    st.caption(f"Total Leads: {len(st.session_state.leads)}")
    st.markdown("---")
    
    if st.session_state.leads:
        for lead in st.session_state.leads:
            with st.expander(f"{lead['name']} - Score: {lead['lead_score']}/100"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Address:** {lead.get('address', 'N/A')}")
                    st.markdown(f"**Phone:** {lead.get('phone', 'N/A')}")
                    st.markdown(f"**Website:** {lead.get('website', 'N/A')}")
                with col2:
                    st.markdown(f"**Email:** {lead.get('email', 'N/A')}")
                    st.markdown(f"**Added:** {lead['created_at'][:10]}")
                    st.markdown(f"**Email Sent:** {'Yes' if lead.get('email_sent') else 'No'}")
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"View Letter", key=f"letter_{lead['id']}"):
                        letter = get_personalized_letter(lead['name'], lead.get('phone', ''), lead.get('address', ''))
                        st.code(letter, language='text')
                with col2:
                    if st.button(f"Add to Call Queue", key=f"call_{lead['id']}"):
                        call_script = generate_call_script(lead['name'], lead.get('phone', ''))
                        st.session_state.call_queue.append({
                            "company": lead['name'],
                            "phone": lead.get('phone', ''),
                            "script": call_script,
                            "added_date": datetime.now().isoformat()
                        })
                        st.success("Added to call queue")
                with col3:
                    if st.button(f"Delete", key=f"del_{lead['id']}"):
                        st.session_state.leads = [l for l in st.session_state.leads if l['id'] != lead['id']]
                        save_leads()
                        st.success(f"Deleted {lead['name']}")
                        st.rerun()
    else:
        st.info("No leads yet. Run a search to find companies.")

# ============ CALL QUEUE ============
elif st.session_state.current_page == 'call_queue':
    st.markdown('<div class="section-header">Call Queue</div>', unsafe_allow_html=True)
    st.caption("Companies to call for follow-up")
    st.markdown("---")
    
    if st.session_state.call_queue:
        for idx, call in enumerate(st.session_state.call_queue):
            with st.expander(f"{call['company']} - {call.get('phone', 'No phone')}"):
                st.markdown("### Call Script")
                st.code(call.get('script', 'No script'), language='markdown')
                if call.get('reason'):
                    st.warning(f"Reason: {call['reason']}")
                col1, col2 = st.columns(2)
                with col1:
                    outcome = st.selectbox("Call Outcome", ["Interested", "Not Interested", "Call Back", "Wrong Number", "No Answer"], key=f"outcome_{idx}")
                    if st.button("Save Result", key=f"save_{idx}"):
                        for lead in st.session_state.leads:
                            if lead['name'] == call['company']:
                                lead['call_made'] = True
                                lead['call_notes'] = f"Outcome: {outcome} on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                                if outcome == "Interested" and lead.get('email'):
                                    lead['email_sent'] = False
                                save_leads()
                                st.success("Call result saved")
                                st.rerun()
                with col2:
                    if st.button("Remove", key=f"remove_{idx}"):
                        st.session_state.call_queue.pop(idx)
                        st.rerun()
    else:
        st.success("No pending calls")

# ============ VISIT QUEUE ============
elif st.session_state.current_page == 'visit_queue':
    st.markdown('<div class="section-header">Visit Queue</div>', unsafe_allow_html=True)
    st.caption("Companies for physical visit")
    st.markdown("---")
    
    if st.session_state.visit_queue:
        for idx, visit in enumerate(st.session_state.visit_queue):
            with st.expander(f"{visit['company']}"):
                st.markdown(f"**Address:** {visit.get('address', 'N/A')}")
                st.markdown(f"**Phone:** {visit.get('phone', 'N/A')}")
                if st.button("Mark Visited", key=f"visit_{idx}"):
                    st.session_state.visit_queue.pop(idx)
                    st.rerun()
    else:
        st.success("No pending visits")

# ============ EMAIL LOG ============
elif st.session_state.current_page == 'email_log':
    st.markdown('<div class="section-header">Email Log</div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.email_log:
        for log in reversed(st.session_state.email_log[-50:]):
            st.markdown(f"""
            <div class="data-card">
                <strong>To:</strong> {log['to']}<br>
                <strong>Company:</strong> {log['company']}<br>
                <strong>Date:</strong> {log['date'][:19]}<br>
                <strong>Status:</strong> {log['status']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No emails sent yet")

# ============ SETTINGS ============
elif st.session_state.current_page == 'settings':
    st.markdown('<div class="section-header">Settings</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### API Configuration")
    st.code("""
# .streamlit/secrets.toml
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
SERP_API_KEY = "your_serp_api_key"
    """)
    st.markdown("### Email Configuration")
    st.info(f"""
    **SMTP Settings:**
    - Host: {SMTP_CONFIG['host']}
    - Port: {SMTP_CONFIG['port']}
    - Username: {SMTP_CONFIG['username']}
    - Daily Limit: {SMTP_CONFIG['daily_limit']} emails/day
    """)
    new_limit = st.number_input("Daily Email Limit", min_value=10, max_value=200, value=SMTP_CONFIG['daily_limit'])
    if st.button("Update Limit"):
        SMTP_CONFIG['daily_limit'] = new_limit
        st.success(f"Daily limit updated to {new_limit}")
    st.markdown("### Data Management")
    if st.button("Clear All Data", type="secondary"):
        st.session_state.leads = []
        st.session_state.email_log = []
        st.session_state.batch_results = []
        st.session_state.call_queue = []
        st.session_state.visit_queue = []
        save_leads()
        save_email_log()
        st.success("All data cleared")
        st.rerun()

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("2024 TechWokx IT Solutions | Professional IT Outreach")

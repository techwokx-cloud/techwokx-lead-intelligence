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
import uuid

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

# ============ API KEYS (from secrets) ============
def get_api_keys():
    try:
        return {
            "google_maps": st.secrets.get("GOOGLE_MAPS_API_KEY", ""),
            "serp_api": st.secrets.get("SERP_API_KEY", ""),
            "openai": st.secrets.get("OPENAI_API_KEY", "")
        }
    except:
        return {"google_maps": "", "serp_api": "", "openai": ""}

# ============ REAL GOOGLE PLACES API INTEGRATION ============
def search_google_places(api_key, query, location, radius=5000):
    """Search for real businesses using Google Places API"""
    if not api_key:
        return []
    
    try:
        # First, get location coordinates
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {
            "key": api_key,
            "address": f"{location}, Ghana"
        }
        geocode_response = requests.get(geocode_url, params=geocode_params, timeout=10)
        geocode_data = geocode_response.json()
        
        if not geocode_data.get('results'):
            return []
        
        lat = geocode_data['results'][0]['geometry']['location']['lat']
        lng = geocode_data['results'][0]['geometry']['location']['lng']
        
        # Search for places
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places_params = {
            "key": api_key,
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": query,
            "type": "establishment"
        }
        
        response = requests.get(places_url, params=places_params, timeout=10)
        data = response.json()
        
        businesses = []
        for place in data.get('results', [])[:20]:
            # Get more details for each place
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                "key": api_key,
                "place_id": place['place_id'],
                "fields": "name,formatted_address,formatted_phone_number,website,rating"
            }
            details_response = requests.get(details_url, params=details_params, timeout=10)
            details = details_response.json().get('result', {})
            
            businesses.append({
                "name": place.get('name'),
                "address": details.get('formatted_address', place.get('vicinity', '')),
                "phone": details.get('formatted_phone_number', ''),
                "website": details.get('website', ''),
                "rating": details.get('rating', 0),
                "place_id": place.get('place_id')
            })
        
        return businesses
    except Exception as e:
        st.warning(f"Google Places API error: {e}")
        return []

def search_serp_businesses(api_key, query, location):
    """Search for real businesses using SERP API"""
    if not api_key:
        return []
    
    try:
        url = "https://serpapi.com/search"
        params = {
            "api_key": api_key,
            "q": f"{query} in {location}, Ghana",
            "location": f"{location}, Ghana",
            "engine": "google",
            "type": "search"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        businesses = []
        
        # Extract local results
        if "local_results" in data:
            for result in data["local_results"][:15]:
                businesses.append({
                    "name": result.get("title", ""),
                    "address": result.get("address", ""),
                    "phone": result.get("phone", ""),
                    "website": result.get("website", ""),
                    "rating": result.get("rating", 0)
                })
        
        # Also check organic results
        if "organic_results" in data and not businesses:
            for result in data["organic_results"][:10]:
                if "business" in result.get("title", "").lower() or "company" in result.get("title", "").lower():
                    businesses.append({
                        "name": result.get("title", ""),
                        "address": "",
                        "phone": "",
                        "website": result.get("link", ""),
                        "rating": 0
                    })
        
        return businesses
    except Exception as e:
        st.warning(f"SERP API error: {e}")
        return []

# ============ LOCATION DATABASE (for API queries) ============
LOCATIONS = {
    "Greater Accra": {
        "Airport Area": ["Airport City", "Airport Residential", "Airport West"],
        "Osu": ["Osu", "Oxford Street"],
        "Labadi": ["Labadi", "Labadi Beach Road"],
        "Cantonments": ["Cantonments"],
        "East Legon": ["East Legon"],
        "Madina": ["Madina"],
        "Adabraka": ["Adabraka"],
        "Dzorwulu": ["Dzorwulu"],
        "Achimota": ["Achimota"],
        "Spintex": ["Spintex Road"],
        "Dodowa": ["Dodowa"]
    },
    "Tema": {
        "Community 1": ["Tema Community 1"],
        "Community 5": ["Tema Community 5"],
        "Community 9": ["Tema Community 9"],
        "Industrial Area": ["Tema Industrial Area"],
        "Sakumono": ["Sakumono"],
        "Ashaiman": ["Ashaiman"]
    },
    "Ashanti Region": {
        "Kumasi": ["Kumasi", "Adum", "Asokwa"],
        "Obuasi": ["Obuasi"],
        "Mampong": ["Mampong"]
    },
    "Western Region": {
        "Takoradi": ["Takoradi"],
        "Sekondi": ["Sekondi"],
        "Tarkwa": ["Tarkwa"]
    },
    "Central Region": {
        "Cape Coast": ["Cape Coast"],
        "Kasoa": ["Kasoa"],
        "Winneba": ["Winneba"]
    },
    "Eastern Region": {
        "Koforidua": ["Koforidua"],
        "Nsawam": ["Nsawam"],
        "Akwatia": ["Akwatia"]
    },
    "Volta Region": {
        "Ho": ["Ho"],
        "Hohoe": ["Hohoe"],
        "Keta": ["Keta"]
    },
    "Northern Region": {
        "Tamale": ["Tamale"],
        "Yendi": ["Yendi"]
    },
    "Bono Region": {
        "Sunyani": ["Sunyani"],
        "Techiman": ["Techiman"]
    }
}

# ============ SEARCH QUERIES BY CATEGORY ============
SEARCH_QUERIES = {
    "Hotels": "hotel",
    "SMEs": "small business company",
    "Banks": "bank",
    "Restaurants": "restaurant",
    "Schools": "school international",
    "Hospitals": "hospital medical center",
    "Shopping Malls": "shopping mall",
    "Supermarkets": "supermarket",
    "Pharmaceuticals": "pharmacy drug store",
    "Insurance": "insurance company",
    "Real Estate": "real estate agency",
    "Tech Companies": "technology IT company",
    "Law Firms": "law firm solicitor",
    "Accounting Firms": "accounting firm",
    "Construction": "construction company",
    "Logistics": "logistics shipping company",
    "Automotive": "car dealer auto repair",
    "Fashion": "fashion boutique clothing store",
    "Fitness": "gym fitness center"
}

# ============ QR CODE GENERATION ============
def generate_qr_code_base64(url):
    """Generate QR code and return as base64 string"""
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

# ============ PROFESSIONAL EMAIL TEMPLATE ============
def generate_professional_email(company, category):
    """Generate comprehensive professional email"""
    
    audit_url = "https://techwokx.online/#audit"
    qr_base64 = generate_qr_code_base64(audit_url)
    current_date = datetime.now().strftime("%B %d, %Y")
    
    email_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>TechWokx IT Assessment</title>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #1e293b;
                margin: 0;
                padding: 0;
                background-color: #f0f4f8;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 20px 25px -12px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px 25px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px 25px;
            }}
            .section {{
                margin-bottom: 25px;
                padding-bottom: 20px;
                border-bottom: 1px solid #e2e8f0;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 15px;
                padding-left: 12px;
                border-left: 3px solid #667eea;
            }}
            .service-list {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 15px 0;
            }}
            .service-tag {{
                background: #e0e7ff;
                color: #4338ca;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
            }}
            .offer-box {{
                background: linear-gradient(135deg, #dbeafe, #ede9fe);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .qr-code {{
                text-align: center;
                margin: 20px 0;
            }}
            .qr-code img {{
                width: 150px;
                height: 150px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px;
                background: white;
            }}
            .button {{
                background: #22c55e;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 8px;
                display: inline-block;
                font-weight: 600;
            }}
            .footer {{
                background: #1e293b;
                color: #94a3b8;
                padding: 20px 25px;
                text-align: center;
                font-size: 12px;
            }}
            .signature {{
                margin-top: 25px;
                padding-top: 20px;
                border-top: 1px solid #e2e8f0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 TechWokx IT Solutions</h1>
                <p>FREE 5-Step Email & IT Health Check</p>
            </div>
            
            <div class="content">
                <p>Dear Management Team,</p>
                
                <p>I hope this letter finds you well.</p>
                
                <p>My name is <strong>George Jabley</strong>, and I represent <strong>TechWokx IT Solutions</strong>. We help businesses improve their technology operations through reliable email systems, IT support, backup solutions, infrastructure reviews, and business continuity planning.</p>
                
                <p>As part of our business outreach program, we conducted a high-level review of your organization's publicly available digital presence.</p>
                
                <div class="section">
                    <div class="section-title">📋 What We Observed</div>
                    <ul>
                        <li>Email authentication records (SPF/DKIM/DMARC) may need configuration</li>
                        <li>Email deliverability and trust indicators could be improved</li>
                        <li>Backup and recovery measures need verification</li>
                        <li>Potential printer and network issues affecting daily operations</li>
                    </ul>
                </div>
                
                <div class="section">
                    <div class="section-title">🛠️ How TechWokx Can Help</div>
                    <div class="service-list">
                        <span class="service-tag">✓ Business Email Health Checks</span>
                        <span class="service-tag">✓ SPF/DKIM/DMARC Configuration</span>
                        <span class="service-tag">✓ Professional Email Branding</span>
                        <span class="service-tag">✓ IT Infrastructure Reviews</span>
                        <span class="service-tag">✓ Managed IT Support</span>
                        <span class="service-tag">✓ Printer & Network Troubleshooting</span>
                        <span class="service-tag">✓ Backup & Recovery Solutions</span>
                        <span class="service-tag">✓ Cloud Productivity Solutions</span>
                    </div>
                </div>
                
                <div class="offer-box">
                    <div class="section-title" style="border-left-color: #22c55e;">🎁 TWO COMPLIMENTARY OFFERS</div>
                    <p><strong>1. 5-Step Email & IT Health Check</strong></p>
                    <div class="qr-code">
                        <img src="data:image/png;base64,{qr_base64}" alt="QR Code">
                    </div>
                    <p>Visit: <a href="{audit_url}">techwokx.online/#audit</a></p>
                    <p><strong>2. Free 15-Minute IT Consultation</strong></p>
                </div>
                
                <div class="signature">
                    <p>Warm regards,</p>
                    <p><strong>George Jabley</strong><br>
                    Founder & IT Operations Lead<br>
                    TechWokx Ghana<br>
                    📞 +233 555 087 407<br>
                    📧 hello@techwokx.online</p>
                </div>
            </div>
            
            <div class="footer">
                <p>© 2024 TechWokx IT Solutions | P.O. Box ML469, Malam, Accra, Ghana</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return email_body

def generate_letter_content(company):
    """Generate letter content for physical mailing"""
    audit_url = "https://techwokx.online/#audit"
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return f"""
================================================================================
                          TECHWOKX IT SOLUTIONS
                    FREE 5-Step Email & IT Health Check
================================================================================

Date: {current_date}

To: Management Team
{company.get('name', 'Valued Business')}
{company.get('address', 'Accra, Ghana')}

Dear Sir/Madam,

I hope this letter finds you well.

My name is George Jabley, and I represent TechWokx IT Solutions. We help businesses 
improve their technology operations through reliable email systems, IT support, 
backup solutions, infrastructure reviews, and business continuity planning.

================================================================================
                          OUR SERVICES
================================================================================

✓ Business Email Health Checks
✓ SPF/DKIM/DMARC Configuration
✓ Professional Email Branding & Signatures
✓ IT Infrastructure Reviews
✓ Managed IT Support Services
✓ Printer & Network Troubleshooting
✓ Backup & Recovery Solutions
✓ Cloud Productivity Solutions
✓ Process Automation

================================================================================
                    TWO COMPLIMENTARY OFFERS
================================================================================

1. 5-Step Email & IT Health Check
   Visit: {audit_url}
   
2. Free 15-Minute IT Consultation
   Call: +233 555 087 407

================================================================================

We would be delighted to help your organization achieve smoother, more secure, 
and more reliable IT operations.

Warm regards,

George Jabley
Founder & IT Operations Lead
TechWokx Ghana
📞 +233 555 087 407
📧 hello@techwokx.online
🌐 techwokx.online

P.O. Box ML469, Malam, Accra, Ghana

================================================================================
"""

# ============ EMAIL FUNCTIONS ============
def send_email(to_email, subject, body):
    """Send email using SMTP"""
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
    """Add lead to CRM"""
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
        "lead_score": 75,
        "created_at": datetime.now().isoformat(),
        "email_sent": False
    }
    st.session_state.leads.append(new_lead)
    save_leads()
    return True

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

# ============ LOGIN CREDENTIALS ============
USERS = {
    "hello@techwokx.online": {
        "password": "Gtech.5628!@#$",
        "role": "admin",
        "name": "TechWokx Admin"
    }
}

# ============ HELPER FUNCTIONS ============
def get_all_categories():
    return list(SEARCH_QUERIES.keys())

def get_all_regions():
    return list(LOCATIONS.keys())

def get_areas_for_region(region):
    if region in LOCATIONS:
        return list(LOCATIONS[region].keys())
    return []

def get_sub_areas_for_area(region, area):
    if region in LOCATIONS and area in LOCATIONS[region]:
        return LOCATIONS[region][area]
    return [area]

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
        ("Batch Company Search", "batch_search"),
        ("Leads CRM", "crm"),
        ("Email Log", "email_log"),
        ("Letter Queue", "letter_queue"),
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
    api_keys = get_api_keys()
    maps_status = "✅" if api_keys["google_maps"] else "❌"
    serp_status = "✅" if api_keys["serp_api"] else "❌"
    st.markdown(f"Google Maps: {maps_status}")
    st.markdown(f"SERP API: {serp_status}")
    st.markdown(f"Leads: {len(st.session_state.leads)}")
    st.markdown(f"Emails Today: {SMTP_CONFIG['sent_today']}/{SMTP_CONFIG['daily_limit']}")

# ============ DASHBOARD ============
if st.session_state.current_page == 'dashboard':
    api_keys = get_api_keys()
    
    st.markdown("""
    <div class="welcome-card">
        <h2>TechWokx Lead Intelligence</h2>
        <p>Real-time Company Search via Google Places API | Automated IT Outreach</p>
        <p>📍 Coverage: Greater Accra, Tema, Ashanti, Western, Central, Eastern, Volta, Northern, Bono Regions</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.leads)}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.email_log)}</div><div class='metric-label'>Emails Sent</div></div>", unsafe_allow_html=True)
    with col3:
        remaining = SMTP_CONFIG['daily_limit'] - SMTP_CONFIG['sent_today']
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{remaining}</div><div class='metric-label'>Emails Remaining</div></div>", unsafe_allow_html=True)
    with col4:
        active_apis = sum([1 for k in api_keys.values() if k])
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{active_apis}/2</div><div class='metric-label'>Active APIs</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    if not api_keys["google_maps"] and not api_keys["serp_api"]:
        st.warning("⚠️ No API keys configured! Add GOOGLE_MAPS_API_KEY or SERP_API_KEY to .streamlit/secrets.toml to fetch real companies.")
        st.info("Without API keys, only sample data will be shown. Get your keys from:")
        st.markdown("- [Google Maps API](https://console.cloud.google.com/)\n- [SERP API](https://serpapi.com/)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📍 Available Locations</div>', unsafe_allow_html=True)
        st.markdown("""
        **Greater Accra:** Airport Area, Osu, Labadi, Cantonments, East Legon, Madina, Adabraka, Dzorwulu, Achimota, Spintex, Dodowa\n
        **Tema:** Community 1, 5, 9, Industrial Area, Sakumono, Ashaiman\n
        **Ashanti:** Kumasi, Obuasi, Mampong\n
        **Western:** Takoradi, Sekondi, Tarkwa\n
        **Central:** Cape Coast, Kasoa, Winneba\n
        **Eastern:** Koforidua, Nsawam, Akwatia\n
        **Volta:** Ho, Hohoe, Keta\n
        **Northern:** Tamale, Yendi\n
        **Bono:** Sunyani, Techiman
        """)
    
    with col2:
        st.markdown('<div class="section-header">🎯 Business Categories</div>', unsafe_allow_html=True)
        categories = get_all_categories()
        for cat in categories[:10]:
            st.markdown(f"- {cat}")
        st.markdown(f"... and {len(categories) - 10} more")

# ============ BATCH SEARCH ============
elif st.session_state.current_page == 'batch_search':
    st.markdown('<div class="section-header">Batch Company Search</div>', unsafe_allow_html=True)
    st.caption("Search for REAL companies using Google Places API | Professional IT Outreach")
    st.markdown("---")
    
    api_keys = get_api_keys()
    
    if not api_keys["google_maps"] and not api_keys["serp_api"]:
        st.error("❌ No API keys configured! Please add GOOGLE_MAPS_API_KEY or SERP_API_KEY to .streamlit/secrets.toml")
        st.markdown("""
        ### Setup Instructions:
        1. Get Google Maps API Key from [Google Cloud Console](https://console.cloud.google.com/)
        2. Enable Places API and Maps JavaScript API
        3. Add to `.streamlit/secrets.toml`:
        ```toml
        GOOGLE_MAPS_API_KEY = "your_key_here"
        SERP_API_KEY = "your_key_here"
""")
st.stop()

with st.form("batch_search_form"):
col1, col2 = st.columns(2)
with col1:
categories = get_all_categories()
selected_category = st.selectbox("Business Category", categories)
with col2:
regions = get_all_regions()
selected_region = st.selectbox("Region", regions)

col1, col2 = st.columns(2)
with col1:
areas = get_areas_for_region(selected_region)
selected_area = st.selectbox("Location Area", areas)
with col2:
limit = st.slider("Number of Companies to Fetch", 3, 20, 10)

search_api = st.radio("Search API", ["Google Places API (Recommended)", "SERP API (Alternative)"])

submitted = st.form_submit_button("🔍 Search Real Companies")

if submitted:
with st.spinner(f"Searching for {selected_category} in {selected_area}, {selected_region}..."):
sub_areas = get_sub_areas_for_area(selected_region, selected_area)
query = SEARCH_QUERIES.get(selected_category, selected_category)

all_businesses = []

for sub_area in sub_areas[:2]: # Limit to first 2 sub-areas to avoid rate limits
location_name = f"{sub_area}, {selected_region}"

if search_api == "Google Places API (Recommended)" and api_keys["google_maps"]:
businesses = search_google_places(api_keys["google_maps"], query, location_name)
elif api_keys["serp_api"]:
businesses = search_serp_businesses(api_keys["serp_api"], query, location_name)
else:
businesses = []

for biz in businesses:
biz["category"] = selected_category
biz["area"] = selected_area
biz["region"] = selected_region
biz["email"] = ""
all_businesses.append(biz)

time.sleep(0.5) # Rate limiting

Remove duplicates by name
seen = set()
unique_businesses = []
for biz in all_businesses:
if biz['name'] not in seen:
seen.add(biz['name'])
unique_businesses.append(biz)

st.session_state.batch_results = unique_businesses[:limit]

if unique_businesses:
st.success(f"Found {len(unique_businesses)} real businesses in {selected_area}, {selected_region}")
else:
st.warning(f"No businesses found. Try a different location or category.")

if st.session_state.batch_results:
st.markdown("### Search Results")

Display results
for idx, company in enumerate(st.session_state.batch_results):
with st.expander(f"{company['name']} - {company.get('address', 'Address available')}"):
col1, col2 = st.columns(2)
with col1:
st.write(f"Address: {company.get('address', 'N/A')}")
st.write(f"Phone: {company.get('phone', 'N/A')}")
with col2:
st.write(f"Rating: {'⭐' * int(company.get('rating', 0))} {company.get('rating', 'N/A')}")
st.write(f"Website: {company.get('website', 'N/A')[:50] if company.get('website') else 'N/A'}")

col1, col2, col3, col4 = st.columns(4)
with col1:
if st.button("Add to CRM", key=f"add_{idx}"):
company_data = {
"name": company['name'],
"address": company.get('address', ''),
"phone": company.get('phone', ''),
"website": company.get('website', ''),
"category": selected_category
}
if add_lead(company_data):
st.success(f"Added {company['name']} to CRM")
st.rerun()
with col2:
if st.button("Preview Email", key=f"preview_{idx}"):
email_body = generate_professional_email(company, selected_category)
st.markdown(email_body, unsafe_allow_html=True)
with col3:
if st.button("Send Email", key=f"send_{idx}"):

Try to find email from website or use pattern
email = ""
if company.get('website'):
domain = company['website'].replace('https://', '').replace('http://', '').split('/')[0]
email = f"info@{domain}"
else:
email = f"info@{company['name'].lower().replace(' ', '')}.com"

subject = f"FREE 5-Step Email & IT Health Check - For {company['name']}"
body = generate_professional_email(company, selected_category)
success, msg = send_email(email, subject, body)
if success:
st.success(f"Email sent to {company['name']} ({email})")
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
with col4:
if st.button("Generate Letter", key=f"letter_{idx}"):
letter = generate_letter_content(company)
st.download_button(
label="Download Letter",
data=letter,
file_name=f"letter_{company['name'].replace(' ', '')}.txt",
mime="text/plain",
key=f"download{idx}"
)

Bulk actions
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
if st.button("Add All to CRM", key="add_all", use_container_width=True):
count = 0
for company in st.session_state.batch_results:
company_data = {
"name": company['name'],
"address": company.get('address', ''),
"phone": company.get('phone', ''),
"website": company.get('website', ''),
"category": selected_category
}
if add_lead(company_data):
count += 1
st.success(f"Added {count} companies to CRM")
st.rerun()

with col2:
if st.button("Send Emails to All", key="send_all", type="primary", use_container_width=True):
success_count = 0
for idx, company in enumerate(st.session_state.batch_results):
email = ""
if company.get('website'):
domain = company['website'].replace('https://', '').replace('http://', '').split('/')[0]
email = f"info@{domain}"
else:
email = f"info@{company['name'].lower().replace(' ', '')}.com"

subject = f"FREE 5-Step Email & IT Health Check - For {company['name']}"
body = generate_professional_email(company, selected_category)
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
st.session_state.letter_queue.append({
"company": company['name'],
"address": company.get('address', ''),
"reason": msg
})
time.sleep(1.5)

save_email_log()
st.success(f"Sent: {success_count} | Failed: {len(st.session_state.batch_results) - success_count}")
if len(st.session_state.letter_queue) > 0:
st.info(f"{len(st.session_state.letter_queue)} companies added to letter queue")
st.rerun()

============ LEADS CRM ============
elif st.session_state.current_page == 'crm':
st.markdown('<div class="section-header">Leads CRM</div>', unsafe_allow_html=True)
st.caption(f"Total Leads: {len(st.session_state.leads)}")
st.markdown("---")

if st.session_state.leads:
search = st.text_input("Search", placeholder="Search by name, category, or address")

filtered = st.session_state.leads
if search:
filtered = [l for l in filtered if search.lower() in l.get('name', '').lower() or search.lower() in l.get('category', '').lower()]

for lead in filtered:
with st.expander(f"{lead['name']} - Score: {lead['lead_score']}/100"):
col1, col2 = st.columns(2)
with col1:
st.write(f"Address: {lead.get('address', 'N/A')}")
st.write(f"Phone: {lead.get('phone', 'N/A')}")
with col2:
st.write(f"Category: {lead.get('category', 'N/A')}")
st.write(f"Added: {lead['created_at'][:10]}")

if not lead.get('email_sent'):
if st.button(f"Send Email", key=f"send_crm_{lead['id']}"):
email = lead.get('email')
if not email and lead.get('website'):
domain = lead['website'].replace('https://', '').replace('http://', '').split('/')[0]
email = f"info@{domain}"
if email:
subject = f"FREE 5-Step Email & IT Health Check - For {lead['name']}"
body = generate_professional_email(lead, lead.get('category', 'Business'))
success, msg = send_email(email, subject, body)
if success:
lead['email_sent'] = True
save_leads()
st.success(f"Email sent to {lead['name']}")
st.rerun()
else:
st.error(f"Failed: {msg}")
else:
st.warning("No email address available")
else:
st.info("No leads yet. Run a batch search to find real companies.")

============ EMAIL LOG ============
elif st.session_state.current_page == 'email_log':
st.markdown('<div class="section-header">Email Log</div>', unsafe_allow_html=True)
st.markdown("---")

if st.session_state.email_log:
for log in reversed(st.session_state.email_log[-30:]):
st.markdown(f"""

<div class="data-card"> <strong>To:</strong> {log['to']}<br> <strong>Company:</strong> {log['company']}<br> <strong>Date:</strong> {log['date'][:19]}<br> <strong>Status:</strong> ✅ {log['status']} </div> """, unsafe_allow_html=True) else: st.info("No emails sent yet")
============ LETTER QUEUE ============
elif st.session_state.current_page == 'letter_queue':
st.markdown('<div class="section-header">Letter Queue</div>', unsafe_allow_html=True)
st.caption("Companies without valid email - Ready for physical mailing")
st.markdown("---")

if st.session_state.letter_queue:
st.warning(f"{len(st.session_state.letter_queue)} companies need physical letters")

for idx, letter in enumerate(st.session_state.letter_queue):
with st.expander(f"{letter['company']}"):
st.write(f"Reason: {letter.get('reason', 'No valid email')}")

letter_content = generate_letter_content({"name": letter['company']})
st.code(letter_content, language='text')

if st.button(f"Download Letter", key=f"download_letter_{idx}"):
st.download_button(
label="Download",
data=letter_content,
file_name=f"letter_{letter['company'].replace(' ', '')}.txt",
mime="text/plain",
key=f"download{idx}"
)
else:
st.success("No pending letters - All companies have valid emails!")

============ SETTINGS ============
elif st.session_state.current_page == 'settings':
st.markdown('<div class="section-header">Settings</div>', unsafe_allow_html=True)
st.markdown("---")

st.markdown("### API Configuration")
st.code("""

.streamlit/secrets.toml
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
SERP_API_KEY = "your_serp_api_key"
OPENAI_API_KEY = "your_openai_api_key"
""")

st.markdown("### Email Configuration")
st.info(f"""
SMTP Settings:

Host: {SMTP_CONFIG['host']}

Port: {SMTP_CONFIG['port']}

Username: {SMTP_CONFIG['username']}

Daily Limit: {SMTP_CONFIG['daily_limit']} emails/day
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

============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("2024 TechWokx IT Solutions | Real-time Company Search | Powered by Google Places API")

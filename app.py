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
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

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

# ============ API KEYS (from secrets) ============
def get_api_keys():
    try:
        return {
            "google_maps": st.secrets.get("GOOGLE_MAPS_API_KEY", ""),
            "serp_api": st.secrets.get("SERP_API_KEY", ""),
        }
    except:
        return {"google_maps": "", "serp_api": ""}

# ============ ALL 16 REGIONS OF GHANA WITH TOWNS ============
ALL_LOCATIONS = {
    "Greater Accra Region": {
        "Accra Metropolitan": ["Airport Residential", "Cantonments", "Labone", "Osu", "Ring Road Central", "Ridge", "North Ridge", "Adabraka", "Kaneshie", "Achimota", "Legon", "Madina", "Adenta", "East Legon", "West Legon", "Dzorwulu", "Labadi", "Teshie", "Nungua", "Spintex", "Sakumono", "Ashaiman", "Tema"],
        "Ga East": ["Abokobi", "Danfa", "Teiman", "Taifa", "Kwabenya", "Dome", "Pokuase", "Haasto"],
        "Ga West": ["Amasaman", "Nsawam", "Medie", "Sarpeiman"],
        "Ga South": ["Weija", "Gbawe", "Mallam", "Kwashieman", "Darkuman", "Kasoa", "Budumburam", "Opeikuma"],
        "Tema Metropolitan": ["Tema Community 1", "Tema Community 2", "Tema Community 3", "Tema Community 4", "Tema Community 5", "Tema Community 6", "Tema Community 7", "Tema Community 8", "Tema Community 9", "Tema Community 10", "Tema Industrial Area", "Kpone", "Sakumono", "Lashibi", "Adjei Kojo", "Afienya", "Dawhenya", "Prampram"]
    },
    "Ashanti Region": {
        "Kumasi Metropolitan": ["Adum", "Bantama", "Asafo", "Asokwa", "Tafo", "Suame", "Oforikrom", "Ayigya", "Bohyen", "Kaase", "Danyame", "Amakom", "Buokrom", "Kwadaso", "Nhyiaeso", "Abuakwa", "Mampong", "Atonsu", "Ahinsan", "Boadi", "Kentinkrono", "Ayeduase", "Kotei", "Santasi"],
        "Obuasi": ["Obuasi Central", "Bekwai", "Anyinam", "Akrokerri"],
        "Mampong": ["Mampong Central", "Asante Mampong", "Dadease", "Kofiase", "Nsuta"]
    },
    "Western Region": {
        "Takoradi": ["Takoradi Central", "Beach Road", "Kojokrom", "Effiakuma", "Anaji", "Nkontompo", "Kwesimintsim", "Apremdo", "Fijai", "Sekondi", "Nkroful"],
        "Sekondi": ["Sekondi Central", "Essikado", "Ketan", "Adiembra"],
        "Tarkwa": ["Tarkwa Central", "Nsuta", "Tamso", "Teberebie", "Prestea", "Bogoso", "Wassa"]
    },
    "Central Region": {
        "Cape Coast": ["Cape Coast Central", "Pedu", "Adisadel", "Amamoma", "Kakumdo", "Abura", "Bakaano", "Siwdu", "Ekon", "Besease"],
        "Kasoa": ["Kasoa Central", "Opeikuma", "Akweley", "Budumburam", "Millennium City", "Amanfrom", "Awutu"],
        "Winneba": ["Winneba Central", "Simpa", "Low Cost", "Effutu", "Ansaful", "Gomoa"],
        "Elmina": ["Elmina Central", "Bantoma", "Besease", "Domi"]
    },
    "Eastern Region": {
        "Koforidua": ["Koforidua Central", "Adweso", "Effiduase", "Oyoko", "New Juaben", "Old Tafo", "Suapong"],
        "Nsawam": ["Nsawam Central", "Nsawam Zongo", "Adoagyiri", "Asuboi"],
        "Akwatia": ["Akwatia Central", "Asamankese", "Akim Oda", "Akim Swedru", "Anyinam"]
    },
    "Volta Region": {
        "Ho": ["Ho Central", "Hliha", "Ahoe", "Bankoe", "Deme", "Dome", "Klefe", "Kpodzi", "Matse", "Nyive", "Shia", "Sokode", "Tanyigbe", "Kpeve", "Kpando"],
        "Hohoe": ["Hohoe Central", "Agate", "Akpafu", "Alavanyo", "Avatime", "Gbi", "Likpe", "Lolobi"],
        "Keta": ["Keta Central", "Abor", "Anloga", "Denu", "Dzodze", "Kedzi", "Sogakope", "Weta"]
    },
    "Northern Region": {
        "Tamale": ["Tamale Central", "Jisonayili", "Dungu", "Lamashegu", "Tishigu", "Vitting", "Gumani", "Nyohini", "Sagnarigu", "Zogbeli"],
        "Yendi": ["Yendi Central", "Bimbilla", "Gushegu", "Karaga", "Mion", "Saboba", "Savelugu", "Tolon"]
    },
    "Upper East Region": {
        "Bolgatanga": ["Bolgatanga Central", "Zuarungu", "Bongo", "Navrongo", "Paga", "Sandema", "Tongo"],
        "Bawku": ["Bawku Central", "Binduri", "Garu", "Manga", "Pusiga", "Zebilla"]
    },
    "Upper West Region": {
        "Wa": ["Wa Central", "Dafiama", "Gwolu", "Han", "Jirapa", "Kaleo", "Lambussie", "Lawra", "Nadowli", "Nandom", "Sissala", "Tumu", "Wechiau"]
    },
    "Western North Region": {
        "Sefwi-Wiawso": ["Wiawso", "Asawinso", "Bibiani", "Sefwi Bekwai", "Akontombra", "Juaboso", "Bodi", "Suaman"]
    },
    "Savannah Region": {
        "Damango": ["Damango", "Bole", "Salaga", "Daboya", "Yapei", "Kafaba", "Ngmayem", "Nkwanta", "Nyankpala", "Tolon", "Wasipe"]
    },
    "North East Region": {
        "Nalerigu": ["Nalerigu", "Gambaga", "Walewale", "Bunkpurugu", "Chereponi", "Garu", "Kpasenkpe", "Mamprugu", "Nakpanduri", "Pulima", "Wawli", "Yunyoo"]
    },
    "Oti Region": {
        "Dambai": ["Dambai", "Jasikan", "Kadjebi", "Kete Krachi", "Nkwanta", "Krachi East", "Krachi West", "Buem", "Akan", "Biakoye", "Worawora", "Bowiri", "Likpe", "Santrokofi"]
    },
    "Ahafo Region": {
        "Goaso": ["Goaso", "Bechem", "Duayaw Nkwanta", "Kenyasi", "Mim", "Abesim", "Acherensua", "Asutifi", "Fosu", "Hwidiem", "Kukuom", "Ntotroso", "Sankore", "Subin", "Yamfo"]
    },
    "Bono East Region": {
        "Techiman": ["Techiman", "Kintampo", "Nkoranza", "Atebubu", "Jema", "Kwame Danso", "Pru", "Sene", "Kintampo North", "Kintampo South", "Nkoranza North", "Nkoranza South", "Techiman North", "Techiman South"]
    },
    "Bono Region": {
        "Sunyani": ["Sunyani Central", "Sunyani West", "Sunyani East", "Dormaa Ahenkro", "Dormaa Central", "Berekum", "Berekum West", "Tain", "Badu", "Seikwa", "Nsoatre", "Chiraa", "Odumase", "Wamfie", "Kwame Danso", "Manso", "Abesim", "Fiapre", "Yamfo"]
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

# ============ REAL GOOGLE PLACES API ============
def search_google_places(api_key, query, location):
    """Search for real businesses using Google Places API"""
    if not api_key:
        return []
    
    try:
        # First, geocode the location to get coordinates
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
            "radius": 5000,
            "keyword": query,
            "type": "establishment"
        }
        
        response = requests.get(places_url, params=places_params, timeout=10)
        data = response.json()
        
        businesses = []
        for place in data.get('results', [])[:20]:
            # Get detailed place information
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                "key": api_key,
                "place_id": place['place_id'],
                "fields": "name,formatted_address,formatted_phone_number,website,rating"
            }
            details_response = requests.get(details_url, params=details_params, timeout=10)
            details = details_response.json().get('result', {})
            
            # Extract website domain for email
            website = details.get('website', '')
            email = ""
            if website:
                ext = tldextract.extract(website)
                domain = f"{ext.domain}.{ext.suffix}"
                email = f"info@{domain}"
            
            businesses.append({
                "name": place.get('name'),
                "address": details.get('formatted_address', place.get('vicinity', '')),
                "phone": details.get('formatted_phone_number', ''),
                "website": website,
                "email": email,
                "rating": details.get('rating', 0),
                "place_id": place.get('place_id')
            })
        
        return businesses
    except Exception as e:
        st.warning(f"Google Places API error: {e}")
        return []

# ============ PROFESSIONAL PROPOSAL TEMPLATE ============
def get_proposal_html(company_name):
    """Return the professional proposal as HTML"""
    audit_url = "https://techwokx.online/#audit"
    qr_base64 = generate_qr_code_base64(audit_url)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>TechWokx IT Assessment</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1e293b; margin: 0; padding: 0; background: #f0f4f8; }}
            .container {{ max-width: 700px; margin: 20px auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 25px -12px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 30px; }}
            .section {{ margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #e2e8f0; }}
            .section-title {{ font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 15px; padding-left: 12px; border-left: 3px solid #667eea; }}
            .observation-box {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; border-radius: 8px; }}
            .service-list {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }}
            .service-tag {{ background: #e0e7ff; color: #4338ca; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }}
            .offer-box {{ background: linear-gradient(135deg, #dbeafe, #ede9fe); border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0; }}
            .qr-code {{ text-align: center; margin: 20px 0; }}
            .qr-code img {{ width: 150px; height: 150px; border: 2px solid #e2e8f0; border-radius: 12px; padding: 10px; background: white; }}
            .button {{ background: #22c55e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: 600; }}
            .footer {{ background: #1e293b; color: #94a3b8; padding: 20px; text-align: center; font-size: 12px; }}
            .signature {{ margin-top: 25px; padding-top: 20px; border-top: 1px solid #e2e8f0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 TechWokx IT Solutions</h1>
                <p>FREE 5-Step Email & IT Health Check</p>
            </div>
            <div class="content">
                <p>Dear Sir/Madam,</p>
                <p>I hope this letter finds you well.</p>
                <p>My name is <strong>George Jabley</strong>, and I represent <strong>TechWokx IT Solutions</strong>. We help businesses improve their technology operations through reliable email systems, IT support, backup solutions, infrastructure reviews, and business continuity planning.</p>
                <p>As part of our business outreach program, we conducted a high-level review of your organization's publicly available digital presence, including your website, domain configuration, SSL certificate status, and email setup.</p>
                
                <div class="section">
                    <div class="section-title">📋 What We Observed</div>
                    <div class="observation-box">
                        <ul>
                            <li>We were unable to verify whether all recommended email authentication records are fully configured.</li>
                            <li>Your company logo does not currently appear alongside emails in supported inboxes.</li>
                            <li>There may be opportunities to improve email deliverability and trust indicators.</li>
                            <li>We could not verify the existence of backup and recovery measures protecting business-critical communications and data.</li>
                            <li>Potential printer and network issues that could be causing daily operational friction.</li>
                        </ul>
                    </div>
                    <p><em>Please note that this review was conducted using publicly available information and from outside your network environment. As such, some findings may already have been addressed internally, and a more detailed assessment would be required to confirm their status.</em></p>
                </div>
                
                <div class="section">
                    <div class="section-title">⚠️ Why This Matters</div>
                    <p>Modern businesses rely heavily on email, cloud services, and digital communication. When these systems are not properly configured or maintained, organizations may experience:</p>
                    <ul>
                        <li>Emails being delivered to spam or junk folders</li>
                        <li>Reduced trust in business communications</li>
                        <li>Difficulty identifying fraudulent communications</li>
                        <li>Loss of important business data</li>
                        <li>Increased downtime during technical issues</li>
                        <li>Challenges recovering from accidental deletions or system failures</li>
                        <li>Printer and network disruptions affecting productivity</li>
                    </ul>
                </div>
                
                <div class="section">
                    <div class="section-title">🛠️ How TechWokx Can Help</div>
                    <p>We provide practical technology solutions designed to improve reliability, productivity, and business continuity.</p>
                    <div class="service-list">
                        <span class="service-tag">✓ Business Email Health Checks</span>
                        <span class="service-tag">✓ Email Deliverability Improvements</span>
                        <span class="service-tag">✓ Professional Email Branding & Signatures</span>
                        <span class="service-tag">✓ IT Infrastructure Reviews</span>
                        <span class="service-tag">✓ Managed IT Support Services</span>
                        <span class="service-tag">✓ Printer & Network Troubleshooting</span>
                        <span class="service-tag">✓ Backup & Recovery Solutions</span>
                        <span class="service-tag">✓ Cloud Productivity Solutions</span>
                        <span class="service-tag">✓ Process Automation</span>
                    </div>
                </div>
                
                <div class="offer-box">
                    <div class="section-title" style="border-left-color: #22c55e;">🎁 TWO COMPLIMENTARY OFFERS</div>
                    <p><strong>1. Find Out Yourself: 5-Step Email & IT Health Check</strong></p>
                    <div class="qr-code">
                        <img src="data:image/png;base64,{qr_base64}" alt="QR Code">
                    </div>
                    <p><strong>Or visit:</strong> <a href="{audit_url}" target="_blank">techwokx.online/#audit</a></p>
                    <p>The assessment takes less than five minutes and provides:</p>
                    <ul style="text-align: left;">
                        <li>A personalized technology health score</li>
                        <li>Email configuration insights</li>
                        <li>Security recommendations</li>
                    </ul>
                    <p><strong>2. Free 15-Minute IT Consultation</strong></p>
                    <p>Discuss your specific challenges and get expert advice at no cost.</p>
                </div>
                
                <div class="signature">
                    <p>Thank you for your time and consideration. We would be delighted to help <strong>{company_name}</strong> achieve smoother, more secure, and more reliable IT operations.</p>
                    <p>Warm regards,</p>
                    <p><strong>George Jabley</strong><br>
                    Founder & IT Operations Lead<br>
                    TechWokx Ghana<br>
                    📞 +233 555 087 407<br>
                    📧 hello@techwokx.online<br>
                    🌐 techwokx.online</p>
                </div>
            </div>
            <div class="footer">
                <p>© 2024 TechWokx IT Solutions | Intelligent Solutions. Secure Futures.</p>
                <p>P.O. Box ML469, Malam, Accra, Ghana</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_letter_content(company_name):
    """Generate printable letter content"""
    audit_url = "https://techwokx.online/#audit"
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return f"""
================================================================================
                          TECHWOKX IT SOLUTIONS
                    FREE 5-Step Email & IT Health Check
================================================================================

Date: {current_date}

To: Management Team
{company_name}
Ghana

Dear Sir/Madam,

I hope this letter finds you well.

My name is George Jabley, and I represent TechWokx IT Solutions. We help businesses 
improve their technology operations through reliable email systems, IT support, 
backup solutions, infrastructure reviews, and business continuity planning.

As part of our business outreach program, we conducted a high-level review of your 
organization's publicly available digital presence.

================================================================================
                          WHAT WE OBSERVED
================================================================================

• We were unable to verify whether all recommended email authentication records 
  (SPF/DKIM/DMARC) are fully configured.

• Your company logo does not currently appear alongside emails in supported inboxes.

• There may be opportunities to improve email deliverability and trust indicators.

• We could not verify the existence of backup and recovery measures protecting 
  business-critical communications and data.

• Potential printer and network issues that could be causing daily operational friction.

Note: This review was conducted using publicly available information from outside 
your network environment. Some findings may already have been addressed internally.

================================================================================
                          WHY THIS MATTERS
================================================================================

Modern businesses rely heavily on email, cloud services, and digital communication. 
When systems are not properly configured, organizations may experience:
• Emails delivered to spam or junk folders
• Reduced trust in business communications
• Difficulty identifying fraudulent communications
• Loss of important business data
• Increased downtime during technical issues
• Printer and network disruptions affecting productivity

================================================================================
                         HOW TECHWOKX CAN HELP
================================================================================

Our services include:
✓ Business Email Health Checks
✓ Email Deliverability Improvements
✓ Professional Email Branding & Signatures
✓ IT Infrastructure Reviews
✓ Managed IT Support Services
✓ Printer & Network Troubleshooting
✓ Backup & Recovery Solutions
✓ Cloud Productivity Solutions
✓ Process Automation

================================================================================
                    TWO (2) COMPLIMENTARY OFFERS
================================================================================

1. 5-Step Email & IT Health Check
   Visit: {audit_url}
   
2. Free 15-Minute IT Consultation
   Call: +233 555 087 407

================================================================================

Thank you for your time and consideration.

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
        "region": lead_data.get("region", ""),
        "district": lead_data.get("district", ""),
        "town": lead_data.get("town", ""),
        "rating": lead_data.get("rating", 0),
        "lead_score": 75,
        "created_at": datetime.now().isoformat(),
        "email_sent": False
    }
    st.session_state.leads.append(new_lead)
    save_leads()
    return True

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
.nav-buttons { display: flex; gap: 10px; margin-bottom: 20px; }
.company-card { background: white; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #e2e8f0; cursor: pointer; transition: all 0.2s; }
.company-card:hover { border-color: #667eea; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
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
        ("📧 Email Log", "email_log"),
        ("📋 Letter Queue", "letter_queue"),
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
    maps_status = "✅" if api_keys["google_maps"] else "❌"
    st.markdown(f"Google Maps: {maps_status}")
    st.markdown(f"Leads: {len(st.session_state.leads)}")
    st.markdown(f"Emails Today: {SMTP_CONFIG['sent_today']}/{SMTP_CONFIG['daily_limit']}")

# ============ DASHBOARD ============
if st.session_state.current_page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>TechWokx Lead Intelligence</h2>
        <p>Professional IT Outreach | Google Places API | All 16 Regions of Ghana</p>
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
        regions_count = len(ALL_LOCATIONS)
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{regions_count}</div><div class='metric-label'>Regions Covered</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📍 Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍 Search Companies", use_container_width=True):
            st.session_state.current_page = 'search'
            st.rerun()
        if st.button("👥 View CRM", use_container_width=True):
            st.session_state.current_page = 'crm'
            st.rerun()
    
    with col2:
        st.markdown('<div class="section-header">📊 Recent Activity</div>', unsafe_allow_html=True)
        for lead in st.session_state.leads[-3:]:
            st.markdown(f"<div class='data-card'><strong>{lead['name']}</strong><br>Added: {lead['created_at'][:10]}</div>", unsafe_allow_html=True)

# ============ SEARCH COMPANIES ============
elif st.session_state.current_page == 'search':
    st.markdown('<div class="section-header">🔍 Search Companies</div>', unsafe_allow_html=True)
    st.caption("Find real businesses across all 16 regions of Ghana using Google Places API")
    st.markdown("---")
    
    api_keys = get_api_keys()
    
    if not api_keys["google_maps"]:
        st.error("❌ Google Maps API key not configured!")
        st.info("Add GOOGLE_MAPS_API_KEY to .streamlit/secrets.toml")
        st.markdown("""
        ```toml
        GOOGLE_MAPS_API_KEY = "your_key_here"
""")
st.stop()

col1, col2 = st.columns(2)
with col1:
regions = list(ALL_LOCATIONS.keys())
selected_region = st.selectbox("Select Region", regions)

with col2:
if selected_region:
districts = list(ALL_LOCATIONS[selected_region].keys())
selected_district = st.selectbox("Select District/Metropolis", districts)

col1, col2 = st.columns(2)
with col1:
if selected_region and selected_district:
towns = ALL_LOCATIONS[selected_region][selected_district]
selected_town = st.selectbox("Select Town/City", towns)

with col2:
categories = list(SEARCH_QUERIES.keys())
selected_category = st.selectbox("Business Category", categories)

limit = st.slider("Number of Companies", 5, 30, 15)

if st.button("🔍 Search", type="primary"):
if selected_town:
with st.spinner(f"Searching for {selected_category} in {selected_town}..."):
query = SEARCH_QUERIES.get(selected_category, selected_category)
businesses = search_google_places(api_keys["google_maps"], query, selected_town)

for biz in businesses:
biz["category"] = selected_category
biz["town"] = selected_town
biz["district"] = selected_district
biz["region"] = selected_region

st.session_state.batch_results = businesses[:limit]
st.success(f"Found {len(businesses)} businesses in {selected_town}")

Save to search history
st.session_state.search_history.append({
"region": selected_region,
"district": selected_district,
"town": selected_town,
"category": selected_category,
"count": len(businesses),
"date": datetime.now().isoformat()
})

if st.session_state.batch_results:
st.markdown("### Search Results")

for idx, company in enumerate(st.session_state.batch_results):
with st.expander(f"🏢 {company['name']}"):
col1, col2 = st.columns(2)
with col1:
st.markdown(f"📍 Address: {company.get('address', 'N/A')}")
st.markdown(f"📞 Phone: {company.get('phone', 'N/A')}")
st.markdown(f"🌐 Website: {company.get('website', 'N/A')}")
with col2:
st.markdown(f"📧 Email: {company.get('email', 'N/A')}")
st.markdown(f"⭐ Rating: {'⭐' * int(company.get('rating', 0))} {company.get('rating', 'N/A')}")
st.markdown(f"📂 Category: {selected_category}")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
if st.button("📝 View Proposal", key=f"view_{idx}"):
st.session_state.selected_company = company
st.session_state.current_page = 'proposal_preview'
st.rerun()

with col2:
if st.button("➕ Add to CRM", key=f"add_{idx}"):
if add_lead(company):
st.success(f"Added {company['name']} to CRM")
st.rerun()
else:
st.warning("Company already exists in CRM")

with col3:
email = company.get('email', '')
if not email and company.get('website'):
ext = tldextract.extract(company['website'])
email = f"info@{ext.domain}.{ext.suffix}"
new_email = st.text_input("Email", value=email, key=f"email_input_{idx}")
if st.button("📧 Send Email", key=f"send_{idx}"):
if new_email:
proposal_html = get_proposal_html(company['name'])
subject = f"FREE 5-Step Email & IT Health Check - For {company['name']}"
success, msg = send_email(new_email, subject, proposal_html)
if success:
st.success(f"Email sent to {company['name']}")
st.session_state.email_log.append({
"to": new_email,
"company": company['name'],
"subject": subject,
"date": datetime.now().isoformat(),
"status": "Sent"
})
save_email_log()
st.rerun()
else:
st.error(f"Failed: {msg}")
else:
st.warning("Please enter an email address")

with col4:
if st.button("📄 Download Letter", key=f"letter_{idx}"):
letter = get_letter_content(company['name'])
st.download_button(
label="Download",
data=letter,
file_name=f"letter_{company['name'].replace(' ', '')}.txt",
mime="text/plain",
key=f"download{idx}"
)

============ PROPOSAL PREVIEW ============
elif st.session_state.current_page == 'proposal_preview' and st.session_state.selected_company:
company = st.session_state.selected_company

st.markdown(f'<div class="section-header">📄 Proposal for {company["name"]}</div>', unsafe_allow_html=True)

Navigation buttons
st.markdown("""

<div style="display: flex; gap: 10px; margin-bottom: 20px;"> <button onclick="history.back()" style="background: #667eea; color: white; padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer;">← Back to Search</button> <button onclick="window.location.href='?page=dashboard'" style="background: #64748b; color: white; padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer;">🏠 Home</button> </div> """, unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])
with col1:
proposal_html = get_proposal_html(company['name'])
st.markdown(proposal_html, unsafe_allow_html=True)

with col2:
st.markdown("### Company Details")
st.markdown(f"Name: {company['name']}")
st.markdown(f"Address: {company.get('address', 'N/A')}")
st.markdown(f"Phone: {company.get('phone', 'N/A')}")
st.markdown(f"Website: {company.get('website', 'N/A')}")
st.markdown(f"Email: {company.get('email', 'N/A')}")
st.markdown(f"Category: {company.get('category', 'N/A')}")
st.markdown(f"Rating: {'⭐' * int(company.get('rating', 0))} {company.get('rating', 'N/A')}")

st.markdown("---")
st.markdown("### Actions")

if st.button("➕ Add to CRM", use_container_width=True):
if add_lead(company):
st.success(f"Added {company['name']} to CRM")
else:
st.warning("Company already exists in CRM")

email = company.get('email', '')
if not email and company.get('website'):
ext = tldextract.extract(company['website'])
email = f"info@{ext.domain}.{ext.suffix}"

email_input = st.text_input("Email Address", value=email)
if st.button("📧 Send Email", use_container_width=True):
if email_input:
proposal_html = get_proposal_html(company['name'])
subject = f"FREE 5-Step Email & IT Health Check - For {company['name']}"
success, msg = send_email(email_input, subject, proposal_html)
if success:
st.success(f"Email sent to {company['name']}")
st.session_state.email_log.append({
"to": email_input,
"company": company['name'],
"subject": subject,
"date": datetime.now().isoformat(),
"status": "Sent"
})
save_email_log()
else:
st.error(f"Failed: {msg}")
else:
st.warning("Please enter an email address")

if st.button("📄 Download Letter", use_container_width=True):
letter = get_letter_content(company['name'])
st.download_button(
label="Download Letter",
data=letter,
file_name=f"letter_{company['name'].replace(' ', '_')}.txt",
mime="text/plain"
)

if st.button("← Back to Search Results", use_container_width=True):
st.session_state.current_page = 'search'
st.rerun()

============ LEADS CRM ============
elif st.session_state.current_page == 'crm':
st.markdown('<div class="section-header">👥 Leads CRM</div>', unsafe_allow_html=True)
st.caption(f"Total Leads: {len(st.session_state.leads)}")
st.markdown("---")

if st.session_state.leads:
search = st.text_input("🔍 Search", placeholder="Search by name, address, or category")

filtered = st.session_state.leads
if search:
filtered = [l for l in filtered if search.lower() in l.get('name', '').lower() or search.lower() in l.get('address', '').lower() or search.lower() in l.get('category', '').lower()]

for lead in filtered:
with st.expander(f"🏢 {lead['name']} - Score: {lead['lead_score']}/100"):
col1, col2 = st.columns(2)
with col1:
st.markdown(f"📍 Address: {lead.get('address', 'N/A')}")
st.markdown(f"📞 Phone: {lead.get('phone', 'N/A')}")
st.markdown(f"🌐 Website: {lead.get('website', 'N/A')}")
with col2:
st.markdown(f"📧 Email: {lead.get('email', 'N/A')}")
st.markdown(f"📂 Category: {lead.get('category', 'N/A')}")
st.markdown(f"📅 Added: {lead['created_at'][:10]}")

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
if st.button(f"📝 View Proposal", key=f"view_{lead['id']}"):
st.session_state.selected_company = lead
st.session_state.current_page = 'proposal_preview'
st.rerun()

with col2:
if not lead.get('email_sent'):
email = lead.get('email', '')
if not email and lead.get('website'):
ext = tldextract.extract(lead['website'])
email = f"info@{ext.domain}.{ext.suffix}"
new_email = st.text_input("Email", value=email, key=f"email_crm_{lead['id']}")
if st.button(f"📧 Send Email", key=f"send_{lead['id']}"):
if new_email:
proposal_html = get_proposal_html(lead['name'])
subject = f"FREE 5-Step Email & IT Health Check - For {lead['name']}"
success, msg = send_email(new_email, subject, proposal_html)
if success:
lead['email_sent'] = True
save_leads()
st.success(f"Email sent to {lead['name']}")
st.rerun()
else:
st.error(f"Failed: {msg}")
else:
st.warning("Please enter an email address")

with col3:
if st.button(f"🗑️ Delete", key=f"del_{lead['id']}"):
st.session_state.leads = [l for l in st.session_state.leads if l['id'] != lead['id']]
save_leads()
st.success(f"Deleted {lead['name']}")
st.rerun()
else:
st.info("No leads yet. Run a search to find companies.")

============ EMAIL LOG ============
elif st.session_state.current_page == 'email_log':
st.markdown('<div class="section-header">📧 Email Log</div>', unsafe_allow_html=True)
st.markdown("---")

if st.session_state.email_log:
for log in reversed(st.session_state.email_log[-50:]):
st.markdown(f"""

<div class="data-card"> <strong>To:</strong> {log['to']}<br> <strong>Company:</strong> {log['company']}<br> <strong>Date:</strong> {log['date'][:19]}<br> <strong>Status:</strong> ✅ {log['status']} </div> """, unsafe_allow_html=True) else: st.info("No emails sent yet")
============ LETTER QUEUE ============
elif st.session_state.current_page == 'letter_queue':
st.markdown('<div class="section-header">📋 Letter Queue</div>', unsafe_allow_html=True)
st.caption("Companies ready for physical mailing")
st.markdown("---")

if st.session_state.letter_queue:
for idx, letter in enumerate(st.session_state.letter_queue):
with st.expander(f"🏢 {letter.get('company', 'Unknown')}"):
letter_content = get_letter_content(letter.get('company', 'Business'))
st.code(letter_content, language='text')
if st.button(f"📄 Download Letter", key=f"download_{idx}"):
st.download_button(
label="Download",
data=letter_content,
file_name=f"letter_{letter.get('company', 'business').replace(' ', '')}.txt",
mime="text/plain",
key=f"btn{idx}"
)
else:
st.success("No pending letters")

============ SETTINGS ============
elif st.session_state.current_page == 'settings':
st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
st.markdown("---")

st.markdown("### API Configuration")
st.code("""

.streamlit/secrets.toml
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
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
st.caption("2024 TechWokx IT Solutions | Professional IT Outreach | Powered by Google Places API")

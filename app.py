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
if 'edit_proposal' not in st.session_state:
    st.session_state.edit_proposal = None

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
        "Accra Metropolitan": ["Airport Residential", "Airport City", "Cantonments", "Labone", "Osu", "Ring Road Central", "Ridge", "North Ridge", "Adabraka", "Asylum Down", "Tudu", "Jamestown", "Usshertown", "Korle Bu", "Mamprobi", "Chorkor", "Kaneshie", "Achimota", "Legon", "Madina", "Adenta", "Haasto", "East Legon", "West Legon", "Dzorwulu", "Shiashie", "Trasacco Valley", "Spintex", "Sakumono", "Teshie", "Nungua", "Lashibi", "Ashaiman", "Tema", "Dodowa"],
        "Tema Metropolitan": ["Tema Community 1", "Tema Community 2", "Tema Community 3", "Tema Community 4", "Tema Community 5", "Tema Community 6", "Tema Community 7", "Tema Community 8", "Tema Community 9", "Tema Community 10", "Tema Industrial Area", "Tema Fishing Harbour", "Tema New Town", "Tema Manhean", "Kpone", "Sakumono", "Lashibi", "Adjei Kojo", "Afienya", "Dawhenya", "Prampram", "Old Ningo"],
        "Ga West": ["Amasaman", "Nsawam", "Medie", "Sarpeiman", "Oblogo", "Weija", "Gbawe", "Mallam", "Kwashieman", "Darkuman", "Ablekuma", "New Mamprobi"],
        "Ga South": ["Ngleshie Amanfro", "Weija", "Bortianor", "Kokrobite", "Langma", "Obom", "Domeabra", "Kasoa", "Budumburam", "Millennium City", "Opeikuma"],
        "Ga East": ["Abokobi", "Danfa", "Teiman", "Ogbojo", "Taifa", "Kisseman", "Ashale Botwe", "Kwabenya", "Dome", "Pokuase", "Haasto"],
        "Ga North": ["Fise", "Ofankor", "Amanfrom", "Ayawaso", "Nkwantanang", "Mayera", "Agbogba", "Oyarifa", "Pantang"]
    },
    "Ashanti Region": {
        "Kumasi Metropolitan": ["Adum", "Bantama", "Asafo", "Asokwa", "Tafo", "Suame", "Oforikrom", "Ayigya", "Bohyen", "Kaase", "Anloga", "Danyame", "Amakom", "Buokrom", "Kwadaso", "Nhyiaeso", "Abuakwa", "Mampong", "Atonsu", "Ahinsan", "Boadi", "Kentinkrono", "Ayeduase", "Kotei", "Patase", "Apatrapa", "Oduom", "Santasi", "Krofrom", "Ridge", "North Suntreso", "South Suntreso", "Asokwa Mampong", "Abrepo", "Bekwai", "Osiem", "Adankwame", "Achiase", "Trede", "Effiduase", "Kenyasi", "Abirem", "Konongo", "Mamponteng"],
        "Obuasi": ["Obuasi Central", "Bekwai", "Anyinam", "Akrokerri", "Tarkwa-Bekwai", "Kokoteasua", "Kwabenakwa", "Binsere", "Brahabebome", "Dokyiwa", "Kwapia", "Kwasi Yeboah", "Mampongteng", "New Abirem", "Nyamebekyere", "Obuasi Number 1, 2, 3, 4, 5", "Papaase", "Tweneboa Kodua", "Wawasi", "Akaporiso", "Anhwiam", "Bekwai Roundabout", "Boete", "Brahabebome", "Dompim", "Heman", "Kokobeng", "Kwabrafoso"],
        "Mampong": ["Mampong Central", "Asante Mampong", "Dadease", "Kofiase", "Nsuta", "Asaam", "Atwima", "Edwumanso", "Feyiase", "Nkwanta", "Abrakaso", "Abuakwa", "Adagya", "Adwoafo", "Afrisipa", "Agyeman", "Ahenema", "Akokora", "Amakom", "Antoa", "Aputuogya", "Asamang", "Asiampong", "Atonsu", "Ayigya", "Bodomase", "Bokankye", "Bomfa", "Brebrem", "Broni", "Buoho", "Daban", "Denase", "Donyina", "Ejuraman", "Foase"]
    },
    "Western Region": {
        "Takoradi": ["Takoradi Central", "Beach Road", "Kojokrom", "Effiakuma", "Anaji", "Nkontompo", "Kwesimintsim", "Apremdo", "Fijai", "Sekondi", "Takoradi Market Circle", "Nkroful", "Mpintsin", "Poasi", "Adiembra", "Kweikuma", "New Takoradi", "Ngyeresia", "Essipong", "Butre", "Brempong"],
        "Sekondi": ["Sekondi Central", "Essikado", "Ketan", "Efiekuma", "Adiembra", "Assorko", "Apremdo", "Beach Road", "Brawie", "Fijai", "Hiatreko", "Kansaworado", "Kweikuma", "Mpoase", "New Town", "Nkroful", "Poasi", "Essipong", "Kokompe", "Market Circle"],
        "Tarkwa": ["Tarkwa Central", "Nsuta", "Tamso", "Teberebie", "Prestea", "Bogoso", "Wassa", "Aboso", "Huni Valley", "Damang", "Bondaye", "Bepo", "Abontiakoon", "Anyinase", "Apinto", "Akyempim", "Bawdie", "Bremang", "Domeabra", "Fante New Town", "Himan", "Huniani"]
    },
    "Central Region": {
        "Cape Coast": ["Cape Coast Central", "Pedu", "Adisadel", "Amamoma", "Kakumdo", "Abura", "Bakaano", "Ayensu", "Duakor", "Ekon", "Etsii Suntreso", "Kokoso", "Mpeasem", "Nkanfoa", "Ola", "Siwdu", "Tuffour", "Atwadzi", "Besease", "Boadi", "Brabedze", "Ebubonko", "Egyir", "Ekon II", "Iron City", "Kakodo", "Kwapro", "Nadzen"],
        "Kasoa": ["Kasoa Central", "Opeikuma", "Akweley", "Budumburam", "Millennium City", "Amanfrom", "Ataa Ayi", "Awutu", "Bawjiase", "Benyadze", "Bowa", "Dampa", "Fianko", "Gomoa", "Mangoase", "Papase", "Senya Beraku"],
        "Winneba": ["Winneba Central", "Simpa", "Low Cost", "Effutu", "Ansaful", "Ateitu", "Ayensudo", "Gomoa", "Kojo Beedu", "Mumford", "Nduakrom", "Nkwanta", "Okyereko", "Sampa", "Sankor", "Sankar", "Tema", "Tsokome"],
        "Elmina": ["Elmina Central", "Bantoma", "Besease", "Domi", "Ekon", "Etsii", "Kokodo", "Kokodo", "Mampong", "Mouri", "Ngyeresia", "Ntafu", "Papaase", "Sampofon", "St. James"]
    },
    "Eastern Region": {
        "Koforidua": ["Koforidua Central", "Adweso", "Effiduase", "Oyoko", "Bethelehem", "Asokore", "Koforidua Zongo", "New Juaben", "Old Tafo", "Suapong", "Akosombo", "Akwatia", "Asamankese", "Begoro", "Donkorkrom", "Kade", "Mpraeso", "Nkawkaw", "Nsawam", "Oda", "Somanya", "Suhum", "Aburi", "Akim Oda", "Akim Swedru", "Anyinam", "Apapam", "Asesewa", "Bunso", "Kyebi", "Mamfe"],
        "Nsawam": ["Nsawam Central", "Nsawam Zongo", "Adoagyiri", "Asuboi", "Dobro", "Gyankama", "Koforidua", "Kwamoso", "Mamfe", "Mangoase", "Mprumem", "Nkurakan", "Nsutam", "Obretema", "Pokuase", "Suapon", "Tinko", "Trobu"],
        "Akwatia": ["Akwatia Central", "Asamankese", "Akim Oda", "Akim Swedru", "Anyinam", "Apam", "Asafo", "Asakyiri", "Asankare", "Asanteman", "Asuboi", "Ateiku", "Atimpoku", "Ayensu", "Bebiano", "Besease", "Boadua", "Bonso", "Bunso", "Dwenteng"]
    },
    "Volta Region": {
        "Ho": ["Ho Central", "Hliha", "Ahoe", "Galenui", "Adaklu", "Akoefe", "Ayebe", "Bankoe", "Bume", "Deme", "Dome", "Dzogbefia", "Dzolo", "Gbi", "Hohoe", "Klefe", "Kpodzi", "Matse", "Nyive", "Shia", "Sokode", "Takla", "Tanyigbe", "Taviefe", "Kpeve", "Kpando", "Afadjato", "Amedzofe", "Anfoega", "Bator", "Fume", "Kadjebi", "Keta", "Kpando", "Kpeve", "Likpe", "Logba", "Mafi", "Nkonya", "Nkwanta", "Nogokpo", "Sogakope", "Tafi", "Tapa"],
        "Hohoe": ["Hohoe Central", "Agate", "Akpafu", "Alavanyo", "Avatime", "Bowiri", "Gbi", "Kadjebi", "Kpassa", "Likpe", "Lolobi", "Logba", "Nyagbo", "Santrokofi", "Siame", "Tafi", "Tapa", "Wli", "Yeji"],
        "Keta": ["Keta Central", "Abor", "Abutia", "Agbozume", "Agorve", "Anloga", "Avenor", "Aveyime", "Battor", "Dabala", "Denu", "Dzodze", "Fievie", "Gakli", "Jasikan", "Kedzi", "Klikor", "Kpoglu", "Kumasi", "Mafi", "Mataheko", "Mepe", "Nogokpo", "Sasekope", "Seva", "Sogakope", "Tegbi", "Torkor", "Tregui", "Tsito", "Weta", "Woe", "Wowui"]
    },
    "Northern Region": {
        "Tamale": ["Tamale Central", "Jisonayili", "Dungu", "Lamashegu", "Tishigu", "Vitting", "Gumani", "Abayori", "Adubiliyili", "Bilpela", "Bugulana", "Chanshegu", "Dohinayili", "Fuo", "Gbulung", "Gumani", "Gurugu", "Jisonaayili", "Kakpagyili", "Kalpohini", "Kanvili", "Kukuo", "Kurugu", "Lakshe", "Malshegu", "Nayilifong", "Nyohini", "Sagnarigu", "Samashegu", "Suahun", "Tali", "Tampion", "Tura", "Vitteng", "Wamale", "Zabzugu", "Zogbeli"],
        "Yendi": ["Yendi Central", "Bimbilla", "Bunkpurugu", "Chereponi", "Gambaga", "Gushegu", "Karaga", "Kpandai", "Kumbungu", "Mion", "Mion", "Nakpali", "Nanumba", "Saboba", "Sagnarigu", "Salaga", "Savelugu", "Sawla", "Tatale", "Tolon", "Wapuli", "Wulensi", "Yapei", "Zabzugu"]
    },
    "Upper East Region": {
        "Bolgatanga": ["Bolgatanga Central", "Zuarungu", "Bongo", "Bawku", "Navrongo", "Paga", "Sandema", "Tongo", "Bongo", "Binduri", "Builsa", "Chiana", "Doba", "Garu", "Kassena", "Manga", "Mirigu", "Nangodi", "Pusiga", "Sakoti", "Tempane", "Widnaba", "Zebilla"],
        "Bawku": ["Bawku Central", "Manga", "Binduri", "Bunkpurugu", "Garu", "Kpalwe", "Kulungugu", "Kurugu", "Larabanga", "Malshegu", "Manga", "Missiga", "Nalerigu", "Nangodi", "Pulmakom", "Pusiga", "Sapeliga", "Sombusi", "Tarikom", "Teshie", "Tilli", "Walewale", "Wulugu", "Zabzugu", "Zebilla"]
    },
    "Upper West Region": {
        "Wa": ["Wa Central", "Dafiama", "Gwolu", "Han", "Jirapa", "Kaleo", "Lambussie", "Lawra", "Nadowli", "Nandom", "Sissala", "Tumu", "Wechiau", "Babile", "Boe", "Chiana", "Danyawuo", "Dikpe", "Dokan", "Dorimon", "Duori", "Fian", "Fielmuo", "Ga", "Gbande", "Gbentiri", "Goli", "Gungeri", "Guzape", "Hain", "Haklim", "Hawai", "Huo", "Jonga", "Kakpale", "Kaleo", "Kalkpene", "Kambali", "Kanga", "Kanten", "Kanton", "Karaga", "Kari", "Kawampe", "Kawara", "Kayeri", "Kazie", "Kodie", "Koke", "Kokotua", "Kole", "Kongo", "Kontu", "Kor", "Kore", "Korley", "Koro", "Kpalwe", "Kparil", "Kpawor", "Kpikpi", "Kpoliyili", "Kukuo", "Kunfuri", "Kunjiri", "Kunwow", "Kurugu"]
    },
    "Western North Region": {
        "Sefwi-Wiawso": ["Wiawso", "Asawinso", "Bibiani", "Sefwi Bekwai", "Akontombra", "Juaboso", "Bodi", "Suaman", "Aowin", "Anhwiaso", "Bia", "Bibiani Anhwiaso Bekwai", "Bodi", "Jomoro", "Juaboso", "Kaku", "Nkroful", "Saman", "Sefwi", "Suaman", "Wiawso"]
    },
    "Savannah Region": {
        "Damango": ["Damango", "Bole", "Salaga", "Kpandai", "Daboya", "Yapei", "Kafaba", "Kalakpa", "Ngmayem", "Nkwanta", "Nyankpala", "Salaga South", "Salaga North", "Tolon", "Wasipe", "Yapei", "Zabzugu"]
    },
    "North East Region": {
        "Nalerigu": ["Nalerigu", "Gambaga", "Walewale", "Bunkpurugu", "Chereponi", "Garu", "Kpasenkpe", "Mamprugu", "Nakpanduri", "Pulima", "Wawli", "Yunyoo"]
    },
    "Oti Region": {
        "Dambai": ["Dambai", "Jasikan", "Kadjebi", "Kete Krachi", "Nkwanta", "Krachi East", "Krachi West", "Krachi Nchumuru", "Buem", "Akan", "Biakoye", "Worawora", "Bowiri", "Likpe", "Santrokofi", "Akpafu", "Lolobi"]
    },
    "Ahafo Region": {
        "Goaso": ["Goaso", "Bechem", "Duayaw Nkwanta", "Kenyasi", "Mim", "Abesim", "Acherensua", "Asutifi", "Bechem", "Fosu", "Hwidiem", "Kukuom", "Mim", "Ntotroso", "Sankore", "Subin", "Yamfo"]
    },
    "Bono East Region": {
        "Techiman": ["Techiman", "Kintampo", "Nkoranza", "Atebubu", "Jema", "Kwame Danso", "Pru", "Sene", "Kintampo North", "Kintampo South", "Nkoranza North", "Nkoranza South", "Techiman North", "Techiman South", "Pru East", "Pru West", "Sene East", "Sene West"]
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

# ============ YOUR EXACT PROFESSIONAL PROPOSAL LETTER ============
def get_proposal_template(company_name):
    """Return the exact professional proposal template you provided"""
    audit_url = "https://techwokx.online/#audit"
    qr_base64 = generate_qr_code_base64(audit_url)
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TechWokx IT Assessment</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ padding: 30px; background: white; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ font-size: 18px; font-weight: bold; color: #667eea; margin-bottom: 15px; border-left: 3px solid #667eea; padding-left: 12px; }}
        .observation-box {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; border-radius: 8px; }}
        .service-list {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }}
        .service-tag {{ background: #e0e7ff; color: #4338ca; padding: 6px 12px; border-radius: 20px; font-size: 12px; }}
        .offer-box {{ background: linear-gradient(135deg, #dbeafe, #ede9fe); border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0; }}
        .qr-code {{ text-align: center; margin: 20px 0; }}
        .qr-code img {{ width: 150px; height: 150px; border: 2px solid #e2e8f0; border-radius: 12px; padding: 10px; background: white; }}
        .button {{ background: #22c55e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; }}
        .footer {{ background: #1e293b; color: #94a3b8; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px; }}
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
                    <span class="service-tag">✓ Backup & Recovery Solutions</span>
                    <span class="service-tag">✓ Cloud Productivity Solutions</span>
                    <span class="service-tag">✓ Process Automation</span>
                </div>
            </div>
            
            <div class="offer-box">
                <div class="section-title" style="border-left-color: #22c55e;">🎁 TWO COMPLIMENTARY OFFERS</div>
                <p><strong>1. Find Out Yourself: 5-Step Email & IT Health Check</strong></p>
                <p>To receive your complimentary assessment:</p>
                <div class="qr-code">
                    <img src="data:image/png;base64,{qr_base64}" alt="QR Code">
                </div>
                <p><strong>Or visit:</strong> <a href="{audit_url}">techwokx.online/#audit</a></p>
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

# ============ LETTER CONTENT (Physical Mail Version) ============
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
organization's publicly available digital presence, including your website, domain 
configuration, SSL certificate status, and email setup.

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

We provide practical technology solutions designed to improve reliability, 
productivity, and business continuity.

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
   The assessment takes less than five minutes and provides:
   • A personalized technology health score
   • Email configuration insights
   • Security recommendations

2. Free 15-Minute IT Consultation
   Discuss your specific challenges and get expert advice at no cost.

================================================================================

Thank you for your time and consideration. We would be delighted to help 
{company_name} achieve smoother, more secure, and more reliable IT operations.

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
        "category": lead_data.get("category", ""),
        "lead_score": 75,
        "created_at": datetime.now().isoformat(),
        "email_sent": False
    }
    st.session_state.leads.append(new_lead)
    save_leads()
    return True

def search_google_places(api_key, query, location):
    """Search for real businesses using Google Places API"""
    if not api_key:
        return []
    
    try:
        # First, geocode the location
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
        for place in data.get('results', [])[:15]:
            businesses.append({
                "name": place.get('name'),
                "address": place.get('vicinity', ''),
                "place_id": place.get('place_id')
            })
        
        return businesses
    except Exception as e:
        return []

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
    st.markdown(f"Google Maps: {maps_status}")
    st.markdown(f"Leads: {len(st.session_state.leads)}")
    st.markdown(f"Emails Today: {SMTP_CONFIG['sent_today']}/{SMTP_CONFIG['daily_limit']}")

# ============ DASHBOARD ============
if st.session_state.current_page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>TechWokx Lead Intelligence</h2>
        <p>Professional IT Outreach | Real Google Places Search | All 16 Regions of Ghana</p>
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
        st.markdown('<div class="section-header">📍 All 16 Regions of Ghana</div>', unsafe_allow_html=True)
        for region in ALL_LOCATIONS.keys():
            st.markdown(f"- {region}")
    
    with col2:
        st.markdown('<div class="section-header">🎯 Business Categories</div>', unsafe_allow_html=True)
        for cat in list(SEARCH_QUERIES.keys())[:10]:
            st.markdown(f"- {cat}")
        st.markdown(f"... and {len(SEARCH_QUERIES) - 10} more")

# ============ BATCH SEARCH ============
elif st.session_state.current_page == 'batch_search':
    st.markdown('<div class="section-header">Batch Company Search</div>', unsafe_allow_html=True)
    st.caption("Search for REAL companies across all 16 regions of Ghana | Professional IT Outreach")
    st.markdown("---")
    
    api_keys = get_api_keys()
    
    if not api_keys["google_maps"]:
        st.warning("⚠️ Google Maps API key not configured! Add to .streamlit/secrets.toml for real search.")
        st.info("Using location-based suggestions. Add API key to fetch real companies.")
    
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
    
    limit = st.slider("Number of Companies to Search", 5, 25, 10)
    
    if st.button("🔍 Search Real Companies", type="primary"):
        if selected_town:
            with st.spinner(f"Searching for {selected_category} in {selected_town}..."):
                query = SEARCH_QUERIES.get(selected_category, selected_category)
                
                if api_keys["google_maps"]:
                    businesses = search_google_places(api_keys["google_maps"], query, selected_town)
                else:
                    # Demo businesses based on town and category
                    businesses = []
                    for i in range(limit):
                        businesses.append({
                            "name": f"{selected_category} {i+1} - {selected_town}",
                            "address": f"{selected_town}, {selected_district}, {selected_region}",
                            "place_id": f"place_{i}"
                        })
                
                for biz in businesses:
                    biz["category"] = selected_category
                    biz["town"] = selected_town
                    biz["district"] = selected_district
                    biz["region"] = selected_region
                
                st.session_state.batch_results = businesses[:limit]
                st.success(f"Found {len(businesses)} businesses in {selected_town}")
    
    if st.session_state.batch_results:
        st.markdown("### Search Results")
        
        for idx, company in enumerate(st.session_state.batch_results):
            with st.expander(f"{company['name']} - {company.get('address', '')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Address:** {company.get('address', 'N/A')}")
                    st.write(f"**Town:** {company.get('town', 'N/A')}")
                    st.write(f"**District:** {company.get('district', 'N/A')}")
                with col2:
                    st.write(f"**Region:** {company.get('region', 'N/A')}")
                    st.write(f"**Category:** {company.get('category', 'N/A')}")
                
                st.markdown("---")
                st.markdown("### 📝 Proposal Letter")
                
                # Generate proposal with company name
                proposal_html = get_proposal_template(company['name'])
                
                # View/Edit toggle
                edit_mode = st.checkbox(f"Edit Proposal", key=f"edit_{idx}")
                
                if edit_mode:
                    edited_proposal = st.text_area("Edit Proposal", proposal_html, height=400, key=f"proposal_edit_{idx}")
                    if st.button("Copy to Clipboard", key=f"copy_{idx}"):
                        st.write("Proposal copied! Press Ctrl+C to copy")
                        st.code(edited_proposal, language='html')
                else:
                    st.markdown(proposal_html, unsafe_allow_html=True)
                    if st.button("Copy Proposal", key=f"copy_view_{idx}"):
                        st.code(proposal_html, language='html')
                
                st.markdown("---")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("Add to CRM", key=f"add_{idx}"):
                        company_data = {
                            "name": company['name'],
                            "address": company.get('address', ''),
                            "category": selected_category
                        }
                        if add_lead(company_data):
                            st.success(f"Added {company['name']} to CRM")
                            st.rerun()
                
                with col2:
                    if st.button("Download Letter", key=f"download_{idx}"):
                        letter = get_letter_content(company['name'])
                        st.download_button(
                            label="Download",
                            data=letter,
                            file_name=f"letter_{company['name'].replace(' ', '_')}.txt",
                            mime="text/plain",
                            key=f"download_btn_{idx}"
                        )
                
                with col3:
                    email_domain = company['name'].lower().replace(' ', '').replace('&', '').replace("'", '')
                    email = st.text_input("Email Address", value=f"info@{email_domain}.com", key=f"email_{idx}")
                    if st.button("Send Email", key=f"send_{idx}"):
                        subject = f"FREE 5-Step Email & IT Health Check - For {company['name']}"
                        success, msg = send_email(email, subject, proposal_html)
                        if success:
                            st.success(f"Email sent to {company['name']}")
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
                        letter = get_letter_content(company['name'])
                        st.download_button(
                            label="Download Letter",
                            data=letter,
                            file_name=f"letter_{company['name'].replace(' ', '_')}.txt",
                            mime="text/plain",
                            key=f"letter_dl_{idx}"
                        )

# ============ LEADS CRM ============
elif st.session_state.current_page == 'crm':
    st.markdown('<div class="section-header">Leads CRM</div>', unsafe_allow_html=True)
    st.caption(f"Total Leads: {len(st.session_state.leads)}")
    st.markdown("---")
    
    if st.session_state.leads:
        search = st.text_input("Search", placeholder="Search by name")
        
        filtered = st.session_state.leads
        if search:
            filtered = [l for l in filtered if search.lower() in l.get('name', '').lower()]
        
        for lead in filtered:
            with st.expander(f"{lead['name']} - Score: {lead['lead_score']}/100"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Address:** {lead.get('address', 'N/A')}")
                    st.write(f"**Category:** {lead.get('category', 'N/A')}")
                with col2:
                    st.write(f"**Added:** {lead['created_at'][:10]}")
                
                if st.button(f"Generate Proposal", key=f"proposal_{lead['id']}"):
                    st.session_state.edit_proposal = lead
                    st.session_state.current_page = 'edit_proposal'
                    st.rerun()
                
                if not lead.get('email_sent'):
                    email = st.text_input("Email", key=f"email_crm_{lead['id']}")
                    if st.button(f"Send Email", key=f"send_crm_{lead['id']}"):
                        if email:
                            proposal_html = get_proposal_template(lead['name'])
                            subject = f"FREE 5-Step Email & IT Health Check - For {lead['name']}"
                            success, msg = send_email(email, subject, proposal_html)
                            if success:
                                lead['email_sent'] = True
                                save_leads()
                                st.success(f"Email sent to {lead['name']}")
                                st.rerun()
                            else:
                                st.error(f"Failed: {msg}")
                        else:
                            st.warning("Please enter email address")
    else:
        st.info("No leads yet. Run a batch search to add leads.")

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
                <strong>Status:</strong> ✅ {log['status']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No emails sent yet")

# ============ LETTER QUEUE ============
elif st.session_state.current_page == 'letter_queue':
    st.markdown('<div class="section-header">Letter Queue</div>', unsafe_allow_html=True)
    st.caption("Companies ready for physical mailing")
    st.markdown("---")
    
    if st.session_state.letter_queue:
        for idx, letter in enumerate(st.session_state.letter_queue):
            with st.expander(f"{letter.get('company', 'Unknown')}"):
                letter_content = get_letter_content(letter.get('company', 'Business'))
                st.code(letter_content, language='text')
                if st.button(f"Download Letter", key=f"queue_download_{idx}"):
                    st.download_button(
                        label="Download",
                        data=letter_content,
                        file_name=f"letter_{letter.get('company', 'business').replace(' ', '_')}.txt",
                        mime="text/plain",
                        key=f"queue_btn_{idx}"
                    )
    else:
        st.success("No pending letters")

# ============ SETTINGS ============
elif st.session_state.current_page == 'settings':
    st.markdown('<div class="section-header">Settings</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### API Configuration")
    st.code("""
    # .streamlit/secrets.toml
    GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
    """)
    
    st.markdown("### Email Configuration")
    st.info(f"""
    **SMTP Settings:**
    - Host: {SMTP_CONFIG['host']}
    - Port: {SMTP_CONFIG['port']}
    - Username: {SMTP_CONFIG['username']}
    - Daily Limit: {SMTP_CONFIG['daily_limit']} emails/day
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

# ============ EDIT PROPOSAL ============
elif st.session_state.current_page == 'edit_proposal' and st.session_state.edit_proposal:
    lead = st.session_state.edit_proposal
    st.markdown(f'<div class="section-header">Edit Proposal for {lead["name"]}</div>', unsafe_allow_html=True)
    
    proposal_html = get_proposal_template(lead['name'])
    edited_proposal = st.text_area("Edit Proposal (HTML)", proposal_html, height=500)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Changes"):
            st.success("Proposal saved (demo)")
    with col2:
        if st.button("Back to CRM"):
            st.session_state.current_page = 'crm'
            st.rerun()
    
    st.markdown("### Preview")
    st.markdown(edited_proposal, unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("2024 TechWokx IT Solutions | Professional IT Outreach | All 16 Regions of Ghana")

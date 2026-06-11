import streamlit as st
import pandas as pd
import json
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
import time
import qrcode
from io import BytesIO
import base64
import re
import tldextract
import socket
from PIL import Image

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
CALL_LOG_FILE = "data/call_log.json"

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

# ============ HEADER IMAGE ============
HEADER_IMAGE_URL = "https://github.com/techwokx-cloud/techwokx-lead-intelligence/blob/main/techwokx_header.png"

# ============ ENHANCED CITY DATABASE ============
ALL_LOCATIONS = {
    "Greater Accra Region": {
        "Accra Metropolitan": [
            "Airport Residential", "Airport City", "Cantonments", "Labone", "Osu", 
            "Ring Road Central", "Ridge", "North Ridge", "Adabraka", "Asylum Down", 
            "Tudu", "Jamestown", "Usshertown", "Korle Bu", "Mamprobi", "Chorkor", 
            "Kaneshie", "Achimota", "Legon", "Madina", "Adenta", "East Legon", 
            "West Legon", "Dzorwulu", "Shiashie", "Trasacco Valley", "Spintex", 
            "Sakumono", "Teshie", "Nungua", "Lashibi", "Ashaiman", "Tema", 
            "Community 1-10", "Tema Industrial Area", "Kpone", "Adjei Kojo", 
            "Afienya", "Dawhenya", "Prampram", "Dodowa", "Abokobi", "Danfa", 
            "Teiman", "Taifa", "Kwabenya", "Dome", "Pokuase", "Haasto", "Amasaman", 
            "Nsawam", "Medie", "Sarpeiman", "Weija", "Gbawe", "Mallam", "Kwashieman", 
            "Darkuman", "Kasoa", "Budumburam", "Opeikuma"
        ],
        "Tema Metropolitan": [
            "Tema Community 1", "Tema Community 2", "Tema Community 3", 
            "Tema Community 4", "Tema Community 5", "Tema Community 6", 
            "Tema Community 7", "Tema Community 8", "Tema Community 9", 
            "Tema Community 10", "Tema Industrial Area", "Kpone", "Sakumono", 
            "Lashibi", "Adjei Kojo", "Afienya", "Dawhenya", "Prampram"
        ]
    },
    "Ashanti Region": {
        "Kumasi Metropolitan": [
            "Adum", "Bantama", "Asafo", "Asokwa", "Tafo", "Suame", "Oforikrom", 
            "Ayigya", "Bohyen", "Kaase", "Danyame", "Amakom", "Buokrom", "Kwadaso", 
            "Nhyiaeso", "Abuakwa", "Mampong", "Atonsu", "Ahinsan", "Boadi", 
            "Kentinkrono", "Ayeduase", "Kotei", "Santasi", "Patase", "Abrepo", 
            "Bekwai", "Osiem", "Adankwame", "Achiase", "Trede", "Effiduase", 
            "Kenyasi", "Abirem", "Konongo", "Mamponteng"
        ]
    },
    "Western Region": {
        "Takoradi": [
            "Takoradi Central", "Beach Road", "Kojokrom", "Effiakuma", "Anaji", 
            "Nkontompo", "Kwesimintsim", "Apremdo", "Fijai", "Sekondi", "Nkroful",
            "Adiembra", "Essikado", "Ketan", "Assorko"
        ]
    },
    "Central Region": {
        "Cape Coast": ["Cape Coast Central", "Pedu", "Adisadel", "Amamoma", "Kakumdo"],
        "Kasoa": ["Kasoa Central", "Opeikuma", "Akweley", "Budumburam", "Millennium City"]
    },
    "Eastern Region": {
        "Koforidua": ["Koforidua Central", "Adweso", "Effiduase", "Oyoko", "New Juaben"]
    },
    "Volta Region": {
        "Ho": ["Ho Central", "Hliha", "Ahoe", "Bankoe", "Deme", "Dome", "Klefe"]
    },
    "Northern Region": {
        "Tamale": ["Tamale Central", "Jisonayili", "Dungu", "Lamashegu", "Tishigu"]
    },
    "Upper East Region": {
        "Bolgatanga": ["Bolgatanga Central", "Zuarungu", "Bongo", "Navrongo", "Paga"]
    },
    "Upper West Region": {
        "Wa": ["Wa Central", "Dafiama", "Gwolu", "Han", "Jirapa"]
    },
    "Western North Region": {
        "Sefwi-Wiawso": ["Wiawso", "Asawinso", "Bibiani", "Sefwi Bekwai"]
    },
    "Savannah Region": {
        "Damango": ["Damango", "Bole", "Salaga", "Daboya", "Yapei"]
    },
    "North East Region": {
        "Nalerigu": ["Nalerigu", "Gambaga", "Walewale", "Bunkpurugu", "Chereponi"]
    },
    "Oti Region": {
        "Dambai": ["Dambai", "Jasikan", "Kadjebi", "Kete Krachi", "Nkwanta"]
    },
    "Ahafo Region": {
        "Goaso": ["Goaso", "Bechem", "Duayaw Nkwanta", "Kenyasi", "Mim"]
    },
    "Bono East Region": {
        "Techiman": ["Techiman", "Kintampo", "Nkoranza", "Atebubu", "Jema"]
    },
    "Bono Region": {
        "Sunyani": ["Sunyani Central", "Sunyani West", "Sunyani East", "Dormaa Ahenkro", "Berekum"]
    }
}

# ============ SEARCH QUERIES (Removed Banks) ============
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
    "Logistics": "logistics shipping company"
}

# ============ CALL SCRIPT TEMPLATE ============
CALL_SCRIPT = """
CALL SCRIPT - TechWokx IT Solutions

Company: {company_name}
Contact Person: _______
Phone: {phone}
Date: _______

----------------- INTRODUCTION -----------------
"Hello, this is George from TechWokx IT Solutions. 
Am I speaking with the person responsible for IT or business operations?"

----------------- IF YES -----------------
"Great! We recently reviewed {company_name}'s online presence and identified 
some areas that could improve your email security and IT reliability."

"Our complimentary IT assessment showed that your email deliverability could be improved
and there may be security gaps that need attention."

"We're offering a FREE 5-Step Email & IT Health Check to help you identify and fix these issues."

----------------- OFFER -----------------
"Would you be interested in receiving our free assessment? It takes less than 5 minutes."

{response}

----------------- IF INTERESTED -----------------
"Perfect! I'll send the assessment link to your email. Could you confirm your email address?"

Email: _______

"Also, would you like me to send a detailed proposal based on the assessment results?"

{response}

----------------- CLOSING -----------------
"Thank you for your time. I'll send the assessment right away."

"Feel free to call me back at +233 555 087 407 if you have any questions."

----------------- NOTES -----------------
Call Outcome: [Interested / Not Interested / Call Back / Wrong Number]
Follow-up Date: _______
Assessment Sent: Yes / No
Proposal Requested: Yes / No
Email Collected: _______

"""

# ============ WEBSITE & EMAIL FUNCTIONS ============
def check_website_status(url):
    if not url:
        return {"working": False, "error": "No website", "spam_risk": False}
    try:
        if not url.startswith("http"):
            url = "https://" + url
        response = requests.get(url, timeout=5, verify=False)
        is_working = response.status_code == 200
        # Check for spam indicators (simplified)
        spam_risk = response.elapsed.total_seconds() > 3 if is_working else True
        return {
            "working": is_working, 
            "status_code": response.status_code,
            "spam_risk": spam_risk,
            "response_time": response.elapsed.total_seconds() * 1000
        }
    except:
        return {"working": False, "error": "Connection failed", "spam_risk": True}

def search_website_by_name(serp_api_key, business_name):
    if not serp_api_key:
        return None
    try:
        url = "https://serpapi.com/search"
        params = {
            "api_key": serp_api_key,
            "q": f"{business_name} Ghana official website",
            "engine": "google",
            "num": 5
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "knowledge_graph" in data:
            website = data["knowledge_graph"].get("website", "")
            if website:
                return website
        if "organic_results" in data:
            for result in data["organic_results"][:3]:
                link = result.get("link", "")
                if link and "facebook" not in link and "twitter" not in link:
                    return link
        return None
    except:
        return None

def generate_possible_emails(company_name, domain=None):
    emails = []
    name_parts = company_name.lower().replace('&', 'and').split()
    base_name = ''.join(name_parts[:2]) if len(name_parts) > 1 else name_parts[0]
    patterns = [
        f"info@{base_name}.com", f"contact@{base_name}.com", f"hello@{base_name}.com",
        f"support@{base_name}.com", f"admin@{base_name}.com", f"enquiries@{base_name}.com"
    ]
    if domain:
        clean_domain = domain.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]
        patterns = [f"info@{clean_domain}", f"contact@{clean_domain}", f"hello@{clean_domain}", f"admin@{clean_domain}"]
    return patterns

def find_email_from_website(website):
    if not website:
        return None
    try:
        if not website.startswith("http"):
            website = "https://" + website
        response = requests.get(website, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, response.text)
            exclude = ['example', 'test', 'noreply', 'jpg', 'png', 'css']
            valid_emails = [e for e in emails if not any(x in e.lower() for x in exclude)]
            business_keywords = ['info', 'contact', 'hello', 'support', 'sales', 'admin']
            for email in valid_emails:
                if any(kw in email.lower() for kw in business_keywords):
                    return email
            return valid_emails[0] if valid_emails else None
        return None
    except:
        return None

def enrich_company_data(company, serp_api_key):
    website_status = None
    if company.get('website'):
        website_status = check_website_status(company['website'])
        if not website_status['working']:
            found_website = search_website_by_name(serp_api_key, company['name'])
            if found_website:
                company['website'] = found_website
                website_status = check_website_status(found_website)
    if not company.get('website'):
        found_website = search_website_by_name(serp_api_key, company['name'])
        if found_website:
            company['website'] = found_website
            website_status = check_website_status(found_website)
    company['website_status'] = website_status
    if not company.get('email'):
        if company.get('website'):
            email = find_email_from_website(company['website'])
            if email:
                company['email'] = email
        if not company.get('email'):
            company['possible_emails'] = generate_possible_emails(company['name'], company.get('website'))
        else:
            company['possible_emails'] = []
    return company

def is_company_searched(company_name):
    return company_name in st.session_state.searched_companies

def mark_company_searched(company_name):
    st.session_state.searched_companies.add(company_name)

def has_email_sent(company_name):
    for log in st.session_state.email_log:
        if log.get('company') == company_name:
            return True, log
    return False, None

# ============ ENHANCED PROPOSAL WITH FULL SERVICES ============
def get_enhanced_proposal_html(company_name, website_status=None):
    """Generate enhanced proposal with full services and pricing"""
    audit_url = "https://techwokx.online/#audit"
    qr_base64 = generate_qr_code_base64(audit_url)
    
    website_warning = ""
    if website_status:
        if not website_status.get('working'):
            website_warning = f"""
            <div style="background: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; margin: 15px 0; border-radius: 8px;">
                <strong>⚠️ Website Issue Detected:</strong> Your website at {website_status.get('url', '')} appears to be down or inaccessible.
                This affects your online credibility and email deliverability.
            </div>
            """
        elif website_status.get('spam_risk'):
            website_warning = f"""
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; border-radius: 8px;">
                <strong>⚠️ Email Deliverability Risk:</strong> Your emails may be going to spam folders.
                We can help fix this with proper email authentication.
            </div>
            """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>TechWokx IT Assessment - {company_name}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1e293b; margin: 0; padding: 0; background: #f0f4f8; }}
            .container {{ max-width: 800px; margin: 20px auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 25px -12px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ font-size: 28px; margin: 0; }}
            .content {{ padding: 30px; }}
            .risk-score-box {{ background: linear-gradient(135deg, #fbbf24, #f59e0b); border-radius: 16px; padding: 25px; text-align: center; margin: 20px 0; }}
            .risk-score-box h2 {{ color: #0f172a; font-size: 24px; margin: 0 0 10px 0; }}
            .risk-score-box p {{ color: #0f172a; font-size: 16px; }}
            .pricing-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
            .pricing-card {{ border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; transition: all 0.3s; }}
            .pricing-card:hover {{ box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); transform: translateY(-2px); }}
            .pricing-card h3 {{ color: #667eea; margin-top: 0; }}
            .price {{ font-size: 28px; font-weight: 700; color: #0f172a; }}
            .price small {{ font-size: 14px; font-weight: normal; }}
            .feature-list {{ list-style: none; padding: 0; margin: 15px 0; }}
            .feature-list li {{ padding: 8px 0; border-bottom: 1px solid #e2e8f0; }}
            .feature-list li:before {{ content: "✓"; color: #22c55e; margin-right: 10px; }}
            .button {{ background: #22c55e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: 600; }}
            .button-secondary {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; display: inline-block; }}
            .qr-code {{ text-align: center; margin: 20px 0; }}
            .qr-code img {{ width: 150px; height: 150px; border: 2px solid #e2e8f0; border-radius: 12px; padding: 10px; background: white; }}
            .footer {{ background: #1e293b; color: #94a3b8; padding: 20px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{HEADER_IMAGE_URL}" alt="TechWokx" style="max-width: 200px; margin-bottom: 15px;">
                <h1>🔍 TechWokx IT Solutions</h1>
                <p>FREE 5-Step Email & IT Health Check</p>
            </div>
            <div class="content">
                <div class="risk-score-box">
                    <h2>📊 Get Your Business Email Risk Score Now</h2>
                    <p>Answer 5 questions. Get your personalised report. Your 1-page summary is sent to you instantly.<br>
                    Full implementation guide goes to our team for follow-up.</p>
                    <a href="{audit_url}" class="button">🚀 Start Free Audit</a>
                </div>
                
                {website_warning}
                
                <h2>🛠️ Our Services</h2>
                <div class="pricing-grid">
                    <div class="pricing-card">
                        <h3>⚡ Entry — Fast Fix</h3>
                        <div class="price">₵1,500 <small>one-time · 1-2 days</small></div>
                        <p>Emails landing in spam, bouncing, or failing to reach clients.</p>
                        <ul class="feature-list">
                            <li>Full email infrastructure audit</li>
                            <li>Email security records configured</li>
                            <li>Email migration if needed</li>
                            <li>Professional signatures for all staff</li>
                            <li>Deliverability test before & after</li>
                            <li>Written fix summary report</li>
                        </ul>
                        <a href="{audit_url}" class="button-secondary">Start With Free Audit →</a>
                    </div>
                    
                    <div class="pricing-card">
                        <h3>🔄 Recurring</h3>
                        <div class="price">₵800 <small>/month · no long contract</small></div>
                        <p>No IT department? We become your on-call IT team.</p>
                        <ul class="feature-list">
                            <li>Remote support for all staff devices</li>
                            <li>WiFi & network troubleshooting</li>
                            <li>POS & booking software support</li>
                            <li>Email & communication issues</li>
                            <li>Monthly system health check</li>
                            <li>4-hour priority response weekdays</li>
                        </ul>
                        <a href="#" class="button-secondary">Discuss Retainer →</a>
                    </div>
                    
                    <div class="pricing-card">
                        <h3>📋 Professional</h3>
                        <div class="price">₵2,000 <small>one-time + optional fix</small></div>
                        <p>A structured professional audit of your entire IT environment.</p>
                        <ul class="feature-list">
                            <li>Email, network & access control review</li>
                            <li>Former staff risk assessment</li>
                            <li>Backup & recovery check</li>
                            <li>Security & device management</li>
                            <li>RED/ORANGE/GREEN risk status</li>
                            <li>Top 5 risks with fix costs</li>
                        </ul>
                        <a href="{audit_url}" class="button-secondary">Start With Free Audit →</a>
                    </div>
                    
                    <div class="pricing-card">
                        <h3>🤖 High Value</h3>
                        <div class="price">₵800 <small>per script</small></div>
                        <p>Business Process Automation Scripts</p>
                        <ul class="feature-list">
                            <li>Invoice & payment reminder automation</li>
                            <li>Email cleanup & archiving scripts</li>
                            <li>File processing & report generation</li>
                            <li>Staff access audit scripts</li>
                            <li>Website uptime monitoring</li>
                            <li>Delivered, tested & documented</li>
                        </ul>
                        <a href="#" class="button-secondary">Describe Your Task →</a>
                    </div>
                </div>
                
                <div class="qr-code">
                    <img src="data:image/png;base64,{qr_base64}" alt="QR Code">
                    <p><strong>Scan to take your free audit</strong></p>
                </div>
                
                <p style="font-size: 18px; font-weight: 500; text-align: center;">📞 Call us: +233 555 087 407 | ✉️ hello@techwokx.online</p>
            </div>
            <div class="footer">
                <p>© 2024 TechWokx IT Solutions | Intelligent Solutions. Secure Futures.</p>
                <p>P.O. Box ML469, Malam, Accra, Ghana</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_personalized_email_body(company_name, website_status=None, ai_recommendation=None):
    """Generate personalized email based on company's specific situation"""
    audit_url = "https://techwokx.online/#audit"
    qr_base64 = generate_qr_code_base64(audit_url)
    
    # Personalize based on website status
    if website_status:
        if not website_status.get('working'):
            opening = f"We noticed that your website appears to be down, which can significantly impact your business credibility and email deliverability."
        elif website_status.get('spam_risk'):
            opening = f"Our analysis indicates your emails may be going to spam folders, causing you to miss important business opportunities."
        else:
            opening = f"We've identified opportunities to improve your email security and IT infrastructure."
    else:
        opening = f"We've identified opportunities to improve your email security and IT infrastructure."
    
    ai_advice = ""
    if ai_recommendation:
        ai_advice = f"""
        <div style="background: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0; border-radius: 8px;">
            <strong>🤖 AI Recommendation:</strong> {ai_recommendation}
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>TechWokx IT Assessment - {company_name}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1e293b; }}
            .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 25px; background: white; }}
            .footer {{ background: #1e293b; color: #94a3b8; padding: 15px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px; }}
            .button {{ background: #22c55e; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; display: inline-block; }}
            .qr-code {{ text-align: center; margin: 20px 0; }}
            .qr-code img {{ width: 120px; height: 120px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{HEADER_IMAGE_URL}" alt="TechWokx" style="max-width: 180px;">
                <h2>FREE 5-Step Email & IT Health Check</h2>
            </div>
            <div class="content">
                <p>Dear Management Team,</p>
                
                <p>{opening}</p>
                
                {ai_advice}
                
                <div style="background: #fbbf24; border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0;">
                    <h3 style="color: #0f172a; margin: 0;">📊 Get Your Business Email Risk Score Now</h3>
                    <p style="color: #0f172a;">Answer 5 questions. Get your personalised report in minutes.</p>
                    <div class="qr-code">
                        <img src="data:image/png;base64,{qr_base64}" alt="QR Code">
                    </div>
                    <a href="{audit_url}" class="button">🚀 Start Free Audit →</a>
                </div>
                
                <h3>💡 Did You Know?</h3>
                <ul>
                    <li>73% of business emails never reach the inbox without proper setup</li>
                    <li>3 seconds is how long a client takes to judge your professionalism from an email</li>
                    <li>Former staff access is the #1 silent security risk for growing businesses</li>
                </ul>
                
                <p>Best regards,<br>
                <strong>George Jabley</strong><br>
                Founder & IT Operations Lead<br>
                TechWokx Ghana<br>
                📞 +233 555 087 407</p>
            </div>
            <div class="footer">
                <p>© 2024 TechWokx IT Solutions | P.O. Box ML469, Malam, Accra, Ghana</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_letter_content(company_name, website_status=None):
    audit_url = "https://techwokx.online/#audit"
    current_date = datetime.now().strftime("%B %d, %Y")
    
    website_note = ""
    if website_status and not website_status.get('working'):
        website_note = "\n⚠️ Your website appears to be down - this urgently needs attention.\n"
    
    return f"""
================================================================================
                          TECHWOKX IT SOLUTIONS
                    FREE 5-Step Email & IT Health Check
================================================================================

Date: {current_date}

To: Management Team
{company_name}
Ghana

Dear Management Team,

My name is George Jabley from TechWokx IT Solutions.{website_note}

================================================================================
                    GET YOUR BUSINESS EMAIL RISK SCORE NOW
================================================================================

Answer 5 questions. Get your personalised report instantly.

📊 Visit: {audit_url}
📱 Scan QR code (printed separately)

================================================================================
                    OUR SERVICES & PRICING
================================================================================

⚡ Entry — Fast Fix: ₵1,500 (one-time)
   Email security setup, DNS configuration, professional signatures

🔄 Recurring IT Retainer: ₵800/month
   24/7 remote support, network troubleshooting, system health checks

📋 Infrastructure Audit: ₵2,000
   Complete IT environment audit with risk report and fix recommendations

🤖 Automation Scripts: ₵800 per script
   Custom automation for your business processes

================================================================================
                    FREE COMPLIMENTARY OFFERS
================================================================================

1. 5-Step Email & IT Health Check - Visit: {audit_url}
2. Free 15-Minute IT Consultation - Call: +233 555 087 407

================================================================================

📞 Call us: +233 555 087 407
✉️ Email: hello@techwokx.online
🌐 Website: techwokx.online

Thank you for your time.

Warm regards,

George Jabley
TechWokx Ghana

================================================================================
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
        for place in data.get('results', [])[:25]:
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
        "possible_emails": lead_data.get("possible_emails", []),
        "website_status": lead_data.get("website_status", {}),
        "category": lead_data.get("category", ""),
        "rating": lead_data.get("rating", 0),
        "lead_score": 75,
        "created_at": datetime.now().isoformat(),
        "email_sent": False,
        "email_sent_date": None,
        "email_responded": False,
        "call_made": False,
        "call_notes": "",
        "followup_sequence": 0,
        "next_followup_date": None
    }
    st.session_state.leads.append(new_lead)
    save_leads()
    return True

def update_email_sent(lead_name, email):
    for lead in st.session_state.leads:
        if lead['name'] == lead_name:
            lead['email_sent'] = True
            lead['email_sent_date'] = datetime.now().isoformat()
            lead['followup_sequence'] = 1
            lead['next_followup_date'] = (datetime.now() + timedelta(days=1)).isoformat()
            save_leads()
            return True
    return False

def update_email_responded(lead_name):
    for lead in st.session_state.leads:
        if lead['name'] == lead_name:
            lead['email_responded'] = True
            save_leads()
            return True
    return False

def update_followup_sequence(lead_name):
    for lead in st.session_state.leads:
        if lead['name'] == lead_name:
            if lead['followup_sequence'] < 5:
                lead['followup_sequence'] += 1
                lead['next_followup_date'] = (datetime.now() + timedelta(days=1)).isoformat()
                save_leads()
            return True
    return False

def get_followup_template(sequence):
    templates = {
        1: "Day 1 Follow-up: Did you have a chance to review our free audit offer?",
        2: "Day 2 Follow-up: Common email security issues we fix...",
        3: "Day 3 Follow-up: Special offer - 15% discount on Email Security package",
        4: "Day 4 Follow-up: Case study - How we helped a similar business",
        5: "Day 5 Follow-up: Final offer - Book your free consultation today"
    }
    return templates.get(sequence, "Follow-up: Let us help secure your business email")

def ai_recommend_action(lead):
    """AI recommendation on whether to call or email"""
    if not lead.get('email_sent'):
        return "📧 Send initial email first"
    if lead.get('email_sent') and not lead.get('email_responded'):
        days_since = (datetime.now() - datetime.fromisoformat(lead['email_sent_date'])).days if lead.get('email_sent_date') else 30
        if days_since > 3:
            return "📞 Call recommended - No response to emails for 3+ days"
        else:
            return "📧 Send follow-up email (Day 2 sequence)"
    if lead.get('email_responded'):
        return "📞 Call to discuss proposal - Lead has shown interest"
    return "📧 Continue email sequence"

# ============ QR CODE ============
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
.proposal-container { background: white; border-radius: 12px; padding: 2rem; border: 1px solid #e2e8f0; max-height: 800px; overflow-y: auto; }
.website-broken { color: #dc2626; font-size: 0.8rem; }
.website-working { color: #22c55e; font-size: 0.8rem; }
.spam-warning { color: #f59e0b; font-size: 0.8rem; }
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
        <p>Professional IT Outreach | Email Tracking | Call Management | Visit Planning</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
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
    with col5:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>16</div><div class='metric-label'>Regions</div></div>", unsafe_allow_html=True)
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
        st.markdown('<div class="section-header">📊 Follow-ups Needed</div>', unsafe_allow_html=True)
        needs_followup = [l for l in st.session_state.leads if l.get('email_sent') and not l.get('email_responded')]
        for lead in needs_followup[:3]:
            st.markdown(f"<div class='data-card'><strong>{lead['name']}</strong><br>Email sent: {lead.get('email_sent_date', '')[:10]}</div>", unsafe_allow_html=True)

# ============ SEARCH COMPANIES ==========
if st.session_state.current_page == 'search':
    st.markdown('<div class="section-header">🔍 Search Companies</div>', unsafe_allow_html=True)
    st.caption("Find businesses across Ghana | Remembers searched companies | Auto-enrichment")
    st.markdown("---")
    api_keys = get_api_keys()
    if not api_keys["google_maps"]:
        st.error("❌ Google Maps API key not configured!")
        st.stop()
    col1, col2 = st.columns(2)
    with col1:
        regions = list(ALL_LOCATIONS.keys())
        selected_region = st.selectbox("Select Region", regions)
    with col2:
        if selected_region:
            cities = ALL_LOCATIONS[selected_region]
            selected_city = st.selectbox("Select City", list(cities.keys()))
    col1, col2 = st.columns(2)
    with col1:
        categories = list(SEARCH_QUERIES.keys())
        selected_category = st.selectbox("Business Category", categories)
    with col2:
        enrich_data = st.checkbox("Enrich missing data", value=True)
        limit = st.slider("Number of Companies", 5, 30, 15)
    if st.button("🔍 Search", type="primary"):
        if selected_city:
            with st.spinner(f"Searching for {selected_category} in {selected_city}..."):
                query = SEARCH_QUERIES.get(selected_category, selected_category)
                towns = ALL_LOCATIONS[selected_region][selected_city]
                all_businesses = []
                for town in towns[:3]:
                    businesses = search_google_places(api_keys["google_maps"], query, town)
                    for biz in businesses:
                        biz["town"] = town
                        biz["city"] = selected_city
                        biz["region"] = selected_region
                        biz["category"] = selected_category
                    all_businesses.extend(businesses)
                    time.sleep(0.5)
                seen = set()
                unique = []
                for b in all_businesses:
                    if b['name'] not in seen:
                        seen.add(b['name'])
                        unique.append(b)
                st.session_state.batch_results = unique[:limit]
                st.success(f"Found {len(unique)} unique businesses")
    if st.session_state.batch_results:
        st.markdown("### Search Results")
        for idx, company in enumerate(st.session_state.batch_results):
            if enrich_data and api_keys["serp_api"]:
                company = enrich_company_data(company, api_keys["serp_api"])
            email_sent_info, email_log = has_email_sent(company['name'])
            with st.expander(f"🏢 {company['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**📍 Address:** {company.get('address', 'N/A')}")
                    st.markdown(f"**📞 Phone:** {company.get('phone', 'N/A')}")
                    website = company.get('website', '')
                    status = company.get('website_status', {})
                    if website:
                        if status.get('working'):
                            st.markdown(f"**🌐 Website:** {website} ✅")
                        else:
                            st.markdown(f"**🌐 Website:** {website} ❌ (Not working)")
                        if status.get('spam_risk') and status.get('working'):
                            st.markdown(f"**⚠️ Spam Risk:** Your emails may go to spam folders")
                    else:
                        st.markdown(f"**🌐 Website:** Not found")
                with col2:
                    email = company.get('email', '')
                    if email:
                        st.markdown(f"**📧 Email:** {email}")
                    else:
                        st.markdown(f"**📧 Email:** Not found")
                        if company.get('possible_emails'):
                            st.markdown(f"**💡 Try:** {', '.join(company['possible_emails'][:2])}")
                    st.markdown(f"**⭐ Rating:** {'⭐' * int(company.get('rating', 0))} {company.get('rating', 'N/A')}")
                if email_sent_info:
                    st.info(f"📧 Email already sent on {email_log.get('date', '')[:10]}")
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
                            mark_company_searched(company['name'])
                            st.success(f"Added {company['name']} to CRM")
                            st.rerun()
                        else:
                            st.warning("Already in CRM")
                with col3:
                    email_options = []
                    if company.get('email'):
                        email_options.append(company['email'])
                    if company.get('possible_emails'):
                        email_options.extend(company['possible_emails'][:3])
                    if email_options:
                        selected_email = st.selectbox("Email", email_options, key=f"email_{idx}")
                    else:
                        selected_email = st.text_input("Email", key=f"email_input_{idx}")
                    if st.button("📧 Send Email", key=f"send_{idx}"):
                        if selected_email:
                            ai_rec = ai_recommend_action({"email_sent": False})
                            email_body = get_personalized_email_body(company['name'], company.get('website_status'), ai_rec)
                            subject = f"FREE IT Assessment for {company['name']}"
                            success, msg = send_email(selected_email, subject, email_body)
                            if success:
                                update_email_sent(company['name'], selected_email)
                                st.success(f"Email sent to {company['name']}")
                                st.session_state.email_log.append({
                                    "to": selected_email, "company": company['name'],
                                    "subject": subject, "date": datetime.now().isoformat(),
                                    "status": "Sent", "followup_sequence": 1
                                })
                                save_email_log()
                                st.rerun()
                            else:
                                st.error(f"Failed: {msg}")
                        else:
                            st.warning("Enter email")
                with col4:
                    if st.button("📞 Call", key=f"call_{idx}"):
                        st.session_state.call_queue.append({
                            "company": company['name'], "phone": company.get('phone', 'No phone'),
                            "script": CALL_SCRIPT.format(company_name=company['name'], phone=company.get('phone', 'No phone')),
                            "added_date": datetime.now().isoformat()
                        })
                        st.success("Added to call queue")

# ============ PROPOSAL PREVIEW ============
elif st.session_state.current_page == 'proposal_preview' and st.session_state.selected_company:
    company = st.session_state.selected_company
    st.markdown(f'<div class="section-header">📄 Proposal for {company["name"]}</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.container():
            st.markdown('<div class="proposal-container">', unsafe_allow_html=True)
            proposal_html = get_enhanced_proposal_html(company['name'], company.get('website_status'))
            st.markdown(proposal_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("### Company Details")
        st.markdown(f"**Name:** {company['name']}")
        st.markdown(f"**Address:** {company.get('address', 'N/A')}")
        st.markdown(f"**Phone:** {company.get('phone', 'N/A')}")
        website = company.get('website', '')
        if website:
            status = company.get('website_status', {})
            st.markdown(f"**Website:** {website} {'✅' if status.get('working') else '❌'}")
        st.markdown(f"**Category:** {company.get('category', 'N/A')}")
        st.markdown("---")
        st.markdown("### Actions")
        if st.button("➕ Add to CRM", use_container_width=True):
            if add_lead(company):
                st.success(f"Added {company['name']} to CRM")
            else:
                st.warning("Already in CRM")
        email_options = []
        if company.get('email'):
            email_options.append(company['email'])
        if company.get('possible_emails'):
            email_options.extend(company['possible_emails'][:3])
        if email_options:
            selected_email = st.selectbox("Select Email", email_options)
        else:
            selected_email = st.text_input("Email Address")
        if st.button("📧 Send Email", use_container_width=True):
            if selected_email:
                ai_rec = ai_recommend_action({"email_sent": False})
                email_body = get_personalized_email_body(company['name'], company.get('website_status'), ai_rec)
                subject = f"FREE IT Assessment for {company['name']}"
                success, msg = send_email(selected_email, subject, email_body)
                if success:
                    update_email_sent(company['name'], selected_email)
                    st.success(f"Email sent to {company['name']}")
                    st.rerun()
                else:
                    st.error(f"Failed: {msg}")
            else:
                st.warning("Enter email")
        if st.button("📄 Download Letter", use_container_width=True):
            letter = get_letter_content(company['name'], company.get('website_status'))
            st.download_button("Download", letter, f"letter_{company['name'].replace(' ', '_')}.txt", "text/plain")
        if st.button("← Back", use_container_width=True):
            st.session_state.current_page = 'search'
            st.rerun()

# ============ LEADS CRM ============
elif st.session_state.current_page == 'crm':
    st.markdown('<div class="section-header">👥 Leads CRM</div>', unsafe_allow_html=True)
    st.caption(f"Total Leads: {len(st.session_state.leads)}")
    st.markdown("---")
    if st.session_state.leads:
        filter_status = st.selectbox("Filter", ["All", "Email Sent", "No Email", "Responded", "Needs Follow-up", "Needs Call"])
        filtered = st.session_state.leads
        if filter_status == "Email Sent":
            filtered = [l for l in filtered if l.get('email_sent')]
        elif filter_status == "No Email":
            filtered = [l for l in filtered if not l.get('email_sent')]
        elif filter_status == "Responded":
            filtered = [l for l in filtered if l.get('email_responded')]
        elif filter_status == "Needs Follow-up":
            filtered = [l for l in filtered if l.get('email_sent') and not l.get('email_responded')]
        elif filter_status == "Needs Call":
            filtered = [l for l in filtered if l.get('email_sent') and not l.get('email_responded')]
        for lead in filtered:
            with st.expander(f"🏢 {lead['name']} - Score: {lead['lead_score']}/100"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**📍 Address:** {lead.get('address', 'N/A')}")
                    st.markdown(f"**📞 Phone:** {lead.get('phone', 'N/A')}")
                    website = lead.get('website', '')
                    if website:
                        st.markdown(f"**🌐 Website:** {website}")
                    else:
                        st.markdown(f"**🌐 Website:** Not found")
                with col2:
                    st.markdown(f"**📧 Email:** {lead.get('email', 'N/A')}")
                    st.markdown(f"**📅 Added:** {lead['created_at'][:10]}")
                    st.markdown(f"**Email Sent:** {'✅' if lead.get('email_sent') else '❌'}")
                    if lead.get('email_sent_date'):
                        st.markdown(f"**Sent:** {lead['email_sent_date'][:10]}")
                    st.markdown(f"**Responded:** {'✅' if lead.get('email_responded') else '❌'}")
                ai_action = ai_recommend_action(lead)
                st.info(f"🤖 {ai_action}")
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button(f"📧 Send Email", key=f"send_{lead['id']}"):
                        email = lead.get('email', '')
                        if not email and lead.get('possible_emails'):
                            email = lead['possible_emails'][0]
                        if email:
                            ai_rec = ai_recommend_action(lead)
                            email_body = get_personalized_email_body(lead['name'], lead.get('website_status'), ai_rec)
                            subject = f"IT Assessment for {lead['name']}"
                            success, msg = send_email(email, subject, email_body)
                            if success:
                                update_email_sent(lead['name'], email)
                                st.success(f"Email sent to {lead['name']}")
                                st.rerun()
                            else:
                                st.error(f"Failed: {msg}")
                        else:
                            st.warning("No email address")
                with col2:
                    if st.button(f"✅ Mark Responded", key=f"resp_{lead['id']}"):
                        update_email_responded(lead['name'])
                        st.success("Marked as responded")
                        st.rerun()
                with col3:
                    if st.button(f"📞 Call", key=f"call_{lead['id']}"):
                        st.session_state.call_queue.append({
                            "company": lead['name'], "phone": lead.get('phone', 'No phone'),
                            "script": CALL_SCRIPT.format(company_name=lead['name'], phone=lead.get('phone', 'No phone')),
                            "added_date": datetime.now().isoformat()
                        })
                        st.success("Added to call queue")
                with col4:
                    if st.button(f"🗑️ Delete", key=f"del_{lead['id']}"):
                        st.session_state.leads = [l for l in st.session_state.leads if l['id'] != lead['id']]
                        save_leads()
                        st.success(f"Deleted {lead['name']}")
                        st.rerun()
    else:
        st.info("No leads yet. Run a search to find companies.")

# ============ CALL QUEUE ============
elif st.session_state.current_page == 'call_queue':
    st.markdown('<div class="section-header">📞 Call Queue</div>', unsafe_allow_html=True)
    st.caption("Companies to call - Use the call script below")
    st.markdown("---")
    if st.session_state.call_queue:
        for idx, call in enumerate(st.session_state.call_queue):
            with st.expander(f"📞 {call['company']} - {call.get('phone', 'No phone')}"):
                st.markdown("### Call Script")
                st.code(call.get('script', 'No script'), language='markdown')
                col1, col2 = st.columns(2)
                with col1:
                    outcome = st.selectbox("Call Outcome", ["Interested", "Not Interested", "Call Back", "Wrong Number", "No Answer"], key=f"outcome_{idx}")
                    if st.button("Save Call Result", key=f"save_{idx}"):
                        for lead in st.session_state.leads:
                            if lead['name'] == call['company']:
                                lead['call_made'] = True
                                lead['call_notes'] = f"Outcome: {outcome} on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                                if outcome == "Interested" and lead.get('email'):
                                    lead['next_followup_date'] = (datetime.now() + timedelta(days=1)).isoformat()
                                save_leads()
                                st.success("Call result saved")
                                st.rerun()
                with col2:
                    if st.button("Remove from Queue", key=f"remove_{idx}"):
                        st.session_state.call_queue.pop(idx)
                        st.rerun()
    else:
        st.success("No pending calls")

# ============ VISIT QUEUE ============
elif st.session_state.current_page == 'visit_queue':
    st.markdown('<div class="section-header">🏢 Visit Queue</div>', unsafe_allow_html=True)
    st.caption("Companies to visit in person")
    st.markdown("---")
    if st.session_state.visit_queue:
        for idx, visit in enumerate(st.session_state.visit_queue):
            with st.expander(f"🏢 {visit['company']} - {visit.get('address', 'No address')}"):
                st.markdown(f"**Phone:** {visit.get('phone', 'N/A')}")
                st.markdown(f"**Added:** {visit.get('added_date', '')[:10]}")
                if st.button("Mark as Visited", key=f"visit_{idx}"):
                    st.session_state.visit_queue.pop(idx)
                    st.success("Marked as visited")
                    st.rerun()
    else:
        st.success("No pending visits")

# ============ EMAIL LOG ============
elif st.session_state.current_page == 'email_log':
    st.markdown('<div class="section-header">📧 Email Log</div>', unsafe_allow_html=True)
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

# ============ SETTINGS ============
elif st.session_state.current_page == 'settings':
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
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
    - Follow-up Sequence: 5 days
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
st.caption("2024 TechWokx IT Solutions | Professional IT Outreach | Email Tracking | Call Management")

import streamlit as st
import pandas as pd
import requests
import re
import json
from datetime import datetime, timedelta
import hashlib
import time

# Page config
st.set_page_config(
    page_title="TechWokx Enterprise Suite",
    page_icon="🔍",
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
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'email_log' not in st.session_state:
    st.session_state.email_log = []
if 'bid_history' not in st.session_state:
    st.session_state.bid_history = []
if 'research_cache' not in st.session_state:
    st.session_state.research_cache = {}

# Login credentials
USERS = {
    "hello@techwokx.online": {
        "password": "Gtech.5628!@#$",
        "role": "admin",
        "name": "TechWokx Admin"
    }
}

# User skills for freelance matching
USER_SKILLS = {
    "it_support": 90,
    "data_entry": 95,
    "excel": 95,
    "research": 85,
    "administrative": 85,
    "hotel_operations": 80,
    "pdf_handling": 90,
    "web_scraping": 75,
    "data_analysis": 80,
    "document_conversion": 88,
    "python": 75,
    "sql": 70,
    "automation": 80,
    "virtual_assistant": 85,
    "customer_service": 80
}

# ============ API KEYS FROM SECRETS ============
def get_api_keys():
    """Get API keys from secrets"""
    return {
        "serp_api": st.secrets.get("SERP_API_KEY", ""),
        "google_maps": st.secrets.get("GOOGLE_MAPS_API_KEY", ""),
        "openai": st.secrets.get("OPENAI_API_KEY", ""),
        "anthropic": st.secrets.get("ANTHROPIC_API_KEY", ""),
        "rapidapi": st.secrets.get("RAPIDAPI_KEY", "")
    }

# ============ REAL GOOGLE MAPS API RESEARCH ============

def search_google_maps(api_key, business_name, location="Ghana"):
    """Search Google Maps API for REAL business information"""
    if not api_key:
        return None
    
    try:
        # Step 1: Find Place ID
        find_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "key": api_key,
            "input": f"{business_name} {location}",
            "inputtype": "textquery",
            "fields": "place_id,name,formatted_address"
        }
        
        response = requests.get(find_place_url, params=params, timeout=10)
        data = response.json()
        
        if not data.get("candidates"):
            return None
        
        place_id = data["candidates"][0].get("place_id")
        business_name_real = data["candidates"][0].get("name")
        
        # Step 2: Get detailed place information
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "key": api_key,
            "place_id": place_id,
            "fields": "name,formatted_address,formatted_phone_number,website,rating,reviews,opening_hours,types,international_phone_number,url,user_ratings_total"
        }
        
        response = requests.get(details_url, params=params, timeout=10)
        details = response.json().get("result", {})
        
        return {
            "name": details.get("name", business_name),
            "address": details.get("formatted_address", ""),
            "phone": details.get("formatted_phone_number", details.get("international_phone_number", "")),
            "website": details.get("website", ""),
            "rating": details.get("rating", 0),
            "rating_count": details.get("user_ratings_total", 0),
            "types": details.get("types", []),
            "maps_url": details.get("url", ""),
            "place_id": place_id
        }
    except Exception as e:
        return None

def search_google_serp(api_key, business_name, location="Ghana"):
    """Search Google SERP for business information"""
    if not api_key:
        return None
    
    try:
        url = "https://serpapi.com/search"
        params = {
            "api_key": api_key,
            "q": f"{business_name} {location}",
            "location": location,
            "engine": "google"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        result = {
            "description": "",
            "social_links": []
        }
        
        # Get knowledge graph
        if "knowledge_graph" in data:
            kg = data["knowledge_graph"]
            result["description"] = kg.get("description", "")
            
            if "profile" in kg:
                for profile in kg.get("profile", []):
                    if isinstance(profile, dict) and "link" in profile:
                        result["social_links"].append(profile["link"])
        
        # Get organic results for description
        if not result["description"] and "organic_results" in data:
            for org in data["organic_results"][:2]:
                if org.get("snippet"):
                    result["description"] = org.get("snippet")
                    break
        
        return result
    except Exception as e:
        return None

def check_website_status(url):
    """Check if website is accessible"""
    if not url:
        return {"reachable": False, "error": "No website"}
    
    try:
        if not url.startswith("http"):
            url = "https://" + url
        
        response = requests.get(url, timeout=10, verify=True)
        return {
            "reachable": response.status_code == 200,
            "status_code": response.status_code,
            "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
        }
    except Exception as e:
        return {"reachable": False, "error": str(e)[:50]}

def analyze_with_openai(api_key, company_data):
    """Analyze company using OpenAI"""
    if not api_key:
        return None
    
    try:
        prompt = f"""Analyze this company in Ghana:

Company: {company_data.get('name')}
Website: {company_data.get('website', 'N/A')}
Address: {company_data.get('address', 'N/A')}
Google Rating: {company_data.get('rating', 'N/A')}/5
Website Status: {'Working' if company_data.get('website_status', {}).get('reachable') else 'Down'}

Provide:
1. Industry
2. Size estimate
3. Main challenges
4. Recommended services

Keep response under 200 words."""

        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return None
    except Exception as e:
        return None

def deep_research_company(company_name):
    """Perform deep research using REAL Google Maps API"""
    
    api_keys = get_api_keys()
    
    result = {
        "name": company_name,
        "website": None,
        "email": None,
        "phone": None,
        "address": None,
        "description": None,
        "rating": None,
        "rating_count": None,
        "maps_url": None,
        "website_status": None,
        "ai_insights": None,
        "lead_score": 0,
        "recommendations": [],
        "sources": []
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Google Maps API - REAL DATA
    status_text.text("📍 Fetching REAL business data from Google Maps...")
    if api_keys["google_maps"]:
        maps_data = search_google_maps(api_keys["google_maps"], company_name)
        if maps_data:
            result["name"] = maps_data.get("name", result["name"])
            result["address"] = maps_data.get("address")
            result["phone"] = maps_data.get("phone")
            result["website"] = maps_data.get("website")
            result["rating"] = maps_data.get("rating")
            result["rating_count"] = maps_data.get("rating_count")
            result["maps_url"] = maps_data.get("maps_url")
            result["sources"].append("Google Maps API")
            status_text.text(f"✅ Found: {result['name']}")
    progress_bar.progress(0.33)
    
    # Step 2: Check website status
    if result["website"]:
        status_text.text("🌐 Checking website status...")
        result["website_status"] = check_website_status(result["website"])
    progress_bar.progress(0.66)
    
    # Step 3: SERP API for description
    status_text.text("🔍 Searching Google for business info...")
    if api_keys["serp_api"]:
        serp_data = search_google_serp(api_keys["serp_api"], company_name)
        if serp_data:
            result["description"] = serp_data.get("description")
            if serp_data.get("description"):
                result["sources"].append("Google Search")
    progress_bar.progress(0.85)
    
    # Step 4: AI Analysis
    status_text.text("🧠 Generating AI insights...")
    if api_keys["openai"]:
        ai_insights = analyze_with_openai(api_keys["openai"], result)
        if ai_insights:
            result["ai_insights"] = ai_insights
            result["sources"].append("OpenAI")
    progress_bar.progress(0.95)
    
    # Calculate lead score
    score = 0
    if result["website"]:
        score += 20
        if result["website_status"] and result["website_status"]["reachable"]:
            score += 15
    if result["address"]:
        score += 10
    if result["phone"]:
        score += 10
    if result["rating"]:
        score += min(int(result["rating"] * 5), 20)
    if result["description"]:
        score += 10
    if result["ai_insights"]:
        score += 5
    result["lead_score"] = min(score, 100)
    
    # Recommendations based on REAL data
    recs = []
    if not result["website"]:
        recs.append("🌐 No website found - Professional website needed")
    elif result["website_status"] and not result["website_status"]["reachable"]:
        recs.append("🔧 Website is DOWN - Emergency IT support required")
    if not result["phone"]:
        recs.append("📞 No phone number on Google Maps - Claim your business listing")
    if not result["address"]:
        recs.append("📍 Address missing - Update Google Business Profile")
    if result["rating"] and result["rating"] < 4.0:
        recs.append(f"⭐ Low Google rating ({result['rating']}/5) - Reputation management needed")
    if len(recs) < 3:
        recs.append("📊 Schedule free IT consultation")
    result["recommendations"] = recs[:5]
    
    progress_bar.progress(1.0)
    status_text.text("✅ Research complete!")
    time.sleep(0.5)
    status_text.empty()
    progress_bar.empty()
    
    return result

# ============ FREELANCE JOB FETCHING (REAL API) ============

def fetch_real_freelancer_jobs(rapidapi_key, keywords=None):
    """Fetch REAL jobs from Freelancer using RapidAPI"""
    if not rapidapi_key:
        return []
    
    try:
        url = "https://freelancer-freelancer-v1.p.rapidapi.com/projects/0.1/projects/active/"
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "freelancer-freelancer-v1.p.rapidapi.com"
        }
        params = {"limit": 20, "compact": True}
        if keywords:
            params["query"] = keywords
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            projects = data.get("result", {}).get("projects", [])
            
            jobs = []
            for project in projects:
                jobs.append({
                    "id": str(project.get("id")),
                    "title": project.get("title", "Untitled"),
                    "description": project.get("description", "")[:300],
                    "platform": "Freelancer",
                    "budget_min": project.get("budget", {}).get("minimum", 10),
                    "budget_max": project.get("budget", {}).get("maximum", 50),
                    "skills_required": [s.get("name", "").lower() for s in project.get("skills", [])],
                    "access_type": "unlock_required" if project.get("prepaid") else "open",
                    "unlock_cost": "$20 required" if project.get("prepaid") else "Free",
                    "url": f"https://www.freelancer.com/projects/{project.get('seo_url', '')}",
                    "bid_count": project.get("bid_stats", {}).get("bid_count", 0)
                })
            return jobs
        return []
    except Exception as e:
        return []

def fetch_real_upwork_jobs(rapidapi_key, keywords=None):
    """Fetch REAL jobs from Upwork using RapidAPI"""
    if not rapidapi_key:
        return []
    
    try:
        url = "https://upwork7.p.rapidapi.com/api/client/projects/search"
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "upwork7.p.rapidapi.com"
        }
        params = {"page": 1, "per_page": 20}
        if keywords:
            params["q"] = keywords
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            projects = data.get("projects", [])
            
            jobs = []
            for project in projects:
                jobs.append({
                    "id": str(project.get("id")),
                    "title": project.get("title", "Untitled"),
                    "description": project.get("description", "")[:300],
                    "platform": "Upwork",
                    "budget_min": project.get("budget", {}).get("min", 10),
                    "budget_max": project.get("budget", {}).get("max", 50),
                    "skills_required": project.get("skills", []),
                    "access_type": "connect_required",
                    "unlock_cost": "8-16 connects",
                    "url": project.get("url", "#"),
                    "bid_count": project.get("proposals_count", 0)
                })
            return jobs
        return []
    except Exception as e:
        return []

# ============ LEAD MANAGEMENT ============

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
    return lead

def calculate_match_score(job):
    """Calculate match score based on user skills"""
    total_score = 0
    for skill in job.get("skills_required", []):
        skill_lower = skill.lower().replace(" ", "_")
        if skill_lower in USER_SKILLS:
            total_score += USER_SKILLS[skill_lower]
    if job.get("skills_required"):
        match = (total_score / (len(job["skills_required"]) * 100)) * 100
    else:
        match = 65
    return min(int(match), 100)

def generate_proposal(job, match_score):
    return f"""Dear Client,

I am very interested in your project: {job['title']}

My relevant skills include:
• Data Entry and Excel (95% proficiency)
• Fast turnaround (24-48 hours)
• 100% accuracy guarantee

Budget: ${job['budget_min']} - ${job['budget_max']}

I am available to start immediately.

Best regards,
George Jabley
TechWokx Freelancer"""

# ============ CSS ============
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fbbf24 !important; }
[data-testid="stSidebar"] .stButton button { background: rgba(251, 191, 36, 0.15); color: #fbbf24 !important; width: 100%; margin: 2px 0; }
.welcome-card { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; color: white; }
.metric-card { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
.metric-label { color: #64748b; font-size: 0.8rem; }
.data-card { background: white; border-radius: 12px; padding: 1.2rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
.section-header { color: #0f172a; font-size: 1.2rem; font-weight: 600; border-left: 3px solid #667eea; padding-left: 1rem; margin: 1.5rem 0 1rem 0; }
.custom-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
.stButton > button { background: linear-gradient(135deg, #667eea, #764ba2); color: white !important; font-weight: 600; border: none; border-radius: 8px; }
.status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
.status-hot { background: #dc2626; color: white; }
.status-warm { background: #f97316; color: white; }
.status-cold { background: #64748b; color: white; }
.api-status { font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; }
.api-active { background: #10b981; color: white; }
.api-inactive { background: #ef4444; color: white; }
</style>
""", unsafe_allow_html=True)

# ============ LOGIN PAGE ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 450px; margin: 100px auto; padding: 2rem; background: white; border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); text-align: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
        <div style="font-size: 1.875rem; font-weight: 700; color: #1e293b;">TechWokx</div>
        <div style="color: #64748b; margin-bottom: 2rem;">Lead Intelligence + Freelance Agent</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Email", placeholder="hello@techwokx.online")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user = USERS[username]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    st.markdown("""
        <div style="background: #f1f5f9; padding: 1rem; border-radius: 12px; margin-top: 1.5rem;">
            <div style="font-size: 0.75rem; color: #64748b;">🔐 Demo Access</div>
            <div style="font-size: 0.8rem; font-family: monospace;">hello@techwokx.online / Gtech.5628!@#$</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### 🔍 TechWokx")
    st.markdown("#### Welcome, " + st.session_state.user['name'])
    st.markdown("---")
    
    nav_items = [
        ("🏠 Dashboard", "dashboard"),
        ("---", "divider0"),
        ("📋 LEAD MANAGEMENT", "header1"),
        ("🔍 Company Research", "company_research"),
        ("📥 Import Leads", "import_leads"),
        ("👥 Lead CRM", "crm"),
        ("---", "divider1"),
        ("🤖 FREELANCE", "header2"),
        ("🎯 Find Jobs", "find_jobs"),
        ("📋 My Bids", "bid_history"),
        ("---", "divider2"),
        ("🛡️ AUDITS", "header3"),
        ("🌐 DNS Audit", "dns_audit"),
        ("🔒 Website Audit", "website_audit"),
        ("📧 Email Security", "email_security"),
        ("---", "divider3"),
        ("⚙️ Settings", "settings"),
        ("🚪 Logout", "logout")
    ]
    
    for label, key in nav_items:
        if label == "---":
            st.markdown("---")
        elif label.startswith("📋") or label.startswith("🤖") or label.startswith("🛡️"):
            st.markdown("<small style='color:#94a3b8'>" + label + "</small>", unsafe_allow_html=True)
        elif st.button(label, key=key, use_container_width=True):
            if key == "logout":
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()
            else:
                st.session_state.page = key
                st.rerun()
    
    st.markdown("---")
    
    # API Status Display
    api_keys = get_api_keys()
    st.markdown("### API Status")
    maps_status = "✅" if api_keys["google_maps"] else "❌"
    serp_status = "✅" if api_keys["serp_api"] else "❌"
    ai_status = "✅" if api_keys["openai"] or api_keys["anthropic"] else "❌"
    rapid_status = "✅" if api_keys["rapidapi"] else "❌"
    st.markdown(f"📍 Maps: {maps_status}")
    st.markdown(f"🔍 SERP: {serp_status}")
    st.markdown(f"🧠 AI: {ai_status}")
    st.markdown(f"⚡ Jobs: {rapid_status}")
    
    st.markdown("---")
    st.markdown(f"📊 Leads: {len(st.session_state.leads)}")
    st.markdown(f"🎯 Bids: {len(st.session_state.bid_history)}")

# ============ DASHBOARD ============
if st.session_state.page == 'dashboard':
    api_keys = get_api_keys()
    
    st.markdown("""
    <div class="welcome-card">
        <h2>🤖 TechWokx Enterprise Suite</h2>
        <p>AI-powered Company Research | Lead Intelligence | Freelance Job Matching</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.leads)}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        hot = sum(1 for l in st.session_state.leads if l.get("score", 0) >= 80)
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        active_apis = sum([1 for k in api_keys.values() if k])
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{active_apis}/4</div><div class='metric-label'>APIs Active</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>✅</div><div class='metric-label'>Ready</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Recent Leads</div>', unsafe_allow_html=True)
        if st.session_state.leads:
            for lead in st.session_state.leads[-5:]:
                status_class = "status-hot" if lead['status'] == "Hot" else "status-warm" if lead['status'] == "Warm" else "status-cold"
                st.markdown(f"<div class='data-card'><strong>{lead['name']}</strong> - Score: {lead['score']}/100 <span class='status-badge {status_class}'>{lead['status']}</span><br><small>{lead['created_at'].strftime('%Y-%m-%d')}</small></div>", unsafe_allow_html=True)
        else:
            st.info("No leads yet. Research companies to get started.")
    
    with col2:
        st.markdown('<div class="section-header">🚀 Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍 Research Company", use_container_width=True):
            st.session_state.page = 'company_research'
            st.rerun()
        if st.button("🎯 Find Freelance Jobs", use_container_width=True):
            st.session_state.page = 'find_jobs'
            st.rerun()
        if st.button("⚙️ Configure APIs", use_container_width=True):
            st.session_state.page = 'settings'
            st.rerun()

# ============ SETTINGS PAGE WITH API CONFIG ============
elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ API Settings</div>', unsafe_allow_html=True)
    st.caption("Configure your API keys for real data fetching")
    st.markdown("---")
    
    st.markdown("""
    ### Required APIs
    
    | API | Purpose | Get Key |
    |-----|---------|---------|
    | **Google Maps API** | Real business addresses, phone numbers, ratings | [Get Key](https://console.cloud.google.com/) |
    | **SERP API** | Google search results, business descriptions | [Get Key](https://serpapi.com/) |
    | **OpenAI API** | AI-powered business insights | [Get Key](https://platform.openai.com/) |
    | **RapidAPI** | Freelancer/Upwork job fetching | [Get Key](https://rapidapi.com/) |
    """)
    
    st.markdown("---")
    st.markdown("### Current Configuration")
    
    api_keys = get_api_keys()
    
    col1, col2 = st.columns(2)
    with col1:
        maps_status = "✅ Configured" if api_keys["google_maps"] else "❌ Missing"
        st.markdown(f"**Google Maps API:** {maps_status}")
        serp_status = "✅ Configured" if api_keys["serp_api"] else "❌ Missing"
        st.markdown(f"**SERP API:** {serp_status}")
    with col2:
        openai_status = "✅ Configured" if api_keys["openai"] else "❌ Missing"
        st.markdown(f"**OpenAI API:** {openai_status}")
        rapid_status = "✅ Configured" if api_keys["rapidapi"] else "❌ Missing"
        st.markdown(f"**RapidAPI:** {rapid_status}")
    
    st.markdown("---")
    st.markdown("### How to Add API Keys")
    
    st.code("""
    # .streamlit/secrets.toml
    SERP_API_KEY = "your_serp_api_key"
    GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
    OPENAI_API_KEY = "your_openai_api_key"
    ANTHROPIC_API_KEY = "your_anthropic_api_key"
    RAPIDAPI_KEY = "your_rapidapi_key"
    """, language="toml")
    
    st.info("After adding keys to secrets.toml, restart the app for changes to take effect.")
    
    # Test buttons
    st.markdown("---")
    st.markdown("### Test API Connections")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Test Google Maps API"):
            if api_keys["google_maps"]:
                test_result = search_google_maps(api_keys["google_maps"], "MTN Ghana")
                if test_result:
                    st.success(f"✅ API Working! Found: {test_result.get('name')}")
                else:
                    st.error("❌ API returned no results. Check your key and quota.")
            else:
                st.error("❌ API key not configured")
    
    with col2:
        if st.button("Test SERP API"):
            if api_keys["serp_api"]:
                test_result = search_google_serp(api_keys["serp_api"], "MTN Ghana")
                if test_result:
                    st.success("✅ API Working!")
                else:
                    st.error("❌ API returned no results")
            else:
                st.error("❌ API key not configured")

# ============ COMPANY RESEARCH PAGE ============
elif st.session_state.page == 'company_research':
    st.markdown('<div class="section-header">🔍 Deep Company Research</div>', unsafe_allow_html=True)
    st.caption("Powered by Google Maps API + SERP API + OpenAI | Real-time business data from Google")
    st.markdown("---")
    
    api_keys = get_api_keys()
    
    # API Status indicators
    col1, col2, col3 = st.columns(3)
    with col1:
        if api_keys["google_maps"]:
            st.success("✅ Google Maps API Ready")
        else:
            st.error("❌ Google Maps API Missing - Add to secrets.toml")
    with col2:
        if api_keys["serp_api"]:
            st.success("✅ SERP API Ready")
        else:
            st.error("❌ SERP API Missing")
    with col3:
        if api_keys["openai"]:
            st.success("✅ OpenAI API Ready")
        else:
            st.warning("⚠️ OpenAI API Missing - AI insights disabled")
    
    st.markdown("---")
    
    company_name = st.text_input("Company Name", placeholder="e.g. Courmack Ghana, MTN Ghana, GCB Bank")
    
    if st.button("🔍 Deep Research", type="primary"):
        if company_name:
            if not api_keys["google_maps"]:
                st.warning("⚠️ Google Maps API key is required for real business data. Add to secrets.toml")
            
            with st.spinner(f"Researching {company_name} using Google Maps API..."):
                result = deep_research_company(company_name)
                
                # Company Information
                st.markdown(f"""
                <div class="data-card">
                    <h4>🏢 Company Information (from Google Maps)</h4>
                    <table style="width:100%">
                        <tr><td><strong>Name:</strong></td><td>{result['name']}</td></tr>
                        <tr><td><strong>Website:</strong></td><td>{result['website'] or 'Not found'}</td></tr>
                        <tr><td><strong>Address:</strong></td><td>{result['address'] or 'Not found'}</td></tr>
                        <tr><td><strong>Phone:</strong></td><td>{result['phone'] or 'Not found'}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
                # Google Rating
                if result['rating']:
                    stars = "⭐" * int(result['rating'])
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>⭐ Google Maps Rating</h4>
                        <p><strong>Rating:</strong> {result['rating']}/5 {stars} ({result['rating_count']} reviews)</p>
                        <p><a href="{result['maps_url']}" target="_blank">View on Google Maps →</a></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Website Status
                if result['website_status']:
                    status_icon = "✅" if result['website_status']['reachable'] else "❌"
                    status_text_result = "Online" if result['website_status']['reachable'] else "Down/Unreachable"
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>🌐 Website Status</h4>
                        <p><strong>Status:</strong> {status_icon} {status_text_result}</p>
                        <p><strong>Details:</strong> {result['website_status'].get('error', 'Working normally')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Description
                if result['description']:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>📝 Business Description</h4>
                        <p>{result['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # AI Insights
                if result['ai_insights']:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>🧠 AI-Powered Insights</h4>
                        <p>{result['ai_insights']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Lead Score
                score_color = "#22c55e" if result['lead_score'] >= 70 else "#f97316" if result['lead_score'] >= 50 else "#ef4444"
                st.markdown(f"""
                <div class="data-card" style="text-align: center;">
                    <h4>🎯 Lead Score</h4>
                    <p style="font-size: 3rem; font-weight: 700; color: {score_color};">{result['lead_score']}/100</p>
                    <p><strong>Data Sources:</strong> {', '.join(result['sources']) if result['sources'] else 'None'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Recommendations
                st.markdown(f"""
                <div class="data-card">
                    <h4>🚀 Recommendations</h4>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in result['recommendations']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Add to CRM
                if st.button("➕ Add to CRM", use_container_width=True):
                    add_lead(
                        result['name'], 
                        "", 
                        result['phone'] or "", 
                        result['lead_score'], 
                        "Google Maps Research"
                    )
                    st.success(f"✅ {result['name']} added to CRM!")
        else:
            st.warning("Please enter a company name")

# ============ FIND JOBS PAGE ============
elif st.session_state.page == 'find_jobs':
    st.markdown('<div class="section-header">🎯 Find Freelance Jobs</div>', unsafe_allow_html=True)
    st.caption("REAL jobs from Freelancer and Upwork via RapidAPI")
    st.markdown("---")
    
    api_keys = get_api_keys()
    
    if not api_keys["rapidapi"]:
        st.error("❌ RapidAPI key missing! Add RAPIDAPI_KEY to secrets.toml to fetch real jobs.")
        st.info("Go to Settings page to configure your API keys.")
        
        if st.button("Go to Settings"):
            st.session_state.page = 'settings'
            st.rerun()
    else:
        keywords = st.text_input("Keywords", placeholder="data entry, excel, virtual assistant")
        
        col1, col2 = st.columns(2)
        with col1:
            platform = st.selectbox("Platform", ["Both", "Freelancer", "Upwork"])
        with col2:
            if st.button("🔍 Fetch Real Jobs", type="primary"):
                with st.spinner("Fetching REAL jobs from Freelancer/Upwork via RapidAPI..."):
                    all_jobs = []
                    
                    if platform in ["Both", "Freelancer"]:
                        freelancer_jobs = fetch_real_freelancer_jobs(api_keys["rapidapi"], keywords)
                        all_jobs.extend(freelancer_jobs)
                        st.info(f"Found {len(freelancer_jobs)} jobs from Freelancer")
                    
                    if platform in ["Both", "Upwork"]:
                        upwork_jobs = fetch_real_upwork_jobs(api_keys["rapidapi"], keywords)
                        all_jobs.extend(upwork_jobs)
                        st.info(f"Found {len(upwork_jobs)} jobs from Upwork")
                    
                    if all_jobs:
                        st.session_state.jobs = all_jobs
                        st.success(f"✅ Fetched {len(all_jobs)} real jobs!")
                    else:
                        st.warning("No jobs found. Try different keywords.")
        
        display_jobs = st.session_state.jobs if st.session_state.jobs else []
        
        if display_jobs:
            st.markdown(f"### Found {len(display_jobs)} Jobs")
            
            for job in display_jobs[:15]:
                match_score = calculate_match_score(job)
                
                with st.expander(f"[{job['platform']}] {job['title']} - Match: {match_score}%"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Description:** {job['description'][:200]}...")
                        st.markdown(f"**Budget:** ${job['budget_min']} - ${job['budget_max']}")
                        st.markdown(f"**Skills:** {', '.join(job.get('skills_required', ['General'])[:5])}")
                        st.markdown(f"**Bids:** {job.get('bid_count', 'N/A')}")
                    with col2:
                        st.markdown(f"**Access:** {job['access_type']}")
                        st.markdown(f"**Cost:** {job['unlock_cost']}")
                        if job.get('url') and job['url'] != "#":
                            st.markdown(f"[View Job]({job['url']})")
                    
                    if match_score >= 70:
                        st.markdown("---")
                        proposal = generate_proposal(job, match_score)
                        st.text_area("Proposal", proposal, height=150)
                        
                        if st.button(f"📤 Save Bid", key=f"bid_{job['id']}"):
                            st.session_state.bid_history.append({
                                "job_title": job['title'],
                                "platform": job['platform'],
                                "bid_amount": (job['budget_min'] + job['budget_max']) // 2,
                                "date": datetime.now(),
                                "status": "Draft"
                            })
                            st.success(f"Bid saved for {job['title']}!")
        else:
            st.info("Click 'Fetch Real Jobs' to see opportunities from Freelancer and Upwork")

# ============ OTHER PAGES ============
elif st.session_state.page == 'import_leads':
    st.markdown('<div class="section-header">📥 Import Leads</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose CSV/Excel file", type=['csv', 'xlsx'])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.dataframe(df.head())
            if st.button("Import"):
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
        except Exception as e:
            st.error(f"Error: {e}")

elif st.session_state.page == 'crm':
    st.markdown('<div class="section-header">👥 Lead CRM</div>', unsafe_allow_html=True)
    if st.session_state.leads:
        for lead in st.session_state.leads[-20:]:
            with st.expander(f"{lead['name']} - Score: {lead['score']}/100"):
                st.write(f"Email: {lead.get('email', 'N/A')}")
                st.write(f"Phone: {lead.get('phone', 'N/A')}")
                st.write(f"Status: {lead['status']}")
                st.write(f"Source: {lead['source']}")
                st.write(f"Date: {lead['created_at'].strftime('%Y-%m-%d %H:%M')}")
    else:
        st.info("No leads yet")

elif st.session_state.page == 'bid_history':
    st.markdown('<div class="section-header">📋 My Bids</div>', unsafe_allow_html=True)
    if st.session_state.bid_history:
        for bid in reversed(st.session_state.bid_history):
            st.markdown(f"<div class='data-card'><strong>{bid['job_title']}</strong><br>Bid: ${bid['bid_amount']}<br>Date: {bid['date'].strftime('%Y-%m-%d %H:%M')}<br>Status: {bid['status']}</div>", unsafe_allow_html=True)
    else:
        st.info("No bids yet")

elif st.session_state.page == 'dns_audit':
    st.markdown('<div class="section-header">🌐 DNS Audit</div>', unsafe_allow_html=True)
    domain = st.text_input("Domain")
    if st.button("Run DNS Audit"):
        st.info(f"DNS Audit for {domain} - Feature coming soon")

elif st.session_state.page == 'website_audit':
    st.markdown('<div class="section-header">🔒 Website Audit</div>', unsafe_allow_html=True)
    url = st.text_input("Website URL")
    if st.button("Run Website Audit"):
        st.info(f"Website Audit for {url} - Feature coming soon")

elif st.session_state.page == 'email_security':
    st.markdown('<div class="section-header">📧 Email Security</div>', unsafe_allow_html=True)
    domain = st.text_input("Domain")
    if st.button("Run Email Security Check"):
        st.info(f"Email Security for {domain} - Feature coming soon")

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Enterprise Suite | Real Google Maps API | Real Freelancer/Upwork Jobs")

import streamlit as st
import pandas as pd
import os
import socket
import platform
import re
import requests
import feedparser
from datetime import datetime, timedelta
import json
import hashlib

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
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {
        'freelancer': '',
        'upwork': '',
        'pph': '',
        'resend': ''
    }

# Login credentials
USERS = {
    "hello@techwokx.online": {
        "password": "Gtech.5628!@#$",
        "role": "admin",
        "name": "TechWokx Admin"
    }
}

# User skills profile
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
    "automation": 80
}

# ============ API INTEGRATIONS ============

def fetch_freelancer_jobs(api_key, keywords=None):
    """Fetch real jobs from Freelancer.com API"""
    if not api_key:
        return []
    
    try:
        # Freelancer API endpoint
        url = "https://www.freelancer.com/api/projects/0.1/projects/active/"
        headers = {
            "Freelancer-OAuth-V1": api_key,
            "Content-Type": "application/json"
        }
        params = {
            "limit": 25,
            "compact": True
        }
        
        if keywords:
            params["query"] = " ".join(keywords)
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for project in data.get("result", {}).get("projects", []):
                # Calculate budget
                budget_min = project.get("budget", {}).get("minimum", 0)
                budget_max = project.get("budget", {}).get("maximum", 0)
                
                if budget_min == 0 and budget_max == 0:
                    # Try to get from bid stats
                    bid_stats = project.get("bid_stats", {})
                    budget_min = bid_stats.get("minimum_bid", 0)
                    budget_max = bid_stats.get("maximum_bid", 0)
                
                jobs.append({
                    "id": str(project.get("id")),
                    "title": project.get("title", "Untitled"),
                    "description": project.get("description", "")[:500],
                    "platform": "Freelancer",
                    "budget_min": budget_min,
                    "budget_max": budget_max,
                    "skills_required": [s.get("name", "").lower() for s in project.get("skills", [])],
                    "access_type": "unlock_required" if project.get("seo_url") and "unlock" in str(project.get("seo_url", "")) else "open",
                    "unlock_cost": "$20 balance required" if project.get("prepaid") else "Free to bid",
                    "posted_date": datetime.fromtimestamp(project.get("submitdate", 0)) if project.get("submitdate") else datetime.now(),
                    "client_rating": project.get("user", {}).get("rating", 0) / 10 if project.get("user", {}).get("rating") else 0,
                    "competition_level": "High" if project.get("bid_stats", {}).get("bid_count", 0) > 20 else "Medium" if project.get("bid_stats", {}).get("bid_count", 0) > 10 else "Low",
                    "bid_count": project.get("bid_stats", {}).get("bid_count", 0),
                    "url": f"https://www.freelancer.com/projects/{project.get('seo_url', '')}" if project.get('seo_url') else "#"
                })
            
            return jobs
        else:
            st.warning(f"Freelancer API error: {response.status_code}")
            return []
            
    except Exception as e:
        st.warning(f"Freelancer API connection error: {str(e)[:100]}")
        return []

def fetch_upwork_jobs(api_key=None, keywords=None):
    """Fetch jobs from Upwork RSS feed"""
    try:
        # Upwork RSS feeds are public
        base_url = "https://www.upwork.com/ab/feed/jobs/rss"
        
        # Build search query
        if keywords:
            query = "+".join(keywords)
            url = f"{base_url}?q={query}"
        else:
            url = base_url
        
        feed = feedparser.parse(url)
        jobs = []
        
        for entry in feed.entries[:25]:
            # Extract budget from description
            description = entry.get("summary", "")
            budget_match = re.search(r'\$(\d+)(?:\s*-\s*\$(\d+))?', description)
            
            if budget_match:
                budget_min = int(budget_match.group(1))
                budget_max = int(budget_match.group(2)) if budget_match.group(2) else budget_min
            else:
                budget_min = 0
                budget_max = 0
            
            jobs.append({
                "id": hashlib.md5(entry.get("link", "").encode()).hexdigest(),
                "title": entry.get("title", "Untitled"),
                "description": description[:500],
                "platform": "Upwork",
                "budget_min": budget_min,
                "budget_max": budget_max,
                "skills_required": [],
                "access_type": "connect_required",
                "unlock_cost": "8-16 connects",
                "posted_date": datetime(*entry.get("published_parsed", (0,0,0,0,0,0))[:6]) if entry.get("published_parsed") else datetime.now(),
                "client_rating": 0,
                "competition_level": "Medium",
                "bid_count": 0,
                "url": entry.get("link", "#")
            })
        
        return jobs
    except Exception as e:
        st.warning(f"Upwork feed error: {str(e)[:100]}")
        return []

def fetch_peopleperhour_jobs(api_key=None, keywords=None):
    """Fetch jobs from PeoplePerHour (requires API key)"""
    if not api_key:
        return []
    
    try:
        url = "https://api-peopleperhour.com/v1/projects"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"limit": 25, "status": "open"}
        
        if keywords:
            params["keywords"] = ",".join(keywords)
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for project in data.get("projects", []):
                jobs.append({
                    "id": str(project.get("id")),
                    "title": project.get("title", "Untitled"),
                    "description": project.get("description", "")[:500],
                    "platform": "PeoplePerHour",
                    "budget_min": project.get("budget", {}).get("min", 0),
                    "budget_max": project.get("budget", {}).get("max", 0),
                    "skills_required": [s.lower() for s in project.get("skills", [])],
                    "access_type": "open",
                    "unlock_cost": "Free",
                    "posted_date": datetime.fromisoformat(project.get("created_at", "")) if project.get("created_at") else datetime.now(),
                    "client_rating": project.get("client", {}).get("rating", 0),
                    "competition_level": "Medium",
                    "bid_count": project.get("bid_count", 0),
                    "url": f"https://www.peopleperhour.com/project/{project.get('slug', '')}"
                })
            
            return jobs
        else:
            return []
            
    except Exception as e:
        st.warning(f"PeoplePerHour API error: {str(e)[:100]}")
        return []

def fetch_freelancer_projects_alternative(keywords=None):
    """Alternative: Scrape Freelancer public listings"""
    try:
        url = "https://www.freelancer.com/jobs/"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        if keywords:
            url += "?keywords=" + "+".join(keywords)
        
        response = requests.get(url, headers=headers, timeout=15)
        
        # For demo, return sample data if scraping fails
        # In production, parse HTML with BeautifulSoup
        return []
        
    except Exception as e:
        return []

def fetch_all_jobs():
    """Fetch jobs from all configured platforms"""
    all_jobs = []
    status_placeholder = st.empty()
    
    # Fetch from Freelancer
    if st.session_state.api_keys.get('freelancer'):
        status_placeholder.text("Fetching from Freelancer...")
        freelancer_jobs = fetch_freelancer_jobs(st.session_state.api_keys['freelancer'])
        all_jobs.extend(freelancer_jobs)
        status_placeholder.text(f"Found {len(freelancer_jobs)} jobs from Freelancer")
    
    # Fetch from Upwork (always available - RSS)
    status_placeholder.text("Fetching from Upwork...")
    upwork_jobs = fetch_upwork_jobs()
    all_jobs.extend(upwork_jobs)
    status_placeholder.text(f"Found {len(upwork_jobs)} jobs from Upwork")
    
    # Fetch from PeoplePerHour
    if st.session_state.api_keys.get('pph'):
        status_placeholder.text("Fetching from PeoplePerHour...")
        pph_jobs = fetch_peopleperhour_jobs(st.session_state.api_keys['pph'])
        all_jobs.extend(pph_jobs)
        status_placeholder.text(f"Found {len(pph_jobs)} jobs from PeoplePerHour")
    
    status_placeholder.empty()
    return all_jobs

# ============ JOB SCORING FUNCTIONS ============

def calculate_match_score(job):
    """Calculate match score based on user skills"""
    total_score = 0
    matched_skills = []
    
    for skill in job.get("skills_required", []):
        skill_lower = skill.lower().replace(" ", "_")
        if skill_lower in USER_SKILLS:
            total_score += USER_SKILLS[skill_lower]
            matched_skills.append(skill)
    
    if job.get("skills_required"):
        max_possible = len(job["skills_required"]) * 100
        if max_possible > 0:
            match_percentage = (total_score / max_possible) * 100
        else:
            match_percentage = 50
    else:
        # If no skills listed, estimate from title
        title_lower = job.get("title", "").lower()
        if "excel" in title_lower or "data" in title_lower:
            match_percentage = 85
        elif "research" in title_lower:
            match_percentage = 80
        else:
            match_percentage = 60
    
    return round(min(match_percentage, 100)), matched_skills

def calculate_roi(job, match_score):
    """Calculate ROI score for bidding decision"""
    avg_budget = (job.get("budget_min", 0) + job.get("budget_max", 0)) / 2
    
    # Calculate competition factor
    comp_map = {"Low": 0.7, "Medium": 0.5, "High": 0.3, "Very High": 0.2}
    comp_factor = comp_map.get(job.get("competition_level", "Medium"), 0.5)
    
    # Calculate win probability
    win_probability = (match_score / 100) * comp_factor * 0.8
    
    # Calculate expected value
    expected_value = avg_budget * win_probability
    
    # Calculate cost
    unlock_text = job.get("unlock_cost", "").lower()
    if "connect" in unlock_text:
        connects = int(re.search(r'\d+', unlock_text).group(0)) if re.search(r'\d+', unlock_text) else 8
        cost = connects * 0.15  # $0.15 per connect
    elif "$" in unlock_text:
        cost = 20  # $20 unlock fee
    else:
        cost = 0
    
    # ROI score (0-100)
    if cost > 0:
        roi_score = min(100, (expected_value / cost) * 20)
    else:
        roi_score = min(100, expected_value / 10)
    
    return round(roi_score, 1), win_probability, expected_value, cost

def generate_proposal(job, match_score):
    """Generate personalized proposal"""
    
    if "PDF" in job["title"] or "Excel" in job["title"]:
        return f"""Hello,

I can accurately transfer the tables from your PDF documents into Excel while preserving the original structure, headers, rows, columns, symbols, and formatting.

My approach includes:
• Extracting data using professional PDF tools and Excel
• Verifying every row and column for accuracy
• Maintaining the original table layout
• Delivering a clean and organized .xlsx file

I have {USER_SKILLS.get('data_entry', 85)}% proficiency in data entry and Excel, with extensive experience in document conversion.

Please share the number of PDF files and pages involved so I can confirm the timeline.

Kind regards,
George Jabley
TechWokx Freelancer"""
    
    elif "Data Entry" in job["title"] or "Product" in job["title"]:
        return f"""Hello,

I am interested in assisting with your {job['title']} project.

I can:
• Research products from company websites and Google
• Collect accurate product names, descriptions, and images
• Upload information into your system
• Verify all entries for consistency and accuracy

My background includes data management and research ({USER_SKILLS.get('research', 85)}% proficiency).

I am available to start immediately.

Best regards,
George Jabley
TechWokx Freelancer"""
    
    else:
        return f"""Hello,

I am very interested in your {job['title']} project.

Based on my experience in {', '.join(job.get('skills_required', ['IT', 'Data', 'Administrative'])[:2])}, I am confident I can deliver high-quality results.

I am available to start immediately and can complete the work within your timeline.

Best regards,
George Jabley
TechWokx Freelancer"""

def get_recommendation(roi_score, match_score, access_type):
    """Get action recommendation"""
    if match_score < 60:
        return "🔴 Skip", "Poor match with your skills", "danger"
    elif roi_score < 30:
        return "🔴 Skip", "ROI too low - not worth the cost", "danger"
    elif roi_score < 50:
        return "🟡 Consider", "Uncertain ROI - proceed with caution", "warning"
    else:
        return "🟢 Bid Now", "High ROI opportunity - strongly recommended", "success"

def send_bid_notification(job, bid_amount):
    """Log bid submission"""
    st.session_state.bid_history.append({
        "job_title": job["title"],
        "platform": job["platform"],
        "bid_amount": bid_amount,
        "date": datetime.now(),
        "status": "Submitted",
        "job_url": job.get("url", "#")
    })
    return True

# ============ SAMPLE DATA (Fallback) ============
SAMPLE_JOBS = [
    {
        "id": "sample_1",
        "title": "PDF-to-Excel Data Transfer",
        "description": "Need accurate transfer of tables from PDF documents to Excel while preserving formatting.",
        "platform": "Freelancer",
        "budget_min": 6,
        "budget_max": 16,
        "skills_required": ["excel", "data_entry", "pdf_handling"],
        "access_type": "unlock_required",
        "unlock_cost": "$20 balance required",
        "posted_date": datetime.now() - timedelta(days=1),
        "client_rating": 4.5,
        "competition_level": "Medium",
        "bid_count": 12,
        "url": "#"
    },
    {
        "id": "sample_2",
        "title": "Tally AR/AP Data Entry Support",
        "description": "Looking for experienced data entry specialist for Tally accounting software.",
        "platform": "Upwork",
        "budget_min": 50,
        "budget_max": 150,
        "skills_required": ["data_entry", "excel", "administrative"],
        "access_type": "connect_required",
        "unlock_cost": "8 connects",
        "posted_date": datetime.now() - timedelta(days=2),
        "client_rating": 4.8,
        "competition_level": "Low",
        "bid_count": 5,
        "url": "#"
    },
    {
        "id": "sample_3",
        "title": "Product Data Entry & Sourcing",
        "description": "Research products from company websites and enter into our system.",
        "platform": "Freelancer",
        "budget_min": 50,
        "budget_max": 100,
        "skills_required": ["research", "data_entry", "excel"],
        "access_type": "open",
        "unlock_cost": "None",
        "posted_date": datetime.now() - timedelta(days=3),
        "client_rating": 4.2,
        "competition_level": "High",
        "bid_count": 25,
        "url": "#"
    }
]

# ============ CSS ============
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fbbf24 !important; }
[data-testid="stSidebar"] .stButton button { background: rgba(251, 191, 36, 0.15); color: #fbbf24 !important; width: 100%; margin: 2px 0; }
.welcome-card { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; color: white; }
.welcome-card h2, .welcome-card p { color: white; }
.metric-card { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
.metric-label { color: #64748b; font-size: 0.8rem; margin-top: 0.25rem; }
.data-card { background: white; border-radius: 12px; padding: 1.2rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.section-header { color: #0f172a; font-size: 1.2rem; font-weight: 600; margin: 1.5rem 0 1rem 0; border-left: 3px solid #667eea; padding-left: 1rem; }
.custom-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
.stButton > button { background: linear-gradient(135deg, #667eea, #764ba2); color: white !important; font-weight: 600; border: none; border-radius: 8px; }
.stButton > button:hover { background: linear-gradient(135deg, #5a67d8, #6b46a0); transform: translateY(-2px); transition: all 0.3s; }
.badge-success { background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
.badge-warning { background: #f59e0b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
.badge-danger { background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ============ LOGIN PAGE ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 450px; margin: 100px auto; padding: 2rem; background: white; border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);">
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
            <div style="font-size: 1.875rem; font-weight: 700; color: #1e293b;">TechWokx</div>
            <div style="color: #64748b; font-size: 0.875rem;">Freelance Intelligence Agent</div>
        </div>
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
        <div style="background: #f1f5f9; padding: 1rem; border-radius: 12px; margin-top: 1.5rem; text-align: center;">
            <div style="font-size: 0.75rem; color: #64748b;">🔐 Demo Access</div>
            <div style="font-size: 0.8rem; color: #334155; font-family: monospace;">hello@techwokx.online / Gtech.5628!@#$</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown(f"### 🔍 TechWokx")
    st.markdown(f"#### Welcome, {st.session_state.user['name']}")
    st.markdown("---")
    
    nav_items = [
        ("🏠 Dashboard", "dashboard"),
        ("🤖 Freelance Intel", "freelance_intel"),
        ("💰 Bid ROI Analyzer", "bid_roi"),
        ("---", "divider1"),
        ("🔑 API Settings", "api_settings"),
        ("---", "divider2"),
        ("📥 Import Leads", "import_leads"),
        ("👥 Lead CRM", "crm"),
        ("---", "divider3"),
        ("💻 System Info", "system_info"),
        ("📊 Analytics", "analytics"),
        ("📋 Bid History", "bid_history"),
        ("⚙️ Settings", "settings"),
        ("---", "divider4"),
        ("🚪 Logout", "logout")
    ]
    
    for label, key in nav_items:
        if label == "---":
            st.markdown("---")
        elif st.button(label, key=key, use_container_width=True):
            if key == "logout":
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()
            else:
                st.session_state.page = key
                st.rerun()
    
    st.markdown("---")
    st.markdown(f"👤 Skills: {len(USER_SKILLS)}")
    api_count = sum(1 for v in st.session_state.api_keys.values() if v)
    st.markdown(f"🔌 APIs: {api_count}/3 configured")

# ============ API SETTINGS PAGE ============
if st.session_state.page == 'api_settings':
    st.markdown('<div class="section-header">🔑 API Configuration</div>', unsafe_allow_html=True)
    st.caption("Configure your API keys for real job fetching")
    st.markdown("---")
    
    st.markdown("""
    ### Get Your API Keys:
    
    **Freelancer.com:**
    1. Go to [Freelancer.com API](https://www.freelancer.com/api)
    2. Register and get your OAuth token
    
    **Upwork:**
    - RSS feeds are public - no API key needed
    
    **PeoplePerHour:**
    1. Go to [PeoplePerHour API](https://www.peopleperhour.com/api)
    2. Request API access
    """)
    
    with st.form("api_keys_form"):
        st.markdown("### Enter Your API Keys")
        
        freelancer_key = st.text_input(
            "Freelancer.com API Key",
            value=st.session_state.api_keys.get('freelancer', ''),
            type="password",
            placeholder="Enter your Freelancer API key"
        )
        
        pph_key = st.text_input(
            "PeoplePerHour API Key",
            value=st.session_state.api_keys.get('pph', ''),
            type="password",
            placeholder="Enter your PeoplePerHour API key"
        )
        
        resend_key = st.text_input(
            "Resend Email API Key",
            value=st.session_state.api_keys.get('resend', ''),
            type="password",
            placeholder="re_..."
        )
        
        if st.form_submit_button("Save API Keys", type="primary"):
            st.session_state.api_keys['freelancer'] = freelancer_key
            st.session_state.api_keys['pph'] = pph_key
            st.session_state.api_keys['resend'] = resend_key
            st.success("API keys saved! You can now fetch real jobs.")
    
    st.markdown("---")
    st.markdown("### Test API Connection")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Test Freelancer API"):
            if st.session_state.api_keys.get('freelancer'):
                with st.spinner("Testing..."):
                    jobs = fetch_freelancer_jobs(st.session_state.api_keys['freelancer'], limit=1)
                    if jobs:
                        st.success("✅ Freelancer API connected successfully!")
                    else:
                        st.warning("⚠️ Freelancer API returned no jobs. Check your API key.")
            else:
                st.error("Please enter your Freelancer API key first")
    
    with col2:
        if st.button("Test Upwork RSS"):
            with st.spinner("Testing..."):
                jobs = fetch_upwork_jobs()
                if jobs:
                    st.success(f"✅ Upwork RSS working! Found {len(jobs)} jobs.")
                else:
                    st.warning("⚠️ Upwork RSS returned no jobs")

# ============ FREELANCE INTELLIGENCE PAGE ============
elif st.session_state.page == 'freelance_intel':
    st.markdown('<div class="section-header">🤖 Freelance Intelligence Agent</div>', unsafe_allow_html=True)
    st.caption("AI-powered job matching with real-time fetching from Freelancer, Upwork, and more")
    st.markdown("---")
    
    # Controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        keywords = st.text_input("Keywords (comma separated)", placeholder="data entry, excel, research")
    with col2:
        platform_filter = st.selectbox("Platform", ["All", "Freelancer", "Upwork", "PeoplePerHour"])
    with col3:
        min_match = st.slider("Min Match %", 0, 100, 50)
    with col4:
        if st.button("🔄 Fetch Jobs", type="primary"):
            with st.spinner("Fetching jobs from all platforms..."):
                fetched_jobs = fetch_all_jobs()
                if fetched_jobs:
                    st.session_state.jobs = fetched_jobs
                    st.success(f"Fetched {len(fetched_jobs)} jobs!")
                else:
                    st.warning("Using sample data. Configure API keys in Settings to fetch real jobs.")
                    st.session_state.jobs = SAMPLE_JOBS
                st.rerun()
    
    # Use fetched jobs or sample
    display_jobs = st.session_state.jobs if st.session_state.jobs else SAMPLE_JOBS
    
    # Apply filters
    if platform_filter != "All":
        display_jobs = [j for j in display_jobs if j["platform"] == platform_filter]
    
    if keywords:
        keyword_list = [k.strip().lower() for k in keywords.split(",")]
        display_jobs = [
            j for j in display_jobs 
            if any(k in j["title"].lower() or k in j["description"].lower() for k in keyword_list)
        ]
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs", len(display_jobs))
    with col2:
        high_match = sum(1 for j in display_jobs if calculate_match_score(j)[0] >= 80)
        st.metric("High Match (80%+)", high_match)
    with col3:
        high_roi = sum(1 for j in display_jobs if calculate_roi(j, calculate_match_score(j)[0])[0] >= 50)
        st.metric("High ROI (50+)", high_roi)
    
    st.markdown("---")
    
    # Display jobs
    for job in display_jobs[:25]:
        match_score, matched_skills = calculate_match_score(job)
        
        if match_score >= min_match:
            roi_score, win_prob, expected_value, cost = calculate_roi(job, match_score)
            recommendation, reason, rec_type = get_recommendation(roi_score, match_score, job.get("access_type"))
            
            border_color = "#10b981" if recommendation == "🟢 Bid Now" else "#f59e0b" if recommendation == "🟡 Consider" else "#ef4444"
            
            with st.expander(f"[{job['platform']}] {job['title']} - Match: {match_score}% - {recommendation}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {job['description'][:300]}...")
                    st.markdown(f"**Budget:** ${job['budget_min']} - ${job['budget_max']}")
                    st.markdown(f"**Skills Required:** {', '.join(job.get('skills_required', ['General'])[:5])}")
                    st.markdown(f"**Matched Skills:** {', '.join(matched_skills[:3]) if matched_skills else 'General fit'}")
                    st.markdown(f"**Access:** {job['access_type']} | {job['unlock_cost']}")
                    if job.get('bid_count'):
                        st.markdown(f"**Bids:** {job['bid_count']} bids placed")
                    if job.get('url') and job['url'] != "#":
                        st.markdown(f"**Link:** [View Job]({job['url']})")
                
                with col2:
                    st.markdown(f"### {recommendation}")
                    st.markdown(f"**Match Score:** {match_score}%")
                    st.markdown(f"**ROI Score:** {roi_score}/100")
                    st.markdown(f"**Win Probability:** {win_prob*100:.0f}%")
                    st.markdown(f"**Expected Value:** ${expected_value:.0f}")
                    st.markdown(f"**Bid Cost:** ${cost:.2f}")
                    st.markdown(f"**Reason:** {reason}")
                
                if recommendation == "🟢 Bid Now" or recommendation == "🟡 Consider":
                    st.markdown("---")
                    st.markdown("### 📝 AI-Generated Proposal")
                    
                    proposal = generate_proposal(job, match_score)
                    st.text_area("Proposal", proposal, height=150)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        bid_amount = st.number_input(
                            "Bid Amount ($)", 
                            min_value=job['budget_min'] if job['budget_min'] > 0 else 5,
                            max_value=job['budget_max'] if job['budget_max'] > 0 else 100,
                            value=max(job['budget_min'], (job['budget_min'] + job['budget_max'])//2) if job['budget_max'] > 0 else 25,
                            key=f"bid_{job['id']}"
                        )
                    with col2:
                        if st.button("📤 Submit Bid", key=f"submit_{job['id']}"):
                            send_bid_notification(job, bid_amount)
                            st.success(f"✅ Bid of ${bid_amount} recorded for {job['title']}!")
                    with col3:
                        if st.button("🔍 Research Client", key=f"research_{job['id']}"):
                            st.info("Client research would open detailed profile here")

# ============ BID ROI ANALYZER ============
elif st.session_state.page == 'bid_roi':
    st.markdown('<div class="section-header">💰 Bid ROI Analyzer</div>', unsafe_allow_html=True)
    st.caption("Calculate ROI before spending connects or unlock fees")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 ROI Calculator")
        
        job_payout = st.number_input("Expected Job Payout ($)", min_value=10, value=100, step=10)
        win_probability = st.slider("Estimated Win Probability (%)", 0, 100, 35)
        bid_cost = st.number_input("Cost to Bid ($ / connects)", min_value=0, value=5, step=1)
        match_score_input = st.slider("Match Score (%)", 0, 100, 85)
        
        expected_value = job_payout * (win_probability / 100)
        roi_percentage = ((expected_value - bid_cost) / bid_cost * 100) if bid_cost > 0 else expected_value * 10
        
        st.markdown("---")
        st.markdown("### 📈 ROI Analysis")
        st.markdown(f"**Expected Value:** ${expected_value:.2f}")
        st.markdown(f"**ROI:** {roi_percentage:.1f}%")
        
        if roi_percentage > 300:
            st.success("🟢 EXCELLENT ROI - Strongly recommend bidding")
            st.progress(0.9)
        elif roi_percentage > 100:
            st.warning("🟡 GOOD ROI - Consider bidding")
            st.progress(0.6)
        else:
            st.error("🔴 POOR ROI - Skip this opportunity")
            st.progress(0.2)
    
    with col2:
        st.markdown("### 💡 Bid Strategy Tips")
        st.markdown("""
        **When to bid:**
        - ✅ Match score > 80%
        - ✅ ROI > 100%
        - ✅ Win probability > 30%
        - ✅ Client rating > 4.5
        
        **When to skip:**
        - ❌ Unlock fee > expected payout
        - ❌ Competition is too high (>20 bids)
        - ❌ Skills match is poor (<60%)
        
        **Platform costs:**
        - Freelancer: $20 unlock fee
        - Upwork: 8-16 connects ($1.20-$2.40)
        - PeoplePerHour: Credit system
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 Quick Recommendation")
        
        if job_payout > 50 and win_probability > 30 and bid_cost < 10:
            st.success("🎯 This looks like a good opportunity!")
            st.info(f"Recommended bid: ${job_payout * 0.3:.0f} - ${job_payout * 0.4:.0f}")
        else:
            st.warning("⚠️ Consider improving your profile before bidding")

# ============ BID HISTORY ============
elif st.session_state.page == 'bid_history':
    st.markdown('<div class="section-header">📋 Bid History</div>', unsafe_allow_html=True)
    st.caption("Track all your submitted bids")
    st.markdown("---")
    
    if st.session_state.bid_history:
        for bid in reversed(st.session_state.bid_history):
            st.markdown(f"""
            <div class="data-card">
                <strong>📌 {bid['job_title']}</strong><br>
                Platform: {bid['platform']} | Bid: ${bid['bid_amount']}<br>
                Status: {bid['status']} | Date: {bid['date'].strftime('%Y-%m-%d %H:%M')}<br>
                <a href="{bid.get('job_url', '#')}" target="_blank">View Job</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No bids submitted yet. Use the Freelance Intelligence page to find and bid on jobs.")

# ============ DASHBOARD ============
elif st.session_state.page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>🤖 Welcome to TechWokx Freelance Intelligence Agent</h2>
        <p>AI-powered job matching with real-time API integration | Bid smarter, win more</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate stats
    display_jobs = st.session_state.jobs if st.session_state.jobs else SAMPLE_JOBS
    total_jobs = len(display_jobs)
    high_match_jobs = sum(1 for j in display_jobs if calculate_match_score(j)[0] >= 80)
    high_roi_jobs = sum(1 for j in display_jobs if calculate_roi(j, calculate_match_score(j)[0])[0] >= 50)
    total_bids = len(st.session_state.bid_history)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_jobs}</div><div class='metric-label'>Available Jobs</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{high_match_jobs}</div><div class='metric-label'>High Match (80%+)</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{high_roi_jobs}</div><div class='metric-label'>High ROI (50+)</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_bids}</div><div class='metric-label'>Bids Submitted</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">🎯 Top Recommended Jobs</div>', unsafe_allow_html=True)
        for job in display_jobs[:3]:
            match_score, _ = calculate_match_score(job)
            roi_score, win_prob, expected_value, cost = calculate_roi(job, match_score)
            recommendation, reason, _ = get_recommendation(roi_score, match_score, job.get("access_type"))
            
            badge_class = "badge-success" if recommendation == "🟢 Bid Now" else "badge-warning" if recommendation == "🟡 Consider" else "badge-danger"
            
            st.markdown(f"""
            <div class="data-card">
                <strong>{job['title']}</strong><br>
                <small>📊 Match: {match_score}% | 💰 ROI: {roi_score} | 🏷️ {job['platform']}</small><br>
                <span class="{badge_class}" style="font-size:0.7rem">{recommendation}</span>
                <small style="color:#64748b"> - {reason}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">📈 Your Skills Profile</div>', unsafe_allow_html=True)
        for skill, level in sorted(USER_SKILLS.items(), key=lambda x: x[1], reverse=True)[:6]:
            st.markdown(f"**{skill.replace('_', ' ').title()}:** {level}%")
            st.progress(level / 100)
        
        st.markdown("---")
        if st.button("🔍 Fetch New Jobs", use_container_width=True):
            with st.spinner("Fetching latest jobs..."):
                jobs = fetch_all_jobs()
                if jobs:
                    st.session_state.jobs = jobs
                    st.success(f"Fetched {len(jobs)} new jobs!")
                    st.rerun()
                else:
                    st.warning("Configure API keys in Settings to fetch real jobs")

# ============ OTHER PAGES ============
elif st.session_state.page == 'import_leads':
    st.markdown('<div class="section-header">📥 Import Leads</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose CSV/Excel file", type=['csv', 'xlsx'])
    if uploaded_file:
        st.success("File uploaded successfully!")

elif st.session_state.page == 'crm':
    st.markdown('<div class="section-header">👥 Lead CRM</div>', unsafe_allow_html=True)
    if st.session_state.leads:
        for lead in st.session_state.leads[-10:]:
            st.markdown(f"<div class='data-card'><strong>{lead.get('name', 'Unknown')}</strong><br>Email: {lead.get('email', 'N/A')}</div>", unsafe_allow_html=True)
    else:
        st.info("No leads yet")

elif st.session_state.page == 'system_info':
    st.markdown('<div class="section-header">💻 System Information</div>', unsafe_allow_html=True)
    info = {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "version": platform.version(),
    }
    st.json(info)

elif st.session_state.page == 'analytics':
    st.markdown('<div class="section-header">📊 Analytics</div>', unsafe_allow_html=True)
    display_jobs = st.session_state.jobs if st.session_state.jobs else SAMPLE_JOBS
    match_scores = [calculate_match_score(j)[0] for j in display_jobs]
    st.bar_chart(pd.DataFrame({"Match Scores": match_scores}))

elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown("### Skills Profile")
    for skill, level in sorted(USER_SKILLS.items(), key=lambda x: x[1], reverse=True):
        st.markdown(f"**{skill.replace('_', ' ').title()}:** {level}%")
        st.progress(level / 100)

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption(f"© 2024 TechWokx Freelance Intelligence Agent | Real-time API Integration")

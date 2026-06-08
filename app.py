import streamlit as st
import pandas as pd
import os
import socket
import platform
import re
import requests
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
        'rapidapi': '',
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

# ============ RAPIDAPI FREELANCER INTEGRATION ============

def fetch_freelancer_jobs_rapidapi(api_key, keywords=None, limit=25):
    """Fetch jobs from Freelancer using RapidAPI"""
    if not api_key:
        return []
    
    try:
        # RapidAPI Freelancer endpoint
        url = "https://freelancer-freelancer-v1.p.rapidapi.com/projects/0.1/projects/active/"
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "freelancer-freelancer-v1.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        params = {
            "limit": limit,
            "compact": True
        }
        
        if keywords:
            params["query"] = keywords
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            projects = data.get("result", {}).get("projects", [])
            
            for project in projects:
                # Extract budget information
                budget_min = project.get("budget", {}).get("minimum", 0)
                budget_max = project.get("budget", {}).get("maximum", 0)
                
                # If no budget, try to get from bid stats
                if budget_min == 0 and budget_max == 0:
                    bid_stats = project.get("bid_stats", {})
                    budget_min = bid_stats.get("minimum_bid", 0)
                    budget_max = bid_stats.get("maximum_bid", 0)
                
                # Extract skills
                skills = []
                for skill in project.get("skills", []):
                    if isinstance(skill, dict):
                        skills.append(skill.get("name", "").lower())
                    elif isinstance(skill, str):
                        skills.append(skill.lower())
                
                # Determine competition level based on bid count
                bid_count = project.get("bid_stats", {}).get("bid_count", 0)
                if bid_count > 20:
                    competition = "High"
                elif bid_count > 10:
                    competition = "Medium"
                else:
                    competition = "Low"
                
                jobs.append({
                    "id": str(project.get("id")),
                    "title": project.get("title", "Untitled"),
                    "description": project.get("description", "")[:500],
                    "platform": "Freelancer",
                    "budget_min": budget_min,
                    "budget_max": budget_max if budget_max > 0 else budget_min,
                    "skills_required": skills,
                    "access_type": "unlock_required" if project.get("prepaid") else "open",
                    "unlock_cost": "$20 balance required" if project.get("prepaid") else "Free to bid",
                    "posted_date": datetime.fromtimestamp(project.get("submitdate", 0)) if project.get("submitdate") else datetime.now(),
                    "client_rating": project.get("user", {}).get("rating", 0) / 10 if project.get("user", {}).get("rating") else 0,
                    "competition_level": competition,
                    "bid_count": bid_count,
                    "url": f"https://www.freelancer.com/projects/{project.get('seo_url', '')}" if project.get('seo_url') else "#"
                })
            
            return jobs
        else:
            st.warning(f"RapidAPI error: {response.status_code} - {response.text[:100]}")
            return []
            
    except requests.exceptions.Timeout:
        st.warning("RapidAPI request timed out")
        return []
    except Exception as e:
        st.warning(f"RapidAPI connection error: {str(e)[:100]}")
        return []

def search_freelancer_by_category(api_key, category, limit=20):
    """Search Freelancer jobs by category"""
    if not api_key:
        return []
    
    try:
        url = "https://freelancer-freelancer-v1.p.rapidapi.com/projects/0.1/projects/"
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "freelancer-freelancer-v1.p.rapidapi.com"
        }
        
        params = {
            "query": category,
            "limit": limit
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            projects = data.get("result", {}).get("projects", [])
            
            jobs = []
            for project in projects:
                jobs.append({
                    "id": str(project.get("id")),
                    "title": project.get("title", "Untitled"),
                    "description": project.get("description", "")[:500],
                    "platform": "Freelancer",
                    "budget_min": project.get("budget", {}).get("minimum", 0),
                    "budget_max": project.get("budget", {}).get("maximum", 0),
                    "skills_required": [s.get("name", "").lower() for s in project.get("skills", [])],
                    "access_type": "open",
                    "unlock_cost": "Free",
                    "posted_date": datetime.now(),
                    "client_rating": 0,
                    "competition_level": "Medium",
                    "bid_count": 0,
                    "url": "#"
                })
            return jobs
        return []
    except Exception as e:
        return []

def fetch_upwork_jobs():
    """Fetch jobs from Upwork RSS feed"""
    try:
        import feedparser
        url = "https://www.upwork.com/ab/feed/jobs/rss"
        feed = feedparser.parse(url)
        jobs = []
        
        for entry in feed.entries[:25]:
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
    except ImportError:
        return []
    except Exception:
        return []

def fetch_fiverr_jobs(api_key=None):
    """Fetch jobs from Fiverr (if API available)"""
    # Fiverr API is limited, returning sample for now
    return []

def fetch_all_jobs(rapidapi_key):
    """Fetch jobs from all platforms"""
    all_jobs = []
    
    # Fetch from Freelancer via RapidAPI
    if rapidapi_key:
        freelancer_jobs = fetch_freelancer_jobs_rapidapi(rapidapi_key, limit=30)
        all_jobs.extend(freelancer_jobs)
    
    # Fetch from Upwork
    upwork_jobs = fetch_upwork_jobs()
    all_jobs.extend(upwork_jobs)
    
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
    
    comp_map = {"Low": 0.7, "Medium": 0.5, "High": 0.3}
    comp_factor = comp_map.get(job.get("competition_level", "Medium"), 0.5)
    
    win_probability = (match_score / 100) * comp_factor * 0.8
    expected_value = avg_budget * win_probability
    
    unlock_text = job.get("unlock_cost", "").lower()
    if "connect" in unlock_text:
        connects = int(re.search(r'\d+', unlock_text).group(0)) if re.search(r'\d+', unlock_text) else 8
        cost = connects * 0.15
    elif "$" in unlock_text:
        cost = 20
    else:
        cost = 0
    
    if cost > 0:
        roi_score = min(100, (expected_value / cost) * 20)
    else:
        roi_score = min(100, expected_value / 10)
    
    return round(roi_score, 1), win_probability, expected_value, cost

def generate_proposal(job, match_score):
    """Generate personalized proposal"""
    if "PDF" in job["title"] or "Excel" in job["title"]:
        return f"""Hello,

I can accurately transfer the tables from your PDF documents into Excel while preserving the original structure and formatting.

My approach includes:
• Extracting data using professional PDF tools and Excel
• Verifying every row and column for accuracy
• Maintaining the original table layout
• Delivering a clean and organized .xlsx file

I have {USER_SKILLS.get('data_entry', 85)}% proficiency in data entry and Excel.

Kind regards,
George Jabley
TechWokx Freelancer"""
    
    elif "Data Entry" in job["title"] or "Product" in job["title"]:
        return f"""Hello,

I am interested in assisting with your {job['title']} project.

I can:
• Research products from company websites
• Collect accurate product information
• Verify all entries for consistency
• Deliver organized data

My background includes data management and research ({USER_SKILLS.get('research', 85)}% proficiency).

Best regards,
George Jabley
TechWokx Freelancer"""
    
    else:
        return f"""Hello,

I am very interested in your {job['title']} project.

Based on my experience, I am confident I can deliver high-quality results.

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

# ============ SAMPLE DATA ============
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
.metric-card { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
.metric-label { color: #64748b; font-size: 0.8rem; }
.data-card { background: white; border-radius: 12px; padding: 1.2rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
.section-header { color: #0f172a; font-size: 1.2rem; font-weight: 600; border-left: 3px solid #667eea; padding-left: 1rem; margin: 1.5rem 0 1rem 0; }
.custom-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
.stButton > button { background: linear-gradient(135deg, #667eea, #764ba2); color: white !important; font-weight: 600; border: none; border-radius: 8px; }
.badge-success { background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
.badge-warning { background: #f59e0b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
.badge-danger { background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ============ LOGIN PAGE ============
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 450px; margin: 100px auto; padding: 2rem; background: white; border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); text-align: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
        <div style="font-size: 1.875rem; font-weight: 700; color: #1e293b;">TechWokx</div>
        <div style="color: #64748b; margin-bottom: 2rem;">Freelance Intelligence Agent</div>
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
    
    st.markdown(f"""
        <div style="background: #f1f5f9; padding: 1rem; border-radius: 12px; margin-top: 1.5rem;">
            <div style="font-size: 0.75rem; color: #64748b;">🔐 Demo Access</div>
            <div style="font-size: 0.8rem; font-family: monospace;">hello@techwokx.online / Gtech.5628!@#$</div>
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
        ("📊 Analytics", "analytics"),
        ("📋 Bid History", "bid_history"),
        ("⚙️ Skills Profile", "settings"),
        ("---", "divider3"),
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
    if st.session_state.api_keys.get('rapidapi'):
        st.markdown("🔌 RapidAPI: ✅ Connected")

# ============ API SETTINGS PAGE ============
if st.session_state.page == 'api_settings':
    st.markdown('<div class="section-header">🔑 API Configuration</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("""
    **Get your RapidAPI Key for Freelancer:**
    1. Go to [RapidAPI Freelancer API](https://rapidapi.com/rockethearts/api/freelancer-freelancer-v1)
    2. Subscribe to the API
    3. Copy your X-RapidAPI-Key
    """)
    
    with st.form("api_keys_form"):
        rapidapi_key = st.text_input(
            "RapidAPI Key (Freelancer)",
            value=st.session_state.api_keys.get('rapidapi', ''),
            type="password",
            placeholder="Enter your X-RapidAPI-Key"
        )
        
        if st.form_submit_button("Save API Keys", type="primary"):
            st.session_state.api_keys['rapidapi'] = rapidapi_key
            st.success("API keys saved! You can now fetch real jobs.")
    
    if st.session_state.api_keys.get('rapidapi'):
        st.markdown("---")
        st.markdown("### Test API Connection")
        if st.button("Test Freelancer API"):
            with st.spinner("Testing..."):
                jobs = fetch_freelancer_jobs_rapidapi(st.session_state.api_keys['rapidapi'], limit=5)
                if jobs:
                    st.success(f"✅ API working! Found {len(jobs)} jobs.")
                else:
                    st.warning("⚠️ API returned no jobs. Check your API key.")

# ============ FREELANCE INTELLIGENCE PAGE ============
if st.session_state.page == 'freelance_intel':
    st.markdown('<div class="section-header">🤖 Freelance Intelligence Agent</div>', unsafe_allow_html=True)
    st.caption("AI-powered job matching using RapidAPI for Freelancer, Upwork RSS")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        keywords = st.text_input("Keywords", placeholder="data entry, excel, research")
    with col2:
        platform_filter = st.selectbox("Platform", ["All", "Freelancer", "Upwork"])
    with col3:
        min_match = st.slider("Min Match %", 0, 100, 50)
    with col4:
        if st.button("🔄 Fetch Jobs", type="primary"):
            with st.spinner("Fetching jobs from Freelancer (RapidAPI) and Upwork..."):
                all_jobs = fetch_all_jobs(st.session_state.api_keys.get('rapidapi', ''))
                if all_jobs:
                    st.session_state.jobs = all_jobs
                    st.success(f"Fetched {len(all_jobs)} jobs!")
                else:
                    st.warning("Using sample data. Configure RapidAPI key to fetch real jobs.")
                    st.session_state.jobs = SAMPLE_JOBS
                st.rerun()
    
    display_jobs = st.session_state.jobs if st.session_state.jobs else SAMPLE_JOBS
    
    if platform_filter != "All":
        display_jobs = [j for j in display_jobs if j["platform"] == platform_filter]
    
    if keywords:
        keyword_list = [k.strip().lower() for k in keywords.split(",")]
        display_jobs = [
            j for j in display_jobs 
            if any(k in j["title"].lower() or k in j["description"].lower() for k in keyword_list)
        ]
    
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
    
    for job in display_jobs[:25]:
        match_score, matched_skills = calculate_match_score(job)
        
        if match_score >= min_match:
            roi_score, win_prob, expected_value, cost = calculate_roi(job, match_score)
            recommendation, reason, rec_type = get_recommendation(roi_score, match_score, job.get("access_type"))
            
            with st.expander(f"[{job['platform']}] {job['title']} - Match: {match_score}% - {recommendation}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {job['description'][:300]}...")
                    st.markdown(f"**Budget:** ${job['budget_min']} - ${job['budget_max']}")
                    st.markdown(f"**Skills:** {', '.join(job.get('skills_required', ['General'])[:5])}")
                    st.markdown(f"**Access:** {job['access_type']} | {job['unlock_cost']}")
                    if job.get('bid_count'):
                        st.markdown(f"**Bids:** {job['bid_count']}")
                
                with col2:
                    st.markdown(f"### {recommendation}")
                    st.markdown(f"**Match Score:** {match_score}%")
                    st.markdown(f"**ROI Score:** {roi_score}/100")
                    st.markdown(f"**Win Probability:** {win_prob*100:.0f}%")
                    st.markdown(f"**Expected Value:** ${expected_value:.0f}")
                
                if recommendation == "🟢 Bid Now" or recommendation == "🟡 Consider":
                    st.markdown("---")
                    st.markdown("### 📝 AI-Generated Proposal")
                    proposal = generate_proposal(job, match_score)
                    st.text_area("Proposal", proposal, height=150)
                    
                    bid_amount = st.number_input(
                        "Bid Amount ($)",
                        min_value=max(5, job['budget_min']),
                        max_value=job['budget_max'] if job['budget_max'] > 0 else 100,
                        value=max(job['budget_min'], (job['budget_min'] + job['budget_max'])//2) if job['budget_max'] > 0 else 25,
                        key=f"bid_{job['id']}"
                    )
                    
                    if st.button("📤 Submit Bid", key=f"submit_{job['id']}"):
                        send_bid_notification(job, bid_amount)
                        st.success(f"✅ Bid recorded for {job['title']}!")

# ============ BID ROI ANALYZER ============
if st.session_state.page == 'bid_roi':
    st.markdown('<div class="section-header">💰 Bid ROI Analyzer</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 ROI Calculator")
        job_payout = st.number_input("Expected Job Payout ($)", min_value=10, value=100)
        win_probability = st.slider("Win Probability (%)", 0, 100, 35)
        bid_cost = st.number_input("Cost to Bid ($)", min_value=0, value=5)
        
        expected_value = job_payout * (win_probability / 100)
        roi_percentage = ((expected_value - bid_cost) / bid_cost * 100) if bid_cost > 0 else expected_value * 10
        
        st.markdown(f"**Expected Value:** ${expected_value:.2f}")
        st.markdown(f"**ROI:** {roi_percentage:.1f}%")
        
        if roi_percentage > 300:
            st.success("🟢 EXCELLENT ROI - Strongly recommend bidding")
        elif roi_percentage > 100:
            st.warning("🟡 GOOD ROI - Consider bidding")
        else:
            st.error("🔴 POOR ROI - Skip this opportunity")
    
    with col2:
        st.markdown("### 💡 Bid Strategy Tips")
        st.markdown("""
        **When to bid:**
        - ✅ Match score > 80%
        - ✅ ROI > 100%
        - ✅ Win probability > 30%
        
        **Platform costs:**
        - Freelancer: $20 unlock fee
        - Upwork: 8-16 connects ($1.20-$2.40)
        """)

# ============ BID HISTORY ============
if st.session_state.page == 'bid_history':
    st.markdown('<div class="section-header">📋 Bid History</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.bid_history:
        for bid in reversed(st.session_state.bid_history):
            st.markdown(f"""
            <div class="data-card">
                <strong>📌 {bid['job_title']}</strong><br>
                Platform: {bid['platform']} | Bid: ${bid['bid_amount']}<br>
                Status: {bid['status']} | Date: {bid['date'].strftime('%Y-%m-%d %H:%M')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No bids submitted yet")

# ============ DASHBOARD ============
if st.session_state.page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>🤖 TechWokx Freelance Intelligence Agent</h2>
        <p>Powered by RapidAPI | AI-powered job matching | Smart bid recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    display_jobs = st.session_state.jobs if st.session_state.jobs else SAMPLE_JOBS
    total_jobs = len(display_jobs)
    high_match = sum(1 for j in display_jobs if calculate_match_score(j)[0] >= 80)
    total_bids = len(st.session_state.bid_history)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_jobs}</div><div class='metric-label'>Available Jobs</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{high_match}</div><div class='metric-label'>High Match</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_bids}</div><div class='metric-label'>Bids Placed</div></div>", unsafe_allow_html=True)
    with col4:
        rapidapi_status = "✅" if st.session_state.api_keys.get('rapidapi') else "❌"
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{rapidapi_status}</div><div class='metric-label'>RapidAPI</div></div>", unsafe_allow_html=True)

# ============ ANALYTICS ============
if st.session_state.page == 'analytics':
    st.markdown('<div class="section-header">📊 Analytics</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    display_jobs = st.session_state.jobs if st.session_state.jobs else SAMPLE_JOBS
    match_scores = [calculate_match_score(j)[0] for j in display_jobs]
    
    st.subheader("Match Score Distribution")
    st.bar_chart(pd.DataFrame({"Match Scores": match_scores}))

# ============ SKILLS PROFILE ============
if st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ Skills Profile</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    for skill, level in sorted(USER_SKILLS.items(), key=lambda x: x[1], reverse=True):
        st.markdown(f"**{skill.replace('_', ' ').title()}:** {level}%")
        st.progress(level / 100)

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption(f"© 2024 TechWokx Freelance Intelligence Agent | Powered by RapidAPI")

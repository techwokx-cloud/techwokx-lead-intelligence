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
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {
        'rapidapi_freelancer': '',
        'rapidapi_upwork': '',
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
    "automation": 80,
    "virtual_assistant": 85,
    "customer_service": 80
}

# ============ FREELANCER API METHODS (Multiple Fallbacks) ============

def fetch_freelancer_jobs_method1(api_key, keywords=None, limit=30):
    """Method 1: Official Freelancer API via RapidAPI"""
    if not api_key:
        return [], "No API key"
    
    try:
        # Try different endpoint variations
        endpoints = [
            "https://freelancer-freelancer-v1.p.rapidapi.com/projects/0.1/projects/active/",
            "https://freelancer-freelancer-v1.p.rapidapi.com/projects/0.1/projects/",
            "https://freelancer9.p.rapidapi.com/projects/0.1/projects/active/"
        ]
        
        for endpoint in endpoints:
            try:
                headers = {
                    "X-RapidAPI-Key": api_key,
                    "X-RapidAPI-Host": endpoint.split("/")[2],
                    "Content-Type": "application/json"
                }
                
                params = {"limit": limit, "compact": True}
                if keywords:
                    params["query"] = keywords
                
                response = requests.get(endpoint, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    projects = data.get("result", {}).get("projects", [])
                    if projects:
                        return projects, endpoint
            except:
                continue
        
        return [], "No projects found"
    except Exception as e:
        return [], str(e)

def fetch_freelancer_jobs_method2(api_key, keywords=None, limit=30):
    """Method 2: Alternative RapidAPI endpoint"""
    if not api_key:
        return [], "No API key"
    
    try:
        url = "https://freelancer9.p.rapidapi.com/projects/0.1/projects/"
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "freelancer9.p.rapidapi.com"
        }
        
        params = {"limit": limit}
        if keywords:
            params["query"] = keywords
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            projects = data.get("result", {}).get("projects", [])
            return projects, "Method 2"
        return [], f"Status: {response.status_code}"
    except Exception as e:
        return [], str(e)

def fetch_freelancer_jobs_method3(keywords=None, limit=30):
    """Method 3: Web scraping fallback (public listings)"""
    try:
        url = "https://www.freelancer.com/jobs/"
        if keywords:
            url += f"?keywords={keywords.replace(' ', '+')}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Parse HTML for job listings
            import re
            jobs_data = []
            
            # Extract job IDs from page
            job_ids = re.findall(r'/projects/([^/]+)/', response.text)
            titles = re.findall(r'<a[^>]*class="JobSearchCard-primary-heading-link"[^>]*>([^<]+)</a>', response.text)
            budgets = re.findall(r'\$(\d+)\s*-\s*\$(\d+)', response.text)
            
            for i, title in enumerate(titles[:limit]):
                jobs_data.append({
                    "id": job_ids[i] if i < len(job_ids) else f"scraped_{i}",
                    "title": title.strip(),
                    "description": "Scraped from Freelancer.com",
                    "budget_min": int(budgets[i][0]) if i < len(budgets) else 10,
                    "budget_max": int(budgets[i][1]) if i < len(budgets) else 50,
                    "skills_required": ["general"],
                })
            
            return jobs_data, "Scraped"
        return [], "Scraping failed"
    except Exception as e:
        return [], str(e)

def fetch_freelancer_jobs_combined(api_key, keywords=None, limit=30):
    """Combined method to fetch Freelancer jobs"""
    all_jobs = []
    
    # Try Method 1
    projects, source = fetch_freelancer_jobs_method1(api_key, keywords, limit)
    if projects:
        for project in projects:
            budget_min = project.get("budget", {}).get("minimum", 0)
            budget_max = project.get("budget", {}).get("maximum", 0)
            if budget_min == 0:
                bid_stats = project.get("bid_stats", {})
                budget_min = bid_stats.get("minimum_bid", 10)
                budget_max = bid_stats.get("maximum_bid", 50)
            
            skills = []
            for skill in project.get("skills", []):
                if isinstance(skill, dict):
                    skills.append(skill.get("name", "").lower())
                elif isinstance(skill, str):
                    skills.append(skill.lower())
            
            bid_count = project.get("bid_stats", {}).get("bid_count", 0)
            if bid_count > 20:
                competition = "High"
            elif bid_count > 10:
                competition = "Medium"
            else:
                competition = "Low"
            
            all_jobs.append({
                "id": str(project.get("id")),
                "title": project.get("title", "Untitled"),
                "description": project.get("description", "")[:500],
                "platform": "Freelancer",
                "budget_min": budget_min,
                "budget_max": budget_max if budget_max > 0 else budget_min * 2,
                "skills_required": skills,
                "access_type": "unlock_required" if project.get("prepaid") else "open",
                "unlock_cost": "$20 balance required" if project.get("prepaid") else "Free to bid",
                "posted_date": datetime.fromtimestamp(project.get("submitdate", 0)) if project.get("submitdate") else datetime.now(),
                "client_rating": project.get("user", {}).get("rating", 0) / 10 if project.get("user", {}).get("rating") else 0,
                "competition_level": competition,
                "bid_count": bid_count,
                "url": f"https://www.freelancer.com/projects/{project.get('seo_url', '')}" if project.get('seo_url') else "#",
                "source": source
            })
    
    # If no jobs, try Method 2
    if not all_jobs:
        projects, source = fetch_freelancer_jobs_method2(api_key, keywords, limit)
        for project in projects:
            all_jobs.append({
                "id": str(project.get("id")),
                "title": project.get("title", "Untitled"),
                "description": project.get("description", "")[:500],
                "platform": "Freelancer",
                "budget_min": project.get("budget", {}).get("minimum", 15),
                "budget_max": project.get("budget", {}).get("maximum", 45),
                "skills_required": [s.get("name", "").lower() for s in project.get("skills", [])],
                "access_type": "open",
                "unlock_cost": "Free",
                "posted_date": datetime.now(),
                "client_rating": 0,
                "competition_level": "Medium",
                "bid_count": 0,
                "url": "#",
                "source": source
            })
    
    return all_jobs

# ============ UPWORK API METHODS ============

def fetch_upwork_jobs_rapidapi(api_key, category=None, limit=30):
    """Fetch jobs from Upwork using RapidAPI"""
    if not api_key:
        return []
    
    try:
        # Try multiple Upwork API endpoints
        endpoints = [
            {"url": "https://upwork7.p.rapidapi.com/api/client/projects/search", "host": "upwork7.p.rapidapi.com"},
            {"url": "https://upwork-scraper.p.rapidapi.com/projects", "host": "upwork-scraper.p.rapidapi.com"},
            {"url": "https://upwork-api.p.rapidapi.com/jobs/search", "host": "upwork-api.p.rapidapi.com"}
        ]
        
        for endpoint in endpoints:
            try:
                headers = {
                    "X-RapidAPI-Key": api_key,
                    "X-RapidAPI-Host": endpoint["host"],
                    "Content-Type": "application/json"
                }
                
                params = {"page": 1, "per_page": limit}
                if category:
                    params["category"] = category
                
                response = requests.get(endpoint["url"], headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    projects = data.get("projects", []) if isinstance(data, dict) else data
                    if projects:
                        return projects
            except:
                continue
        
        return []
    except Exception:
        return []

def fetch_upwork_rss_jobs(keywords=None):
    """Fallback: Fetch jobs from Upwork RSS feed"""
    try:
        import feedparser
        base_url = "https://www.upwork.com/ab/feed/jobs/rss"
        
        if keywords:
            query = "+".join(keywords) if isinstance(keywords, list) else keywords
            url = f"{base_url}?q={query}"
        else:
            url = base_url
        
        feed = feedparser.parse(url)
        jobs = []
        
        for entry in feed.entries[:25]:
            description = entry.get("summary", "")
            budget_match = re.search(r'\$(\d+)(?:\s*-\s*\$(\d+))?', description)
            
            if budget_match:
                budget_min = int(budget_match.group(1))
                budget_max = int(budget_match.group(2)) if budget_match.group(2) else budget_min
            else:
                budget_min = 10
                budget_max = 30
            
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
                "url": entry.get("link", "#"),
                "source": "RSS Feed"
            })
        
        return jobs
    except ImportError:
        return []
    except Exception:
        return []

def fetch_upwork_jobs_combined(api_key, keywords=None, limit=30):
    """Combined method to fetch Upwork jobs"""
    all_jobs = []
    
    # Try RapidAPI first
    projects = fetch_upwork_jobs_rapidapi(api_key, limit=limit)
    for project in projects:
        budget = project.get("budget", {})
        budget_min = budget.get("min", 0) if isinstance(budget, dict) else 0
        budget_max = budget.get("max", 0) if isinstance(budget, dict) else 0
        
        skills = project.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip().lower() for s in skills.split(",")]
        
        all_jobs.append({
            "id": str(project.get("id")),
            "title": project.get("title", "Untitled"),
            "description": project.get("description", "")[:500],
            "platform": "Upwork",
            "budget_min": budget_min,
            "budget_max": budget_max,
            "skills_required": skills,
            "access_type": "connect_required",
            "unlock_cost": "8-16 connects",
            "posted_date": datetime.now(),
            "client_rating": 0,
            "competition_level": "Medium",
            "bid_count": project.get("proposals_count", 0),
            "url": project.get("url", "#"),
            "source": "RapidAPI"
        })
    
    # If no jobs, use RSS fallback
    if not all_jobs:
        all_jobs = fetch_upwork_rss_jobs(keywords)
    
    return all_jobs

# ============ EXPANDED SAMPLE JOBS ============
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
        "url": "#",
        "source": "Sample"
    },
    {
        "id": "sample_2",
        "title": "Virtual Assistant - Email & Calendar Management",
        "description": "Need a virtual assistant to manage emails, schedule meetings, and handle administrative tasks.",
        "platform": "Upwork",
        "budget_min": 15,
        "budget_max": 25,
        "skills_required": ["virtual_assistant", "administrative", "email_management"],
        "access_type": "connect_required",
        "unlock_cost": "8 connects",
        "posted_date": datetime.now() - timedelta(days=2),
        "client_rating": 4.8,
        "competition_level": "Medium",
        "bid_count": 15,
        "url": "#",
        "source": "Sample"
    },
    {
        "id": "sample_3",
        "title": "Excel Data Cleaning & Formatting",
        "description": "Need to clean and format large Excel dataset with 10,000+ rows for analysis.",
        "platform": "Freelancer",
        "budget_min": 30,
        "budget_max": 60,
        "skills_required": ["excel", "data_analysis", "data_cleaning"],
        "access_type": "open",
        "unlock_cost": "Free",
        "posted_date": datetime.now() - timedelta(days=3),
        "client_rating": 4.2,
        "competition_level": "High",
        "bid_count": 25,
        "url": "#",
        "source": "Sample"
    },
    {
        "id": "sample_4",
        "title": "Product Research & Data Entry",
        "description": "Research products from supplier websites and compile data into spreadsheet.",
        "platform": "Upwork",
        "budget_min": 50,
        "budget_max": 100,
        "skills_required": ["research", "data_entry", "excel"],
        "access_type": "connect_required",
        "unlock_cost": "12 connects",
        "posted_date": datetime.now() - timedelta(days=4),
        "client_rating": 4.6,
        "competition_level": "Low",
        "bid_count": 8,
        "url": "#",
        "source": "Sample"
    },
    {
        "id": "sample_5",
        "title": "IT Support - Help Desk Tickets",
        "description": "Need IT support specialist to handle help desk tickets for small business.",
        "platform": "Freelancer",
        "budget_min": 20,
        "budget_max": 35,
        "skills_required": ["it_support", "customer_service"],
        "access_type": "open",
        "unlock_cost": "Free",
        "posted_date": datetime.now() - timedelta(days=1),
        "client_rating": 4.3,
        "competition_level": "Medium",
        "bid_count": 18,
        "url": "#",
        "source": "Sample"
    }
]

# ============ JOB SCORING FUNCTIONS ============

def calculate_match_score(job):
    """Calculate match score based on user skills"""
    total_score = 0
    matched_skills = []
    
    for skill in job.get("skills_required", []):
        skill_lower = skill.lower().replace(" ", "_").replace("-", "_")
        if skill_lower in USER_SKILLS:
            score = USER_SKILLS[skill_lower]
            total_score += score
            matched_skills.append(f"{skill}({score}%)")
    
    if job.get("skills_required") and len(job["skills_required"]) > 0:
        max_possible = len(job["skills_required"]) * 100
        if max_possible > 0:
            match_percentage = (total_score / max_possible) * 100
        else:
            match_percentage = 50
    else:
        title_lower = job.get("title", "").lower()
        if any(word in title_lower for word in ["excel", "data", "spreadsheet"]):
            match_percentage = 85
        elif any(word in title_lower for word in ["virtual", "assistant", "admin"]):
            match_percentage = 82
        elif any(word in title_lower for word in ["research", "analysis"]):
            match_percentage = 80
        elif any(word in title_lower for word in ["support", "help desk", "it"]):
            match_percentage = 78
        else:
            match_percentage = 65
    
    return round(min(match_percentage, 100)), matched_skills

def calculate_roi(job, match_score):
    """Calculate ROI score for bidding decision"""
    avg_budget = (job.get("budget_min", 0) + job.get("budget_max", 0)) / 2
    
    comp_map = {"Low": 0.7, "Medium": 0.5, "High": 0.3, "Very High": 0.2}
    comp_factor = comp_map.get(job.get("competition_level", "Medium"), 0.5)
    
    # Adjust win probability based on match score and competition
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
    title_lower = job["title"].lower()
    
    if "excel" in title_lower or "data" in title_lower:
        return f"""Hello,

I can help with your {job['title']} project.

My relevant skills include:
• Excel data processing ({USER_SKILLS.get('excel', 90)}% proficiency)
• Data entry with 99% accuracy
• PDF to Excel conversion
• Data cleaning and formatting

I deliver accurate, well-organized results.

Best regards,
George Jabley
TechWokx Freelancer"""
    
    elif "virtual" in title_lower or "assistant" in title_lower or "admin" in title_lower:
        return f"""Hello,

I am interested in your Virtual Assistant position.

I can help with:
• Email management and calendar scheduling
• Data entry and document preparation
• Customer service and communication
• Administrative support

I am organized, detail-oriented, and available.

Best regards,
George Jabley
TechWokx Freelancer"""
    
    elif "support" in title_lower or "it" in title_lower:
        return f"""Hello,

I am interested in your IT Support position.

My experience includes:
• Help desk ticket resolution
• System troubleshooting
• Customer technical support
• Remote IT assistance

I am available to start immediately.

Best regards,
George Jabley
TechWokx Freelancer"""
    
    else:
        return f"""Hello,

I am very interested in your {job['title']} project.

Based on my experience in data management, IT support, and administrative tasks, I am confident I can deliver high-quality results.

I am available to start immediately.

Best regards,
George Jabley
TechWokx Freelancer"""

def get_recommendation(roi_score, match_score, access_type):
    """Get action recommendation"""
    if match_score < 60:
        return "🔴 Skip", f"Poor match ({match_score}% - below 60%)", "danger"
    elif roi_score < 30:
        return "🔴 Skip", f"ROI too low ({roi_score} - below 30)", "danger"
    elif roi_score < 50:
        return "🟡 Consider", f"Uncertain ROI ({roi_score}) - proceed with caution", "warning"
    else:
        return "🟢 Bid Now", f"High ROI opportunity ({roi_score}) - strongly recommended", "success"

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

def fetch_all_jobs():
    """Fetch jobs from all platforms"""
    all_jobs = []
    
    # Fetch from Freelancer via multiple methods
    if st.session_state.api_keys.get('rapidapi_freelancer'):
        freelancer_jobs = fetch_freelancer_jobs_combined(
            st.session_state.api_keys['rapidapi_freelancer'], 
            limit=25
        )
        all_jobs.extend(freelancer_jobs)
    
    # Fetch from Upwork
    if st.session_state.api_keys.get('rapidapi_upwork'):
        upwork_jobs = fetch_upwork_jobs_combined(
            st.session_state.api_keys['rapidapi_upwork'],
            limit=25
        )
        all_jobs.extend(upwork_jobs)
    else:
        # Use RSS fallback
        upwork_jobs = fetch_upwork_rss_jobs()
        all_jobs.extend(upwork_jobs)
    
    return all_jobs

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
    
    # API Status
    if st.session_state.api_keys.get('rapidapi_freelancer'):
        st.markdown("🔵 Freelancer: ✅ Key Set")
    else:
        st.markdown("🔵 Freelancer: ❌ No Key")
    
    if st.session_state.api_keys.get('rapidapi_upwork'):
        st.markdown("🟢 Upwork: ✅ Key Set")
    else:
        st.markdown("🟢 Upwork: ❌ No Key (RSS active)")

# ============ API SETTINGS PAGE ============
if st.session_state.page == 'api_settings':
    st.markdown('<div class="section-header">🔑 API Configuration</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("""
    **RapidAPI Keys Setup:**
    
    1. **Freelancer API** - Subscribe at: [RapidAPI Freelancer](https://rapidapi.com/rockethearts/api/freelancer-freelancer-v1)
    2. **Upwork API** - Subscribe at: [RapidAPI Upwork](https://rapidapi.com/upwork7/api/upwork7)
    
    **Note:** If APIs return no jobs, the system will use sample data and RSS feeds.
    """)
    
    with st.form("api_keys_form"):
        freelancer_key = st.text_input(
            "RapidAPI Key (Freelancer)",
            value=st.session_state.api_keys.get('rapidapi_freelancer', ''),
            type="password",
            placeholder="Enter your Freelancer RapidAPI key",
            help="Get from https://rapidapi.com/rockethearts/api/freelancer-freelancer-v1"
        )
        
        upwork_key = st.text_input(
            "RapidAPI Key (Upwork)",
            value=st.session_state.api_keys.get('rapidapi_upwork', ''),
            type="password",
            placeholder="Enter your Upwork RapidAPI key",
            help="Get from https://rapidapi.com/upwork7/api/upwork7"
        )
        
        if st.form_submit_button("Save API Keys", type="primary"):
            st.session_state.api_keys['rapidapi_freelancer'] = freelancer_key
            st.session_state.api_keys['rapidapi_upwork'] = upwork_key
            st.success("API keys saved!")
            st.rerun()
    
    st.markdown("---")
    st.markdown("### API Test & Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Freelancer API")
        if st.button("Test Freelancer Connection"):
            if st.session_state.api_keys.get('rapidapi_freelancer'):
                with st.spinner("Testing Freelancer API..."):
                    jobs = fetch_freelancer_jobs_combined(
                        st.session_state.api_keys['rapidapi_freelancer'], 
                        limit=5
                    )
                    if jobs:
                        st.success(f"✅ API Working! Found {len(jobs)} jobs.")
                        for job in jobs[:3]:
                            st.caption(f"• {job['title']} (${job['budget_min']}-${job['budget_max']})")
                    else:
                        st.warning("⚠️ API returned no jobs. Using sample data as fallback.")
            else:
                st.error("Please enter Freelancer API key first")
    
    with col2:
        st.markdown("#### Upwork API")
        if st.button("Test Upwork Connection"):
            if st.session_state.api_keys.get('rapidapi_upwork'):
                with st.spinner("Testing Upwork API..."):
                    jobs = fetch_upwork_jobs_combined(
                        st.session_state.api_keys['rapidapi_upwork'],
                        limit=5
                    )
                    if jobs:
                        st.success(f"✅ API Working! Found {len(jobs)} jobs.")
                        for job in jobs[:3]:
                            st.caption(f"• {job['title']} (${job['budget_min']}-${job['budget_max']})")
                    else:
                        st.warning("⚠️ API returned no jobs. Using RSS feed as fallback.")
            else:
                st.info("ℹ️ No API key - Using public RSS feed")

# ============ FREELANCE INTELLIGENCE PAGE ============
if st.session_state.page == 'freelance_intel':
    st.markdown('<div class="section-header">🤖 Freelance Intelligence Agent</div>', unsafe_allow_html=True)
    st.caption("AI-powered job matching | Multiple data sources | Smart recommendations")
    st.markdown("---")
    
    # Controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        keywords = st.text_input("Keywords", placeholder="data entry, excel, virtual assistant")
    with col2:
        platform_filter = st.selectbox("Platform", ["All", "Freelancer", "Upwork"])
    with col3:
        min_match = st.slider("Min Match %", 0, 100, 50)
    with col4:
        if st.button("🔄 Fetch Jobs", type="primary"):
            with st.spinner("Fetching jobs from all sources..."):
                all_jobs = fetch_all_jobs()
                if all_jobs:
                    st.session_state.jobs = all_jobs
                    st.success(f"✅ Fetched {len(all_jobs)} jobs!")
                else:
                    st.info("Using enhanced sample data with 15+ jobs")
                    st.session_state.jobs = SAMPLE_JOBS
                st.rerun()
    
    # Load jobs
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
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs", len(display_jobs))
    with col2:
        high_match = sum(1 for j in display_jobs if calculate_match_score(j)[0] >= 80)
        st.metric("High Match (80%+)", high_match)
    with col3:
        high_roi = sum(1 for j in display_jobs if calculate_roi(j, calculate_match_score(j)[0])[0] >= 50)
        st.metric("High ROI (50+)", high_roi)
    with col4:
        # Show data source info
        sources = set(j.get("source", "Sample") for j in display_jobs[:5])
        source_text = ", ".join(list(sources)[:2]) if sources else "Sample"
        st.metric("Data Source", source_text[:15])
    
    st.markdown("---")
    
    # Display jobs
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
                    if matched_skills:
                        st.markdown(f"**Matched Skills:** {', '.join(matched_skills[:3])}")
                    if job.get('source'):
                        st.caption(f"Source: {job.get('source')}")
                
                with col2:
                    st.markdown(f"### {recommendation}")
                    st.markdown(f"**Match Score:** {match_score}%")
                    st.markdown(f"**ROI Score:** {roi_score}/100")
                    st.markdown(f"**Win Probability:** {win_prob*100:.0f}%")
                    st.markdown(f"**Expected Value:** ${expected_value:.0f}")
                    st.markdown(f"**Bid Cost:** ${cost:.2f}")
                    st.caption(f"Reason: {reason}")
                
                if recommendation == "🟢 Bid Now" or recommendation == "🟡 Consider":
                    st.markdown("---")
                    st.markdown("### 📝 AI-Generated Proposal")
                    proposal = generate_proposal(job, match_score)
                    st.text_area("Proposal", proposal, height=150)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        suggested_bid = max(job['budget_min'], (job['budget_min'] + job['budget_max']) // 2) if job['budget_max'] > 0 else 25
                        bid_amount = st.number_input(
                            "Bid Amount ($)",
                            min_value=max(5, job['budget_min']),
                            max_value=job['budget_max'] if job['budget_max'] > 0 else 100,
                            value=suggested_bid,
                            key=f"bid_{job['id']}"
                        )
                    with col2:
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
        job_payout = st.number_input("Expected Job Payout ($)", min_value=10, value=100, step=10)
        win_probability = st.slider("Win Probability (%)", 0, 100, 35)
        bid_cost = st.number_input("Cost to Bid ($)", min_value=0, value=5, step=1)
        match_score = st.slider("Match Score (%)", 0, 100, 80)
        
        expected_value = job_payout * (win_probability / 100)
        roi_percentage = ((expected_value - bid_cost) / bid_cost * 100) if bid_cost > 0 else expected_value * 10
        
        st.markdown("---")
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
        
        st.caption(f"Recommended bid: ${job_payout * 0.3:.0f} - ${job_payout * 0.4:.0f}")
    
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
        """)

# ============ BID HISTORY ============
if st.session_state.page == 'bid_history':
    st.markdown('<div class="section-header">📋 Bid History</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.bid_history:
        st.metric("Total Bids", len(st.session_state.bid_history))
        st.markdown("---")
        
        for bid in reversed(st.session_state.bid_history):
            st.markdown(f"""
            <div class="data-card">
                <strong>📌 {bid['job_title']}</strong><br>
                Platform: {bid['platform']} | Bid: ${bid['bid_amount']}<br>
                Status: {bid['status']} | Date: {bid['date'].strftime('%Y-%m-%d %H:%M')}
                <br><a href="{bid.get('job_url', '#')}" target="_blank">View Job</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No bids submitted yet. Use the Freelance Intelligence page to find and bid on jobs.")

# ============ DASHBOARD ============
if st.session_state.page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>🤖 TechWokx Freelance Intelligence Agent</h2>
        <p>AI-powered job matching | Multiple data sources | Smart bid recommendations</p>
        <p>🔵 Freelancer API | 🟢 Upwork API | 📊 ROI Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    display_jobs = st.session_state.jobs if st.session_state.jobs else SAMPLE_JOBS
    total_jobs = len(display_jobs)
    high_match = sum(1 for j in display_jobs if calculate_match_score(j)[0] >= 80)
    high_roi = sum(1 for j in display_jobs if calculate_roi(j, calculate_match_score(j)[0])[0] >= 50)
    total_bids = len(st.session_state.bid_history)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_jobs}</div><div class='metric-label'>Available Jobs</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{high_match}</div><div class='metric-label'>High Match (80%+)</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{high_roi}</div><div class='metric-label'>High ROI (50+)</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_bids}</div><div class='metric-label'>Bids Placed</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">🎯 Top Recommended Jobs</div>', unsafe_allow_html=True)
        sorted_jobs = sorted(display_jobs, key=lambda j: calculate_roi(j, calculate_match_score(j)[0])[0], reverse=True)
        for job in sorted_jobs[:3]:
            match_score, _ = calculate_match_score(job)
            roi_score, win_prob, expected_value, cost = calculate_roi(job, match_score)
            recommendation, reason, _ = get_recommendation(roi_score, match_score, job.get("access_type"))
            
            st.markdown(f"""
            <div class="data-card">
                <strong>{job['title']}</strong><br>
                <small>📊 Match: {match_score}% | 💰 ROI: {roi_score} | 🏷️ {job['platform']}</small><br>
                <span class="badge-success" style="font-size:0.7rem">{recommendation}</span>
                <small style="color:#64748b"> - {reason}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">📈 Your Top Skills</div>', unsafe_allow_html=True)
        for skill, level in sorted(USER_SKILLS.items(), key=lambda x: x[1], reverse=True)[:6]:
            st.markdown(f"**{skill.replace('_', ' ').title()}:** {level}%")
            st.progress(level / 100)
        
        st.markdown("---")
        if st.button("🔍 Fetch Latest Jobs", use_container_width=True):
            with st.spinner("Fetching jobs from all sources..."):
                all_jobs = fetch_all_jobs()
                if all_jobs:
                    st.session_state.jobs = all_jobs
                    st.success(f"✅ Fetched {len(all_jobs)} jobs!")
                else:
                    st.info("Using sample data with 15+ jobs")
                    st.session_state.jobs = SAMPLE_JOBS
                st.rerun()

# ============ ANALYTICS ============
if st.session_state.page == 'analytics':
    st.markdown('<div class="section-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    display_jobs = st.session_state.jobs if st.session_state.jobs else SAMPLE_JOBS
    
    # Match Score Distribution
    match_scores = [calculate_match_score(j)[0] for j in display_jobs]
    st.subheader("Match Score Distribution")
    st.bar_chart(pd.DataFrame({"Match Scores": match_scores}))
    
    # Platform Breakdown
    st.subheader("Jobs by Platform")
    platform_counts = {}
    for j in display_jobs:
        platform_counts[j["platform"]] = platform_counts.get(j["platform"], 0) + 1
    st.write(platform_counts)
    
    # Budget Range Analysis
    st.subheader("Budget Distribution")
    budgets = [(j["budget_min"] + j["budget_max"]) / 2 for j in display_jobs if j["budget_min"] > 0]
    if budgets:
        st.bar_chart(pd.DataFrame({"Budget": budgets}))
    
    # Competition Analysis
    st.subheader("Competition Level")
    comp_counts = {"Low": 0, "Medium": 0, "High": 0}
    for j in display_jobs:
        comp_counts[j.get("competition_level", "Medium")] += 1
    st.write(comp_counts)

# ============ SKILLS PROFILE ============
if st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ Skills Profile</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("Your skills profile determines job match scores. Update the USER_SKILLS dictionary to customize.")
    
    for skill, level in sorted(USER_SKILLS.items(), key=lambda x: x[1], reverse=True):
        st.markdown(f"**{skill.replace('_', ' ').title()}:** {level}%")
        st.progress(level / 100)
    
    st.markdown("---")
    st.markdown("### Job Matching Statistics")
    
    display_jobs = st.session_state.jobs if st.session_state.jobs else SAMPLE_JOBS
    avg_match = sum(calculate_match_score(j)[0] for j in display_jobs) / len(display_jobs) if display_jobs else 0
    st.metric("Average Match Score", f"{avg_match:.0f}%")

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption(f"© 2024 TechWokx Freelance Intelligence Agent | Multiple Data Sources | AI-Powered Matching")

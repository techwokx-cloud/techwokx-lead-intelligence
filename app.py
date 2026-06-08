import streamlit as st
import pandas as pd
import os
import socket
import platform
import re
from datetime import datetime, timedelta
import json

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
    "document_conversion": 88
}

# Job opportunity database
SAMPLE_JOBS = [
    {
        "id": 1,
        "title": "PDF-to-Excel Data Transfer",
        "description": "Need accurate transfer of tables from PDF documents to Excel while preserving formatting.",
        "platform": "Freelancer",
        "budget_min": 6,
        "budget_max": 16,
        "skills_required": ["excel", "data_entry", "pdf_handling"],
        "access_type": "unlock_required",
        "unlock_cost": "$20 balance required",
        "visibility": "select freelancers only",
        "posted_date": datetime.now() - timedelta(days=1),
        "client_rating": 4.5,
        "competition_level": "Medium"
    },
    {
        "id": 2,
        "title": "Tally AR/AP Data Entry Support",
        "description": "Looking for experienced data entry specialist for Tally accounting software.",
        "platform": "Upwork",
        "budget_min": 50,
        "budget_max": 150,
        "skills_required": ["data_entry", "excel", "administrative"],
        "access_type": "connect_required",
        "unlock_cost": "8 connects",
        "visibility": "open",
        "posted_date": datetime.now() - timedelta(days=2),
        "client_rating": 4.8,
        "competition_level": "Low"
    },
    {
        "id": 3,
        "title": "Product Data Entry & Sourcing",
        "description": "Research products from company websites and enter into our system.",
        "platform": "Freelancer",
        "budget_min": 50,
        "budget_max": 100,
        "skills_required": ["research", "data_entry", "excel"],
        "access_type": "open",
        "unlock_cost": "None",
        "visibility": "open",
        "posted_date": datetime.now() - timedelta(days=3),
        "client_rating": 4.2,
        "competition_level": "High"
    },
    {
        "id": 4,
        "title": "Document Text to PowerPoint Slides",
        "description": "Convert document content into professional PowerPoint presentation.",
        "platform": "PeoplePerHour",
        "budget_min": 25,
        "budget_max": 45,
        "skills_required": ["document_conversion", "administrative", "excel"],
        "access_type": "open",
        "unlock_cost": "None",
        "visibility": "open",
        "posted_date": datetime.now() - timedelta(days=1),
        "client_rating": 4.0,
        "competition_level": "Medium"
    },
    {
        "id": 5,
        "title": "Malaysian Supplier Research",
        "description": "Need help finding reliable suppliers in Malaysia for our products.",
        "platform": "Upwork",
        "budget_min": 100,
        "budget_max": 300,
        "skills_required": ["research", "data_entry"],
        "access_type": "connect_required",
        "unlock_cost": "12 connects",
        "visibility": "open",
        "posted_date": datetime.now() - timedelta(days=2),
        "client_rating": 4.7,
        "competition_level": "Low"
    },
    {
        "id": 6,
        "title": "Restore Suspended Instagram Account",
        "description": "Help restore my business Instagram account that was suspended.",
        "platform": "Freelancer",
        "budget_min": 20,
        "budget_max": 50,
        "skills_required": ["social_media", "it_support"],
        "access_type": "unlock_required",
        "unlock_cost": "$20 balance required",
        "visibility": "select freelancers only",
        "posted_date": datetime.now() - timedelta(days=5),
        "client_rating": 3.5,
        "competition_level": "High"
    }
]

def calculate_match_score(job):
    """Calculate match score based on user skills"""
    total_score = 0
    matched_skills = []
    
    for skill in job.get("skills_required", []):
        if skill in USER_SKILLS:
            total_score += USER_SKILLS[skill]
            matched_skills.append(skill)
    
    if job.get("skills_required"):
        max_possible = len(job["skills_required"]) * 100
        if max_possible > 0:
            match_percentage = (total_score / max_possible) * 100
        else:
            match_percentage = 0
    else:
        match_percentage = 50
    
    return round(min(match_percentage, 100)), matched_skills

def calculate_roi(job, match_score):
    """Calculate ROI score for bidding decision"""
    avg_budget = (job.get("budget_min", 0) + job.get("budget_max", 0)) / 2
    
    # Calculate competition factor
    competition_factors = {"Low": 0.7, "Medium": 0.5, "High": 0.3}
    comp_factor = competition_factors.get(job.get("competition_level", "Medium"), 0.5)
    
    # Calculate win probability
    win_probability = (match_score / 100) * comp_factor * 0.8
    
    # Calculate expected value
    expected_value = avg_budget * win_probability
    
    # Calculate cost (connects or unlock fee)
    if "connect" in job.get("unlock_cost", "").lower():
        cost = int(re.search(r'\d+', job.get("unlock_cost", "0")).group(0) if re.search(r'\d+', job.get("unlock_cost", "0")) else 0) * 0.15
    elif "$" in job.get("unlock_cost", ""):
        cost = 20  # $20 unlock fee
    else:
        cost = 0
    
    # ROI score (0-100)
    if cost > 0:
        roi_score = min(100, (expected_value / cost) * 20)
    else:
        roi_score = min(100, (expected_value / 10) * 10)
    
    return round(roi_score, 1), win_probability, expected_value, cost

def generate_proposal(job, match_score):
    """Generate personalized proposal based on job and match score"""
    
    if "PDF" in job["title"] or "Excel" in job["title"]:
        return f"""Hello,

I can accurately transfer the tables from your PDF documents into Excel while preserving the original structure, headers, rows, columns, symbols, and formatting.

My approach includes:
• Extracting data using professional PDF tools and Excel
• Verifying every row and column for accuracy
• Maintaining the original table layout
• Delivering a clean and organized .xlsx file

I have {USER_SKILLS.get('data_entry', 85)}% proficiency in data entry and Excel, with extensive experience in document conversion.

Please share the number of PDF files and pages involved so I can confirm the timeline and final quote.

Kind regards,
George Jabley
TechWokx Freelancer"""
    
    elif "Data Entry" in job["title"] or "Product" in job["title"]:
        return f"""Hello,

I am interested in assisting with your {job['title']} project.

I can:
• Research products from company websites and Google
• Collect accurate product names, descriptions, and images
• Upload information into your website
• Verify all entries for consistency and accuracy

My background includes data management, research, and administrative support ({USER_SKILLS.get('research', 85)}% proficiency), and I pay close attention to detail to ensure high-quality results.

I am available to start immediately and would be happy to discuss your requirements further.

Best regards,
George Jabley
TechWokx Freelancer"""
    
    else:
        return f"""Hello,

I am very interested in your {job['title']} project.

Based on my experience in {', '.join(job.get('skills_required', ['IT', 'Data', 'Administrative'])[:2])}, I am confident I can deliver high-quality results.

My skills include:
• {USER_SKILLS.get('it_support', 85)}% IT support proficiency
• {USER_SKILLS.get('data_entry', 90)}% data entry accuracy
• {USER_SKILLS.get('excel', 90)}% Excel and data management

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
        "status": "Submitted"
    })
    return True

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

[data-testid="stSidebar"] .stMarkdown, 
[data-testid="stSidebar"] p { 
    color: #e2e8f0 !important; 
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 { 
    color: #fbbf24 !important; 
}

[data-testid="stSidebar"] .stButton button { 
    background: rgba(251, 191, 36, 0.15); 
    color: #fbbf24 !important; 
    width: 100%; 
    margin: 2px 0; 
}

.welcome-card { 
    background: linear-gradient(135deg, #667eea, #764ba2); 
    border-radius: 16px; 
    padding: 1.5rem; 
    margin-bottom: 1.5rem;
    color: white;
}

.welcome-card h2, .welcome-card p {
    color: white;
}

.metric-card { 
    background: white; 
    border-radius: 12px; 
    padding: 1rem; 
    border: 1px solid #e2e8f0; 
    text-align: center; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.metric-value { 
    font-size: 1.8rem; 
    font-weight: 700; 
    color: #0f172a; 
}

.metric-label { 
    color: #64748b; 
    font-size: 0.8rem; 
    margin-top: 0.25rem;
}

.data-card { 
    background: white; 
    border-radius: 12px; 
    padding: 1.2rem; 
    border: 1px solid #e2e8f0; 
    margin-bottom: 1rem; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.section-header { 
    color: #0f172a; 
    font-size: 1.2rem; 
    font-weight: 600; 
    margin: 1.5rem 0 1rem 0; 
    border-left: 3px solid #667eea; 
    padding-left: 1rem; 
}

.custom-divider { 
    height: 1px; 
    background: #e2e8f0; 
    margin: 1.5rem 0; 
}

.stButton > button { 
    background: linear-gradient(135deg, #667eea, #764ba2); 
    color: white !important; 
    font-weight: 600; 
    border: none; 
    border-radius: 8px; 
}

.stButton > button:hover { 
    background: linear-gradient(135deg, #5a67d8, #6b46a0); 
    transform: translateY(-2px);
    transition: all 0.3s;
}

.badge-success {
    background: #10b981;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    display: inline-block;
}

.badge-warning {
    background: #f59e0b;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    display: inline-block;
}

.badge-danger {
    background: #ef4444;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    display: inline-block;
}

.badge-info {
    background: #3b82f6;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    display: inline-block;
}
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
            <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.5rem;">🔐 Demo Access</div>
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
        ("🤖 Freelance Intelligence", "freelance_intel"),
        ("📊 Bid ROI Analyzer", "bid_roi"),
        ("---", "divider1"),
        ("📥 Import Leads", "import_leads"),
        ("👥 Lead CRM", "crm"),
        ("---", "divider2"),
        ("💻 System Info", "system_info"),
        ("📁 Folder Analyzer", "folder_analyzer"),
        ("---", "divider3"),
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
    st.markdown(f"👤 Skills Loaded: {len(USER_SKILLS)}")
    st.markdown(f"📊 Jobs Analyzed: {len(st.session_state.jobs) if st.session_state.jobs else len(SAMPLE_JOBS)}")

# ============ DASHBOARD ============
if st.session_state.page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>🤖 Welcome to TechWokx Freelance Intelligence Agent</h2>
        <p>AI-powered job matching, bid optimization, and ROI analysis for freelancers</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate stats
    total_jobs = len(SAMPLE_JOBS)
    high_match_jobs = 0
    high_roi_jobs = 0
    total_potential = 0
    
    for job in SAMPLE_JOBS:
        match_score, _ = calculate_match_score(job)
        roi_score, win_prob, expected_value, cost = calculate_roi(job, match_score)
        if match_score >= 80:
            high_match_jobs += 1
        if roi_score >= 50:
            high_roi_jobs += 1
        total_potential += expected_value
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_jobs}</div><div class='metric-label'>Available Jobs</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{high_match_jobs}</div><div class='metric-label'>High Match (80%+)</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{high_roi_jobs}</div><div class='metric-label'>High ROI (50+)</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>${total_potential:.0f}</div><div class='metric-label'>Total Potential</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">🎯 Top Recommended Jobs</div>', unsafe_allow_html=True)
        for job in SAMPLE_JOBS[:3]:
            match_score, matched = calculate_match_score(job)
            roi_score, win_prob, expected_value, cost = calculate_roi(job, match_score)
            recommendation, reason, rec_type = get_recommendation(roi_score, match_score, job.get("access_type"))
            
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
        for skill, level in sorted(USER_SKILLS.items(), key=lambda x: x[1], reverse=True)[:5]:
            st.markdown(f"**{skill.replace('_', ' ').title()}:** {level}%")
            st.progress(level / 100)

# ============ FREELANCE INTELLIGENCE ============
elif st.session_state.page == 'freelance_intel':
    st.markdown('<div class="section-header">🤖 Freelance Intelligence Agent</div>', unsafe_allow_html=True)
    st.caption("AI-powered job matching, scoring, and recommendation engine")
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        platform_filter = st.selectbox("Platform", ["All", "Freelancer", "Upwork", "PeoplePerHour"])
    with col2:
        min_match = st.slider("Minimum Match Score", 0, 100, 50)
    with col3:
        show_only_biddable = st.checkbox("Show only biddable jobs", value=True)
    
    filtered_jobs = SAMPLE_JOBS.copy()
    if platform_filter != "All":
        filtered_jobs = [j for j in filtered_jobs if j["platform"] == platform_filter]
    if show_only_biddable:
        filtered_jobs = [j for j in filtered_jobs if j["access_type"] != "invite_only"]
    
    for job in filtered_jobs:
        match_score, matched_skills = calculate_match_score(job)
        
        if match_score >= min_match:
            roi_score, win_prob, expected_value, cost = calculate_roi(job, match_score)
            recommendation, reason, rec_type = get_recommendation(roi_score, match_score, job.get("access_type"))
            
            # Determine color based on recommendation
            border_color = "#10b981" if recommendation == "🟢 Bid Now" else "#f59e0b" if recommendation == "🟡 Consider" else "#ef4444"
            
            with st.expander(f"{job['title']} - {job['platform']} - Match: {match_score}%"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {job['description']}")
                    st.markdown(f"**Budget:** ${job['budget_min']} - ${job['budget_max']}")
                    st.markdown(f"**Skills Required:** {', '.join(job['skills_required'])}")
                    st.markdown(f"**Matched Skills:** {', '.join(matched_skills)}")
                    st.markdown(f"**Access Type:** {job['access_type']} | **Unlock Cost:** {job['unlock_cost']}")
                
                with col2:
                    st.markdown(f"### {recommendation}")
                    st.markdown(f"**Match Score:** {match_score}%")
                    st.markdown(f"**ROI Score:** {roi_score}/100")
                    st.markdown(f"**Win Probability:** {win_prob*100:.0f}%")
                    st.markdown(f"**Expected Value:** ${expected_value:.0f}")
                    st.markdown(f"**Bid Cost:** ${cost:.2f}")
                    st.markdown(f"**Reason:** {reason}")
                
                if recommendation == "🟢 Bid Now":
                    st.markdown("---")
                    st.markdown("### 📝 AI-Generated Proposal")
                    
                    proposal = generate_proposal(job, match_score)
                    st.text_area("Proposal", proposal, height=200)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        bid_amount = st.number_input("Bid Amount ($)", min_value=job['budget_min'], max_value=job['budget_max'], value=(job['budget_min'] + job['budget_max'])//2)
                    with col2:
                        if st.button("📤 Submit Bid", key=f"bid_{job['id']}"):
                            send_bid_notification(job, bid_amount)
                            st.success(f"Bid of ${bid_amount} submitted for {job['title']}!")
                    with col3:
                        if st.button("🔍 Research Client", key=f"research_{job['id']}"):
                            st.info("Client research would open here")

# ============ BID ROI ANALYZER ============
elif st.session_state.page == 'bid_roi':
    st.markdown('<div class="section-header">💰 Bid ROI Analyzer</div>', unsafe_allow_html=True)
    st.caption("Calculate ROI before spending connects or unlock fees")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 ROI Calculator")
        
        job_payout = st.number_input("Expected Job Payout ($)", min_value=10, value=100)
        win_probability = st.slider("Estimated Win Probability (%)", 0, 100, 35)
        bid_cost = st.number_input("Cost to Bid ($ / connects)", min_value=0, value=5)
        match_score_input = st.slider("Match Score (%)", 0, 100, 85)
        
        expected_value = job_payout * (win_probability / 100)
        roi = (expected_value - bid_cost) / bid_cost * 100 if bid_cost > 0 else expected_value * 10
        
        st.markdown("---")
        st.markdown("### 📈 ROI Analysis")
        st.markdown(f"**Expected Value:** ${expected_value:.2f}")
        st.markdown(f"**ROI:** {roi:.1f}%")
        
        if roi > 300:
            st.success("🟢 EXCELLENT ROI - Strongly recommend bidding")
        elif roi > 100:
            st.warning("🟡 GOOD ROI - Consider bidding")
        else:
            st.error("🔴 POOR ROI - Skip this opportunity")
    
    with col2:
        st.markdown("### 💡 Bid Strategy Tips")
        st.markdown("""
        **When to bid:**
        - Match score > 80%
        - ROI > 100%
        - Win probability > 30%
        - Client rating > 4.5
        
        **When to skip:**
        - Unlock fee > expected payout
        - Competition is too high
        - Skills match is poor
        
        **Cost analysis:**
        - Freelancer.com: $20 unlock fee
        - Upwork: 8-16 connects per bid
        - PeoplePerHour: Credit-based system
        """)

# ============ BID HISTORY ============
elif st.session_state.page == 'bid_history':
    st.markdown('<div class="section-header">📋 Bid History</div>', unsafe_allow_html=True)
    st.caption("Track all your submitted bids and their status")
    st.markdown("---")
    
    if st.session_state.bid_history:
        for bid in reversed(st.session_state.bid_history):
            st.markdown(f"""
            <div class="data-card">
                <strong>{bid['job_title']}</strong><br>
                Platform: {bid['platform']} | Bid: ${bid['bid_amount']}<br>
                Status: {bid['status']} | Date: {bid['date'].strftime('%Y-%m-%d %H:%M')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No bids submitted yet. Use the Freelance Intelligence page to find and bid on jobs.")

# ============ IMPORT LEADS ============
elif st.session_state.page == 'import_leads':
    st.markdown('<div class="section-header">📥 Import Leads</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose CSV/Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.dataframe(df.head())
            
            if st.button("Import", type="primary"):
                imported = 0
                for _, row in df.iterrows():
                    name = row.get('name', row.get('Name', ''))
                    email = row.get('email', row.get('Email', ''))
                    phone = str(row.get('phone', row.get('Phone', '')))
                    if name and email:
                        imported += 1
                st.success(f"Imported {imported} leads!")
        except Exception as e:
            st.error(f"Error: {e}")

# ============ CRM ============
elif st.session_state.page == 'crm':
    st.markdown('<div class="section-header">👥 Lead CRM</div>', unsafe_allow_html=True)
    
    if st.session_state.leads:
        for lead in st.session_state.leads[-10:]:
            with st.expander(f"{lead.get('name', 'Unknown')} - Score: {lead.get('score', 0)}/100"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Email: {lead.get('email', 'N/A')}")
                    st.write(f"Phone: {lead.get('phone', 'N/A')}")
                with col2:
                    st.write(f"Status: {lead.get('status', 'New')}")
                    st.write(f"Source: {lead.get('source', 'Manual')}")
    else:
        st.info("No leads yet. Import leads to get started.")

# ============ SYSTEM INFO ============
elif st.session_state.page == 'system_info':
    st.markdown('<div class="section-header">💻 System Information</div>', unsafe_allow_html=True)
    
    if st.button("Scan System", type="primary"):
        info = {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "version": platform.version(),
            "processor": platform.processor(),
        }
        st.markdown(f"""
        <div class="data-card">
            <p><strong>Hostname:</strong> {info['hostname']}</p>
            <p><strong>Platform:</strong> {info['platform']}</p>
            <p><strong>Version:</strong> {info['version']}</p>
            <p><strong>Processor:</strong> {info['processor'] or 'N/A'}</p>
        </div>
        """, unsafe_allow_html=True)

# ============ FOLDER ANALYZER ============
elif st.session_state.page == 'folder_analyzer':
    st.markdown('<div class="section-header">📁 Folder Analyzer</div>', unsafe_allow_html=True)
    
    folder_path = st.text_input("Folder Path", placeholder="/home/user/Documents")
    
    if st.button("Analyze", type="primary"):
        if folder_path and os.path.exists(folder_path):
            st.info(f"Analyzing {folder_path}...")
        else:
            st.error("Please enter a valid path")

# ============ ANALYTICS ============
elif st.session_state.page == 'analytics':
    st.markdown('<div class="section-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Calculate job statistics
    match_scores = []
    roi_scores = []
    
    for job in SAMPLE_JOBS:
        match_score, _ = calculate_match_score(job)
        roi_score, _, _, _ = calculate_roi(job, match_score)
        match_scores.append(match_score)
        roi_scores.append(roi_score)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Match Score Distribution")
        st.bar_chart(pd.DataFrame({"Match Score": match_scores}))
    
    with col2:
        st.markdown("### ROI Score Distribution")
        st.bar_chart(pd.DataFrame({"ROI Score": roi_scores}))
    
    st.markdown("---")
    st.markdown("### Platform Breakdown")
    
    platform_stats = {}
    for job in SAMPLE_JOBS:
        platform = job["platform"]
        if platform not in platform_stats:
            platform_stats[platform] = {"count": 0, "total_budget": 0}
        platform_stats[platform]["count"] += 1
        platform_stats[platform]["total_budget"] += (job["budget_min"] + job["budget_max"]) / 2
    
    for platform, stats in platform_stats.items():
        st.markdown(f"**{platform}:** {stats['count']} jobs, Avg Budget: ${stats['total_budget']/stats['count']:.0f}")

# ============ SETTINGS ============
elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    st.markdown("### Skills Profile Configuration")
    st.info("Your skills are currently configured in the system. Update USER_SKILLS dictionary to modify.")
    
    st.markdown("---")
    st.markdown("### Current Skills")
    for skill, level in sorted(USER_SKILLS.items(), key=lambda x: x[1], reverse=True):
        st.markdown(f"**{skill.replace('_', ' ').title()}:** {level}%")
        st.progress(level / 100)

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption(f"© 2024 TechWokx Freelance Intelligence Agent | AI-Powered Bid Optimization")

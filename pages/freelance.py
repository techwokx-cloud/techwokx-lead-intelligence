import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="TechWokx Freelance Jobs",
    page_icon="💼",
    layout="wide"
)

# Session state for freelance module
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'bid_history' not in st.session_state:
    st.session_state.bid_history = []

# CSS for freelance page
st.markdown("""
<style>
.stApp { background: #f8fafc; }
[data-testid="stSidebar"] { background: #0f172a; }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #e2e8f0; }
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

# User skills profile for job matching
USER_SKILLS = {
    "data_entry": 95,
    "excel": 95,
    "research": 85,
    "administrative": 85,
    "virtual_assistant": 85,
    "pdf_handling": 90,
    "web_scraping": 75,
    "data_analysis": 80
}

# ============ JOB SEARCH FUNCTIONS ============
def search_freelance_jobs(keyword="data entry"):
    """Search for freelance jobs from multiple platforms"""
    jobs = [
        {
            "id": 1,
            "title": f"{keyword.title()} Specialist - Remote",
            "description": f"We need an experienced {keyword} specialist for ongoing work. Attention to detail required.",
            "platform": "Upwork",
            "budget_min": 15,
            "budget_max": 25,
            "budget_type": "hourly",
            "skills": [keyword, "excel", "attention to detail"],
            "posted": "2 hours ago",
            "proposals": "5-10",
            "client_rating": 4.8,
            "url": "https://www.upwork.com/jobs/sample"
        },
        {
            "id": 2,
            "title": f"Large {keyword.title()} Project - 5000 records",
            "description": f"Looking for someone to handle {keyword} for a large dataset. Must be accurate and fast.",
            "platform": "Freelancer",
            "budget_min": 200,
            "budget_max": 400,
            "budget_type": "fixed",
            "skills": [keyword, "data_analysis", "excel"],
            "posted": "1 day ago",
            "proposals": "20-30",
            "client_rating": 4.2,
            "url": "https://www.freelancer.com/projects/sample"
        },
        {
            "id": 3,
            "title": f"Virtual Assistant with {keyword.title()} Skills",
            "description": f"Need VA with strong {keyword} background for administrative tasks and data management.",
            "platform": "Upwork",
            "budget_min": 10,
            "budget_max": 20,
            "budget_type": "hourly",
            "skills": [keyword, "virtual_assistant", "administrative"],
            "posted": "3 hours ago",
            "proposals": "15-20",
            "client_rating": 4.5,
            "url": "https://www.upwork.com/jobs/sample2"
        },
        {
            "id": 4,
            "title": f"Excel & {keyword.title()} Expert Needed",
            "description": f"Looking for expert in Excel and {keyword} for business reporting.",
            "platform": "Freelancer",
            "budget_min": 50,
            "budget_max": 100,
            "budget_type": "fixed",
            "skills": ["excel", keyword, "data_analysis"],
            "posted": "5 hours ago",
            "proposals": "10-15",
            "client_rating": 4.0,
            "url": "https://www.freelancer.com/projects/sample3"
        },
        {
            "id": 5,
            "title": f"Research Assistant - {keyword.title()}",
            "description": f"Need research assistant for {keyword} projects. Must have excellent research skills.",
            "platform": "Upwork",
            "budget_min": 20,
            "budget_max": 30,
            "budget_type": "hourly",
            "skills": ["research", keyword],
            "posted": "1 day ago",
            "proposals": "8-12",
            "client_rating": 4.7,
            "url": "https://www.upwork.com/jobs/sample4"
        }
    ]
    return jobs

def calculate_match_score(job):
    """Calculate match score based on user skills"""
    total_score = 0
    matched = []
    for skill in job.get("skills", []):
        if skill in USER_SKILLS:
            total_score += USER_SKILLS[skill]
            matched.append(skill)
    
    if job.get("skills"):
        max_score = len(job["skills"]) * 100
        match = (total_score / max_score) * 100 if max_score > 0 else 50
    else:
        match = 50
    
    return min(int(match), 100), matched

def generate_proposal(job, match_score):
    """Generate proposal for job"""
    return f"""Dear Client,

I am very interested in your {job['title']} position.

Based on my skills and experience, I am confident I can deliver high-quality results:

**My Relevant Skills:**
{chr(10).join([f'• {skill.replace("_", " ").title()}: {USER_SKILLS.get(skill, 0)}%' for skill in job.get("skills", []) if skill in USER_SKILLS])}

**Why Choose Me:**
• Fast turnaround (24-48 hours)
• 100% accuracy guarantee
• Available for ongoing work
• Excellent communication

**My Process:**
1. Review requirements thoroughly
2. Complete work with attention to detail
3. Deliver organized, error-free results
4. Provide revisions if needed

I am available to start immediately.

Best regards,
George Jabley
TechWokx Freelancer
"""

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### 💼 TechWokx")
    st.markdown("#### Freelance Intelligence")
    st.markdown("---")
    st.markdown(f"Welcome back")
    st.markdown("---")
    st.markdown(f"👤 Skills: {len(USER_SKILLS)}")
    st.markdown(f"🎯 Jobs: {len(st.session_state.jobs)}")
    st.markdown(f"📊 Bids: {len(st.session_state.bid_history)}")
    st.markdown("---")
    if st.button("← Back to Main App", use_container_width=True):
        st.switch_page("app.py")

# ============ MAIN CONTENT ============
st.markdown('<div class="welcome-card"><h2>💼 Freelance Intelligence Agent</h2><p>AI-powered job matching | Smart bid recommendations | Proposal generator</p></div>', unsafe_allow_html=True)

# Search controls
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    keyword = st.text_input("Job Keyword", value="data entry", placeholder="data entry, excel, virtual assistant")
with col2:
    min_match = st.slider("Min Match %", 0, 100, 50)
with col3:
    if st.button("🔍 Search Jobs", type="primary"):
        with st.spinner("Searching for jobs..."):
            jobs = search_freelance_jobs(keyword)
            st.session_state.jobs = jobs
            st.success(f"Found {len(jobs)} jobs")
            st.rerun()

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Statistics
if st.session_state.jobs:
    display_jobs = st.session_state.jobs
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs", len(display_jobs))
    with col2:
        high_match = sum(1 for j in display_jobs if calculate_match_score(j)[0] >= 80)
        st.metric("High Match (80%+)", high_match)
    with col3:
        st.metric("Ready to Bid", len([j for j in display_jobs if calculate_match_score(j)[0] >= 70]))

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Display jobs
    for job in display_jobs:
        match_score, matched_skills = calculate_match_score(job)
        
        if match_score >= min_match:
            # Calculate bid recommendation
            avg_budget = (job['budget_min'] + job['budget_max']) / 2
            recommended_bid = avg_budget * 0.4 if job['budget_type'] == 'hourly' else avg_budget * 0.6
            
            with st.expander(f"[{job['platform']}] {job['title']} - Match: {match_score}% - Budget: ${job['budget_min']}-${job['budget_max']} ({job['budget_type']})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {job['description']}")
                    st.markdown(f"**Skills Required:** {', '.join(job['skills'])}")
                    st.markdown(f"**Posted:** {job['posted']}")
                    st.markdown(f"**Proposals:** {job['proposals']}")
                    st.markdown(f"**Client Rating:** ⭐ {job['client_rating']}/5")
                    if matched_skills:
                        st.markdown(f"**Matched Skills:** {', '.join(matched_skills)}")
                
                with col2:
                    st.markdown(f"### Match Score: {match_score}%")
                    st.markdown(f"**Recommended Bid:** ${recommended_bid:.0f}")
                    st.markdown(f"**Competition:** {job['proposals']}")
                    if match_score >= 80:
                        st.success("🟢 High Match - Strongly Recommended")
                    elif match_score >= 60:
                        st.warning("🟡 Good Match - Consider Bidding")
                    else:
                        st.error("🔴 Low Match - Skip")
                
                # Proposal section
                st.markdown("---")
                st.markdown("### 📝 Your Proposal")
                
                proposal = generate_proposal(job, match_score)
                edited_proposal = st.text_area("Edit Proposal", proposal, height=250, key=f"proposal_{job['id']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    bid_amount = st.number_input("Bid Amount ($)", min_value=float(job['budget_min']), max_value=float(job['budget_max']), value=float(recommended_bid), step=5.0, key=f"bid_{job['id']}")
                with col2:
                    if st.button(f"💾 Save Bid Draft", key=f"save_{job['id']}"):
                        st.session_state.bid_history.append({
                            "job_title": job['title'],
                            "platform": job['platform'],
                            "bid_amount": bid_amount,
                            "date": datetime.now().isoformat(),
                            "status": "Draft",
                            "proposal": edited_proposal[:200]
                        })
                        st.success(f"Bid draft saved for {job['title']}!")
                with col3:
                    if st.button(f"📤 Submit Bid", key=f"submit_{job['id']}", type="primary"):
                        st.session_state.bid_history.append({
                            "job_title": job['title'],
                            "platform": job['platform'],
                            "bid_amount": bid_amount,
                            "date": datetime.now().isoformat(),
                            "status": "Submitted",
                            "proposal": edited_proposal[:200],
                            "job_url": job.get('url')
                        })
                        st.balloons()
                        st.success(f"Bid of ${bid_amount:.2f} submitted for {job['title']}!")
                        st.info("Navigate to the job platform to complete the submission.")
                        if job.get('url'):
                            st.markdown(f"[View Job on {job['platform']}]({job['url']})")
else:
    st.info("Enter a keyword and click 'Search Jobs' to find freelance opportunities")

# ============ BID HISTORY ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header">📋 My Bid History</div>', unsafe_allow_html=True)

if st.session_state.bid_history:
    for bid in reversed(st.session_state.bid_history[-10:]):
        st.markdown(f"""
        <div class="data-card">
            <strong>{bid['job_title']}</strong><br>
            Platform: {bid['platform']} | Bid: ${bid['bid_amount']:.2f}<br>
            Status: {bid['status']} | Date: {bid['date'][:19]}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No bids yet. Search for jobs and save or submit bids.")

# ============ SKILLS PROFILE ============
with st.expander("📊 Your Skills Profile"):
    for skill, level in sorted(USER_SKILLS.items(), key=lambda x: x[1], reverse=True):
        st.markdown(f"**{skill.replace('_', ' ').title()}:** {level}%")
        st.progress(level / 100)

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("2024 TechWokx Freelance Intelligence | Find, Match, and Win More Jobs")
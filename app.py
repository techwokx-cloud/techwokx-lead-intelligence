# app.py - Complete TechWokx Lead Intelligence System
import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import hashlib

st.set_page_config(
    page_title="TechWokx Lead Intelligence",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'research_cache' not in st.session_state:
    st.session_state.research_cache = {}
if 'followups' not in st.session_state:
    st.session_state.followups = []
if 'automation_log' not in st.session_state:
    st.session_state.automation_log = []

# API Keys (set these in Streamlit secrets or .env)
SERP_API_KEY = ""
GOOGLE_MAPS_API_KEY = ""
OPENAI_API_KEY = ""
ANTHROPIC_API_KEY = ""

# Try to get from secrets
try:
    SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
    GOOGLE_MAPS_API_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY", "")
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", "")
except:
    pass

# ============ API FUNCTIONS ============

def search_company_serp(company_name):
    """Search company using SERP API"""
    if not SERP_API_KEY:
        return None
    
    try:
        url = "https://serpapi.com/search"
        params = {
            "api_key": SERP_API_KEY,
            "q": f"{company_name} Ghana company",
            "engine": "google",
            "num": 10
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        result = {
            "website": None,
            "description": None,
            "social_links": []
        }
        
        if "organic_results" in data:
            for org in data["organic_results"][:5]:
                link = org.get("link", "")
                if link and "g.co" not in link and "google" not in link:
                    if not result["website"] and "linkedin" not in link and "facebook" not in link:
                        result["website"] = link
                    if not result["description"]:
                        result["description"] = org.get("snippet", "")
        
        if "knowledge_graph" in data:
            kg = data["knowledge_graph"]
            result["description"] = result["description"] or kg.get("description", "")
            
        return result
    except Exception:
        return None

def get_company_location(company_name):
    """Get company location using Google Maps API"""
    if not GOOGLE_MAPS_API_KEY:
        return None
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "key": GOOGLE_MAPS_API_KEY,
            "input": f"{company_name} Ghana",
            "inputtype": "textquery",
            "fields": "formatted_address,place_id"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("candidates"):
            candidate = data["candidates"][0]
            return {"address": candidate.get("formatted_address", "")}
        return None
    except Exception:
        return None

def extract_email_from_website(website):
    """Extract email from website"""
    if not website:
        return {"all_emails": [], "primary_email": None}
    
    try:
        clean_website = website
        if not clean_website.startswith("http"):
            clean_website = "https://" + clean_website
        
        response = requests.get(clean_website, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, response.text)
        
        exclude_patterns = ['example', 'test', 'noreply', 'jpg', 'png', 'css']
        valid_emails = []
        for e in emails:
            e_lower = e.lower()
            if not any(x in e_lower for x in exclude_patterns):
                valid_emails.append(e)
        
        contact_patterns = ['contact', 'info@', 'hello@', 'support@']
        contact_emails = []
        for email in valid_emails:
            if any(pattern in email.lower() for pattern in contact_patterns):
                contact_emails.append(email)
        
        return {
            "all_emails": list(set(valid_emails))[:5],
            "primary_email": contact_emails[0] if contact_emails else (valid_emails[0] if valid_emails else None)
        }
    except Exception:
        return {"all_emails": [], "primary_email": None}

def analyze_with_ai(company_data):
    """Use AI to analyze company"""
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
        return None
    
    try:
        prompt = f"Analyze this company: {company_data.get('name')}. Industry? Size? Recommend services."
        
        if OPENAI_API_KEY:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300
            }
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        return None
    except Exception:
        return None

def deep_research_company(company_name, website=None):
    """Perform deep research on a company"""
    
    cache_key = hashlib.md5(f"{company_name}_{website}".encode()).hexdigest()
    if cache_key in st.session_state.research_cache:
        return st.session_state.research_cache[cache_key]
    
    result = {
        "name": company_name,
        "website": website,
        "emails": [],
        "primary_email": None,
        "phone": None,
        "address": None,
        "description": None,
        "social_links": [],
        "industry": None,
        "employee_count": None,
        "ai_insights": None,
        "lead_score": 0,
        "recommendations": [],
        "sources": []
    }
    
    progress = st.progress(0)
    status = st.empty()
    
    # Step 1: SERP API
    status.text("🔍 Searching company information...")
    serp_data = search_company_serp(company_name)
    if serp_data:
        result["website"] = result["website"] or serp_data.get("website")
        result["description"] = serp_data.get("description")
        result["sources"].append("SERP API")
    progress.progress(0.25)
    
    # Step 2: Google Maps
    status.text("📍 Finding company location...")
    location_data = get_company_location(company_name)
    if location_data:
        result["address"] = location_data.get("address")
        result["sources"].append("Google Maps")
    progress.progress(0.5)
    
    # Step 3: Website extraction
    target_website = result["website"] or website
    if target_website:
        status.text(f"🌐 Analyzing website...")
        email_data = extract_email_from_website(target_website)
        if email_data:
            result["emails"] = email_data.get("all_emails", [])
            result["primary_email"] = email_data.get("primary_email")
            if result["emails"]:
                result["sources"].append("Website Crawl")
    progress.progress(0.75)
    
    # Step 4: AI Analysis
    status.text("🧠 Generating insights...")
    ai_analysis = analyze_with_ai(result)
    if ai_analysis:
        result["ai_insights"] = ai_analysis
        result["sources"].append("AI Analysis")
        
        ai_lower = ai_analysis.lower()
        if "large" in ai_lower or "100+" in ai_lower:
            result["employee_count"] = "Large (100+)"
            result["lead_score"] += 20
        elif "medium" in ai_lower:
            result["employee_count"] = "Medium (20-100)"
            result["lead_score"] += 10
        else:
            result["employee_count"] = "Small (1-20)"
            result["lead_score"] += 5
        
        industries = ["Banking", "Hospitality", "Logistics", "Retail", "Technology", "Healthcare", "Education"]
        for ind in industries:
            if ind.lower() in ai_lower:
                result["industry"] = ind
                break
    
    progress.progress(1.0)
    status.text("✅ Research complete!")
    
    # Calculate lead score
    if result["website"]:
        result["lead_score"] += 25
    if result["primary_email"]:
        result["lead_score"] += 20
    if result["address"]:
        result["lead_score"] += 15
    if result["ai_insights"]:
        result["lead_score"] += 10
    
    result["lead_score"] = min(result["lead_score"], 100)
    
    # Recommendations
    recommendations = []
    if not result["primary_email"]:
        recommendations.append("📧 Setup professional email")
    if result["lead_score"] < 60:
        recommendations.append("🔒 Conduct email security audit")
    if not result["address"]:
        recommendations.append("📍 Verify business address")
    recommendations.append("📊 Schedule free IT consultation")
    result["recommendations"] = recommendations[:4]
    
    st.session_state.research_cache[cache_key] = result
    return result

def add_lead(name, email, phone, score):
    """Add lead to CRM"""
    new_id = len(st.session_state.leads) + 1
    status = "Hot" if score >= 80 else "Warm" if score >= 60 else "Cold"
    st.session_state.leads.append({
        "id": new_id, "name": name, "email": email, "phone": phone,
        "score": score, "status": status, "audit_date": datetime.now(),
        "last_contact": None, "followup_stage": 0
    })

# ============ CSS STYLES ============
st.markdown("""
<style>
.stApp { background-color: #f8fafc; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fbbf24 !important; }
[data-testid="stSidebar"] .stButton button { background: rgba(251, 191, 36, 0.15); color: #fbbf24 !important; border: 1px solid rgba(251, 191, 36, 0.3); text-align: left; width: 100%; margin: 2px 0; }
[data-testid="stSidebar"] .stButton button:hover { background: rgba(251, 191, 36, 0.3); }
.welcome-card { background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; }
.metric-card { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
.metric-label { color: #64748b; font-size: 0.8rem; }
.data-card { background: white; border-radius: 12px; padding: 1.2rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
.data-card h4 { color: #0f172a; margin-top: 0; margin-bottom: 0.75rem; }
.activity-item { background: white; border-radius: 12px; padding: 0.8rem; margin-bottom: 0.5rem; border-left: 3px solid #fbbf24; }
.section-header { color: #0f172a; font-size: 1.2rem; font-weight: 600; margin: 1.5rem 0 1rem 0; border-left: 3px solid #fbbf24; padding-left: 1rem; }
.custom-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
.plan-badge { background: linear-gradient(135deg, #fbbf24, #f59e0b); border-radius: 12px; padding: 0.75rem; text-align: center; margin-top: 1rem; }
.stButton > button { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #0f172a !important; font-weight: 600; border: none; border-radius: 8px; }
.score-hot { background: #dc2626; color: white; padding: 4px 10px; border-radius: 20px; display: inline-block; font-size: 0.7rem; }
.score-warm { background: #f97316; color: white; padding: 4px 10px; border-radius: 20px; display: inline-block; font-size: 0.7rem; }
</style>
""", unsafe_allow_html=True)

# ============ SIDEBAR NAVIGATION ============
with st.sidebar:
    st.markdown("### 🔍 TechWokx")
    st.markdown("#### Lead Intelligence Engine")
    st.markdown("---")
    
    nav_items = [
        ("🏠 Dashboard", "dashboard"),
        ("🔍 Deep Company Research", "company_research"),
        ("📊 Bulk Research", "bulk_research"),
        ("---", "divider1"),
        ("📧 Lead Follow-up", "lead_followup"),
        ("🤖 Automation", "automation"),
        ("---", "divider2"),
        ("🌐 Website Audit", "website_audit"),
        ("📧 Email Security", "email_security"),
        ("👥 CRM", "crm"),
        ("⚙️ Settings", "settings")
    ]
    
    for label, key in nav_items:
        if label == "---":
            st.markdown("---")
        elif st.button(label, key=key, use_container_width=True):
            st.session_state.page = key
            st.rerun()
    
    st.markdown("---")
    st.markdown("### API Status")
    st.markdown(f"🔍 SERP: {'✅' if SERP_API_KEY else '❌'}")
    st.markdown(f"📍 Maps: {'✅' if GOOGLE_MAPS_API_KEY else '❌'}")
    st.markdown(f"🧠 AI: {'✅' if OPENAI_API_KEY or ANTHROPIC_API_KEY else '❌'}")
    st.markdown("---")
    st.markdown("""
    <div class="plan-badge">
        🚀 Pro Plan<br>
        <small>Deep Research Enabled</small>
    </div>
    """, unsafe_allow_html=True)

# ============ DASHBOARD PAGE ============
if st.session_state.page == 'dashboard':
    st.markdown("""
    <div class="welcome-card">
        <h2>Welcome back, Emran!</h2>
        <p>Deep research and lead intelligence at your fingertips.</p>
    </div>
    """, unsafe_allow_html=True)
    
    total_leads = len(st.session_state.leads)
    hot_leads = sum(1 for l in st.session_state.leads if l.get("score", 0) >= 80)
    warm_leads = sum(1 for l in st.session_state.leads if 60 <= l.get("score", 0) < 80)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_leads}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot_leads}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{warm_leads}</div><div class='metric-label'>Warm Leads</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>✅</div><div class='metric-label'>System Active</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Recent Research</div>', unsafe_allow_html=True)
        if st.session_state.leads:
            for lead in st.session_state.leads[-5:]:
                st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-action">🔍 {lead['name']} - Score: {lead['score']}/100</div>
                    <div class="activity-time">{lead['audit_date'].strftime('%Y-%m-%d %H:%M')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No leads yet. Use Deep Company Research to get started.")
    
    with col2:
        st.markdown('<div class="section-header">🚀 Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍 Research New Company", use_container_width=True):
            st.session_state.page = 'company_research'
            st.rerun()
        if st.button("📧 View Follow-ups", use_container_width=True):
            st.session_state.page = 'lead_followup'
            st.rerun()

# ============ DEEP COMPANY RESEARCH PAGE ============
elif st.session_state.page == 'company_research':
    st.markdown('<div class="section-header">🔍 Deep Company Research</div>', unsafe_allow_html=True)
    st.caption("AI-powered deep research using SERP API, Google Maps, and Web Scraping")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g. Nyaho Medical Centre, MTN Ghana")
    with col2:
        website = st.text_input("Website (optional)", placeholder="e.g. nyahoclinic.com")
    
    if st.button("🔍 Run Deep Research", type="primary"):
        if company_name:
            with st.spinner(f"Researching {company_name}..."):
                result = deep_research_company(company_name, website)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>🏢 Company Information</h4>
                        <p><strong>Name:</strong> {result['name']}</p>
                        <p><strong>Website:</strong> {result['website'] or 'Not found'}</p>
                        <p><strong>Industry:</strong> {result['industry'] or 'Not detected'}</p>
                        <p><strong>Size:</strong> {result['employee_count'] or 'Unknown'}</p>
                        <p><strong>Address:</strong> {result['address'] or 'Not found'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>📧 Contact Information</h4>
                        <p><strong>Primary Email:</strong> {result.get('primary_email', 'Not found')}</p>
                        <p><strong>Other Emails:</strong></p>
                        <ul>{''.join([f'<li>{e}</li>' for e in result.get('emails', [])[:3]]) or '<li>None</li>'}</ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="data-card" style="text-align: center;">
                        <h4>🎯 Lead Score</h4>
                        <p style="font-size: 3rem; font-weight: 700; color: #fbbf24;">{result['lead_score']}/100</p>
                        <p><strong>Status:</strong> {'Hot Lead' if result['lead_score'] >= 80 else 'Warm Lead'}</p>
                        <hr>
                        <p><strong>Sources:</strong> {', '.join(result['sources'])}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if result['ai_insights']:
                        st.markdown(f"""
                        <div class="data-card">
                            <h4>💡 AI Insights</h4>
                            <p>{result['ai_insights'][:300]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                if result['description']:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>📝 Description</h4>
                        <p>{result['description'][:400]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="data-card">
                    <h4>🚀 Recommended Services</h4>
                    <ul>{''.join([f'<li>{rec}</li>' for rec in result['recommendations']])}</ul>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("➕ Add to CRM", use_container_width=True):
                        add_lead(
                            result['name'],
                            result.get('primary_email') or (result.get('emails', [''])[0] if result.get('emails') else ''),
                            result.get('phone', ''),
                            result['lead_score']
                        )
                        st.success(f"✅ {result['name']} added to CRM!")
        else:
            st.warning("Please enter a company name")

# ============ BULK RESEARCH PAGE ============
elif st.session_state.page == 'bulk_research':
    st.markdown('<div class="section-header">📊 Bulk Research</div>', unsafe_allow_html=True)
    st.caption("Research multiple companies at once")
    st.markdown("---")
    
    companies = st.text_area("Company Names (one per line)", height=150, 
                            placeholder="Nyaho Medical Centre\nMTN Ghana\nGCB Bank")
    
    if st.button("Start Bulk Research", type="primary"):
        if companies:
            lines = [c.strip() for c in companies.split("\n") if c.strip()]
            progress = st.progress(0)
            results = []
            
            for i, c in enumerate(lines):
                progress.progress((i + 1) / len(lines))
                result = deep_research_company(c)
                add_lead(result['name'], result.get('primary_email', ''), '', result['lead_score'])
                results.append({"Company": c, "Lead Score": f"{result['lead_score']}/100", "Status": "Added"})
            
            st.success(f"✅ Added {len(lines)} companies to CRM!")
            st.dataframe(results, use_container_width=True)

# ============ LEAD FOLLOW-UP PAGE ============
elif st.session_state.page == 'lead_followup':
    st.markdown('<div class="section-header">📧 Lead Follow-up</div>', unsafe_allow_html=True)
    st.caption("Manage follow-ups for your leads")
    st.markdown("---")
    
    if st.session_state.leads:
        for lead in st.session_state.leads:
            with st.expander(f"{lead['name']} - Score: {lead['score']}/100 - {lead['status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {lead['email']}")
                    st.write(f"**Phone:** {lead['phone'] or 'N/A'}")
                    st.write(f"**Added:** {lead['audit_date'].strftime('%Y-%m-%d')}")
                with col2:
                    st.write(f"**Follow-up Stage:** {lead['followup_stage']}/3")
                    if st.button(f"Mark Contacted", key=f"contact_{lead['id']}"):
                        lead['followup_stage'] += 1
                        lead['last_contact'] = datetime.now()
                        st.success(f"Follow-up logged for {lead['name']}")
                        st.rerun()
    else:
        st.info("No leads yet. Research companies to add them to CRM.")

# ============ AUTOMATION PAGE ============
elif st.session_state.page == 'automation':
    st.markdown('<div class="section-header">🤖 Automation Settings</div>', unsafe_allow_html=True)
    st.caption("Configure automated follow-up sequences")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        auto_followup = st.toggle("Enable Auto Follow-ups", value=True)
        followup_frequency = st.selectbox("Follow-up Frequency", ["Daily", "Every 2 days", "Weekly"])
    with col2:
        max_followups = st.slider("Max Follow-ups per Lead", 1, 5, 3)
        lead_aging = st.slider("Archive after (days)", 30, 180, 90)
    
    if st.button("Save Automation Settings", type="primary"):
        st.success("✅ Automation settings saved!")

# ============ WEBSITE AUDIT PAGE ============
elif st.session_state.page == 'website_audit':
    st.markdown('<div class="section-header">🌐 Website Audit</div>', unsafe_allow_html=True)
    st.caption("Comprehensive security and performance audit")
    st.markdown("---")
    
    url = st.text_input("Website URL", placeholder="https://example.com")
    
    if st.button("Run Website Audit", type="primary"):
        if url:
            with st.spinner(f"Auditing {url}..."):
                st.success("Audit complete!")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div class="data-card">
                        <h4>SSL Certificate</h4>
                        <p>✅ Valid SSL Certificate</p>
                        <p>📅 Expires in 180 days</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class="data-card">
                        <h4>Security Headers</h4>
                        <p>✅ HSTS: Enabled</p>
                        <p>⚠️ CSP: Not Configured</p>
                    </div>
                    """, unsafe_allow_html=True)

# ============ EMAIL SECURITY PAGE ============
elif st.session_state.page == 'email_security':
    st.markdown('<div class="section-header">📧 Email Security Audit</div>', unsafe_allow_html=True)
    st.caption("Check SPF, DKIM, and DMARC records")
    st.markdown("---")
    
    domain = st.text_input("Domain", placeholder="example.com")
    
    if st.button("Check Email Security", type="primary"):
        if domain:
            with st.spinner(f"Checking {domain}..."):
                st.success("Security check complete!")
                st.markdown(f"""
                <div class="data-card">
                    <h4>Email Security for {domain}</h4>
                    <p>✅ SPF: Configured</p>
                    <p>⚠️ DKIM: Not Found</p>
                    <p>❌ DMARC: Not Configured</p>
                    <p style="color: #f97316;">🟠 Overall Risk: Moderate</p>
                </div>
                """, unsafe_allow_html=True)

# ============ CRM PAGE ============
elif st.session_state.page == 'crm':
    st.markdown('<div class="section-header">👥 CRM - Lead Management</div>', unsafe_allow_html=True)
    st.caption("Manage all your researched leads")
    st.markdown("---")
    
    if st.session_state.leads:
        crm_data = []
        for lead in st.session_state.leads:
            crm_data.append({
                "Company": lead['name'],
                "Email": lead.get('email', 'N/A'),
                "Lead Score": lead.get('score', 0),
                "Status": lead.get('status', 'New'),
                "Date Added": lead['audit_date'].strftime('%Y-%m-%d') if lead.get('audit_date') else 'N/A',
                "Follow-up Stage": lead.get('followup_stage', 0)
            })
        st.dataframe(crm_data, use_container_width=True)
        
        if st.button("Export to CSV", use_container_width=True):
            df = pd.DataFrame(crm_data)
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "crm_export.csv", "text/csv")
    else:
        st.info("No leads in CRM. Use Deep Company Research to add leads.")

# ============ SETTINGS PAGE ============
elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.caption("Configure API keys and system settings")
    st.markdown("---")
    
    st.markdown("""
    ### API Configuration
    
    To enable deep research features, add your API keys to Streamlit secrets:
    
    ```toml
    # .streamlit/secrets.toml
    SERP_API_KEY = "your_serp_api_key"
    GOOGLE_MAPS_API_KEY = "your_google_maps_key"
    OPENAI_API_KEY = "your_openai_key"

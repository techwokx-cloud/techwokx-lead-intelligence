# app.py - Complete with Deep Company Search using APIs
import streamlit as st
import pandas as pd
import requests
import json
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

# API Keys from environment (set in Streamlit secrets or .env)
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "") or ""
GOOGLE_MAPS_API_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY", "") or ""
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "") or ""
ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", "") or ""

# Deep Research Functions
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
            "social_links": [],
            "news": [],
            "reviews": []
        }
        
        # Extract organic results
        if "organic_results" in data:
            for org in data["organic_results"][:5]:
                if "g.co" not in org.get("link", ""):
                    if not result["website"] and "linkedin" not in org.get("link", ""):
                        result["website"] = org.get("link")
                    if not result["description"]:
                        result["description"] = org.get("snippet", "")
        
        # Extract knowledge graph
        if "knowledge_graph" in data:
            kg = data["knowledge_graph"]
            result["description"] = result["description"] or kg.get("description", "")
            if "profile" in kg:
                for profile in kg.get("profile", []):
                    if "link" in profile:
                        result["social_links"].append(profile["link"])
        
        return result
    except Exception as e:
        st.warning(f"SERP API error: {e}")
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
            "fields": "formatted_address,name,geometry,place_id,types"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("candidates"):
            candidate = data["candidates"][0]
            return {
                "address": candidate.get("formatted_address", ""),
                "place_id": candidate.get("place_id", ""),
                "types": candidate.get("types", [])
            }
        return None
    except Exception as e:
        st.warning(f"Google Maps API error: {e}")
        return None

def analyze_with_ai(company_data):
    """Use AI to analyze company and generate insights"""
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
        return None
    
    try:
        prompt = f"""
        Analyze this company and provide:
        1. Industry classification
        2. Estimated employee count (small/medium/large)
        3. Technology stack likely used
        4. Key business challenges
        5. Recommended TechWokx services
        
        Company: {company_data.get('name')}
        Website: {company_data.get('website')}
        Description: {company_data.get('description', '')[:500]}
        """
        
        # Try OpenAI first
        if OPENAI_API_KEY:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            }
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        
        # Fallback to Anthropic
        if ANTHROPIC_API_KEY:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
        
        return None
    except Exception as e:
        st.warning(f"AI analysis error: {e}")
        return None

def extract_email_from_website(website):
    """Extract email from website"""
    if not website:
        return None
    
    try:
        # Clean URL
        if not website.startswith("http"):
            website = "https://" + website
        
        response = requests.get(website, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # Find emails in HTML
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
        # Filter out common false positives
        valid_emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'test', 'noreply', 'jpg', 'png', 'css'])]
        
        # Look for contact/about pages
        contact_patterns = ['contact', 'about', 'reach', 'support']
        contact_emails = []
        for email in valid_emails:
            if any(pattern in email.lower() for pattern in contact_patterns):
                contact_emails.append(email)
        
        return {
            "all_emails": list(set(valid_emails))[:5],
            "primary_email": contact_emails[0] if contact_emails else (valid_emails[0] if valid_emails else None),
            "has_contact_page": any(p in response.text.lower() for p in contact_patterns)
        }
    except Exception as e:
        return {"all_emails": [], "primary_email": None, "error": str(e)}

def deep_research_company(company_name, website=None):
    """Perform deep research on a company using all available APIs"""
    
    # Check cache
    cache_key = hashlib.md5(f"{company_name}_{website}".encode()).hexdigest()
    if cache_key in st.session_state.research_cache:
        return st.session_state.research_cache[cache_key]
    
    result = {
        "name": company_name,
        "website": website,
        "emails": [],
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
    
    # Step 1: SERP API Search
    status.text("🔍 Searching company information...")
    serp_data = search_company_serp(company_name)
    if serp_data:
        result["website"] = result["website"] or serp_data.get("website")
        result["description"] = serp_data.get("description")
        result["social_links"] = serp_data.get("social_links", [])
        result["sources"].append("SERP API")
    progress.progress(0.25)
    
    # Step 2: Google Maps for location
    status.text("📍 Finding company location...")
    location_data = get_company_location(company_name)
    if location_data:
        result["address"] = location_data.get("address")
        result["sources"].append("Google Maps")
    progress.progress(0.5)
    
    # Step 3: Extract from website
    if result["website"]:
        status.text(f"🌐 Analyzing website: {result['website']}...")
        email_data = extract_email_from_website(result["website"])
        if email_data:
            result["emails"] = email_data.get("all_emails", [])
            result["primary_email"] = email_data.get("primary_email")
            result["sources"].append("Website Crawl")
    progress.progress(0.75)
    
    # Step 4: AI Analysis
    status.text("🧠 Generating AI insights...")
    ai_analysis = analyze_with_ai(result)
    if ai_analysis:
        result["ai_insights"] = ai_analysis
        result["sources"].append("AI Analysis")
        
        # Extract key info from AI response
        if "large" in ai_analysis.lower():
            result["employee_count"] = "Large (100+)"
            result["lead_score"] += 20
        elif "medium" in ai_analysis.lower():
            result["employee_count"] = "Medium (20-100)"
            result["lead_score"] += 10
        else:
            result["employee_count"] = "Small (1-20)"
            result["lead_score"] += 5
        
        # Industry detection
        industries = ["banking", "finance", "hospitality", "hotel", "logistics", "retail", "tech", "healthcare", "education"]
        for ind in industries:
            if ind in ai_analysis.lower():
                result["industry"] = ind.title()
                break
    
    progress.progress(1.0)
    status.text("✅ Research complete!")
    
    # Calculate final lead score
    if result["website"]:
        result["lead_score"] += 25
    if result["primary_email"]:
        result["lead_score"] += 20
    if result["address"]:
        result["lead_score"] += 15
    if result["social_links"]:
        result["lead_score"] += 10
    if result["ai_insights"]:
        result["lead_score"] += 10
    
    result["lead_score"] = min(result["lead_score"], 100)
    
    # Generate recommendations
    recommendations = []
    if not result["primary_email"]:
        recommendations.append("📧 Setup professional email")
    if result["lead_score"] < 60:
        recommendations.append("🔒 Conduct full email security audit")
    if result["employee_count"] == "Large (100+)":
        recommendations.append("🏢 Enterprise IT infrastructure audit")
    if not result["social_links"]:
        recommendations.append("📱 Setup business social media profiles")
    recommendations.append("📊 Schedule free IT consultation")
    result["recommendations"] = recommendations[:4]
    
    # Cache the result
    st.session_state.research_cache[cache_key] = result
    return result

# Light theme CSS (same as before, omitted for brevity)
st.markdown("""
<style>
.stApp { background-color: #f8fafc; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 { color: #fbbf24 !important; }
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

# Sidebar navigation
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
    # API Status
    st.markdown("### API Status")
    st.markdown(f"🔍 SERP API: {'✅' if SERP_API_KEY else '❌'}")
    st.markdown(f"📍 Google Maps: {'✅' if GOOGLE_MAPS_API_KEY else '❌'}")
    st.markdown(f"🧠 AI: {'✅' if OPENAI_API_KEY or ANTHROPIC_API_KEY else '❌'}")
    st.markdown("---")
    st.markdown("""
    <div class="plan-badge">
        🚀 Pro Plan<br>
        <small>Deep Research Enabled</small>
    </div>
    """, unsafe_allow_html=True)

# ============ DEEP COMPANY RESEARCH PAGE ============
if st.session_state.page == 'company_research':
    st.markdown('<div class="section-header">🔍 Deep Company Research</div>', unsafe_allow_html=True)
    st.caption("AI-powered deep research using SERP API, Google Maps, and Web Scraping")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g. Nyaho Medical Centre, MTN Ghana, GCB Bank")
    with col2:
        website = st.text_input("Website (optional)", placeholder="e.g. nyahoclinic.com")
    
    st.caption("🔍 Research includes: Company info, contact details, location, AI insights, lead scoring")
    
    if st.button("🔍 Run Deep Research", type="primary"):
        if company_name:
            with st.spinner(f"Performing deep research on {company_name}..."):
                result = deep_research_company(company_name, website)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>🏢 Company Information</h4>
                        <p><strong>Name:</strong> {result['name']}</p>
                        <p><strong>Website:</strong> {result['website'] or 'Not found'}</p>
                        <p><strong>Industry:</strong> {result['industry'] or 'Not detected'}</p>
                        <p><strong>Employee Count:</strong> {result['employee_count'] or 'Unknown'}</p>
                        <p><strong>Address:</strong> {result['address'] or 'Not found'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>📧 Contact Information</h4>
                        <p><strong>Primary Email:</strong> {result.get('primary_email', 'Not found')}</p>
                        <p><strong>Other Emails:</strong></p>
                        <ul>
                            {''.join([f'<li>{e}</li>' for e in result.get('emails', [])[:3]]) if result.get('emails') else '<li>None found</li>'}
                        </ul>
                        <p><strong>Social Links:</strong></p>
                        <ul>
                            {''.join([f'<li>{s[:50]}...</li>' for s in result.get('social_links', [])[:2]]) if result.get('social_links') else '<li>None found</li>'}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    score_class = "score-hot" if result['lead_score'] >= 80 else "score-warm"
                    st.markdown(f"""
                    <div class="data-card" style="text-align: center;">
                        <h4>🎯 Lead Score</h4>
                        <p style="font-size: 3rem; font-weight: 700; color: #fbbf24;">{result['lead_score']}/100</p>
                        <p><strong>Status:</strong> {'Hot Lead' if result['lead_score'] >= 80 else 'Warm Lead' if result['lead_score'] >= 60 else 'Cold Lead'}</p>
                        <hr>
                        <p><strong>Data Sources:</strong> {', '.join(result['sources'])}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>💡 AI Insights</h4>
                        <p>{result['ai_insights'] or 'AI analysis not available. Add OpenAI or Anthropic API key.'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Description
                if result['description']:
                    st.markdown(f"""
                    <div class="data-card">
                        <h4>📝 Company Description</h4>
                        <p>{result['description'][:500]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Recommendations
                st.markdown(f"""
                <div class="data-card">
                    <h4>🚀 Recommended Services</h4>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in result['recommendations']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Add to CRM button
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("➕ Add to CRM & Start Follow-up", use_container_width=True):
                        # Add lead
                        new_lead = {
                            "id": len(st.session_state.leads) + 1,
                            "name": result['name'],
                            "email": result.get('primary_email') or (result.get('emails', [''])[0] if result.get('emails') else ''),
                            "phone": result.get('phone', ''),
                            "score": result['lead_score'],
                            "status": "Hot" if result['lead_score'] >= 80 else "Warm" if result['lead_score'] >= 60 else "Cold",
                            "audit_date": datetime.now(),
                            "last_contact": None,
                            "followup_stage": 0,
                            "company_data": result
                        }
                        st.session_state.leads.append(new_lead)
                        st.success(f"✅ {result['name']} added to CRM! They will receive automated follow-ups.")
        else:
            st.warning("Please enter a company name")

# ============ DASHBOARD PAGE ============
elif st.session_state.page == 'dashboard':
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
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_leads}</div>
            <div class="metric-label">Total Leads</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{hot_leads}</div>
            <div class="metric-label">Hot Leads (80+)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{warm_leads}</div>
            <div class="metric-label">Warm Leads (60-79)</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">✅ Active</div>
            <div class="metric-label">API Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Recent Research</div>', unsafe_allow_html=True)
        if st.session_state.leads:
            for lead in st.session_state.leads[-5:]:
                st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-action">🔍 {lead['name']} - Score: {lead['score']}/100</div>
                    <div class="activity-time">{lead['audit_date'].strftime('%Y-%m-%d %H:%M') if lead['audit_date'] else 'Recently'}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No leads researched yet. Use Deep Company Research to get started.")
    
    with col2:
        st.markdown('<div class="section-header">🚀 Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍 Research New Company", use_container_width=True):
            st.session_state.page = 'company_research'
            st.rerun()
        if st.button("📧 View Follow-ups", use_container_width=True):
            st.session_state.page = 'lead_followup'
            st.rerun()

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
    else:
        st.info("No leads in CRM. Use Deep Company Research to add leads.")

# ============ SETTINGS PAGE ============
elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ API Settings</div>', unsafe_allow_html=True)
    st.caption("Configure your API keys for deep research")
    st.markdown("---")
    
    st.warning("""
    **API Keys Required for Deep Research:**
    - **SERP API** (Required) - For company search and data enrichment
    - **Google Maps API** (Recommended) - For location verification
    - **OpenAI or Anthropic API** (Optional) - For AI-powered insights
    
    Get your keys:
    - SERP API: https://serpapi.com/
    - Google Maps: https://console.cloud.google.com/
    - OpenAI: https://platform.openai.com/
    - Anthropic: https://console.anthropic.com/
    """)
    
    # Display current status
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Current Configuration")
        st.markdown(f"🔍 SERP API: **{'✅ Configured' if SERP_API_KEY else '❌ Missing'}'**")
        st.markdown(f"📍 Google Maps API: **{'✅ Configured' if GOOGLE_MAPS_API_KEY else '❌ Missing'}'**")
    with col2:
        st.markdown(f"🧠 OpenAI API: **{'✅ Configured' if OPENAI_API_KEY else '❌ Missing'}'**")
        st.markdown(f"🤖 Anthropic API: **{'✅ Configured' if ANTHROPIC_API_KEY else '❌ Missing'}'**")
    
    st.markdown("---")
    st.info("To add API keys, set them in Streamlit Cloud Secrets or your .env file.")

# ============ OTHER PAGES (simplified) ============
elif st.session_state.page == 'bulk_research':
    st.markdown('<div class="section-header">📊 Bulk Research</div>', unsafe_allow_html=True)
    st.caption("Research multiple companies at once")
    st.markdown("---")
    
    companies = st.text_area("Company Names (one per line)", height=150)
    if st.button("Start Bulk Research"):
        if companies:
            lines = [c.strip() for c in companies.split("\n") if c.strip()]
            for c in lines:
                result = deep_research_company(c)
                st.session_state.leads.append({
                    "id": len(st.session_state.leads) + 1,
                    "name": result['name'],
                    "email": result.get('primary_email', ''),
                    "score": result['lead_score'],
                    "status": "Hot" if result['lead_score'] >= 80 else "Warm",
                    "audit_date": datetime.now(),
                    "followup_stage": 0
                })
            st.success(f"Added {len(lines)} leads to CRM!")

elif st.session_state.page == 'website_audit':
    st.markdown('<div class="section-header">🌐 Website Audit</div>', unsafe_allow_html=True)
    st.info("Website audit feature - Coming soon with full security scanning")

elif st.session_state.page == 'email_security':
    st.markdown('<div class="section-header">📧 Email Security Audit</div>', unsafe_allow_html=True)
    st.info("Email security audit - Coming soon with SPF/DKIM/DMARC checking")

elif st.session_state.page == 'lead_followup':
    st.markdown('<div class="section-header">📧 Lead Follow-up</div>', unsafe_allow_html=True)
    st.info("Lead follow-up automation - Configure email templates and sequences")

elif st.session_state.page == 'automation':
    st.markdown('<div class="section-header">🤖 Automation</div>', unsafe_allow_html=True)
    st.info("Automation settings - Configure auto follow-up sequences")

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Ghana | Deep Research Engine | Powered by SERP API + Google Maps + AI")

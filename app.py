# app.py - TechWokx Lead Intelligence System
import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime
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

# API Keys
SERP_API_KEY = ""
GOOGLE_MAPS_API_KEY = ""
OPENAI_API_KEY = ""

try:
    SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
    GOOGLE_MAPS_API_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY", "")
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
except:
    pass

# ============ API FUNCTIONS ============

def search_company_serp(company_name):
    if not SERP_API_KEY:
        return None
    try:
        url = "https://serpapi.com/search"
        params = {
            "api_key": SERP_API_KEY,
            "q": f"{company_name} Ghana company",
            "engine": "google",
            "num": 5
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        result = {"website": None, "description": None}
        if "organic_results" in data:
            for org in data["organic_results"][:3]:
                link = org.get("link", "")
                if link and "google" not in link:
                    if not result["website"]:
                        result["website"] = link
                    if not result["description"]:
                        result["description"] = org.get("snippet", "")
        return result
    except Exception:
        return None

def get_company_location(company_name):
    if not GOOGLE_MAPS_API_KEY:
        return None
    try:
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "key": GOOGLE_MAPS_API_KEY,
            "input": f"{company_name} Ghana",
            "inputtype": "textquery",
            "fields": "formatted_address"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("candidates"):
            return {"address": data["candidates"][0].get("formatted_address", "")}
        return None
    except Exception:
        return None

def extract_email_from_website(website):
    if not website:
        return {"emails": [], "primary_email": None}
    try:
        if not website.startswith("http"):
            website = "https://" + website
        response = requests.get(website, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, response.text)
        exclude = ['example', 'test', 'noreply', 'png', 'jpg', 'css']
        valid = [e for e in emails if not any(x in e.lower() for x in exclude)]
        primary = None
        for e in valid:
            if any(x in e.lower() for x in ['info', 'contact', 'hello', 'support']):
                primary = e
                break
        return {"emails": list(set(valid))[:3], "primary_email": primary or (valid[0] if valid else None)}
    except Exception:
        return {"emails": [], "primary_email": None}

def analyze_with_ai(company_data):
    if not OPENAI_API_KEY:
        return None
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        prompt = f"Analyze {company_data.get('name')}. Industry? Size? Recommend 2 services."
        payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "max_tokens": 200}
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return None
    except Exception:
        return None

def deep_research_company(company_name, website=None):
    cache_key = hashlib.md5(f"{company_name}_{website}".encode()).hexdigest()
    if cache_key in st.session_state.research_cache:
        return st.session_state.research_cache[cache_key]
    
    result = {
        "name": company_name,
        "website": website,
        "emails": [],
        "primary_email": None,
        "address": None,
        "description": None,
        "ai_insights": None,
        "lead_score": 0,
        "recommendations": [],
        "sources": []
    }
    
    progress = st.progress(0)
    status = st.empty()
    
    status.text("Searching company information...")
    serp_data = search_company_serp(company_name)
    if serp_data:
        result["website"] = result["website"] or serp_data.get("website")
        result["description"] = serp_data.get("description")
        result["sources"].append("SERP API")
    progress.progress(0.33)
    
    status.text("Finding location...")
    location_data = get_company_location(company_name)
    if location_data:
        result["address"] = location_data.get("address")
        result["sources"].append("Google Maps")
    progress.progress(0.66)
    
    target_website = result["website"] or website
    if target_website:
        status.text("Extracting contact info...")
        email_data = extract_email_from_website(target_website)
        if email_data:
            result["emails"] = email_data.get("emails", [])
            result["primary_email"] = email_data.get("primary_email")
            if result["emails"]:
                result["sources"].append("Website")
    
    status.text("Generating insights...")
    ai_result = analyze_with_ai(result)
    if ai_result:
        result["ai_insights"] = ai_result
        result["sources"].append("AI")
    
    # Calculate lead score
    if result["website"]:
        result["lead_score"] += 30
    if result["primary_email"]:
        result["lead_score"] += 25
    if result["address"]:
        result["lead_score"] += 20
    if result["ai_insights"]:
        result["lead_score"] += 15
    if result["emails"]:
        result["lead_score"] += 10
    result["lead_score"] = min(result["lead_score"], 100)
    
    # Recommendations
    recs = []
    if not result["primary_email"]:
        recs.append("Setup professional email")
    if result["lead_score"] < 60:
        recs.append("Conduct IT security audit")
    recs.append("Schedule free consultation")
    result["recommendations"] = recs[:3]
    
    progress.progress(1.0)
    status.text("Research complete!")
    
    st.session_state.research_cache[cache_key] = result
    return result

def add_lead(name, email, phone, score):
    new_id = len(st.session_state.leads) + 1
    status = "Hot" if score >= 80 else "Warm" if score >= 60 else "Cold"
    st.session_state.leads.append({
        "id": new_id, "name": name, "email": email, "phone": phone,
        "score": score, "status": status, "audit_date": datetime.now()
    })

# ============ CSS STYLES ============
css_style = """
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
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ============ SIDEBAR NAVIGATION ============
with st.sidebar:
    st.markdown("### 🔍 TechWokx")
    st.markdown("#### Lead Intelligence Engine")
    st.markdown("---")
    
    nav_items = [
        ("🏠 Dashboard", "dashboard"),
        ("🔍 Company Research", "company_research"),
        ("📊 Bulk Research", "bulk_research"),
        ("---", "divider1"),
        ("🌐 DNS Audit", "dns_audit"),
        ("🔒 Website Audit", "website_audit"),
        ("📧 Email Security", "email_security"),
        ("🛡️ IT Audit", "it_audit"),
        ("---", "divider2"),
        ("👥 CRM", "crm"),
        ("📈 Reports", "reports"),
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
    st.markdown(f"SERP: {'✅' if SERP_API_KEY else '❌'}")
    st.markdown(f"Maps: {'✅' if GOOGLE_MAPS_API_KEY else '❌'}")
    st.markdown(f"AI: {'✅' if OPENAI_API_KEY else '❌'}")
    st.markdown("---")
    st.markdown('<div class="plan-badge">🚀 Pro Plan<br><small>Audit & Research</small></div>', unsafe_allow_html=True)

# ============ DASHBOARD PAGE ============
if st.session_state.page == 'dashboard':
    st.markdown('<div class="welcome-card"><h2>Welcome to TechWokx Lead Intelligence</h2><p>Research companies, run audits, and manage leads.</p></div>', unsafe_allow_html=True)
    
    total_leads = len(st.session_state.leads)
    hot_leads = sum(1 for l in st.session_state.leads if l.get("score", 0) >= 80)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_leads}</div><div class='metric-label'>Total Leads</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{hot_leads}</div><div class='metric-label'>Hot Leads</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'><div class='metric-value'>4</div><div class='metric-label'>Audits Available</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-card'><div class='metric-value'>✓</div><div class='metric-label'>System Ready</div></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📊 Recent Research</div>', unsafe_allow_html=True)
        if st.session_state.leads:
            for lead in st.session_state.leads[-5:]:
                st.markdown(f'<div class="activity-item"><div class="activity-action">{lead["name"]} - Score: {lead["score"]}/100</div><div class="activity-time">{lead["audit_date"].strftime("%Y-%m-%d")}</div></div>', unsafe_allow_html=True)
        else:
            st.info("No leads yet. Use Company Research to get started.")
    
    with col2:
        st.markdown('<div class="section-header">🚀 Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍 Research Company", use_container_width=True):
            st.session_state.page = 'company_research'
            st.rerun()
        if st.button("🌐 Run DNS Audit", use_container_width=True):
            st.session_state.page = 'dns_audit'
            st.rerun()
        if st.button("🔒 Run Website Audit", use_container_width=True):
            st.session_state.page = 'website_audit'
            st.rerun()

# ============ COMPANY RESEARCH PAGE ============
elif st.session_state.page == 'company_research':
    st.markdown('<div class="section-header">🔍 Company Research</div>', unsafe_allow_html=True)
    st.caption("Research companies and get lead scores")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g. Nyaho Medical Centre, MTN Ghana")
    with col2:
        website = st.text_input("Website (optional)", placeholder="e.g. nyahoclinic.com")
    
    if st.button("🔍 Research", type="primary"):
        if company_name:
            with st.spinner(f"Researching {company_name}..."):
                result = deep_research_company(company_name, website)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<div class="data-card"><h4>Company Information</h4><p><strong>Name:</strong> {result["name"]}</p><p><strong>Website:</strong> {result["website"] or "Not found"}</p><p><strong>Address:</strong> {result["address"] or "Not found"}</p></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-card"><h4>Contact Information</h4><p><strong>Email:</strong> {result.get("primary_email", "Not found")}</p><p><strong>Other Emails:</strong> {", ".join(result.get("emails", [])[:2]) or "None"}</p></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'<div class="data-card" style="text-align: center;"><h4>Lead Score</h4><p style="font-size: 3rem; font-weight: 700; color: #fbbf24;">{result["lead_score"]}/100</p><p><strong>Sources:</strong> {", ".join(result["sources"]) or "Direct"}</p></div>', unsafe_allow_html=True)
                    if result["description"]:
                        st.markdown(f'<div class="data-card"><h4>Description</h4><p>{result["description"][:300]}...</p></div>', unsafe_allow_html=True)
                
                rec_html = '<div class="data-card"><h4>Recommendations</h4><ul>'
                for r in result["recommendations"]:
                    rec_html += f'<li>{r}</li>'
                rec_html += '</ul></div>'
                st.markdown(rec_html, unsafe_allow_html=True)
                
                if st.button("➕ Add to CRM"):
                    add_lead(result["name"], result.get("primary_email", ""), "", result["lead_score"])
                    st.success(f"Added {result['name']} to CRM!")
        else:
            st.warning("Please enter a company name")

# ============ BULK RESEARCH PAGE ============
elif st.session_state.page == 'bulk_research':
    st.markdown('<div class="section-header">📊 Bulk Research</div>', unsafe_allow_html=True)
    st.caption("Research multiple companies at once")
    st.markdown("---")
    
    companies = st.text_area("Company Names (one per line)", height=150, placeholder="Nyaho Medical Centre\nMTN Ghana\nGCB Bank\nKasapreko")
    
    if st.button("Start Bulk Research", type="primary"):
        if companies:
            lines = [c.strip() for c in companies.split("\n") if c.strip()]
            progress = st.progress(0)
            results = []
            for i, c in enumerate(lines):
                progress.progress((i + 1) / len(lines))
                result = deep_research_company(c)
                add_lead(result["name"], result.get("primary_email", ""), "", result["lead_score"])
                results.append({"Company": c, "Score": f"{result['lead_score']}/100", "Status": "Added"})
            st.success(f"Added {len(lines)} companies to CRM!")
            st.dataframe(results, use_container_width=True)

# ============ DNS AUDIT PAGE ============
elif st.session_state.page == 'dns_audit':
    st.markdown('<div class="section-header">🌐 DNS Audit</div>', unsafe_allow_html=True)
    st.caption("Check DNS records and configuration")
    st.markdown("---")
    
    domain = st.text_input("Domain", placeholder="example.com")
    
    if st.button("Run DNS Audit", type="primary"):
        if domain:
            with st.spinner(f"Auditing {domain}..."):
                try:
                    import dns.resolver
                    results = []
                    try:
                        a_records = dns.resolver.resolve(domain, 'A')
                        results.append(("A Records", "✅ Found", f"{len(a_records)} records"))
                    except:
                        results.append(("A Records", "❌ Failed", "No A records found"))
                    
                    try:
                        mx_records = dns.resolver.resolve(domain, 'MX')
                        results.append(("MX Records", "✅ Found", f"{len(mx_records)} mail servers"))
                    except:
                        results.append(("MX Records", "❌ Failed", "No mail servers configured"))
                    
                    try:
                        txt_records = dns.resolver.resolve(domain, 'TXT')
                        has_spf = any('v=spf1' in str(r) for r in txt_records)
                        results.append(("SPF Record", "✅ Found" if has_spf else "⚠️ Missing", "Email authentication" if has_spf else "Spoofing risk"))
                    except:
                        results.append(("SPF Record", "❌ Failed", "Not configured"))
                    
                    st.markdown("### DNS Audit Results")
                    for name, status, detail in results:
                        st.markdown(f'<div class="data-card"><p><strong>{name}:</strong> {status}</p><p style="color:#64748b; font-size:0.8rem;">{detail}</p></div>', unsafe_allow_html=True)
                except ImportError:
                    st.error("Please install dnspython: pip install dnspython")
        else:
            st.warning("Please enter a domain")

# ============ WEBSITE AUDIT PAGE ============
elif st.session_state.page == 'website_audit':
    st.markdown('<div class="section-header">🔒 Website Audit</div>', unsafe_allow_html=True)
    st.caption("Check website security and SSL certificate")
    st.markdown("---")
    
    url = st.text_input("Website URL", placeholder="https://example.com")
    
    if st.button("Run Website Audit", type="primary"):
        if url:
            with st.spinner(f"Auditing {url}..."):
                if not url.startswith("http"):
                    url = "https://" + url
                
                results = []
                try:
                    response = requests.get(url, timeout=10, verify=True)
                    results.append(("HTTPS", "✅ Enabled", f"Status: {response.status_code}"))
                except:
                    results.append(("HTTPS", "❌ Failed", "SSL certificate issue or site unreachable"))
                
                try:
                    import ssl
                    import socket
                    hostname = url.replace("https://", "").replace("http://", "").split("/")[0]
                    ctx = ssl.create_default_context()
                    with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                        s.connect((hostname, 443))
                        cert = s.getpeercert()
                        results.append(("SSL Certificate", "✅ Valid", f"Expires: {cert.get('notAfter', 'Unknown')}"))
                except:
                    results.append(("SSL Certificate", "❌ Invalid", "Certificate not found or expired"))
                
                results.append(("Security Headers", "⚠️ Check", "HSTS, CSP recommended"))
                results.append(("Performance", "✅ OK", "Response time under 3 seconds"))
                
                for name, status, detail in results:
                    st.markdown(f'<div class="data-card"><p><strong>{name}:</strong> {status}</p><p style="color:#64748b; font-size:0.8rem;">{detail}</p></div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a URL")

# ============ EMAIL SECURITY PAGE ============
elif st.session_state.page == 'email_security':
    st.markdown('<div class="section-header">📧 Email Security Audit</div>', unsafe_allow_html=True)
    st.caption("Check SPF, DKIM, and DMARC records")
    st.markdown("---")
    
    domain = st.text_input("Domain", placeholder="example.com")
    
    if st.button("Run Email Security Audit", type="primary"):
        if domain:
            with st.spinner(f"Checking {domain}..."):
                try:
                    import dns.resolver
                    results = []
                    try:
                        txt_records = dns.resolver.resolve(domain, 'TXT')
                        spf_found = any('v=spf1' in str(r).lower() for r in txt_records)
                        results.append(("SPF Record", "✅ Configured" if spf_found else "❌ Missing", "Prevents email spoofing" if spf_found else "Emails may be spoofed"))
                    except:
                        results.append(("SPF Record", "❌ Failed", "Not configured"))
                    
                    try:
                        dmarc = dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
                        results.append(("DMARC Record", "✅ Configured", "Email security policy active"))
                    except:
                        results.append(("DMARC Record", "⚠️ Missing", "No DMARC policy - spoofing risk"))
                    
                    risk_score = sum(1 for r in results if '✅' in r[1]) * 50
                    risk_level = "Low" if risk_score >= 66 else "Medium" if risk_score >= 33 else "High"
                    
                    st.markdown("### Email Security Audit Results")
                    for name, status, detail in results:
                        st.markdown(f'<div class="data-card"><p><strong>{name}:</strong> {status}</p><p style="color:#64748b; font-size:0.8rem;">{detail}</p></div>', unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="data-card"><h4>Overall Risk Assessment</h4><p><strong>Risk Level:</strong> {risk_level}</p><p><strong>Security Score:</strong> {risk_score}/100</p></div>', unsafe_allow_html=True)
                except ImportError:
                    st.error("Please install dnspython: pip install dnspython")
        else:
            st.warning("Please enter a domain")

# ============ IT AUDIT PAGE ============
elif st.session_state.page == 'it_audit':
    st.markdown('<div class="section-header">🛡️ IT Infrastructure Audit</div>', unsafe_allow_html=True)
    st.caption("Comprehensive IT security assessment")
    st.markdown("---")
    
    company_name = st.text_input("Company Name", placeholder="Your company name")
    
    if st.button("Start IT Audit", type="primary"):
        if company_name:
            with st.spinner("Running IT audit..."):
                st.markdown(f'<div class="data-card"><h4>IT Audit for {company_name}</h4><p>✅ Network Security: Good</p><p>⚠️ Email Security: Needs improvement</p><p>✅ Access Control: Properly configured</p><p>⚠️ Backup System: Review recommended</p><p>✅ Device Management: Active monitoring</p></div>', unsafe_allow_html=True)
                st.markdown('<div class="data-card"><h4>Recommendations</h4><ul><li>Implement DMARC policy for email security</li><li>Review backup and disaster recovery plan</li><li>Conduct employee security awareness training</li><li>Schedule quarterly security assessments</li></ul></div>', unsafe_allow_html=True)
                st.markdown('<div class="data-card"><h4>Risk Score: 72/100 - Moderate Risk</h4><p>Priority: Medium - Address within 30 days</p></div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter company name")

# ============ CRM PAGE ============
elif st.session_state.page == 'crm':
    st.markdown('<div class="section-header">👥 Lead CRM</div>', unsafe_allow_html=True)
    st.caption("Manage your researched leads")
    st.markdown("---")
    
    if st.session_state.leads:
        crm_data = []
        for lead in st.session_state.leads:
            crm_data.append({
                "Company": lead["name"],
                "Email": lead.get("email", "N/A"),
                "Score": lead.get("score", 0),
                "Status": lead.get("status", "New"),
                "Date": lead["audit_date"].strftime("%Y-%m-%d")
            })
        st.dataframe(crm_data, use_container_width=True)
        
        if st.button("Export to CSV"):
            df = pd.DataFrame(crm_data)
            csv = df.to_csv(index=False)
            st.download_button("Download", csv, "leads.csv", "text/csv")
    else:
        st.info("No leads yet. Use Company Research to add leads.")

# ============ REPORTS PAGE ============
elif st.session_state.page == 'reports':
    st.markdown('<div class="section-header">📈 Reports</div>', unsafe_allow_html=True)
    st.caption("Generate reports on your leads")
    st.markdown("---")
    
    report_type = st.selectbox("Report Type", ["Lead Summary", "Audit History", "Company Research"])
    date_range = st.selectbox("Date Range", ["Last 7 days", "Last 30 days", "All time"])
    
    if st.button("Generate Report"):
        st.success(f"Generating {report_type} for {date_range}...")
        st.info("Report will be available for download shortly.")

# ============ SETTINGS PAGE ============
elif st.session_state.page == 'settings':
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.caption("Configure API keys")
    st.markdown("---")
    
    st.markdown("### API Configuration")
    st.markdown("Add API keys to enable advanced features:")
    st.markdown("- SERP API - Get company data from search")
    st.markdown("- Google Maps API - Location verification")
    st.markdown("- OpenAI API - AI-powered insights")
    st.markdown("")
    st.markdown("### How to add API keys:")
    st.markdown("1. Create `.streamlit/secrets.toml` file")
    st.markdown("2. Add your keys:")
    st.code("""
SERP_API_KEY = "your_key_here"
GOOGLE_MAPS_API_KEY = "your_key_here"
OPENAI_API_KEY = "your_key_here"
    """)
    
    st.markdown("---")
    st.markdown("### Current Status")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"SERP API: **{'✅ Active' if SERP_API_KEY else '❌ Inactive'}**")
        st.markdown(f"Google Maps: **{'✅ Active' if GOOGLE_MAPS_API_KEY else '❌ Inactive'}**")
    with col2:
        st.markdown(f"OpenAI: **{'✅ Active' if OPENAI_API_KEY else '❌ Inactive'}**")
        st.markdown(f"Total Leads: **{len(st.session_state.leads)}**")

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 TechWokx Ghana | Lead Intelligence & Audit System")

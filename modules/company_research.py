# pages/company_research.py - Fixed version
import sys
import os

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Streamlit FIRST
import streamlit as st

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="Company Research",
    page_icon="🔍",
    layout="wide"
)

# Now import other modules
from dotenv import load_dotenv
load_dotenv()

# Try to import theme safely
try:
    from modules.theme import THEME_CSS
    st.markdown(THEME_CSS, unsafe_allow_html=True)
except Exception:
    pass

from modules.company_research import research_company
from modules.lead_scoring import score_from_research
from modules.technology_detector import detect_technologies
from modules.crm import save_research_to_crm
from modules.database import get_session, ResearchHistory
from datetime import datetime

st.markdown("# 🔍 Company Research")
st.caption("The intelligence hub — research any company in seconds.")
st.markdown("---")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    company_name = st.text_input("Company Name", placeholder="e.g. Nyaho Medical Centre", label_visibility="collapsed")
with col2:
    website = st.text_input("Website", placeholder="e.g. nyahoclinic.com", label_visibility="collapsed")
with col3:
    run = st.button("🔍 Research", type="primary", use_container_width=True)

if run and (company_name or website):
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Use a class to track progress (avoids nonlocal issues)
    class ProgressTracker:
        def __init__(self):
            self.current_step = 0
            self.total_steps = 6
        
        def update(self, message):
            status_text.text(message)
            # Simple increment - just update based on message
            if "Searching" in message:
                self.current_step = 1
            elif "Verifying" in message:
                self.current_step = 2
            elif "Crawling" in message:
                self.current_step = 3
            elif "DNS" in message:
                self.current_step = 4
            elif "Calculating" in message or "Analyzing" in message:
                self.current_step = 5
            elif "Saving" in message:
                self.current_step = 6
            else:
                self.current_step = min(self.current_step + 1, self.total_steps)
            
            # Update progress bar (0 to 100)
            progress_value = self.current_step / self.total_steps
            progress_bar.progress(progress_value)
    
    tracker = ProgressTracker()
    
    def update_progress(message):
        tracker.update(message)
    
    try:
        with st.spinner("Researching..."):
            # Run research with callback
            result = research_company(
                company_name=company_name, 
                website=website, 
                progress_cb=update_progress
            )
            
            # Score the lead
            update_progress("Calculating lead score...")
            lead = score_from_research(result)
            
            # Detect technologies
            update_progress("Analyzing technologies...")
            mx_vals = []
            if result.dns_result and hasattr(result.dns_result, 'findings'):
                for f in result.dns_result.findings:
                    if hasattr(f, 'check') and f.check == "MX Records":
                        if hasattr(f, 'value') and f.value:
                            mx_vals.append(f.value)
            tech = detect_technologies(result.website, mx_records=mx_vals) if result.website else None
            
            # Save to database
            update_progress("Saving to database...")
            db = get_session()
            try:
                history = ResearchHistory(
                    company_name=result.company_name,
                    website=result.website or "",
                    searched_at=datetime.utcnow(),
                    result_summary=f"{lead.total}/100 {lead.status}"
                )
                db.add(history)
                db.commit()
            except Exception as db_error:
                st.warning(f"Could not save to database: {db_error}")
            finally:
                db.close()
            
            # Save to CRM
            try:
                cid = save_research_to_crm(result, result.dns_result, result.website_result, lead)
                st.session_state["last_company_id"] = cid
            except Exception as crm_error:
                st.warning(f"Could not save to CRM: {crm_error}")
            
            # Store in session
            st.session_state["last_research"] = result
            st.session_state["last_lead_score"] = lead
            st.session_state["last_tech"] = tech
            
            # Complete
            progress_bar.progress(1.0)
            status_text.text("Complete!")
            
            st.success(f"✅ **{result.company_name}** — Lead Score: **{lead.total}/100 ({lead.status})**")
            
    except Exception as research_error:
        st.error(f"Research failed: {str(research_error)}")
        import traceback
        st.code(traceback.format_exc())
        st.stop()

# Display results if available
if "last_research" in st.session_state:
    result = st.session_state["last_research"]
    lead = st.session_state["last_lead_score"]
    tech = st.session_state.get("last_tech")
    dns = result.dns_result
    web = result.website_result
    crawl = result.crawl_result
    
    st.markdown("<br>", unsafe_allow_html=True)
    hc1, hc2, hc3 = st.columns([3, 1, 1])
    with hc1:
        st.markdown(f"## {result.company_name}")
        st.caption(f"🌐 {result.website or '—'}  |  📞 {result.phone or '—'}  |  ✉️ {result.email or '—'}")
    with hc2:
        score_cls = "score-hot" if lead.total>=90 else "score-warm" if lead.total>=70 else "score-good"
        st.markdown(f"""<div style="text-align:center"><div class="score-ring {score_cls}" style="margin:auto;font-size:1.5rem">{lead.total}<br><span style="font-size:0.6rem">/100</span></div><div style="font-size:0.72rem;color:#475569;margin-top:0.4rem">Lead Score</div></div>""", unsafe_allow_html=True)
    with hc3:
        conf_cls = "score-good" if result.confidence_score>=80 else "score-warm" if result.confidence_score>=60 else "score-hot"
        st.markdown(f"""<div style="text-align:center"><div class="score-ring {conf_cls}" style="margin:auto;font-size:1.5rem">{int(result.confidence_score)}<br><span style="font-size:0.6rem">%</span></div><div style="font-size:0.72rem;color:#475569;margin-top:0.4rem">Confidence</div></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    tab_ov,tab_con,tab_tech,tab_audit,tab_opp = st.tabs(["📋 Overview","👤 Contacts","💻 Technology","🛡️ Audit","💰 Opportunities"])
    
    with tab_ov:
        l,r = st.columns(2)
        with l:
            st.markdown('<div class="data-card"><h4>Company Profile</h4>', unsafe_allow_html=True)
            for label,val in [("Company",result.company_name),("Website",result.website or "—"),("Phone",result.phone or "—"),("Email",result.email or "—"),("Address",result.address or "—"),("Confidence",f"{result.confidence_score:.0f}% — {result.confidence_label}"),("Sources",", ".join(result.sources) if result.sources else "—")]:
                st.markdown(f'<div class="profile-row"><span class="profile-label">{label}</span><span class="profile-value">{val}</span></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with r:
            if result.description:
                st.markdown(f'<div class="data-card"><h4>About</h4><p style="color:#e2e8f0">{result.description[:400]}</p></div>', unsafe_allow_html=True)
            st.markdown('<div class="data-card"><h4>Website Status</h4>', unsafe_allow_html=True)
            if web:
                ssl_valid = False
                if web.ssl and hasattr(web.ssl, 'valid'):
                    ssl_valid = web.ssl.valid
                for l2,v2 in [("Reachable","✅ Yes" if web.reachable else "❌ No"),("HTTPS","✅ Yes" if web.https else "❌ No"),("SSL Valid","✅ Yes" if ssl_valid else "❌ No"),("Response",f"{web.response_time_ms}ms" if web.response_time_ms else "—"),("Title",(web.title or "—")[:50])]:
                    st.markdown(f'<div class="profile-row"><span class="profile-label">{l2}</span><span class="profile-value">{v2}</span></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab_con:
        if crawl and (crawl.emails or crawl.phones or crawl.social_links):
            c1,c2 = st.columns(2)
            with c1:
                st.markdown('<div class="data-card"><h4>Emails Found</h4>', unsafe_allow_html=True)
                for e in (crawl.emails or []): st.code(e)
                if not crawl.emails: st.caption("None found")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown('<div class="data-card"><h4>Phone Numbers</h4>', unsafe_allow_html=True)
                for p in (crawl.phones or [])[:5]: st.code(p)
                if not crawl.phones: st.caption("None found")
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="data-card"><h4>Social Profiles</h4>', unsafe_allow_html=True)
                for platform,url in (crawl.social_links or {}).items(): st.markdown(f"[{platform.title()}]({url})")
                if not crawl.social_links: st.caption("None found")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state"><div class="empty-state-icon">👤</div><div class="empty-state-title">No contact data extracted</div><div class="empty-state-sub">Website may not be crawlable</div></div>', unsafe_allow_html=True)
    
    with tab_tech:
        if tech and tech.detected:
            st.markdown('<div class="data-card"><h4>Detected Technologies</h4>', unsafe_allow_html=True)
            st.markdown("".join(f'<span class="tech-chip">✦ {t}</span>' for t in tech.detected), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if hasattr(tech, 'categories') and tech.categories:
                cats = list(tech.categories.items())
                cols = st.columns(min(len(cats), 4))
                for col,(cat,items) in zip(cols,cats):
                    with col:
                        st.markdown(f'<div class="data-card"><h4>{cat}</h4>', unsafe_allow_html=True)
                        for i in items: st.markdown(f"• {i}")
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state"><div class="empty-state-icon">💻</div><div class="empty-state-title">No technologies detected</div><div class="empty-state-sub">Run research on a live website</div></div>', unsafe_allow_html=True)
    
    with tab_audit:
        if dns:
            s1,s2,s3 = st.columns(3)
            ssl_score = 0
            if web and web.ssl and hasattr(web.ssl, 'valid') and web.ssl.valid:
                ssl_score = 100
            for col,(title,score,color,grade) in zip([s1,s2,s3],[
                ("Email Security", dns.score, "#22c55e" if dns.score>=75 else "#f97316" if dns.score>=50 else "#ef4444", dns.grade),
                ("SSL / HTTPS", ssl_score, "#22c55e" if ssl_score else "#ef4444", "A" if ssl_score else "F"),
                ("Lead Opportunity", lead.total, "#ef4444" if lead.total>=90 else "#f97316" if lead.total>=70 else "#22c55e", "Hot" if lead.total>=90 else "Warm" if lead.total>=70 else "Cold"),
            ]):
                with col:
                    st.markdown(f'<div class="scorecard"><div class="scorecard-title">{title}</div><div class="scorecard-score" style="color:{color}">{score}</div><div class="scorecard-grade">Grade: {grade}</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            for f in dns.findings:
                status = getattr(f, 'status', 'WARNING')
                check = getattr(f, 'check', 'Unknown')
                detail = getattr(f, 'detail', 'No details')
                if status == "PASS":
                    st.success(f"✅ **{check}** — {detail}")
                elif status == "FAIL":
                    st.error(f"❌ **{check}** — {detail}")
                else:
                    st.warning(f"⚠️ **{check}** — {detail}")
        else:
            st.info("DNS audit not available.")
    
    with tab_opp:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="data-card"><h4>Score Breakdown</h4>', unsafe_allow_html=True)
            triggered = [r for r in lead.rules if r.triggered]
            for r in triggered:
                st.markdown(f'<div class="profile-row"><span class="profile-label" style="color:#fb923c">+{r.points}</span><span class="profile-value">{r.reason}</span></div>', unsafe_allow_html=True)
            if not triggered: st.caption("No critical issues")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f'<div class="data-card"><h4>Opportunity Summary</h4><p style="color:#e2e8f0;font-size:0.85rem">{lead.opportunity_summary}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="data-card"><h4>Recommended Services</h4>', unsafe_allow_html=True)
            actions = []
            if dns and hasattr(dns, 'has_dmarc') and not dns.has_dmarc:
                actions.append(("📧","Fix email security","Business Email Fix"))
            if web and web.ssl and hasattr(web.ssl, 'valid') and not web.ssl.valid:
                actions.append(("🔒","Fix SSL certificate","Website Security"))
            if not result.email:
                actions.append(("📬","Setup professional email","Email Setup"))
            actions.append(("📊","Full infrastructure audit","IT Audit"))
            for icon,action,svc in actions:
                st.markdown(f'<div class="profile-row"><span class="profile-label">{icon}</span><span class="profile-value">{action} <span class="badge badge-info">{svc}</span></span></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    a1,a2,a3,a4 = st.columns(4)
    with a1:
        if st.button("🧠 AI Analysis", use_container_width=True):
            try:
                st.switch_page("pages/Lead_Intelligence.py")
            except:
                st.info("Please navigate to Lead Intelligence from sidebar")
    with a2:
        if st.button("📄 Proposal", use_container_width=True):
            try:
                st.switch_page("pages/Proposal_Generator.py")
            except:
                st.info("Please navigate to Proposal Generator from sidebar")
    with a3:
        if st.button("👥 CRM", use_container_width=True):
            try:
                st.switch_page("pages/CRM.py")
            except:
                st.info("Please navigate to CRM from sidebar")
    with a4:
        if st.button("🔄 New Search", use_container_width=True):
            for k in ["last_research","last_lead_score","last_tech","last_company_id"]:
                st.session_state.pop(k, None)
            st.rerun()
else:
    # Empty state
    st.markdown("""<div class="empty-state" style="margin-top:5rem">
        <div class="empty-state-icon">🔍</div>
        <div class="empty-state-title">Search for a company to begin</div>
        <div class="empty-state-sub">Enter a company name or website above and click Research</div>
    </div>""", unsafe_allow_html=True)

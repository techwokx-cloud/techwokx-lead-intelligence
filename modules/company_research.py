import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Research — TechWokx LIE", layout="wide")
from modules.theme import THEME_CSS
st.markdown(THEME_CSS, unsafe_allow_html=True)

from modules.company_research import research_company
from modules.lead_scoring import score_from_research
from modules.technology_detector import detect_technologies
from modules.crm import save_research_to_crm, log_activity
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
    prog = st.progress(0, text="Initialising...")
    step = [0]
    def cb(msg):
        step[0] += 1
        prog.progress(min(step[0]*18, 95), text=msg)
    with st.spinner(""):
        result = research_company(company_name=company_name, website=website, progress_cb=cb)
        lead   = score_from_research(result)
        mx_vals = [f.value for f in result.dns_result.findings if f.check=="MX Records" and f.value] if result.dns_result else []
        tech   = detect_technologies(result.website, mx_records=mx_vals) if result.website else None
    prog.progress(100, text="Complete!")
    st.session_state.update({"last_research": result, "last_lead_score": lead, "last_tech": tech})
    db = get_session()
    db.add(ResearchHistory(company_name=result.company_name, website=result.website, searched_at=datetime.utcnow(), result_summary=f"{lead.total}/100 {lead.status}"))
    db.commit(); db.close()
    cid = save_research_to_crm(result, result.dns_result, result.website_result, lead)
    st.session_state["last_company_id"] = cid
    st.success(f"✅ **{result.company_name}** — Lead Score: **{lead.total}/100 ({lead.status})**")

if "last_research" not in st.session_state:
    st.markdown("""<div class="empty-state" style="margin-top:5rem">
        <div class="empty-state-icon">🔍</div>
        <div class="empty-state-title">Search for a company to begin</div>
        <div class="empty-state-sub">Enter a company name or website above and click Research</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

result = st.session_state["last_research"]
lead   = st.session_state["last_lead_score"]
tech   = st.session_state.get("last_tech")
dns    = result.dns_result
web    = result.website_result
crawl  = result.crawl_result

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
            st.markdown(f'<div class="data-card"><h4>About</h4><p style="color:#94a3b8">{result.description[:400]}</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="data-card"><h4>Website Status</h4>', unsafe_allow_html=True)
        if web:
            for l2,v2 in [("Reachable","✅ Yes" if web.reachable else "❌ No"),("HTTPS","✅ Yes" if web.https else "❌ No"),("SSL Valid","✅ Yes" if (web.ssl and web.ssl.valid) else "❌ No"),("Response",f"{web.response_time_ms}ms" if web.response_time_ms else "—"),("Title",(web.title or "—")[:50])]:
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
        if tech.categories:
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
        ssl_score = 100 if (web and web.ssl and web.ssl.valid) else 0
        for col,(title,score,color,grade) in zip([s1,s2,s3],[
            ("Email Security", dns.score, "#22c55e" if dns.score>=75 else "#f97316" if dns.score>=50 else "#ef4444", dns.grade),
            ("SSL / HTTPS", ssl_score, "#22c55e" if ssl_score else "#ef4444", "A" if ssl_score else "F"),
            ("Lead Opportunity", lead.total, "#ef4444" if lead.total>=90 else "#f97316" if lead.total>=70 else "#22c55e", "Hot" if lead.total>=90 else "Warm" if lead.total>=70 else "Cold"),
        ]):
            with col:
                st.markdown(f'<div class="scorecard"><div class="scorecard-title">{title}</div><div class="scorecard-score" style="color:{color}">{score}</div><div class="scorecard-grade">Grade: {grade}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        for f in dns.findings:
            if f.status=="PASS": st.success(f"✅ **{f.check}** — {f.detail}")
            elif f.status=="FAIL": st.error(f"❌ **{f.check}** — {f.detail}")
            else: st.warning(f"⚠️ **{f.check}** — {f.detail}")
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
        st.markdown(f'<div class="data-card"><h4>Opportunity Summary</h4><p style="color:#94a3b8;font-size:0.85rem">{lead.opportunity_summary}</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="data-card"><h4>Recommended Services</h4>', unsafe_allow_html=True)
        actions = []
        if dns and not dns.has_dmarc: actions.append(("📧","Fix email security","Business Email Fix"))
        if not ssl_score if dns else True: actions.append(("🔒","Fix SSL certificate","Website Security"))
        if not result.email: actions.append(("📬","Setup professional email","Email Setup"))
        actions.append(("📊","Full infrastructure audit","IT Audit"))
        for icon,action,svc in actions:
            st.markdown(f'<div class="profile-row"><span class="profile-label">{icon}</span><span class="profile-value">{action} <span class="badge badge-info">{svc}</span></span></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
a1,a2,a3,a4 = st.columns(4)
with a1:
    if st.button("🧠 AI Analysis", use_container_width=True): st.switch_page("pages/Lead_Intelligence.py")
with a2:
    if st.button("📄 Proposal", use_container_width=True): st.switch_page("pages/Proposal_Generator.py")
with a3:
    if st.button("👥 CRM", use_container_width=True): st.switch_page("pages/CRM.py")
with a4:
    if st.button("🔄 New Search", use_container_width=True):
        for k in ["last_research","last_lead_score","last_tech","last_company_id"]: st.session_state.pop(k,None)
        st.rerun()

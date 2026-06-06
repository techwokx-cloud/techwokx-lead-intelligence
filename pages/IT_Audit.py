import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from modules.theme import THEME_CSS
st.markdown(THEME_CSS, unsafe_allow_html=True)
from modules.dns_audit import run_dns_audit
from modules.website_verifier import verify_website
from modules.lead_scoring import calculate_lead_score

st.markdown("# 🛡️ DNS & Email Security Audit")
st.caption("Standalone audit tool — check any domain's DNS, email security, and SSL.")
st.markdown("---")

c1,c2,c3 = st.columns([3,1,1])
with c1: domain_input = st.text_input("Domain or URL", placeholder="e.g. example.com", label_visibility="collapsed")
with c2: run_dns = st.checkbox("DNS Audit", value=True)
with c3: run_web = st.checkbox("SSL Check", value=True)
run = st.button("🚀 Run Audit", type="primary", use_container_width=True)

if run and domain_input:
    domain = domain_input.lower().replace("https://","").replace("http://","").replace("www.","").split("/")[0]
    with st.spinner("Running audit..."):
        dns = run_dns_audit(domain) if run_dns else None
        web = verify_website(f"https://www.{domain}") if run_web else None
    st.session_state.update({"audit_dns":dns,"audit_web":web,"audit_domain":domain})
    st.success(f"Audit complete for **{domain}**")

if "audit_dns" not in st.session_state:
    st.markdown("""<div class="empty-state" style="margin-top:5rem">
        <div class="empty-state-icon">🛡️</div>
        <div class="empty-state-title">Enter a domain to audit</div>
        <div class="empty-state-sub">DNS, email security, and SSL checks will run automatically</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

dns = st.session_state.get("audit_dns")
web = st.session_state.get("audit_web")
domain = st.session_state.get("audit_domain","")

# Scorecards
st.markdown("<br>", unsafe_allow_html=True)
s1,s2,s3 = st.columns(3)
dns_score = dns.score if dns else 0
ssl_score = 100 if (web and web.ssl and web.ssl.valid) else 0
ls = calculate_lead_score(has_dmarc=dns.has_dmarc if dns else False, has_spf=dns.has_spf if dns else False,
    has_mx=dns.has_mx if dns else False, has_dkim=dns.has_dkim if dns else False,
    ssl_valid=web.ssl.valid if (web and web.ssl) else False, website_up=web.reachable if web else False) if dns or web else None

for col,(title,score,color,grade) in zip([s1,s2,s3],[
    ("Email Security Score", dns_score, "#22c55e" if dns_score>=75 else "#f97316" if dns_score>=50 else "#ef4444", dns.grade if dns else "—"),
    ("Website Security Score", ssl_score, "#22c55e" if ssl_score else "#ef4444", "A" if ssl_score else "F"),
    ("Lead Opportunity Score", ls.total if ls else 0, "#ef4444" if (ls and ls.total>=90) else "#f97316" if (ls and ls.total>=70) else "#22c55e", ls.status if ls else "—"),
]):
    with col:
        st.markdown(f'<div class="scorecard"><div class="scorecard-title">{title}</div><div class="scorecard-score" style="color:{color}">{score}</div><div class="scorecard-grade">Grade: {grade}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
left,right = st.columns(2)

with left:
    st.markdown("### 📧 Email Security Findings")
    if dns:
        st.caption(f"Domain: **{domain}**  |  Email Provider: **{dns.email_provider}**")
        st.progress(dns.score/100)
        for f in dns.findings:
            if f.status=="PASS": st.success(f"✅ **{f.check}** — {f.detail}")
            elif f.status=="FAIL": st.error(f"❌ **{f.check}** — {f.detail}")
            else: st.warning(f"⚠️ **{f.check}** — {f.detail}")

with right:
    st.markdown("### 🌐 Website & SSL")
    if web:
        items = [("Reachable","✅ Yes" if web.reachable else "❌ No"),("HTTPS","✅ Yes" if web.https else "❌ No"),
                 ("SSL Valid","✅ Yes" if (web.ssl and web.ssl.valid) else "❌ No"),
                 ("Status Code",str(web.status_code) if web.status_code else "—"),
                 ("Response",f"{web.response_time_ms}ms" if web.response_time_ms else "—"),
                 ("Page Title",(web.title or "—")[:60])]
        for l,v in items:
            st.markdown(f'<div class="profile-row"><span class="profile-label">{l}</span><span class="profile-value">{v}</span></div>', unsafe_allow_html=True)
        if web.ssl and web.ssl.valid:
            st.info(f"🔒 Issued by: **{web.ssl.issuer}**  |  Expires in: **{web.ssl.days_remaining} days**")
            if web.ssl.days_remaining < 30: st.warning("⚠️ SSL expires in less than 30 days!")
        elif web.ssl and web.ssl.error:
            st.error(f"SSL Error: {web.ssl.error}")

    if ls:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🎯 Opportunity Breakdown")
        for r in [r for r in ls.rules if r.triggered]:
            st.markdown(f'<div class="profile-row"><span class="profile-label" style="color:#fb923c">+{r.points}</span><span class="profile-value">{r.reason}</span></div>', unsafe_allow_html=True)
        st.caption(ls.opportunity_summary)

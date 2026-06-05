import streamlit as st
from modules.dns_audit import run_dns_audit
from modules.website_verifier import verify_website
from modules.lead_scoring import calculate_lead_score

st.set_page_config(page_title="IT Audit — TechWokx LIE", layout="wide")
st.title("🔐 IT Audit")
st.caption("Run a standalone DNS, SSL and website audit on any domain.")

domain_input = st.text_input("Domain or URL", placeholder="e.g. example.com or https://example.com")

col1, col2 = st.columns(2)
with col1:
    run_dns = st.checkbox("DNS & Email Security Audit", value=True)
with col2:
    run_web = st.checkbox("Website & SSL Audit", value=True)

if st.button("🚀 Run Audit", type="primary", use_container_width=True) and domain_input:
    domain = domain_input.lower().replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    url = f"https://www.{domain}"

    with st.spinner("Running audit..."):
        dns_result = run_dns_audit(domain) if run_dns else None
        web_result = verify_website(url) if run_web else None

    st.session_state["audit_dns"] = dns_result
    st.session_state["audit_web"] = web_result
    st.session_state["audit_domain"] = domain
    st.success(f"Audit complete for **{domain}**")

if "audit_dns" in st.session_state or "audit_web" in st.session_state:
    dns = st.session_state.get("audit_dns")
    web = st.session_state.get("audit_web")
    domain = st.session_state.get("audit_domain", "")

    st.markdown("---")
    left, right = st.columns(2)

    # ── Website & SSL ──
    with left:
        st.subheader("🌐 Website & SSL")
        if web:
            status_data = {
                "Website Reachable": ("✅ Yes" if web.reachable else "❌ No", web.reachable),
                "HTTPS Enabled":     ("✅ Yes" if web.https else "❌ No", web.https),
                "SSL Valid":         ("✅ Yes" if (web.ssl and web.ssl.valid) else "❌ No", web.ssl and web.ssl.valid),
                "Status Code":       (str(web.status_code), web.status_code == 200),
            }
            for label, (display, ok) in status_data.items():
                col_l, col_r = st.columns([2, 1])
                col_l.write(label)
                col_r.write(display)

            if web.ssl and web.ssl.valid:
                st.info(f"🔒 SSL Issuer: **{web.ssl.issuer}**  |  Expires in: **{web.ssl.days_remaining} days**")
                if web.ssl.days_remaining < 30:
                    st.warning("⚠️ SSL expires in less than 30 days!")
            elif web.ssl and not web.ssl.valid:
                st.error(f"❌ SSL Error: {web.ssl.error}")

            if web.title:
                st.info(f"📄 Page Title: {web.title}")
            if web.error:
                st.error(f"Error: {web.error}")
        else:
            st.info("Website audit not selected")

    # ── DNS Audit ──
    with right:
        st.subheader("📧 Email Security")
        if dns:
            grade_map = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴", "F": "🔴"}
            st.metric("Email Security Score", f"{dns.score}/100", delta=f"Grade {dns.grade}")
            st.progress(dns.score / 100)
            st.caption(f"Email Provider Detected: **{dns.email_provider}**")

            for f in dns.findings:
                if f.status == "PASS":
                    st.success(f"✅ {f.check}: {f.detail}")
                elif f.status == "FAIL":
                    st.error(f"❌ {f.check}: {f.detail}")
                else:
                    st.warning(f"⚠️ {f.check}: {f.detail}")
        else:
            st.info("DNS audit not selected")

    # ── Lead Score from audit ──
    st.markdown("---")
    st.subheader("🎯 Opportunity Score")
    if dns and web:
        ls = calculate_lead_score(
            has_dmarc=dns.has_dmarc, has_spf=dns.has_spf, has_mx=dns.has_mx, has_dkim=dns.has_dkim,
            ssl_valid=web.ssl.valid if web.ssl else False,
            website_up=web.reachable
        )
        score_emoji = "🔴" if ls.total >= 90 else "🟠" if ls.total >= 70 else "🟢"
        st.metric(f"{score_emoji} Lead Score", f"{ls.total}/100 — {ls.status}")
        st.progress(ls.total / 100)
        st.caption(ls.opportunity_summary)
        triggered = [r for r in ls.rules if r.triggered]
        if triggered:
            with st.expander("View scoring breakdown"):
                for r in triggered:
                    st.markdown(f"- 🔸 **+{r.points}** — {r.reason}")

from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from modules.website_verifier import verify_website
from modules.technology_detector import detect_technologies

st.markdown("# 🌐 Website & SSL Audit")
st.caption("Check website reachability, SSL certificate, and detect technologies.")
st.markdown("---")

c1,c2 = st.columns([4,1])
with c1: url = st.text_input("", placeholder="Enter URL e.g. https://nyahoclinic.com", label_visibility="collapsed")
with c2: run = st.button("🚀 Audit", type="primary", use_container_width=True)

if run and url:
    with st.spinner("Auditing..."):
        web  = verify_website(url)
        tech = detect_technologies(url)
    st.session_state.update({"wa_web":web,"wa_tech":tech,"wa_url":url})

if "wa_web" not in st.session_state:
    st.markdown('<div class="empty-state" style="margin-top:5rem"><div class="empty-state-icon">🌐</div><div class="empty-state-title">Enter a URL to audit</div></div>', unsafe_allow_html=True)
    st.stop()

web  = st.session_state["wa_web"]
tech = st.session_state["wa_tech"]

l,r = st.columns(2)
with l:
    st.markdown("### 🔐 Website Status")
    for label,val in [("Reachable","✅ Yes" if web.reachable else "❌ No"),("HTTPS","✅ Yes" if web.https else "❌ No"),("SSL Valid","✅ Yes" if (web.ssl and web.ssl.valid) else "❌ No"),("Status Code",str(web.status_code) if web.status_code else "—"),("Response",f"{web.response_time_ms}ms" if web.response_time_ms else "—"),("Page Title",(web.title or "—")[:60])]:
        st.markdown(f'<div class="profile-row"><span class="profile-label">{label}</span><span class="profile-value">{val}</span></div>', unsafe_allow_html=True)
    if web.ssl and web.ssl.valid:
        st.success(f"🔒 SSL: **{web.ssl.issuer}** — Expires in **{web.ssl.days_remaining} days**")
        if web.ssl.days_remaining < 30: st.warning("⚠️ Expiring soon!")
    elif web.ssl: st.error(f"SSL Error: {web.ssl.error}")

with r:
    st.markdown("### 💻 Technologies Detected")
    if tech and tech.detected:
        st.markdown("".join(f'<span class="tech-chip">✦ {t}</span>' for t in tech.detected), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        for cat,items in (tech.categories or {}).items():
            st.markdown(f"**{cat}:** {', '.join(items)}")
    else:
        st.caption("No technologies detected or site unreachable")

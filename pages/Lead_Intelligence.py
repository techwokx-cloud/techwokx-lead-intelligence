from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from modules.ai_analysis import generate_ai_analysis
from modules.crm import get_all_companies, get_company, log_activity
import os

st.markdown("# 🧠 Lead Intelligence")
st.caption("AI-powered analysis — risks, opportunities and recommended actions.")
st.markdown("---")

has_ai = bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))
provider = "claude" if os.getenv("ANTHROPIC_API_KEY") else "openai"

if not has_ai:
    st.warning("⚠️ No AI API key set. Add keys in **Settings**. Fallback analysis will be used.")

tab1, tab2 = st.tabs(["From Last Research", "Select from CRM"])

with tab1:
    if "last_research" in st.session_state:
        result = st.session_state["last_research"]
        lead   = st.session_state.get("last_lead_score")
        c1,c2  = st.columns([3,1])
        with c1: st.info(f"Ready to analyse: **{result.company_name}**  |  Score: **{lead.total if lead else '—'}/100**")
        with c2:
            if st.button("🤖 Run Analysis", type="primary", use_container_width=True):
                with st.spinner("Generating AI analysis..."):
                    ai = generate_ai_analysis(result, result.dns_result, result.website_result, lead, provider=provider)
                st.session_state["last_ai"] = ai
                if "last_company_id" in st.session_state:
                    log_activity(st.session_state["last_company_id"], "AI Analysis", f"Urgency: {ai.get('urgency','—')}")
    else:
        st.markdown("""<div class="empty-state"><div class="empty-state-icon">🔍</div>
            <div class="empty-state-title">No research loaded</div>
            <div class="empty-state-sub">Run a Company Research first, then return here for AI analysis</div>
        </div>""", unsafe_allow_html=True)

with tab2:
    companies = get_all_companies()
    if companies:
        opts = {f"{c.company_name} — {c.lead_status or 'Cold'} — {int(c.lead_score or 0)}/100": c.id for c in companies}
        sel = st.selectbox("Choose company", list(opts.keys()))
        if st.button("🤖 Analyse", type="primary"):
            co = get_company(opts[sel])
            class R:
                company_name=co.company_name; website=co.website or ""; domain=(co.website or "").replace("https://","").replace("http://","").replace("www.","").split("/")[0]
                phone=co.phone or ""; email=co.email or ""; address=co.address or ""; description=co.description or ""; confidence_score=co.confidence_score or 0; dns_result=None; website_result=None
            class L:
                total=int(co.lead_score or 0); status=co.lead_status or "Cold"; rules=[]
            with st.spinner("Generating..."):
                ai = generate_ai_analysis(R(), None, None, L(), provider=provider)
            st.session_state["last_ai"] = ai
            log_activity(opts[sel], "AI Analysis", "Generated from CRM")
    else:
        st.caption("No companies in CRM yet.")

# ── Results ──
if "last_ai" not in st.session_state:
    st.stop()

ai = st.session_state["last_ai"]
st.markdown("---")

urgency = ai.get("urgency","MEDIUM")
urg_color = {"HIGH":"#ef4444","MEDIUM":"#f97316","LOW":"#22c55e"}.get(urgency,"#f97316")
st.markdown(f'<div style="background:rgba(0,0,0,0.2);border-left:4px solid {urg_color};padding:0.75rem 1rem;border-radius:0 8px 8px 0;margin-bottom:1.5rem"><span style="color:{urg_color};font-weight:700;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em">Urgency: {urgency}</span></div>', unsafe_allow_html=True)

c1,c2 = st.columns(2)
with c1:
    st.markdown('<div class="data-card"><h4>Company Summary</h4>', unsafe_allow_html=True)
    st.write(ai.get("company_summary","—"))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="data-card"><h4>Business Risks</h4>', unsafe_allow_html=True)
    for r in ai.get("business_risks",[]):
        st.markdown(f'<div class="profile-row"><span style="color:#f87171;margin-right:0.5rem">▸</span><span class="profile-value">{r}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="data-card"><h4>Technology Risks</h4>', unsafe_allow_html=True)
    for r in ai.get("technology_risks",[]):
        st.markdown(f'<div class="profile-row"><span style="color:#fb923c;margin-right:0.5rem">▸</span><span class="profile-value">{r}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="data-card"><h4>Email Security Risks</h4>', unsafe_allow_html=True)
    for r in ai.get("email_risks",[]):
        st.markdown(f'<div class="profile-row"><span style="color:#fbbf24;margin-right:0.5rem">▸</span><span class="profile-value">{r}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="data-card"><h4>Recommended Services</h4>', unsafe_allow_html=True)
    for s in ai.get("recommended_services",[]):
        st.markdown(f'<div class="profile-row"><span style="color:#4ade80;margin-right:0.5rem">✓</span><span class="profile-value" style="font-weight:600">{s}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="data-card"><h4>Revenue Opportunity</h4>', unsafe_allow_html=True)
    st.info(ai.get("sales_opportunity","—"))
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
if st.button("📄 Generate Proposal from This Analysis", type="primary"):
    st.session_state["ai_for_proposal"] = ai
    st.switch_page("pages/Proposal_Generator.py")

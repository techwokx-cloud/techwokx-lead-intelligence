from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from modules.proposal_generator import generate_cold_email, generate_whatsapp_message, generate_pdf_proposal
from modules.crm import get_all_companies, get_company, log_activity, update_stage
from datetime import datetime

st.markdown("# 📄 Proposal Generator")
st.caption("Generate personalised emails, WhatsApp pitches and branded PDF proposals.")
st.markdown("---")

def get_ctx():
    if "last_research" in st.session_state:
        r = st.session_state["last_research"]
        l = st.session_state.get("last_lead_score")
        ai = st.session_state.get("ai_for_proposal") or st.session_state.get("last_ai") or {}
        dns = r.dns_result
        findings = [f"{f.check}: {f.detail}" for f in dns.findings] if dns else []
        return {"company_name":r.company_name,"website":r.website or "","address":r.address or "","email":r.email or "","phone":r.phone or "","lead_score":l.total if l else 0,"findings":findings,"risks":ai.get("business_risks",["Email security issues","Website security gap"]),"recommendations":ai.get("recommended_services",["Business Email Fix","IT Audit"]),"ai_summary":ai.get("company_summary","")}, st.session_state.get("last_company_id")
    return None, None

ctx, cid = get_ctx()

use_crm = st.toggle("Select from CRM pipeline")
if use_crm:
    companies = get_all_companies()
    if companies:
        opts = {f"{c.company_name} — Score {int(c.lead_score or 0)}": c.id for c in companies}
        sel = st.selectbox("Company", list(opts.keys()))
        cid = opts[sel]
        c = get_company(cid)
        ctx = {"company_name":c.company_name,"website":c.website or "","address":c.address or "","email":c.email or "","phone":c.phone or "","lead_score":int(c.lead_score or 0),"findings":[f"Email score: {c.dns_score}/100"],"risks":["Email impersonation risk","Website security gap"],"recommendations":["Business Email Fix","IT Infrastructure Audit"],"ai_summary":c.ai_summary or ""}

if not ctx:
    st.markdown("""<div class="empty-state" style="margin-top:4rem"><div class="empty-state-icon">📄</div>
        <div class="empty-state-title">No company loaded</div>
        <div class="empty-state-sub">Run a Company Research first or select from CRM above</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# Editable details
with st.expander("✏️ Edit contact details"):
    ec1,ec2 = st.columns(2)
    with ec1:
        ctx["company_name"] = st.text_input("Company Name", ctx["company_name"])
        ctx["address"] = st.text_input("Address", ctx.get("address",""))
    with ec2:
        contact = st.text_input("Contact Name / Title", "The Director")
        ctx["email"] = st.text_input("Email", ctx.get("email",""))

st.markdown("---")

# ── Split layout: controls left, preview right ──
left, right = st.columns([1, 1.2])

with left:
    st.markdown("### 📝 Generate")
    tab1,tab2,tab3 = st.tabs(["📧 Cold Email","💬 WhatsApp","📑 PDF"])

    with tab1:
        if st.button("Generate Email", type="primary", use_container_width=True):
            e = generate_cold_email(ctx["company_name"], contact, ctx["findings"], ctx["risks"], ctx["lead_score"])
            st.session_state["gen_email"] = e
            if cid: log_activity(cid, "Email Generated", f"Cold email for {ctx['company_name']}")
        if "gen_email" in st.session_state:
            e = st.session_state["gen_email"]
            st.text_input("Subject", e["subject"])
            st.download_button("⬇️ Download .txt", e["body"], file_name=f"email_{ctx['company_name'].replace(' ','_')}.txt")

    with tab2:
        if st.button("Generate WhatsApp", type="primary", use_container_width=True):
            wa = generate_whatsapp_message(ctx["company_name"], ctx["findings"], ctx["lead_score"])
            st.session_state["gen_wa"] = wa
            if cid: log_activity(cid, "WhatsApp Generated", f"WhatsApp for {ctx['company_name']}")
        if "gen_wa" in st.session_state:
            wa_enc = st.session_state["gen_wa"].replace(" ","%20").replace("\n","%0A")
            st.markdown(f"[📱 Open in WhatsApp](https://wa.me/?text={wa_enc})")
            st.download_button("⬇️ Download", st.session_state["gen_wa"], file_name="whatsapp.txt")

    with tab3:
        if st.button("Generate PDF Proposal", type="primary", use_container_width=True):
            with st.spinner("Building PDF..."):
                try:
                    pdf = generate_pdf_proposal({"company_name":ctx["company_name"],"lead_score":ctx["lead_score"]}, ctx["findings"][:8], ctx["risks"][:6], ctx["recommendations"], ctx.get("ai_summary",""))
                    st.session_state["gen_pdf"] = pdf
                    if cid: log_activity(cid,"Proposal Generated","PDF proposal created"); update_stage(cid,"Proposal Sent")
                except Exception as ex:
                    st.error(f"Error: {ex}")
        if "gen_pdf" in st.session_state:
            st.download_button("⬇️ Download PDF", st.session_state["gen_pdf"],
                file_name=f"TechWokx_Proposal_{ctx['company_name'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")

with right:
    st.markdown("### 👁️ Live Preview")
    preview_type = st.radio("", ["Email","WhatsApp","About Company"], horizontal=True, label_visibility="collapsed")

    if preview_type == "Email" and "gen_email" in st.session_state:
        e = st.session_state["gen_email"]
        st.markdown(f'<div class="data-card"><div style="font-size:0.8rem;color:#475569;margin-bottom:0.5rem">Subject</div><div style="font-weight:600;color:#e2e8f0;font-size:0.9rem">{e["subject"]}</div></div>', unsafe_allow_html=True)
        st.text_area("", e["body"], height=480, label_visibility="collapsed")
    elif preview_type == "WhatsApp" and "gen_wa" in st.session_state:
        st.markdown(f'<div class="data-card" style="border-radius:12px;max-width:380px"><div style="background:#1a472a;padding:0.75rem 1rem;border-radius:10px;font-size:0.85rem;color:#e2e8f0;white-space:pre-wrap">{st.session_state["gen_wa"]}</div></div>', unsafe_allow_html=True)
    elif preview_type == "About Company":
        score_cls = "score-hot" if ctx["lead_score"]>=90 else "score-warm" if ctx["lead_score"]>=70 else "score-good"
        st.markdown(f"""<div class="data-card">
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
                <div class="score-ring {score_cls}" style="width:70px;height:70px;font-size:1.2rem">{ctx['lead_score']}<br><span style="font-size:0.55rem">/100</span></div>
                <div><div style="font-size:1.1rem;font-weight:700;color:#e2e8f0">{ctx['company_name']}</div>
                <div style="font-size:0.8rem;color:#475569">{ctx.get('website','—')}</div></div>
            </div>""", unsafe_allow_html=True)
        for l,v in [("Phone",ctx.get("phone","—")),("Email",ctx.get("email","—")),("Address",ctx.get("address","—")),("Score",f"{ctx['lead_score']}/100")]:
            st.markdown(f'<div class="profile-row"><span class="profile-label">{l}</span><span class="profile-value">{v}</span></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-state"><div class="empty-state-icon">👁️</div><div class="empty-state-title">Generate content to preview it here</div></div>', unsafe_allow_html=True)

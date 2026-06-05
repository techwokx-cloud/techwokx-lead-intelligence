import streamlit as st
from modules.proposal_generator import generate_cold_email, generate_whatsapp_message, generate_pdf_proposal
from modules.crm import get_all_companies, get_company, log_activity
from datetime import datetime

st.set_page_config(page_title="Proposal Generator — TechWokx LIE", layout="wide")
st.title("📄 Proposal Generator")
st.caption("Generate cold emails, WhatsApp messages, and PDF proposals.")

# ── Load data ──
def get_context():
    if "last_research" in st.session_state:
        r = st.session_state["last_research"]
        lead = st.session_state.get("last_lead_score")
        dns = r.dns_result
        ai = st.session_state.get("ai_for_proposal") or st.session_state.get("last_ai") or {}
        findings = [f"{f.check}: {f.detail}" for f in dns.findings] if dns else []
        risks = ai.get("business_risks", ["Email security issues found", "Website security needs improvement"])
        recommendations = ai.get("recommended_services", ["Business Email Fix", "IT Infrastructure Audit"])
        return {
            "company_name": r.company_name, "website": r.website, "address": r.address,
            "email": r.email, "phone": r.phone, "lead_score": lead.total if lead else 0,
            "findings": findings, "risks": risks, "recommendations": recommendations,
            "ai_summary": ai.get("company_summary", ""),
        }, st.session_state.get("last_company_id")
    return None, None

ctx, cid = get_context()

# Override with CRM selection
companies = get_all_companies()
use_crm = st.toggle("Select company from CRM instead")
if use_crm and companies:
    opts = {f"{c.company_name} — Score {c.lead_score or 0}": c.id for c in companies}
    sel = st.selectbox("Company", list(opts.keys()))
    cid = opts[sel]
    c = get_company(cid)
    ctx = {
        "company_name": c.company_name, "website": c.website or "", "address": c.address or "",
        "email": c.email or "", "phone": c.phone or "", "lead_score": c.lead_score or 0,
        "findings": [f"Email score: {c.dns_score}/100", "Review infrastructure"],
        "risks": ["Email impersonation risk", "Website security gap"],
        "recommendations": ["Business Email Fix", "IT Infrastructure Audit"],
        "ai_summary": c.ai_summary or "",
    }

if not ctx:
    st.info("Run a Company Research first, or select a company from CRM above.")
    st.stop()

# ── Form overrides ──
with st.expander("✏️ Edit Contact Details"):
    col1, col2 = st.columns(2)
    with col1:
        ctx["company_name"] = st.text_input("Company Name", ctx["company_name"])
        ctx["address"] = st.text_input("Address", ctx.get("address", ""))
    with col2:
        contact_name = st.text_input("Contact Name / Title", "The Director")
        ctx["email"] = st.text_input("Contact Email", ctx.get("email", ""))

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📧 Cold Email", "💬 WhatsApp Message", "📑 PDF Proposal"])

# ── Cold Email ──
with tab1:
    if st.button("Generate Cold Email", type="primary"):
        email_data = generate_cold_email(
            company=ctx["company_name"], contact=contact_name,
            findings=ctx["findings"], risks=ctx["risks"], lead_score=ctx["lead_score"]
        )
        st.session_state["generated_email"] = email_data
        if cid:
            log_activity(cid, "Email Generated", f"Cold email generated for {ctx['company_name']}")

    if "generated_email" in st.session_state:
        e = st.session_state["generated_email"]
        st.text_input("Subject", e["subject"])
        body_edit = st.text_area("Email Body", e["body"], height=500)
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📋 Copy Subject"):
                st.write("Subject copied to clipboard (use Ctrl+A in the field above)")
        with col_b:
            st.download_button("⬇️ Download .txt", body_edit, file_name=f"email_{ctx['company_name'].replace(' ','_')}.txt")

# ── WhatsApp ──
with tab2:
    if st.button("Generate WhatsApp Message", type="primary"):
        wa = generate_whatsapp_message(ctx["company_name"], ctx["findings"], ctx["lead_score"])
        st.session_state["generated_wa"] = wa
        if cid:
            log_activity(cid, "WhatsApp Generated", f"WhatsApp message generated for {ctx['company_name']}")

    if "generated_wa" in st.session_state:
        wa_edit = st.text_area("WhatsApp Message", st.session_state["generated_wa"], height=200)
        wa_encoded = wa_edit.replace(" ", "%20").replace("\n", "%0A")
        st.markdown(f"[📱 Open in WhatsApp](https://wa.me/?text={wa_encoded})", unsafe_allow_html=True)
        st.download_button("⬇️ Download .txt", wa_edit, file_name="whatsapp_message.txt")

# ── PDF Proposal ──
with tab3:
    st.caption("Generate a professional PDF proposal with TechWokx branding and QR code.")
    if st.button("📑 Generate PDF Proposal", type="primary"):
        with st.spinner("Generating PDF..."):
            try:
                pdf_bytes = generate_pdf_proposal(
                    company_data={
                        "company_name": ctx["company_name"],
                        "lead_score": ctx["lead_score"],
                    },
                    findings=ctx["findings"][:8],
                    risks=ctx["risks"][:6],
                    recommendations=ctx["recommendations"],
                    ai_summary=ctx.get("ai_summary", ""),
                )
                st.success("PDF generated!")
                st.download_button(
                    "⬇️ Download PDF Proposal",
                    pdf_bytes,
                    file_name=f"TechWokx_Proposal_{ctx['company_name'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
                if cid:
                    log_activity(cid, "Proposal Generated", f"PDF proposal generated")
                    from modules.crm import update_stage
                    update_stage(cid, "Proposal Sent")
            except Exception as ex:
                st.error(f"PDF error: {ex}. Check reportlab and qrcode are installed.")

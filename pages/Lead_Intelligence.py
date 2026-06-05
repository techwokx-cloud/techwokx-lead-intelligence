import streamlit as st
from modules.ai_analysis import generate_ai_analysis
from modules.crm import get_all_companies, get_company, log_activity
import os

st.set_page_config(page_title="Lead Intelligence — TechWokx LIE", layout="wide")
st.title("🤖 Lead Intelligence")
st.caption("AI-powered analysis of company risks, opportunities, and recommended services.")

# Check API keys
has_claude = bool(os.getenv("ANTHROPIC_API_KEY"))
has_openai = bool(os.getenv("OPENAI_API_KEY"))
if not has_claude and not has_openai:
    st.warning("⚠️ No AI API key found. Add keys in **Settings** for full AI analysis. Fallback analysis will be used.")

provider = "claude" if has_claude else "openai" if has_openai else "fallback"

# ── Source selector ──
tab1, tab2 = st.tabs(["From Last Research", "Select from CRM"])

with tab1:
    if "last_research" in st.session_state:
        result = st.session_state["last_research"]
        lead = st.session_state.get("last_lead_score")
        st.info(f"Using research data for: **{result.company_name}**")
        if st.button("🤖 Run AI Analysis", type="primary"):
            with st.spinner("Generating AI analysis..."):
                ai = generate_ai_analysis(result, result.dns_result, result.website_result, lead, provider=provider)
            st.session_state["last_ai"] = ai
            if "last_company_id" in st.session_state:
                log_activity(st.session_state["last_company_id"], "AI Analysis", f"AI analysis generated. Urgency: {ai.get('urgency','—')}")
    else:
        st.info("Run a Company Research first to populate data here.")

with tab2:
    companies = get_all_companies()
    if companies:
        options = {f"{c.company_name} ({c.lead_status or 'Cold'}) — Score: {c.lead_score or 0}": c.id for c in companies}
        selected = st.selectbox("Select Company", list(options.keys()))
        cid = options[selected]
        if st.button("🤖 Analyse Selected Company", type="primary"):
            company = get_company(cid)

            class MockResearch:
                company_name = company.company_name
                website = company.website or ""
                domain = company.website.replace("https://","").replace("http://","").replace("www.","").split("/")[0] if company.website else ""
                phone = company.phone or ""
                email = company.email or ""
                address = company.address or ""
                description = company.description or ""
                confidence_score = company.confidence_score or 0
                dns_result = None
                website_result = None

            class MockLead:
                total = company.lead_score or 0
                status = company.lead_status or "Cold"
                rules = []

            with st.spinner("Generating AI analysis..."):
                ai = generate_ai_analysis(MockResearch(), None, None, MockLead(), provider=provider)
            st.session_state["last_ai"] = ai
            log_activity(cid, "AI Analysis", f"AI analysis generated.")
    else:
        st.info("No companies in CRM yet. Run Company Research first.")

# ── Display AI Results ──
if "last_ai" in st.session_state:
    ai = st.session_state["last_ai"]
    st.markdown("---")

    urgency = ai.get("urgency", "MEDIUM")
    urgency_color = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟢"}.get(urgency, "🟡")
    st.subheader(f"{urgency_color} Urgency: {urgency}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏢 Company Summary")
        st.write(ai.get("company_summary", "—"))

        st.subheader("⚠️ Business Risks")
        for r in ai.get("business_risks", []):
            st.markdown(f"- 🔸 {r}")

        st.subheader("💻 Technology Risks")
        for r in ai.get("technology_risks", []):
            st.markdown(f"- 🔧 {r}")

    with col2:
        st.subheader("📧 Email Risks")
        for r in ai.get("email_risks", []):
            st.markdown(f"- 📩 {r}")

        st.subheader("✅ Recommended Services")
        for s in ai.get("recommended_services", []):
            st.markdown(f"- ✅ **{s}**")

        st.subheader("💰 Sales Opportunity")
        st.info(ai.get("sales_opportunity", "—"))

    if st.button("📄 Generate Proposal from This Analysis", type="primary"):
        st.session_state["ai_for_proposal"] = ai
        st.switch_page("pages/Proposal_Generator.py")

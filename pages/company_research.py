# pages/company_research.py
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Try to import with error handling
try:
    from modules.theme import THEME_CSS
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    
    from modules.company_research import research_company
    from modules.lead_scoring import score_from_research
    from modules.technology_detector import detect_technologies
    from modules.crm import save_research_to_crm
    from modules.database import get_session, ResearchHistory
    from datetime import datetime
    
    IMPORT_SUCCESS = True
except Exception as e:
    IMPORT_SUCCESS = False
    st.error(f"❌ Import Error: {str(e)}")
    st.info("""
    Please make sure all required modules exist:
    - modules/company_research.py
    - modules/lead_scoring.py
    - modules/technology_detector.py
    - modules/crm.py
    - modules/database.py
    - modules/theme.py
    - modules/website_verifier.py
    - modules/website_crawler.py
    - modules/dns_audit.py
    """)
    st.stop()

if IMPORT_SUCCESS:
    st.set_page_config(
        page_title="Company Research",
        page_icon="🔍",
        layout="wide"
    )
    
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
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(msg):
            status_text.text(msg)
            # Increment progress
            current = progress_bar.progress.value if hasattr(progress_bar, 'value') else 0
            progress_bar.progress(min(current + 0.1, 0.95))
        
        try:
            with st.spinner("Researching..."):
                result = research_company(company_name=company_name, website=website, progress_cb=update_progress)
                lead = score_from_research(result)
                
                # Detect technologies
                mx_vals = []
                if result.dns_result and hasattr(result.dns_result, 'findings'):
                    mx_vals = [f.value for f in result.dns_result.findings if f.check == "MX Records" and f.value]
                tech = detect_technologies(result.website, mx_records=mx_vals) if result.website else None
                
                # Save to database
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
                
                progress_bar.progress(1.0)
                status_text.text("Complete!")
                
                st.success(f"✅ **{result.company_name}** — Lead Score: **{lead.total}/100 ({lead.status})**")
                
        except Exception as research_error:
            st.error(f"Research failed: {str(research_error)}")
            st.stop()
    
    # Display results if available
    if "last_research" in st.session_state:
        result = st.session_state["last_research"]
        lead = st.session_state["last_lead_score"]
        tech = st.session_state.get("last_tech")
        
        # Display company info
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"## {result.company_name}")
            st.caption(f"🌐 {result.website or '—'} | 📞 {result.phone or '—'} | ✉️ {result.email or '—'}")
        with col2:
            st.metric("Lead Score", f"{lead.total}/100", delta=lead.status)
        with col3:
            st.metric("Confidence", f"{int(result.confidence_score)}%", delta=result.confidence_label)
        
        st.markdown("---")
        
        # Simple tabs
        tabs = st.tabs(["Overview", "Contacts", "Technology", "Actions"])
        
        with tabs[0]:
            st.markdown("**Company Information**")
            st.write(f"**Name:** {result.company_name}")
            st.write(f"**Website:** {result.website or 'N/A'}")
            st.write(f"**Phone:** {result.phone or 'N/A'}")
            st.write(f"**Email:** {result.email or 'N/A'}")
            st.write(f"**Address:** {result.address or 'N/A'}")
            if result.description:
                st.write(f"**Description:** {result.description}")
        
        with tabs[1]:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Emails Found**")
                if result.crawl_result and result.crawl_result.emails:
                    for email in result.crawl_result.emails:
                        st.code(email)
                else:
                    st.caption("No emails found")
            
            with col2:
                st.markdown("**Phone Numbers Found**")
                if result.crawl_result and result.crawl_result.phones:
                    for phone in result.crawl_result.phones[:5]:
                        st.code(phone)
                else:
                    st.caption("No phones found")
        
        with tabs[2]:
            if tech and tech.detected:
                st.markdown("**Detected Technologies**")
                st.write(", ".join(tech.detected))
            else:
                st.info("No technologies detected")
        
        with tabs[3]:
            st.markdown("**Recommended Actions**")
            if not result.email:
                st.warning("📧 No email found - Setup professional email")
            if not result.phone:
                st.warning("📞 No phone found - Add contact number")
            if result.dns_result and not result.dns_result.has_dmarc:
                st.warning("🔒 No DMARC - Improve email security")
            st.info("📊 Schedule a full IT audit")
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🔄 New Search", use_container_width=True):
                for k in ["last_research", "last_lead_score", "last_tech", "last_company_id"]:
                    st.session_state.pop(k, None)
                st.rerun()
    else:
        # Empty state
        st.info("👈 Enter a company name or website above and click 'Research' to begin")

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

# Error handling for imports
try:
    from modules.theme import THEME_CSS
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    
    from modules.company_research import research_company
    from modules.lead_scoring import score_from_research
    from modules.database import get_session, ResearchHistory
    from datetime import datetime
    
except Exception as e:
    st.error(f"Import Error: {str(e)}")
    st.info("Please make sure all modules are properly installed")
    st.stop()

st.markdown("# 📊 Bulk Company Research")
st.caption("Research multiple companies at once")
st.markdown("---")

# Bulk research UI
company_list = st.text_area(
    "Enter company names (one per line)",
    placeholder="Nyaho Medical Centre\nNakomachi Financial Services\nKasapreko Company Limited",
    height=150
)

if st.button("🚀 Research All", type="primary"):
    if company_list:
        companies = [c.strip() for c in company_list.split("\n") if c.strip()]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        for i, company in enumerate(companies):
            status_text.text(f"Researching {company}...")
            try:
                result = research_company(company_name=company, website="")
                lead = score_from_research(result)
                results.append({
                    "Company": result.company_name,
                    "Website": result.website,
                    "Lead Score": f"{lead.total}/100",
                    "Status": lead.status,
                    "Email": result.email or "N/A",
                    "Phone": result.phone or "N/A"
                })
                
                # Save to database
                db = get_session()
                db.add(ResearchHistory(
                    company_name=result.company_name,
                    website=result.website,
                    searched_at=datetime.utcnow(),
                    result_summary=f"{lead.total}/100 {lead.status}"
                ))
                db.commit()
                db.close()
                
            except Exception as e:
                results.append({
                    "Company": company,
                    "Website": "Error",
                    "Lead Score": "Error",
                    "Status": str(e)[:50],
                    "Email": "N/A",
                    "Phone": "N/A"
                })
            
            progress_bar.progress((i + 1) / len(companies))
        
        status_text.text("Research complete!")
        
        # Display results
        st.markdown("## Results")
        st.dataframe(results, use_container_width=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            import pandas as pd
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "bulk_research.csv", "text/csv")
    else:
        st.warning("Please enter at least one company name")

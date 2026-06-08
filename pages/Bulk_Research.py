# pages/Bulk_Research.py
import sys
import os

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Streamlit FIRST
import streamlit as st

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="Bulk Company Research",
    page_icon="📊",
    layout="wide"
)

# Then import other modules
from dotenv import load_dotenv
load_dotenv()

# Try to import theme safely
try:
    from modules.theme import THEME_CSS
    st.markdown(THEME_CSS, unsafe_allow_html=True)
except Exception:
    pass  # Theme is optional

# Import other modules with error handling
try:
    from modules.company_research import research_company
    from modules.lead_scoring import score_from_research
    from modules.database import get_session, ResearchHistory
    from datetime import datetime
    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False
    st.error(f"⚠️ Import Error: {e}")
    st.info("Make sure all module files exist in the 'modules' folder")
    # Don't stop, allow basic functionality

# Page title
st.markdown("# 📊 Bulk Company Research")
st.caption("Research multiple companies at once and export results")
st.markdown("---")

# Input section
company_list = st.text_area(
    "📝 Enter Company Names (one per line)",
    placeholder="Nyaho Medical Centre\nNakomachi Financial Services\nKasapreko Company Limited\nMTN Ghana\nGCB Bank",
    height=200,
    help="Enter one company name per line. Maximum 20 companies at once."
)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    country = st.selectbox("Country", ["Ghana", "Nigeria", "Kenya", "South Africa", "Other"])
with col2:
    max_companies = st.number_input("Max Companies", min_value=1, max_value=20, value=10)
with col3:
    run_bulk = st.button("🚀 Start Bulk Research", type="primary", use_container_width=True)

# Store results in session state
if 'bulk_results' not in st.session_state:
    st.session_state.bulk_results = []
if 'research_complete' not in st.session_state:
    st.session_state.research_complete = False

# Function to save to database
def save_to_database(company_name, website, lead_score, status):
    try:
        db = get_session()
        history = ResearchHistory(
            company_name=company_name,
            website=website or "",
            searched_at=datetime.utcnow(),
            result_summary=f"{lead_score}/100 {status}"
        )
        db.add(history)
        db.commit()
        db.close()
        return True
    except Exception as e:
        st.warning(f"Could not save to database: {e}")
        return False

# Run bulk research
if run_bulk and company_list:
    companies = [c.strip() for c in company_list.split("\n") if c.strip()]
    
    # Limit number of companies
    if len(companies) > max_companies:
        st.warning(f"Limiting to first {max_companies} companies")
        companies = companies[:max_companies]
    
    if not companies:
        st.error("Please enter at least one company name")
        st.stop()
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    results = []
    
    for i, company in enumerate(companies):
        status_text.text(f"🔍 Researching {i+1}/{len(companies)}: {company}")
        
        try:
            # Research the company
            result = research_company(company_name=company, website="")
            
            # Score the lead
            if IMPORT_SUCCESS:
                lead = score_from_research(result)
                lead_score = lead.total
                lead_status = lead.status
                opportunity = lead.opportunity_summary[:100] if hasattr(lead, 'opportunity_summary') else ""
            else:
                lead_score = 0
                lead_status = "Unknown"
                opportunity = "Scoring module not available"
            
            # Save to database
            save_to_database(result.company_name, result.website, lead_score, lead_status)
            
            # Store result
            results.append({
                "Company": result.company_name,
                "Website": result.website or "N/A",
                "Email": result.email or "N/A",
                "Phone": result.phone or "N/A",
                "Lead Score": f"{lead_score}/100",
                "Status": lead_status,
                "Confidence": f"{int(result.confidence_score)}%",
                "Has Email": "✅" if result.email else "❌",
                "Has Phone": "✅" if result.phone else "❌"
            })
            
        except Exception as e:
            st.error(f"Error researching {company}: {str(e)[:100]}")
            results.append({
                "Company": company,
                "Website": "Error",
                "Email": "N/A",
                "Phone": "N/A",
                "Lead Score": "Error",
                "Status": "Failed",
                "Confidence": "0%",
                "Has Email": "❌",
                "Has Phone": "❌"
            })
        
        # Update progress
        progress_bar.progress((i + 1) / len(companies))
        
        # Show live results
        with results_container:
            st.markdown(f"### Results ({i+1}/{len(companies)})")
            
            # Create DataFrame for display
            import pandas as pd
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
    
    status_text.text("✅ Research Complete!")
    st.session_state.bulk_results = results
    st.session_state.research_complete = True
    
    # Success message
    st.balloons()
    st.success(f"✅ Successfully researched {len(results)} companies!")
    
    # Export options
    st.markdown("---")
    st.markdown("## 📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export to CSV
        if st.button("📊 Export to CSV", use_container_width=True):
            import pandas as pd
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV File",
                data=csv,
                file_name=f"bulk_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        # Export to JSON
        if st.button("📋 Export to JSON", use_container_width=True):
            import json
            json_str = json.dumps(results, indent=2, default=str)
            st.download_button(
                label="Download JSON File",
                data=json_str,
                file_name=f"bulk_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        # Clear results
        if st.button("🔄 Clear Results", use_container_width=True):
            st.session_state.bulk_results = []
            st.session_state.research_complete = False
            st.rerun()

elif run_bulk and not company_list:
    st.warning("⚠️ Please enter at least one company name to research")

# Display previous results if they exist
if st.session_state.research_complete and st.session_state.bulk_results:
    st.markdown("---")
    st.markdown("## 📈 Summary Statistics")
    
    results = st.session_state.bulk_results
    
    # Calculate statistics
    total = len(results)
    successful = sum(1 for r in results if r.get("Website") != "Error")
    
    # Extract scores safely
    scores = []
    for r in results:
        try:
            score_str = r.get("Lead Score", "0/100")
            score = int(score_str.split('/')[0]) if '/' in score_str else 0
            scores.append(score)
        except:
            scores.append(0)
    
    avg_score = sum(scores) / len(scores) if scores else 0
    hot_leads = sum(1 for s in scores if s >= 70)
    warm_leads = sum(1 for s in scores if 50 <= s < 70)
    cold_leads = sum(1 for s in scores if s < 50)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Companies", total)
    with col2:
        st.metric("Successful", successful)
    with col3:
        st.metric("Avg Lead Score", f"{avg_score:.0f}/100")
    with col4:
        st.metric("Hot Leads (70+)", hot_leads)
    with col5:
        st.metric("Warm Leads (50-69)", warm_leads)
    
    # Show top leads
    st.markdown("### 🔥 Top 5 Hot Leads")
    
    # Sort by lead score
    sorted_results = sorted(results, key=lambda x: int(x.get("Lead Score", "0/100").split('/')[0]) if x.get("Lead Score") != "Error" else 0, reverse=True)
    top_leads = [r for r in sorted_results if r.get("Lead Score") != "Error"][:5]
    
    if top_leads:
        for i, lead in enumerate(top_leads, 1):
            with st.expander(f"{i}. {lead['Company']} - Score: {lead['Lead Score']} ({lead['Status']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Website:** {lead['Website']}")
                    st.write(f"**Email:** {lead['Email']}")
                with col2:
                    st.write(f"**Phone:** {lead['Phone']}")
                    st.write(f"**Confidence:** {lead['Confidence']}")
    else:
        st.info("No hot leads found in this batch")

# Empty state
elif not run_bulk and not st.session_state.bulk_results:
    st.info("👆 Enter company names above and click 'Start Bulk Research' to begin")
    
    with st.expander("📖 How to use Bulk Research"):
        st.markdown("""
        **Instructions:**
        1. Enter one company name per line in the text area
        2. Select the country (helps with search accuracy)
        3. Set maximum number of companies to research (1-20)
        4. Click 'Start Bulk Research'
        5. Wait for the research to complete
        6. Export results to CSV or JSON
        
        **Tips:**
        - Use exact company names for best results
        - Maximum 20 companies per batch to avoid timeouts
        - Results are automatically saved to the CRM
        - Hot leads (score 70+) are highlighted
        """)
    
    # Example companies
    st.markdown("### 📝 Example Companies to Try")
    if st.button("Load Example Companies"):
        example = """MTN Ghana
GCB Bank
Nyaho Medical Centre
Kasapreko Company Limited
Nakomachi Financial Services"""
        st.session_state.example_loaded = True
        st.rerun()
    
    if st.session_state.get('example_loaded'):
        st.text_area("Companies loaded!", value=example, height=150, disabled=True)

# Footer
st.markdown("---")
st.caption("TechWokx Lead Intelligence - Bulk Research Module")

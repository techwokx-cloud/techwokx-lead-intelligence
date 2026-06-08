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

# Now import other modules
from dotenv import load_dotenv
load_dotenv()

# Try to import theme safely
try:
    from modules.theme import THEME_CSS
    st.markdown(THEME_CSS, unsafe_allow_html=True)
except Exception:
    pass

# Import with error handling
try:
    from modules.company_research import research_company
    from modules.lead_scoring import score_from_research
    from modules.database import get_session, ResearchHistory
    from datetime import datetime
    import pandas as pd
    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False
    st.error(f"⚠️ Import Error: {e}")
    st.info("Please make sure all module files exist in the 'modules' folder")
    st.stop()

st.markdown("# 📊 Bulk Company Research")
st.caption("Research multiple companies at once and export results")
st.markdown("---")

# Initialize session state
if 'bulk_results' not in st.session_state:
    st.session_state.bulk_results = []
if 'research_complete' not in st.session_state:
    st.session_state.research_complete = False

# Input section
company_list = st.text_area(
    "📝 Enter Company Names (one per line)",
    placeholder="Nyaho Medical Centre\nMTN Ghana\nGCB Bank\nKasapreko Company Limited",
    height=150,
    help="Enter one company name per line"
)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    max_companies = st.number_input("Max Companies", min_value=1, max_value=20, value=10)
with col2:
    run_bulk = st.button("🚀 Start Bulk Research", type="primary", use_container_width=True)
with col3:
    if st.button("🔄 Clear Results", use_container_width=True):
        st.session_state.bulk_results = []
        st.session_state.research_complete = False
        st.rerun()

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
        return False

# Run bulk research
if run_bulk and company_list:
    companies = [c.strip() for c in company_list.split("\n") if c.strip()]
    
    if len(companies) > max_companies:
        st.warning(f"⚠️ Limiting to first {max_companies} companies")
        companies = companies[:max_companies]
    
    if not companies:
        st.error("❌ Please enter at least one company name")
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
            lead = score_from_research(result)
            lead_score = lead.total
            lead_status = lead.status
            
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
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
    
    progress_bar.progress(1.0)
    status_text.text("✅ Research Complete!")
    st.session_state.bulk_results = results
    st.session_state.research_complete = True
    
    st.balloons()
    st.success(f"✅ Successfully researched {len(results)} companies!")

# Display results if they exist
if st.session_state.research_complete and st.session_state.bulk_results:
    results = st.session_state.bulk_results
    
    st.markdown("---")
    st.markdown("## 📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to CSV", use_container_width=True):
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"bulk_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            df = pd.DataFrame(results)
            st.info("Select all data in the table above and copy (Ctrl+C)")
    
    with col3:
        if st.button("🔄 New Research", use_container_width=True):
            st.session_state.bulk_results = []
            st.session_state.research_complete = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 📈 Summary Statistics")
    
    # Calculate statistics
    total = len(results)
    successful = sum(1 for r in results if r.get("Website") != "Error")
    
    scores = []
    for r in results:
        score_str = r.get("Lead Score", "0/100")
        try:
            score = int(score_str.split('/')[0]) if '/' in score_str else 0
            scores.append(score)
        except:
            scores.append(0)
    
    avg_score = sum(scores) / len(scores) if scores else 0
    hot_leads = sum(1 for s in scores if s >= 70)
    warm_leads = sum(1 for s in scores if 50 <= s < 70)
    cold_leads = sum(1 for s in scores if s < 50 and s > 0)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Companies", total)
    with col2:
        st.metric("Successful", successful)
    with col3:
        st.metric("Avg Lead Score", f"{avg_score:.0f}/100")
    with col4:
        st.metric("🔥 Hot Leads (70+)", hot_leads)
    with col5:
        st.metric("📊 Warm Leads (50-69)", warm_leads)
    
    # Show top leads
    if hot_leads > 0:
        st.markdown("---")
        st.markdown("### 🔥 Hot Leads")
        
        hot_companies = [r for r in results if r.get("Lead Score") != "Error" and int(r.get("Lead Score", "0/100").split('/')[0]) >= 70]
        for lead in hot_companies[:5]:
            with st.expander(f"📌 {lead['Company']} - Score: {lead['Lead Score']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Website:** {lead['Website']}")
                    st.write(f"**Email:** {lead['Email']}")
                with col2:
                    st.write(f"**Phone:** {lead['Phone']}")
                    st.write(f"**Confidence:** {lead['Confidence']}")

# Empty state
elif not run_bulk and not st.session_state.bulk_results:
    st.info("👆 Enter company names above and click 'Start Bulk Research' to begin")
    
    with st.expander("📖 How to use Bulk Research"):
        st.markdown("""
        **Instructions:**
        1. Enter one company name per line
        2. Set maximum number of companies (1-20)
        3. Click 'Start Bulk Research'
        4. Results will appear as they complete
        5. Export to CSV when done
        
        **Tips:**
        - Use exact company names for best results
        - Maximum 20 companies per batch
        - Results are saved to the database automatically
        """)
    
    # Example companies
    st.markdown("### 📝 Example Companies")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏥 Medical Companies", use_container_width=True):
            example = "Nyaho Medical Centre\nKorle Bu Teaching Hospital\nUniversity of Ghana Medical Centre"
            st.session_state.example_loaded = example
            st.rerun()
    
    with col2:
        if st.button("🏦 Financial Companies", use_container_width=True):
            example = "GCB Bank\nMTN Ghana\nKasapreko Company Limited"
            st.session_state.example_loaded = example
            st.rerun()
    
    if st.session_state.get('example_loaded'):
        st.text_area("Companies loaded!", value=st.session_state.example_loaded, height=100)

# Footer
st.markdown("---")
st.caption(f"TechWokx Bulk Research • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

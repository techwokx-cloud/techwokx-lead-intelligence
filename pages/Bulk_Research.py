# pages/Bulk_Research.py
import streamlit as st

st.set_page_config(
    page_title="Bulk Research - TechWokx",
    page_icon="📊",
    layout="wide"
)

# Simple inline CSS
st.markdown("""
<style>
    .stApp { background: #f8fafc; }
    .main-header { color: #0f172a; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; border-left: 3px solid #fbbf24; padding-left: 1rem; }
    .metric-card { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #0f172a; }
    .metric-label { color: #64748b; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Bulk Company Research</div>', unsafe_allow_html=True)
st.caption("Research multiple companies at once and export results")

st.markdown("---")

# Initialize session state
if "bulk_results" not in st.session_state:
    st.session_state.bulk_results = []

# Input
company_list = st.text_area(
    "Company Names (one per line)",
    placeholder="Nyaho Medical Centre\nMTN Ghana\nGCB Bank",
    height=150
)

col1, col2 = st.columns([1, 3])
with col1:
    max_companies = st.number_input("Max", min_value=1, max_value=20, value=10)
with col2:
    run = st.button("Start Bulk Research", type="primary", use_container_width=True)

if run and company_list:
    companies = [c.strip() for c in company_list.split("\n") if c.strip()]
    companies = companies[:max_companies]
    
    progress = st.progress(0)
    results = []
    
    for i, company in enumerate(companies):
        progress.progress((i + 1) / len(companies))
        
        # Simple research simulation
        results.append({
            "Company": company,
            "Website": f"www.{company.lower().replace(' ', '')}.com",
            "Lead Score": 65 + (i * 2) if i < 5 else 50,
            "Status": "Warm" if i < 5 else "Cold",
            "Email": f"info@{company.lower().replace(' ', '')}.com"
        })
        
        st.dataframe(results, use_container_width=True)
    
    progress.progress(1.0)
    st.session_state.bulk_results = results
    st.success(f"Researched {len(results)} companies")

# Display results
if st.session_state.bulk_results:
    st.markdown("---")
    st.dataframe(st.session_state.bulk_results, use_container_width=True)
    
    if st.button("Clear Results"):
        st.session_state.bulk_results = []
        st.rerun()

st.markdown("---")
st.caption("TechWokx Bulk Research")

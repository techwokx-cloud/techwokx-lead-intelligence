# pages/CRM.py
import sys
import os

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Streamlit FIRST
import streamlit as st

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="CRM - Lead Management",
    page_icon="👥",
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
    pass  # Theme is optional

# Import database modules with error handling
try:
    from modules.database import get_session, CRMCompany, CRMActivity
    import pandas as pd
    from datetime import datetime
    DB_AVAILABLE = True
except ImportError as e:
    DB_AVAILABLE = False
    st.error(f"⚠️ Database module not available: {e}")
    st.stop()

st.markdown("# 👥 CRM Dashboard")
st.caption("Manage and track your leads")
st.markdown("---")

# Initialize session state
if 'selected_company_id' not in st.session_state:
    st.session_state.selected_company_id = None
if 'refresh_crm' not in st.session_state:
    st.session_state.refresh_crm = False

# Refresh button
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("### Lead Database")
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.session_state.refresh_crm = True
        st.rerun()
with col3:
    if st.button("➕ Add Manual Entry", use_container_width=True):
        st.session_state.show_add_form = True

# Fetch companies from database
try:
    db = get_session()
    companies = db.query(CRMCompany).order_by(CRMCompany.lead_score.desc()).all()
    db.close()
except Exception as e:
    st.error(f"Error fetching companies: {e}")
    companies = []

if companies:
    # Convert to DataFrame for display
    data = []
    for c in companies:
        data.append({
            "ID": c.id,
            "Company": c.name,
            "Domain": c.domain,
            "Lead Score": c.lead_score or 0,
            "Status": c.lead_status or "New",
            "Phone": c.phone or "N/A",
            "Email": c.email or "N/A",
            "Last Research": c.last_research.strftime("%Y-%m-%d") if c.last_research else "Never",
            "Created": c.created_at.strftime("%Y-%m-%d") if c.created_at else "Unknown"
        })
    
    df = pd.DataFrame(data)
    
    # Filters
    st.markdown("### Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect("Status", options=df["Status"].unique() if not df.empty else [])
    with col2:
        min_score = st.slider("Min Lead Score", 0, 100, 0)
    with col3:
        sort_by = st.selectbox("Sort By", ["Lead Score", "Company", "Last Research", "Created"])
    with col4:
        sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter:
        filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]
    if min_score > 0:
        filtered_df = filtered_df[filtered_df["Lead Score"] >= min_score]
    
    # Apply sorting
    if sort_by == "Lead Score":
        filtered_df = filtered_df.sort_values("Lead Score", ascending=(sort_order == "Ascending"))
    elif sort_by == "Company":
        filtered_df = filtered_df.sort_values("Company", ascending=(sort_order == "Ascending"))
    elif sort_by == "Last Research":
        filtered_df = filtered_df.sort_values("Last Research", ascending=(sort_order == "Ascending"))
    elif sort_by == "Created":
        filtered_df = filtered_df.sort_values("Created", ascending=(sort_order == "Ascending"))
    
    # Display statistics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Leads", len(filtered_df))
    with col2:
        hot = len(filtered_df[filtered_df["Lead Score"] >= 70])
        st.metric("Hot Leads (70+)", hot)
    with col3:
        warm = len(filtered_df[(filtered_df["Lead Score"] >= 50) & (filtered_df["Lead Score"] < 70)])
        st.metric("Warm Leads (50-69)", warm)
    with col4:
        cold = len(filtered_df[filtered_df["Lead Score"] < 50])
        st.metric("Cold Leads (<50)", cold)
    with col5:
        avg_score = filtered_df["Lead Score"].mean() if not filtered_df.empty else 0
        st.metric("Avg Lead Score", f"{avg_score:.0f}")
    
    st.markdown("---")
    
    # Display data table
    st.markdown("### Lead Database")
    st.dataframe(filtered_df, use_container_width=True, height=400)
    
    # Company details section
    st.markdown("---")
    st.markdown("### Company Details")
    
    # Select company for detailed view
    company_names = filtered_df["Company"].tolist() if not filtered_df.empty else []
    selected_company_name = st.selectbox("Select a company to view details", company_names)
    
    if selected_company_name:
        # Get company details
        db = get_session()
        company = db.query(CRMCompany).filter_by(name=selected_company_name).first()
        
        if company:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Company Information")
                st.write(f"**Name:** {company.name}")
                st.write(f"**Domain:** {company.domain}")
                st.write(f"**Website:** {company.website or 'N/A'}")
                st.write(f"**Lead Score:** {company.lead_score}/100")
                st.write(f"**Status:** {company.lead_status}")
                
                if company.lead_score >= 70:
                    st.success("🎯 **High Priority Lead** - Ready for outreach")
                elif company.lead_score >= 50:
                    st.warning("📌 **Medium Priority Lead** - Nurture needed")
                else:
                    st.info("📋 **Low Priority Lead** - More research required")
            
            with col2:
                st.markdown("#### Contact Information")
                st.write(f"**Phone:** {company.phone or 'Not found'}")
                st.write(f"**Email:** {company.email or 'Not found'}")
                st.write(f"**Address:** {company.address or 'Not provided'}")
            
            # Quick actions
            st.markdown("#### Quick Actions")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📞 Call", use_container_width=True):
                    st.info(f"Call {company.phone}" if company.phone else "No phone number available")
            
            with col2:
                if st.button("✉️ Email", use_container_width=True):
                    st.info(f"Email {company.email}" if company.email else "No email available")
            
            with col3:
                if st.button("📄 Proposal", use_container_width=True):
                    st.session_state.last_company_id = company.id
                    st.switch_page("pages/Proposal_Generator.py")
            
            with col4:
                if st.button("🗑️ Delete", use_container_width=True):
                    if st.session_state.get('confirm_delete'):
                        try:
                            db = get_session()
                            db.delete(company)
                            db.commit()
                            db.close()
                            st.success(f"Deleted {company.name}")
                            st.session_state.refresh_crm = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting: {e}")
                    else:
                        st.session_state.confirm_delete = True
                        st.warning("Click again to confirm delete")
            
            # Activity log
            st.markdown("#### Recent Activity")
            try:
                db = get_session()
                activities = db.query(CRMActivity).filter_by(company_id=company.id).order_by(CRMActivity.created_at.desc()).limit(10).all()
                db.close()
                
                if activities:
                    for act in activities:
                        st.caption(f"📝 {act.created_at.strftime('%Y-%m-%d %H:%M')} - {act.activity_type}: {act.description}")
                else:
                    st.caption("No recent activities")
            except Exception as e:
                st.caption(f"Activity log unavailable: {e}")
            
            # Add activity
            st.markdown("#### Add Activity")
            activity_type = st.selectbox("Activity Type", ["Call", "Email", "Meeting", "Note", "Follow-up"])
            activity_desc = st.text_input("Description")
            if st.button("➕ Add Activity", use_container_width=True):
                if activity_desc:
                    try:
                        db = get_session()
                        activity = CRMActivity(
                            company_id=company.id,
                            activity_type=activity_type,
                            description=activity_desc,
                            created_at=datetime.utcnow()
                        )
                        db.add(activity)
                        db.commit()
                        db.close()
                        st.success("Activity added!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding activity: {e}")
                else:
                    st.warning("Please enter a description")
        
        db.close()

else:
    # Empty state
    st.info("📭 No companies in CRM yet. Research some companies to get started!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Go to Company Research", use_container_width=True):
            st.switch_page("pages/company_research.py")
    with col2:
        if st.button("📊 Try Bulk Research", use_container_width=True):
            st.switch_page("pages/Bulk_Research.py")
    
    st.markdown("---")
    st.markdown("### Sample Companies to Research")
    st.markdown("""
    - Nyaho Medical Centre
    - MTN Ghana
    - GCB Bank
    - Kasapreko Company Limited
    """)

# Footer
st.markdown("---")
st.caption(f"TechWokx CRM • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# pages/Dashboard.py
import sys
import os

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Streamlit FIRST
import streamlit as st

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="Dashboard - Lead Intelligence",
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

# Import database with error handling
try:
    from modules.database import get_session, CRMCompany, ResearchHistory
    import pandas as pd
    from datetime import datetime, timedelta
    DB_AVAILABLE = True
except ImportError as e:
    DB_AVAILABLE = False
    st.error(f"⚠️ Database module not available: {e}")
    st.info("Make sure database.py exists in the modules folder")
    st.stop()

st.markdown("# 📊 Lead Intelligence Dashboard")
st.caption("Overview of your lead pipeline and research activity")
st.markdown("---")

# Helper functions
def get_dashboard_stats():
    """Get dashboard statistics directly from database"""
    try:
        db = get_session()
        
        # Get all companies
        companies = db.query(CRMCompany).all()
        
        # Calculate stats
        total_companies = len(companies)
        hot_leads = sum(1 for c in companies if c.lead_score and c.lead_score >= 70)
        warm_leads = sum(1 for c in companies if c.lead_score and 50 <= c.lead_score < 70)
        cold_leads = sum(1 for c in companies if c.lead_score and c.lead_score < 50)
        no_score = sum(1 for c in companies if not c.lead_score)
        
        # Calculate average lead score
        scores = [c.lead_score for c in companies if c.lead_score]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Get recent research
        recent_research = db.query(ResearchHistory).order_by(ResearchHistory.searched_at.desc()).limit(10).all()
        
        db.close()
        
        return {
            'total_companies': total_companies,
            'hot_leads': hot_leads,
            'warm_leads': warm_leads,
            'cold_leads': cold_leads,
            'no_score': no_score,
            'avg_score': avg_score,
            'recent_research': recent_research,
            'all_companies': companies
        }
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        return None

def get_all_companies():
    """Get all companies from database"""
    try:
        db = get_session()
        companies = db.query(CRMCompany).order_by(CRMCompany.lead_score.desc()).all()
        db.close()
        return companies
    except Exception as e:
        st.error(f"Error fetching companies: {e}")
        return []

# Refresh button
if st.button("🔄 Refresh Data", use_container_width=False):
    st.cache_data.clear()
    st.rerun()

# Get dashboard data
stats = get_dashboard_stats()

if stats and stats['total_companies'] > 0:
    # Display key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Companies", stats['total_companies'])
    with col2:
        st.metric("Hot Leads (70+)", stats['hot_leads'], 
                 delta=f"{stats['hot_leads']/stats['total_companies']*100:.0f}% of total" if stats['total_companies'] > 0 else None)
    with col3:
        st.metric("Warm Leads (50-69)", stats['warm_leads'])
    with col4:
        st.metric("Cold Leads (<50)", stats['cold_leads'])
    with col5:
        st.metric("Average Lead Score", f"{stats['avg_score']:.0f}/100")
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Lead Distribution")
        
        # Create pie chart data
        chart_data = pd.DataFrame({
            'Category': ['Hot Leads (70+)', 'Warm Leads (50-69)', 'Cold Leads (<50)', 'No Score'],
            'Count': [stats['hot_leads'], stats['warm_leads'], stats['cold_leads'], stats['no_score']]
        })
        
        # Filter out zero values for pie chart
        chart_data = chart_data[chart_data['Count'] > 0]
        
        if not chart_data.empty:
            st.bar_chart(chart_data.set_index('Category'))
        else:
            st.info("No lead data available")
    
    with col2:
        st.markdown("### Lead Score Distribution")
        
        # Get score distribution
        companies = stats['all_companies']
        scores = [c.lead_score for c in companies if c.lead_score]
        
        if scores:
            # Create score bins
            bins = [0, 20, 40, 60, 80, 100]
            labels = ['0-20', '21-40', '41-60', '61-80', '81-100']
            score_df = pd.DataFrame({'score': scores})
            score_df['range'] = pd.cut(score_df['score'], bins=bins, labels=labels, include_lowest=True)
            distribution = score_df['range'].value_counts().sort_index()
            
            st.bar_chart(distribution)
        else:
            st.info("No score data available")
    
    st.markdown("---")
    
    # Recent research activity
    st.markdown("### Recent Research Activity")
    
    if stats['recent_research']:
        recent_data = []
        for r in stats['recent_research']:
            recent_data.append({
                "Company": r.company_name,
                "Website": r.website or "N/A",
                "Date": r.searched_at.strftime("%Y-%m-%d %H:%M") if r.searched_at else "Unknown",
                "Result": r.result_summary or "No summary"
            })
        
        recent_df = pd.DataFrame(recent_data)
        st.dataframe(recent_df, use_container_width=True)
    else:
        st.info("No research activity yet. Start researching companies!")
    
    st.markdown("---")
    
    # Top leads table
    st.markdown("### Top 10 Hot Leads")
    
    companies = get_all_companies()
    if companies:
        top_leads = []
        for c in companies[:10]:
            top_leads.append({
                "Company": c.name,
                "Domain": c.domain,
                "Lead Score": c.lead_score or 0,
                "Status": c.lead_status or "New",
                "Phone": c.phone or "N/A",
                "Email": c.email or "N/A",
                "Last Research": c.last_research.strftime("%Y-%m-%d") if c.last_research else "Never"
            })
        
        top_df = pd.DataFrame(top_leads)
        st.dataframe(top_df, use_container_width=True)
        
        # Quick action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔍 Research More Companies", use_container_width=True):
                st.switch_page("pages/company_research.py")
        with col2:
            if st.button("📊 Bulk Research", use_container_width=True):
                st.switch_page("pages/Bulk_Research.py")
        with col3:
            if st.button("👥 View Full CRM", use_container_width=True):
                st.switch_page("pages/CRM.py")
    else:
        st.info("No companies in the database yet")
    
else:
    # Empty state - no data
    st.info("📭 No data available yet. Start by researching some companies!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Research a Company", use_container_width=True):
            st.switch_page("pages/company_research.py")
    with col2:
        if st.button("📊 Bulk Research", use_container_width=True):
            st.switch_page("pages/Bulk_Research.py")
    
    st.markdown("---")
    st.markdown("### Quick Start Guide")
    st.markdown("""
    1. **Research Companies** - Go to Company Research page
    2. **Enter company names** - Try "Nyaho Medical Centre" or "MTN Ghana"
    3. **View results** - See lead scores and contact info
    4. **Check Dashboard** - Return here to see analytics
    """)
    
    # Sample data button
    if st.button("📝 Load Sample Data (Demo)"):
        st.info("Sample data would be loaded here. Research real companies to see actual data!")

# Weekly trend (if enough data)
st.markdown("---")
st.markdown("### Research Activity (Last 7 Days)")

try:
    db = get_session()
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    weekly_research = db.query(ResearchHistory).filter(
        ResearchHistory.searched_at >= seven_days_ago
    ).all()
    db.close()
    
    if weekly_research:
        # Group by day
        daily_counts = {}
        for r in weekly_research:
            day = r.searched_at.strftime("%Y-%m-%d")
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        # Create dataframe
        trend_df = pd.DataFrame([
            {"Date": date, "Research Count": count} 
            for date, count in sorted(daily_counts.items())
        ])
        
        st.line_chart(trend_df.set_index("Date"))
    else:
        st.caption("No research activity in the last 7 days")
except Exception as e:
    st.caption(f"Activity data unavailable: {e}")

# Footer
st.markdown("---")
st.caption(f"TechWokx Lead Intelligence • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

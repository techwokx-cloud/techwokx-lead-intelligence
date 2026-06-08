# pages/Lead_Intelligence.py
import sys
import os

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Streamlit FIRST
import streamlit as st

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="Lead Intelligence",
    page_icon="🧠",
    layout="wide"
)

# Now import other modules
from dotenv import load_dotenv
load_dotenv()

# Import CRM functions
try:
    from modules.crm import get_all_companies, get_company, log_activity
    from modules.database import get_session
    from datetime import datetime
    import pandas as pd
    CRM_AVAILABLE = True
except ImportError as e:
    CRM_AVAILABLE = False
    st.error(f"⚠️ CRM module not available: {e}")
    st.stop()

# Page title
st.markdown("# 🧠 Lead Intelligence")
st.caption("AI-powered insights and recommendations for your leads")
st.markdown("---")

# Initialize session state for theme
if 'proposal_light_mode' not in st.session_state:
    st.session_state.proposal_light_mode = False

# Theme toggle for this page only
col1, col2 = st.columns([3, 1])
with col2:
    light_mode = st.toggle("☀️ Light Mode", value=st.session_state.proposal_light_mode)
    if light_mode != st.session_state.proposal_light_mode:
        st.session_state.proposal_light_mode = light_mode
        st.rerun()

# Apply light mode CSS if enabled
if st.session_state.proposal_light_mode:
    st.markdown("""
    <style>
        /* Light mode override */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1e293b !important;
        }
        p, li, .stMarkdown {
            color: #334155 !important;
        }
        [data-testid="stMetricValue"] {
            color: #f59e0b !important;
        }
        [data-testid="stMetricLabel"] {
            color: #64748b !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
        }
        .stTextInput > div > div > input {
            background: white;
            border: 1px solid #e2e8f0;
            color: #1e293b;
        }
        .dataframe th {
            background: #f1f5f9;
            color: #1e293b;
        }
        .dataframe td {
            background: white;
            color: #334155;
        }
    </style>
    """, unsafe_allow_html=True)

# Get company from session state
company_id = st.session_state.get("last_company_id")

if company_id:
    company = get_company(company_id)
    
    if company:
        st.markdown(f"## AI Analysis for {company.name}")
        
        # Company overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Lead Score", f"{company.lead_score}/100")
        with col2:
            st.metric("Status", company.lead_status or "New")
        with col3:
            st.metric("Domain", company.domain)
        
        st.markdown("---")
        
        # AI Insights
        st.markdown("### 🤖 AI-Powered Insights")
        
        # Generate insights based on lead score
        if company.lead_score >= 70:
            st.success("### 🎯 High-Quality Lead")
            st.markdown("""
            **Key Insights:**
            - This company shows strong potential for immediate engagement
            - Digital infrastructure appears well-established
            - Ready for enterprise-level solutions
            - Recommended action: Schedule a discovery call within 48 hours
            """)
        elif company.lead_score >= 50:
            st.warning("### 📌 Medium-Quality Lead")
            st.markdown("""
            **Key Insights:**
            - Moderate potential - needs further nurturing
            - Some gaps in digital presence identified
            - Opportunity for targeted solutions
            - Recommended action: Send educational content and schedule follow-up
            """)
        else:
            st.info("### 📋 Low-Quality Lead")
            st.markdown("""
            **Key Insights:**
            - Limited digital presence
            - More research needed to identify needs
            - May require basic IT infrastructure first
            - Recommended action: Gather more information before direct outreach
            """)
        
        st.markdown("---")
        
        # Opportunity Analysis
        st.markdown("### 💼 Opportunity Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Detected Needs")
            needs = []
            if not company.email:
                needs.append("• Professional email setup required")
            if not company.phone:
                needs.append("• Business phone system needed")
            if company.lead_score and company.lead_score < 60:
                needs.append("• Digital presence improvement")
            needs.append("• IT security assessment")
            
            for need in needs:
                st.markdown(need)
        
        with col2:
            st.markdown("#### Recommended Solutions")
            solutions = [
                "• Managed IT Services",
                "• Cloud Migration",
                "• Cybersecurity Assessment",
                "• Website Optimization"
            ]
            for solution in solutions:
                st.markdown(solution)
        
        st.markdown("---")
        
        # Recommendations
        st.markdown("### 📊 Strategic Recommendations")
        
        rec_col1, rec_col2 = st.columns(2)
        
        with rec_col1:
            st.markdown("#### Immediate Actions")
            st.markdown("""
            1. **Connect on LinkedIn** - Research key decision makers
            2. **Send personalized email** - Reference their specific business
            3. **Schedule demo** - Show relevant solutions
            4. **Prepare case study** - Similar industry success
            """)
        
        with rec_col2:
            st.markdown("#### Long-term Strategy")
            st.markdown("""
            1. **Account-based marketing** - Targeted campaigns
            2. **Quarterly business reviews** - Build relationship
            3. **Referral program** - Leverage satisfied clients
            4. **Thought leadership** - Share industry insights
            """)
        
        st.markdown("---")
        
        # Competitor Analysis
        st.markdown("### 🏢 Competitor Context")
        
        if company.domain:
            competitors = [
                f"Other companies in same domain space",
                "Similar-sized businesses in the region",
                "Industry-specific solution providers"
            ]
            for comp in competitors:
                st.markdown(f"• {comp}")
        
        st.markdown("---")
        
        # Action buttons
        st.markdown("### 🚀 Take Action")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Generate Proposal", use_container_width=True):
                st.switch_page("pages/Proposal_Generator.py")
        
        with col2:
            if st.button("📝 Log Activity", use_container_width=True):
                st.session_state.show_activity_log = True
        
        with col3:
            if st.button("🔄 Refresh Analysis", use_container_width=True):
                st.rerun()
        
        # Activity log modal
        if st.session_state.get('show_activity_log'):
            st.markdown("#### Log Activity")
            activity_type = st.selectbox("Activity Type", ["Call", "Email", "Meeting", "Note", "Follow-up"])
            activity_desc = st.text_area("Description")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Activity", use_container_width=True):
                    if activity_desc:
                        log_activity(company.id, activity_type, activity_desc)
                        st.success("Activity logged!")
                        st.session_state.show_activity_log = False
                        st.rerun()
                    else:
                        st.warning("Please enter a description")
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_activity_log = False
                    st.rerun()
        
        # Recent activity
        st.markdown("---")
        st.markdown("### 📝 Recent Activity")
        st.caption("Activity logging coming soon - Your interactions will appear here")
        
    else:
        st.error("Company not found in database")
else:
    st.info("💡 No company selected. Please research a company first from the Company Research page.")
    
    # Show recent companies
    st.markdown("### Recent Companies")
    try:
        companies = get_all_companies()
        if companies:
            recent_companies = companies[:5]
            for comp in recent_companies:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{comp.name}** - Score: {comp.lead_score}/100")
                with col2:
                    if st.button(f"Select", key=comp.id):
                        st.session_state.last_company_id = comp.id
                        st.rerun()
        else:
            st.caption("No companies researched yet")
    except:
        pass
    
    if st.button("🔍 Go to Company Research", use_container_width=True):
        try:
            st.switch_page("pages/company_research.py")
        except:
            st.info("Please navigate to Company Research from the sidebar")

# Footer
st.markdown("---")
st.caption(f"Lead Intelligence • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

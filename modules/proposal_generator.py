# pages/Proposal_Generator.py - Light Mode Version
import sys
import os

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Streamlit FIRST
import streamlit as st

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="Proposal Generator",
    page_icon="📄",
    layout="wide"
)

# Now import other modules
from dotenv import load_dotenv
load_dotenv()

# Import database modules
try:
    from modules.database import get_session, CRMCompany
    from datetime import datetime
    DB_AVAILABLE = True
except ImportError as e:
    DB_AVAILABLE = False
    st.error(f"⚠️ Database module not available: {e}")
    st.stop()

# Light mode CSS for Proposal Generator only
st.markdown("""
<style>
    /* Light mode for Proposal Generator */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
    }
    
    /* Main content area */
    .main .block-container {
        background: transparent;
    }
    
    /* Headers - Dark color for light background */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
    }
    
    /* Paragraph text */
    p, li, .stMarkdown, .stCaption {
        color: #334155 !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #f59e0b !important;
        font-size: 1.8rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #d97706, #b45309);
        transform: translateY(-2px);
    }
    
    /* Text input */
    .stTextInput > div > div > input {
        background: white;
        border: 1px solid #e2e8f0;
        color: #1e293b;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #f59e0b;
        box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.1);
    }
    
    /* Text area */
    .stTextArea > div > div > textarea {
        background: white;
        border: 1px solid #e2e8f0;
        color: #1e293b;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background: white;
        border: 1px solid #e2e8f0;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #334155 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f1f5f9;
        border-radius: 8px;
        color: #1e293b;
    }
    
    .streamlit-expanderHeader:hover {
        background: #e2e8f0;
    }
    
    /* Code blocks / Text area for proposal */
    .stTextArea textarea {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        color: #1e293b !important;
        font-family: monospace;
    }
    
    /* Dividers */
    hr {
        border-color: #e2e8f0;
    }
    
    /* Info messages */
    .stAlert {
        background-color: #fef3c7 !important;
        border-left: 4px solid #f59e0b !important;
        color: #92400e !important;
    }
    
    /* Success messages */
    .stAlert[data-baseweb="notification"] {
        background-color: #d1fae5 !important;
        border-left: 4px solid #10b981 !important;
        color: #065f46 !important;
    }
    
    /* Warning messages */
    .stAlert[data-baseweb="notification"]:has(.stAlertWarning) {
        background-color: #fed7aa !important;
        border-left: 4px solid #f97316 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📄 Proposal Generator")
st.caption("Create professional proposals for your leads (Light Mode)")
st.markdown("---")

# Get company from session state
company_id = st.session_state.get("last_company_id")

if company_id:
    try:
        db = get_session()
        company = db.query(CRMCompany).filter_by(id=company_id).first()
        db.close()
        
        if company:
            st.markdown(f"## Generating Proposal for {company.name}")
            
            # Company Information Display
            with st.expander("Company Information", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Company Details:**")
                    st.write(f"• Name: {company.name}")
                    st.write(f"• Domain: {company.domain}")
                    st.write(f"• Website: {company.website or 'N/A'}")
                with col2:
                    st.write("**Contact Information:**")
                    st.write(f"• Phone: {company.phone or 'N/A'}")
                    st.write(f"• Email: {company.email or 'N/A'}")
                    st.write(f"• Lead Score: {company.lead_score}/100")
            
            # Service selection
            st.markdown("### Select Services to Include")
            
            services = []
            
            col1, col2 = st.columns(2)
            with col1:
                if st.checkbox("📧 Email Security & DMARC Setup", value=True):
                    services.append("Email Security & DMARC Implementation")
                
                if st.checkbox("🔒 SSL Certificate Installation"):
                    services.append("SSL Certificate Installation")
                
                if st.checkbox("📬 Professional Email Setup"):
                    services.append("Business Email Configuration (Google/Microsoft 365)")
                
                if st.checkbox("🛡️ IT Infrastructure Audit"):
                    services.append("Complete IT Security Audit")
            
            with col2:
                if st.checkbox("🌐 Website Development"):
                    services.append("Professional Website Development")
                
                if st.checkbox("📈 SEO & Digital Marketing"):
                    services.append("SEO & Digital Marketing Package")
                
                if st.checkbox("☁️ Cloud Migration"):
                    services.append("Cloud Migration & Setup")
                
                if st.checkbox("🔐 Cybersecurity Assessment"):
                    services.append("Cybersecurity Risk Assessment")
            
            # Additional options
            st.markdown("### Proposal Details")
            additional_notes = st.text_area("Additional Notes/Special Requirements", 
                                           placeholder="Any specific requirements or notes to include in the proposal...")
            
            if services:
                # Generate proposal based on lead score
                if company.lead_score and company.lead_score >= 70:
                    urgency = "High Priority - Immediate Action Recommended"
                    discount = "10% early engagement discount"
                elif company.lead_score and company.lead_score >= 50:
                    urgency = "Medium Priority - Schedule Discussion"
                    discount = "5% early engagement discount"
                else:
                    urgency = "Discovery Phase - Further Assessment Needed"
                    discount = "Contact for custom pricing"
                
                # Create proposal
                proposal = f"""TECHWOKX PROPOSAL

Prepared For: {company.name.upper()}
Date: {datetime.now().strftime('%Y-%m-%d')}
Priority Level: {urgency}

EXECUTIVE SUMMARY
-----------------
This proposal outlines technology services to enhance {company.name}'s digital infrastructure, 
security posture, and operational efficiency. Based on our initial assessment, we have identified 
key areas for improvement that will drive business growth and security.

PROPOSED SERVICES
----------------
{chr(10).join([f'{i+1}. {s}' for i, s in enumerate(services)])}

INVESTMENT OVERVIEW
------------------
The following investment is recommended for the proposed services:

| Service Category | Investment (GHS) |
|-----------------|------------------|
{chr(10).join([f'| {s[:40]}... | To be discussed |' for s in services])}

Discount Available: {discount}

WHY TECHWOKX?
-------------
• 24/7 Technical Support
• Certified Professionals
• Proven Track Record
• Customized Solutions
• Local Presence

DELIVERABLES & TIMELINE
-----------------------
• Initial Assessment: Week 1
• Implementation: Weeks 2-4
• Testing & Validation: Week 5
• Training & Handover: Week 6
• Ongoing Support: Continuous

NEXT STEPS
----------
1. Schedule discovery call
2. Detailed requirements gathering
3. Customized implementation plan
4. Project kickoff meeting

TERMS & CONDITIONS
-----------------
• Payment: 50% upfront, 50% upon completion
• Warranty: 30 days post-implementation
• Support: Included for first 3 months

{additional_notes if additional_notes else ""}

CONTACT INFORMATION
------------------
TechWokx Technologies
Email: sales@techwokx.com
Phone: +233 XX XXX XXXX

This proposal is valid for 30 days from the date above.

---
Proposal Generated by TechWokx Lead Intelligence System
"""
                
                # Display proposal
                st.markdown("### Proposal Preview")
                st.text_area("Proposal Content", proposal, height=400)
                
                # Download button
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        label="📥 Download as Text File",
                        data=proposal,
                        file_name=f"proposal_{company.name.replace(' ', '_')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("📋 Copy to Clipboard", use_container_width=True):
                        st.success("Select all text in the proposal box and copy (Ctrl+C / Cmd+C)")
                
                with col3:
                    if st.button("🔄 Reset Form", use_container_width=True):
                        st.rerun()
            else:
                st.warning("⚠️ Please select at least one service to generate a proposal")
        else:
            st.error("Company not found in database")
    except Exception as e:
        st.error(f"Error loading company data: {str(e)}")
else:
    st.info("💡 No company selected. Please research a company first from the Company Research page.")
    st.markdown("""
    ### How to generate a proposal:
    1. Go to **Company Research** page
    2. Search for a company
    3. Return here to generate a proposal
    """)
    
    if st.button("🔍 Go to Company Research", use_container_width=True):
        try:
            st.switch_page("pages/company_research.py")
        except:
            st.info("Please navigate to Company Research from the sidebar")

# Footer
st.markdown("---")
st.caption(f"Proposal Generator (Light Mode) • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

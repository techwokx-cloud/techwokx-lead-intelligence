# pages/Lead_Followup.py
import sys
import os

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Streamlit FIRST
import streamlit as st

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="Lead Follow-up",
    page_icon="🌱",
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

# Import database modules
from modules.database import get_session, CRMCompany, CRMActivity
from datetime import datetime, timedelta
import pandas as pd

# Try to import email automation
try:
    import resend
    import os
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    st.warning("⚠️ Resend not installed. Run: pip install resend")

# Page title
st.markdown("# 🌱 Lead Follow-up Automation")
st.caption("Auto-follow-up sequences for leads from ads and audits")
st.markdown("---")

# Initialize Resend if available
if RESEND_AVAILABLE:
    resend.api_key = os.getenv("RESEND_API_KEY", "")

# Get stats from database
db = get_session()

# Count leads by status
total_leads = db.query(CRMCompany).count()
red_leads = db.query(CRMCompany).filter_by(lead_status='RED').count()
orange_leads = db.query(CRMCompany).filter_by(lead_status='ORANGE').count()
green_leads = db.query(CRMCompany).filter_by(lead_status='GREEN').count()

db.close()

# Display metrics
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Leads", total_leads)
with col2:
    st.metric("🔴 RED - Critical", red_leads, delta="High Priority")
with col3:
    st.metric("🟠 ORANGE - Moderate", orange_leads)
with col4:
    st.metric("🟢 GREEN - Healthy", green_leads)
with col5:
    st.metric("Resend Status", "✅ Ready" if RESEND_AVAILABLE else "❌ Not configured")

st.markdown("---")

# Tabs for different functions
tab1, tab2, tab3, tab4 = st.tabs(["📧 Due for Follow-up", "📝 Manual Email", "📊 Lead Analytics", "⚙️ Settings"])

# Tab 1: Due for Follow-up
with tab1:
    st.markdown("### 📧 Leads Due for Follow-up")
    st.caption("Leads that haven't been contacted in the last 3 days")
    
    # Get leads due for follow-up
    db = get_session()
    cutoff = datetime.utcnow() - timedelta(days=3)
    
    # Get leads with no recent activity
    from sqlalchemy import not_
    due_leads = db.query(CRMCompany).filter(
        not_(CRMCompany.activities.any(CRMActivity.created_at > cutoff))
    ).all()
    
    if due_leads:
        st.info(f"Found {len(due_leads)} leads needing follow-up")
        
        for lead in due_leads[:10]:  # Show first 10
            with st.expander(f"{lead.name} - {lead.lead_status} - Score: {lead.lead_score}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {lead.email}")
                    st.write(f"**Business:** {lead.domain}")
                    st.write(f"**Source:** {getattr(lead, 'source', 'Audit')}")
                    st.write(f"**Last Contact:** {lead.last_contact if hasattr(lead, 'last_contact') else 'Never'}")
                
                with col2:
                    if st.button(f"📧 Send Follow-up", key=f"send_{lead.id}"):
                        if RESEND_AVAILABLE and resend.api_key:
                            try:
                                # Simple email template
                                email_content = f"""
                                <h2>Follow-up for {lead.name}</h2>
                                <p>Your audit showed {lead.lead_status} level risks.</p>
                                <p>Schedule a free consultation: <a href="{os.getenv('CALENDLY_LINK', 'https://calendly.com/techwokx')}">Book Now</a></p>
                                """
                                
                                params = {
                                    "from": f"TechWokx <{os.getenv('RESEND_FROM_EMAIL', 'hello@techwokx.online')}>",
                                    "to": [lead.email],
                                    "subject": f"Follow-up: Your email audit results",
                                    "html": email_content,
                                }
                                
                                email = resend.Emails.send(params)
                                
                                # Log activity
                                activity = CRMActivity(
                                    company_id=lead.id,
                                    activity_type="Email",
                                    description=f"Manual follow-up sent via Resend"
                                )
                                db.add(activity)
                                db.commit()
                                
                                st.success("✅ Email sent successfully!")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Failed to send: {e}")
                        else:
                            st.error("Resend not configured. Check API key.")
    else:
        st.success("✅ All leads have been followed up recently!")
    
    db.close()

# Tab 2: Manual Email Broadcast
with tab2:
    st.markdown("### 📝 Manual Email Broadcast")
    st.caption("Send custom emails to selected leads")
    
    db = get_session()
    
    # Get all leads for selection
    all_leads = db.query(CRMCompany).all()
    lead_options = {f"{lead.name} ({lead.email})": lead.id for lead in all_leads}
    
    selected_leads = st.multiselect("Select Recipients", list(lead_options.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Email Subject", placeholder="Important update about your email security")
    with col2:
        email_type = st.selectbox("Email Type", ["Follow-up", "Newsletter", "Promotion", "Urgent Fix"])
    
    message = st.text_area("Email Content (HTML supported)", 
                           placeholder="<p>Dear customer,</p><p>Your email security needs attention...</p>",
                           height=200)
    
    if st.button("📧 Send Broadcast", type="primary"):
        if selected_leads and subject and message:
            if RESEND_AVAILABLE and resend.api_key:
                success_count = 0
                progress_bar = st.progress(0)
                
                for i, selected in enumerate(selected_leads):
                    lead_id = lead_options[selected]
                    lead = db.query(CRMCompany).filter_by(id=lead_id).first()
                    
                    try:
                        params = {
                            "from": f"TechWokx <{os.getenv('RESEND_FROM_EMAIL', 'hello@techwokx.online')}>",
                            "to": [lead.email],
                            "subject": subject,
                            "html": message.replace("{name}", lead.name),
                        }
                        
                        resend.Emails.send(params)
                        
                        # Log activity
                        activity = CRMActivity(
                            company_id=lead.id,
                            activity_type="Broadcast Email",
                            description=f"{email_type}: {subject[:50]}"
                        )
                        db.add(activity)
                        success_count += 1
                        
                    except Exception as e:
                        st.error(f"Failed to send to {lead.email}: {e}")
                    
                    progress_bar.progress((i + 1) / len(selected_leads))
                
                db.commit()
                st.success(f"✅ Sent {success_count} of {len(selected_leads)} emails")
            else:
                st.error("Resend not configured")
        else:
            st.warning("Please select recipients, add subject, and message")

    db.close()

# Tab 3: Lead Analytics
with tab3:
    st.markdown("### 📊 Lead Analytics")
    
    db = get_session()
    all_leads = db.query(CRMCompany).all()
    
    if all_leads:
        # Create DataFrame
        data = []
        for lead in all_leads:
            data.append({
                "Name": lead.name,
                "Email": lead.email,
                "Status": lead.lead_status,
                "Score": lead.lead_score,
                "Source": getattr(lead, 'source', 'Audit'),
                "Created": lead.created_at.strftime("%Y-%m-%d") if lead.created_at else "Unknown"
            })
        
        df = pd.DataFrame(data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Lead Status Distribution")
            status_counts = df['Status'].value_counts()
            st.bar_chart(status_counts)
        
        with col2:
            st.markdown("#### Score Distribution")
            st.bar_chart(df['Score'].value_counts().sort_index())
        
        st.markdown("#### All Leads")
        st.dataframe(df, use_container_width=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "leads_export.csv", "text/csv")
    else:
        st.info("No leads in database yet")
    
    db.close()

# Tab 4: Settings
with tab4:
    st.markdown("### ⚙️ Email Settings")
    
    # Check Resend configuration
    st.markdown("#### Resend Configuration")
    
    if RESEND_AVAILABLE:
        api_key_set = bool(os.getenv("RESEND_API_KEY"))
        from_email = os.getenv("RESEND_FROM_EMAIL", "Not set")
        
        st.write(f"**API Key:** {'✅ Configured' if api_key_set else '❌ Missing'}")
        st.write(f"**From Email:** {from_email}")
        
        if not api_key_set:
            st.warning("""
            **To configure Resend:**
            1. Sign up at [Resend.com](https://resend.com)
            2. Add your domain and verify DNS
            3. Copy API key to `.env` file:

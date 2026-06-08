# pages/Lead_Nurture.py
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.database import get_session, CRMCompany, CRMActivity
from modules.email_automation import send_follow_up, get_leads_due_for_followup

st.set_page_config(page_title="Lead Nurture", page_icon="🌱", layout="wide")

st.markdown("# 🌱 Lead Nurture Automation")
st.markdown("Auto-follow-up sequences for leads from ads")

# Stats
db = get_session()
red_leads = db.query(CRMCompany).filter_by(lead_status='RED').count()
orange_leads = db.query(CRMCompany).filter_by(lead_status='ORANGE').count()
green_leads = db.query(CRMCompany).filter_by(lead_status='GREEN').count()
db.close()

col1, col2, col3 = st.columns(3)
col1.metric("🔴 RED - Critical", red_leads)
col2.metric("🟠 ORANGE - Moderate", orange_leads)
col3.metric("🟢 GREEN - Healthy", green_leads)

# Due for follow-up
st.subheader("📧 Leads Due for Follow-Up")
due_leads = get_leads_due_for_followup()

if due_leads:
    for lead in due_leads[:10]:
        with st.expander(f"{lead.name} - {lead.lead_status} - Score: {lead.lead_score}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Email: {lead.email}")
                st.write(f"Business: {lead.domain}")
            with col2:
                if st.button(f"Send Now", key=lead.id):
                    if send_follow_up(lead, 'initial'):
                        st.success("Email sent!")
                        # Log activity
                        db = get_session()
                        activity = CRMActivity(
                            company_id=lead.id,
                            activity_type="Email",
                            description="Automated follow-up sent"
                        )
                        db.add(activity)
                        db.commit()
                        db.close()
                        st.rerun()
                    else:
                        st.error("Failed to send")
else:
    st.info("No leads due for follow-up")

# Manual email
st.markdown("---")
st.subheader("📝 Manual Broadcast")
with st.form("broadcast"):
    audience = st.selectbox("Audience", ["RED Leads", "ORANGE Leads", "GREEN Leads", "All Leads"])
    subject = st.text_input("Subject")
    message = st.text_area("Message")
    
    if st.form_submit_button("Send Broadcast"):
        st.warning(f"This would send to {audience} (configure SMTP in production)")

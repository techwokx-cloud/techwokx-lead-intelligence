# pages/unsubscribe.py
import streamlit as st
from modules.database import get_session, CRMCompany

st.set_page_config(page_title="Unsubscribe", page_icon="📧")

# Get email from query params
query_params = st.query_params
email = query_params.get("email", [None])[0]

if email:
    db = get_session()
    lead = db.query(CRMCompany).filter_by(email=email).first()
    
    if lead:
        lead.unsubscribed = True  # Add this column to database
        db.commit()
        st.success("✅ You've been unsubscribed from future emails.")
        st.info("You can re-subscribe anytime by completing another audit.")
    else:
        st.warning("Email not found in our system.")
    
    db.close()
else:
    st.info("No email provided. Use the link from any email to unsubscribe.")

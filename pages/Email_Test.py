# pages/Email_Test.py
import streamlit as st
import resend
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Email Test", page_icon="📧")

st.markdown("# 📧 Test Resend Email")

# Check configuration
resend.api_key = os.getenv("RESEND_API_KEY")

st.info(f"From Email: {os.getenv('RESEND_FROM_EMAIL', 'Not set')}")
st.info(f"API Key Set: {'✅ Yes' if os.getenv('RESEND_API_KEY') else '❌ No'}")

test_email = st.text_input("Test Email Address", value="your-email@example.com")

if st.button("Send Test Email"):
    try:
        params = {
            "from": f"TechWokx Test <{os.getenv('RESEND_FROM_EMAIL', 'hello@techwokx.online')}>",
            "to": [test_email],
            "subject": "Test Email from TechWokx",
            "html": "<strong>✅ Resend is working!</strong><p>Your email automation is ready.</p>",
        }
        
        email = resend.Emails.send(params)
        st.success(f"Email sent! ID: {email.get('id')}")
        
    except Exception as e:
        st.error(f"Error: {e}")

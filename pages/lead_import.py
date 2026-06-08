# pages/Lead_Import.py
import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
from modules.database import get_session, CRMCompany, CRMActivity

st.set_page_config(page_title="Lead Import", page_icon="📥", layout="wide")

st.markdown("# 📥 Import Leads from Ads")
st.caption("Import Facebook, Google, or Excel leads")

# Required columns
REQUIRED_COLUMNS = ['name', 'email', 'phone', 'business_name']
OPTIONAL_COLUMNS = ['audit_score', 'source', 'campaign', 'pain_point']

uploaded_file = st.file_uploader("Upload CSV/Excel file", type=['csv', 'xlsx'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    # Validate columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()
    
    st.dataframe(df.head())
    
    if st.button("Import Leads"):
        db = get_session()
        for _, row in df.iterrows():
            email_hash = hashlib.md5(row['email'].encode()).hexdigest()
            
            existing = db.query(CRMCompany).filter_by(email_hash=email_hash).first()
            if not existing:
                lead = CRMCompany(
                    name=row['name'],
                    email=row['email'],
                    phone=str(row.get('phone', '')),
                    domain=row['business_name'].lower().replace(' ', '') + '.com',
                    lead_score=row.get('audit_score', 50),
                    lead_status='RED' if row.get('audit_score', 50) < 40 else 'ORANGE' if row.get('audit_score', 50) < 65 else 'GREEN',
                    email_hash=email_hash,
                    source=row.get('source', 'Facebook'),
                    campaign=row.get('campaign', 'Audit'),
                    created_at=datetime.utcnow()
                )
                db.add(lead)
                db.commit()
                
                # Log activity
                activity = CRMActivity(
                    company_id=lead.id,
                    activity_type="Lead Import",
                    description=f"Imported from {row.get('source', 'Facebook')} - Score: {row.get('audit_score', 'N/A')}"
                )
                db.add(activity)
                db.commit()
        
        db.close()
        st.success(f"Imported {len(df)} leads")

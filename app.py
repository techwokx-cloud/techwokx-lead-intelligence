import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="TechWokx Lead Intelligence Engine",
    page_icon="🔍", layout="wide",
    initial_sidebar_state="expanded"
)

from modules.theme import THEME_CSS
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ── Navigation (Streamlit 1.36+ compatible) ──
pg = st.navigation({
    "Main": [
        st.Page("pages/Dashboard.py",        title="Dashboard",         icon="🏠"),
    ],
    "Research": [
        st.Page("pages/Company_Research.py", title="Company Search",    icon="🔍"),
        st.Page("pages/Bulk_Research.py",    title="Bulk Research",     icon="📋"),
    ],
    "Audits": [
        st.Page("pages/IT_Audit.py",         title="DNS & Email Audit", icon="🛡️"),
        st.Page("pages/Website_Audit.py",    title="Website & SSL",     icon="🌐"),
    ],
    "Intelligence": [
        st.Page("pages/Lead_Intelligence.py",title="AI Analysis",       icon="🧠"),
    ],
    "Sales": [
        st.Page("pages/Proposal_Generator.py",title="Proposals",        icon="📄"),
        st.Page("pages/CRM.py",              title="CRM Pipeline",      icon="👥"),
    ],
    "System": [
        st.Page("pages/Settings.py",         title="Settings",          icon="⚙️"),
    ],
})
pg.run()

import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="TechWokx Lead Intelligence Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0D1526; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.metric-card { background: #111e33; border: 1px solid rgba(255,255,255,0.07); border-radius: 10px; padding: 1rem; text-align: center; }
.metric-val  { font-size: 2rem; font-weight: 700; color: #EA580C; }
.metric-label{ font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
.hot  { color: #f87171 !important; font-weight: 700; }
.warm { color: #fb923c !important; font-weight: 700; }
.cold { color: #60a5fa !important; }
.badge-hot  { background: rgba(220,38,38,0.15); color: #f87171; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; }
.badge-warm { background: rgba(234,88,12,0.15); color: #fb923c; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; }
.badge-cold { background: rgba(96,165,250,0.15); color: #60a5fa; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; }
.finding-fail { color: #f87171; }
.finding-warn { color: #fb923c; }
.finding-pass { color: #4ade80; }
div.stButton > button { background: #EA580C; color: white; border: none; border-radius: 8px; font-weight: 600; }
div.stButton > button:hover { background: #c2410c; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
# 🔍 TechWokx Lead Intelligence Engine
**Automate research · Score leads · Generate proposals · Manage pipeline**
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("👈 Use the sidebar to navigate between modules")
with col2:
    st.info("🔑 Add API keys in **Settings** before running AI analysis")
with col3:
    st.info("📊 All leads are saved automatically to your CRM pipeline")

st.markdown("---")
st.markdown("""
### Quick Start
1. Go to **Company Research** — enter a company name or website
2. Run the full audit (website, DNS, email security)
3. View **Lead Intelligence** for AI-generated analysis
4. Generate proposals in **Proposal Generator**
5. Track everything in **CRM**
""")

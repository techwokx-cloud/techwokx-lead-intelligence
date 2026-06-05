import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv, set_key

load_dotenv()
ENV_FILE = Path(".env")

st.set_page_config(page_title="Settings — TechWokx LIE", layout="wide")
st.title("⚙️ Settings")
st.caption("Configure API keys and application settings. Keys are saved to your .env file.")

# ── API Keys ──
st.subheader("🔑 API Keys")

def show_key_status(env_var: str) -> str:
    val = os.getenv(env_var, "")
    if val and len(val) > 8:
        return f"✅ Set ({val[:6]}...{val[-4:]})"
    return "❌ Not set"

with st.form("api_keys_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"Claude API Key: {show_key_status('ANTHROPIC_API_KEY')}")
        claude_key = st.text_input("Anthropic (Claude) API Key", type="password", placeholder="sk-ant-...")

        st.caption(f"OpenAI API Key: {show_key_status('OPENAI_API_KEY')}")
        openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")

    with col2:
        st.caption(f"Google Maps Key: {show_key_status('GOOGLE_MAPS_API_KEY')}")
        gmaps_key = st.text_input("Google Maps API Key", type="password", placeholder="AIza...")

        st.caption(f"SerpAPI Key: {show_key_status('SERP_API_KEY')}")
        serp_key = st.text_input("SerpAPI Key", type="password", placeholder="...")

    submitted = st.form_submit_button("💾 Save API Keys", type="primary", use_container_width=True)

if submitted:
    if not ENV_FILE.exists():
        ENV_FILE.write_text("")
    if claude_key:
        set_key(str(ENV_FILE), "ANTHROPIC_API_KEY", claude_key)
        os.environ["ANTHROPIC_API_KEY"] = claude_key
    if openai_key:
        set_key(str(ENV_FILE), "OPENAI_API_KEY", openai_key)
        os.environ["OPENAI_API_KEY"] = openai_key
    if gmaps_key:
        set_key(str(ENV_FILE), "GOOGLE_MAPS_API_KEY", gmaps_key)
        os.environ["GOOGLE_MAPS_API_KEY"] = gmaps_key
    if serp_key:
        set_key(str(ENV_FILE), "SERP_API_KEY", serp_key)
        os.environ["SERP_API_KEY"] = serp_key
    st.success("✅ API keys saved to .env file")

st.markdown("---")

# ── Database Info ──
st.subheader("🗄️ Database")
from modules.database import DB_PATH, engine
from modules.crm import get_dashboard_stats
stats = get_dashboard_stats()

col_a, col_b, col_c = st.columns(3)
col_a.metric("Total Companies", stats["total"])
col_b.metric("Hot Leads", stats["hot"])
col_c.metric("Database Path", DB_PATH)

if st.button("🗑️ Clear All Data", type="secondary"):
    confirm = st.checkbox("I confirm I want to delete all leads data")
    if confirm:
        from modules.database import Base
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        st.success("Database cleared")

st.markdown("---")

# ── About ──
st.subheader("ℹ️ About")
st.markdown("""
**TechWokx Lead Intelligence Engine v2**

Built by: George Jabley | TechWokx IT Solutions

| Module | Status |
|---|---|
| Company Research | ✅ Active |
| DNS & Email Audit | ✅ Active |
| Website & SSL Audit | ✅ Active |
| AI Analysis (Claude) | ✅ Active with API key |
| AI Analysis (OpenAI) | ✅ Active with API key |
| PDF Proposal Generator | ✅ Active |
| CRM Pipeline | ✅ Active |
| Bulk Research | 🔜 Coming soon |

**hello@techwokx.online | techwokx.online**
""")

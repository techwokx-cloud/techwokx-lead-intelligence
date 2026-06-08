# NEW (safe)
try:
    from modules.theme import THEME_CSS
    st.markdown(THEME_CSS, unsafe_allow_html=True)
except Exception:
    # Fallback - no theme styling
    pass
import os
from pathlib import Path
from dotenv import set_key
from modules.database import DB_PATH, engine
from modules.crm import get_dashboard_stats

ENV_FILE = Path(".env")

st.markdown("# ⚙️ Settings")
st.caption("Configure API keys and application preferences.")
st.markdown("---")

def key_status(env_var):
    v = os.getenv(env_var,"")
    return f"✅ {v[:6]}...{v[-4:]}" if v and len(v)>10 else "❌ Not set"

# ── API Keys ──
st.markdown("### 🔑 API Keys")
with st.form("keys"):
    c1,c2 = st.columns(2)
    with c1:
        st.caption(f"Claude (Anthropic): {key_status('ANTHROPIC_API_KEY')}")
        ck = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        st.caption(f"OpenAI: {key_status('OPENAI_API_KEY')}")
        ok = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    with c2:
        st.caption(f"Google Maps: {key_status('GOOGLE_MAPS_API_KEY')}")
        gk = st.text_input("Google Maps API Key", type="password", placeholder="AIza...")
        st.caption(f"SerpAPI: {key_status('SERP_API_KEY')}")
        sk = st.text_input("SerpAPI Key", type="password", placeholder="...")
    save = st.form_submit_button("💾 Save Keys", type="primary", use_container_width=True)

if save:
    if not ENV_FILE.exists(): ENV_FILE.write_text("")
    for key,val in [("ANTHROPIC_API_KEY",ck),("OPENAI_API_KEY",ok),("GOOGLE_MAPS_API_KEY",gk),("SERP_API_KEY",sk)]:
        if val: set_key(str(ENV_FILE),key,val); os.environ[key]=val
    st.success("✅ Keys saved")

st.markdown("---")
st.markdown("### 🗄️ Database")
stats = get_dashboard_stats()
m1,m2,m3,m4 = st.columns(4)
m1.metric("Total Leads", stats["total"])
m2.metric("Hot Leads",   stats["hot"])
m3.metric("Won Deals",   stats["won"])
m4.metric("DB Path",     DB_PATH)

if st.button("🗑️ Clear All Data", type="secondary"):
    confirm = st.checkbox("Confirm — this deletes all leads and cannot be undone")
    if confirm:
        from modules.database import Base
        Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
        st.success("Database cleared")

st.markdown("---")
st.markdown("### ℹ️ About")
st.markdown("""
| Module | Status |
|---|---|
| Company Research (DuckDuckGo + Crawler) | ✅ |
| DNS & Email Audit (MX/SPF/DKIM/DMARC/BIMI) | ✅ |
| Website & SSL Audit | ✅ |
| Technology Detector | ✅ |
| Lead Scoring (Rule-based) | ✅ |
| AI Analysis (Claude / OpenAI) | ✅ with key |
| Proposal Generator (Email/WhatsApp/PDF) | ✅ |
| CRM Pipeline (Kanban + Table) | ✅ |
| Bulk Research (CSV Upload) | 🔜 |
| Google Maps Integration | 🔜 |

**TechWokx IT Solutions** | hello@techwokx.online | techwokx.online
""")

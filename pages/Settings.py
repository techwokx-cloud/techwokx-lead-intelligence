# pages/Settings.py
import sys
import os

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Streamlit FIRST
import streamlit as st

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="Settings - Lead Intelligence",
    page_icon="⚙️",
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
try:
    from modules.database import get_session, CRMCompany, ResearchHistory
    import sqlite3
    import pandas as pd
    from datetime import datetime
    import json
    DB_AVAILABLE = True
except ImportError as e:
    DB_AVAILABLE = False
    st.error(f"⚠️ Database module not available: {e}")

st.markdown("# ⚙️ Settings")
st.caption("Configure API keys and system settings")
st.markdown("---")

# Initialize session state for API keys
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {
        'google_maps': os.getenv('GOOGLE_MAPS_API_KEY', ''),
        'serp_api': os.getenv('SERP_API_KEY', ''),
        'anthropic': os.getenv('ANTHROPIC_API_KEY', ''),
        'openai': os.getenv('OPENAI_API_KEY', ''),
        'resend': os.getenv('RESEND_API_KEY', ''),
    }

# Save function
def save_api_keys():
    """Save API keys to .env file"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    # Read existing .env content
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
    
    # Update with new values
    for key, value in st.session_state.api_keys.items():
        if value:
            env_vars[key.upper()] = value
    
    # Write back to .env
    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    # Reload environment
    load_dotenv(override=True)
    st.success("✅ API keys saved successfully!")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔑 API Keys", "📊 Database", "🔍 Research", "🎨 Display", "📋 About"])

# Tab 1: API Keys
with tab1:
    st.markdown("### API Configuration")
    st.caption("Configure your API keys for enhanced functionality")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌐 Google Maps API")
        google_maps_key = st.text_input(
            "Google Maps API Key",
            value=st.session_state.api_keys['google_maps'],
            type="password",
            placeholder="AIzaSy...",
            help="Used for address validation and geocoding"
        )
        st.session_state.api_keys['google_maps'] = google_maps_key
        
        if google_maps_key:
            st.caption("✅ Used for: Address validation, location data")
        
        st.markdown("---")
        
        st.markdown("#### 🔍 SERP API")
        serp_api_key = st.text_input(
            "SERP API Key",
            value=st.session_state.api_keys['serp_api'],
            type="password",
            placeholder="your_serp_api_key",
            help="Used for Google search results"
        )
        st.session_state.api_keys['serp_api'] = serp_api_key
        
        if serp_api_key:
            st.caption("✅ Used for: Search engine results, competitor analysis")
    
    with col2:
        st.markdown("#### 🧠 Anthropic API (Claude)")
        anthropic_key = st.text_input(
            "Anthropic API Key",
            value=st.session_state.api_keys['anthropic'],
            type="password",
            placeholder="sk-ant-...",
            help="Used for AI analysis and lead intelligence"
        )
        st.session_state.api_keys['anthropic'] = anthropic_key
        
        if anthropic_key:
            st.caption("✅ Used for: AI-powered insights, lead scoring")
        
        st.markdown("---")
        
        st.markdown("#### 🤖 OpenAI API (GPT)")
        openai_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.api_keys['openai'],
            type="password",
            placeholder="sk-...",
            help="Used for AI analysis and content generation"
        )
        st.session_state.api_keys['openai'] = openai_key
        
        if openai_key:
            st.caption("✅ Used for: AI analysis, proposal generation")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📧 Resend (Email)")
        resend_key = st.text_input(
            "Resend API Key",
            value=st.session_state.api_keys['resend'],
            type="password",
            placeholder="re_...",
            help="Used for sending follow-up emails"
        )
        st.session_state.api_keys['resend'] = resend_key
        
        if resend_key:
            st.caption("✅ Used for: Email automation, lead nurturing")
    
    with col2:
        st.markdown("#### 📅 Calendly")
        calendly_link = st.text_input(
            "Calendly Link",
            value=os.getenv('CALENDLY_LINK', ''),
            placeholder="https://calendly.com/your-link",
            help="Booking link for consultations"
        )
        if calendly_link:
            st.session_state.calendly_link = calendly_link
    
    with col3:
        st.markdown("#### 🌍 Default Country")
        default_country = st.selectbox(
            "Default Country for Research",
            ["Ghana", "Nigeria", "Kenya", "South Africa", "Egypt", "Other"]
        )
        st.session_state.default_country = default_country
    
    st.markdown("---")
    
    # Save button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Save All API Keys", type="primary", use_container_width=True):
            save_api_keys()
            
            # Update environment variables in memory
            if google_maps_key:
                os.environ['GOOGLE_MAPS_API_KEY'] = google_maps_key
            if serp_api_key:
                os.environ['SERP_API_KEY'] = serp_api_key
            if anthropic_key:
                os.environ['ANTHROPIC_API_KEY'] = anthropic_key
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key
            if resend_key:
                os.environ['RESEND_API_KEY'] = resend_key
            
            st.balloons()
    
    # API Status Summary
    st.markdown("---")
    st.markdown("### API Status Summary")
    
    status_cols = st.columns(4)
    apis = {
        "Google Maps": bool(st.session_state.api_keys['google_maps']),
        "SERP API": bool(st.session_state.api_keys['serp_api']),
        "Anthropic": bool(st.session_state.api_keys['anthropic']),
        "OpenAI": bool(st.session_state.api_keys['openai']),
        "Resend": bool(st.session_state.api_keys['resend'])
    }
    
    for i, (api_name, is_configured) in enumerate(apis.items()):
        with status_cols[i % 4]:
            if is_configured:
                st.success(f"✅ {api_name}")
            else:
                st.warning(f"⚠️ {api_name}")

# Tab 2: Database Settings
with tab2:
    st.markdown("### Database Management")
    
    db_path = "data/company_research.db"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Database Information")
        st.write(f"**Database Path:** `{db_path}`")
        
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / 1024
            st.write(f"**Database Size:** {db_size:.2f} KB")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM crm_companies")
                company_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM research_history")
                research_count = cursor.fetchone()[0]
                
                conn.close()
                
                st.write(f"**Companies:** {company_count}")
                st.write(f"**Research History:** {research_count}")
                
            except Exception as e:
                st.warning(f"Could not read database stats: {e}")
        else:
            st.warning("Database file not found")
    
    with col2:
        st.markdown("#### Database Actions")
        
        if st.button("💾 Backup Database", use_container_width=True):
            if os.path.exists(db_path):
                backup_path = f"data/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                import shutil
                shutil.copy2(db_path, backup_path)
                st.success(f"✅ Database backed up to: {backup_path}")
            else:
                st.warning("No database file to backup")
        
        if st.button("🔄 Vacuum Database", use_container_width=True):
            try:
                conn = sqlite3.connect(db_path)
                conn.execute("VACUUM")
                conn.close()
                st.success("Database optimized successfully!")
            except Exception as e:
                st.error(f"Optimization failed: {e}")

# Tab 3: Research Settings
with tab3:
    st.markdown("### Research Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### API Sources")
        use_google_maps = st.checkbox("Use Google Maps API", value=bool(st.session_state.api_keys['google_maps']))
        use_serp = st.checkbox("Use SERP API", value=bool(st.session_state.api_keys['serp_api']))
        use_ai_analysis = st.checkbox("Use AI Analysis", value=bool(st.session_state.api_keys['anthropic'] or st.session_state.api_keys['openai']))
        
        st.markdown("#### Timeout Settings")
        timeout = st.slider("Request Timeout (seconds)", 5, 30, 10)
    
    with col2:
        st.markdown("#### Crawler Settings")
        crawl_depth = st.slider("Website Crawl Depth", 1, 10, 3)
        max_pages = st.slider("Maximum Pages to Crawl", 1, 20, 5)
        
        st.markdown("#### AI Model Preference")
        ai_model = st.selectbox("Preferred AI Model", ["Anthropic Claude", "OpenAI GPT", "Both (fallback)"])
    
    if st.button("💾 Save Research Settings", type="primary", use_container_width=True):
        st.session_state.research_settings = {
            'timeout': timeout,
            'crawl_depth': crawl_depth,
            'max_pages': max_pages,
            'use_google_maps': use_google_maps,
            'use_serp': use_serp,
            'use_ai_analysis': use_ai_analysis,
            'ai_model': ai_model
        }
        st.success("Research settings saved!")

# Tab 4: Display Settings
with tab4:
    st.markdown("### Display Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Theme")
        theme = st.selectbox("Theme", ["Dark", "Light", "System"])
        
        st.markdown("#### Dashboard Defaults")
        default_view = st.selectbox("Default Dashboard View", ["Summary", "Detailed", "Compact"])
        items_per_page = st.selectbox("Items per page", [10, 25, 50, 100])
    
    with col2:
        st.markdown("#### Chart Settings")
        chart_theme = st.selectbox("Chart Theme", ["Streamlit", "Plotly"])
        show_animations = st.checkbox("Show animations", value=True)
        
        st.markdown("#### Notification Settings")
        email_notifications = st.checkbox("Email notifications", value=False)
    
    if st.button("🎨 Apply Display Settings", use_container_width=True):
        st.session_state.theme = theme
        st.success("Display settings applied!")
        st.rerun()

# Tab 5: About
with tab5:
    st.markdown("### About TechWokx Lead Intelligence")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Version:** 2.0.0
        
        **Features:**
        - 🔍 Company Research (Single & Bulk)
        - 📊 Lead Scoring & Intelligence
        - 👥 CRM Integration
        - 📄 Proposal Generator
        - 🌐 Website & SSL Audit
        - 📈 Analytics Dashboard
        - 📧 Email Automation (Resend)
        - 🧠 AI Analysis (Claude/GPT)
        
        **API Integrations:**
        - Google Maps API - Address validation
        - SERP API - Search results
        - Anthropic Claude - AI insights
        - OpenAI GPT - Content generation
        - Resend - Email delivery
        
        **Support:**
        - Email: hello@techwokx.online
        - WhatsApp: +233 555 087 407
        - Website: https://techwokx.online
        """)
    
    with col2:
        st.markdown("### System Info")
        
        import sys
        st.write(f"**Python:** {sys.version.split()[0]}")
        st.write(f"**Streamlit:** {st.__version__}")
        
        # API Status
        st.markdown("**API Status:**")
        apis_configured = sum(1 for v in st.session_state.api_keys.values() if v)
        st.write(f"✅ {apis_configured}/5 APIs configured")
        
        # Reset app button
        st.markdown("---")
        if st.button("🔄 Reset All Settings", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.success("All settings reset! Please restart the app.")
            st.rerun()

# Footer
st.markdown("---")
st.caption(f"Settings • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

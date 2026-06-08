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

# Import database modules with error handling
try:
    from modules.database import get_session, CRMCompany, ResearchHistory
    import sqlite3
    import pandas as pd
    from datetime import datetime
    DB_AVAILABLE = True
except ImportError as e:
    DB_AVAILABLE = False
    st.error(f"⚠️ Database module not available: {e}")

st.markdown("# ⚙️ Settings")
st.caption("Configure your lead intelligence platform")
st.markdown("---")

# Create tabs for different settings
tab1, tab2, tab3, tab4 = st.tabs(["📊 Database", "🔍 Research Settings", "🎨 Display", "📋 About"])

# Tab 1: Database Settings
with tab1:
    st.markdown("### Database Management")
    
    # Get database path
    db_path = "data/company_research.db"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Database Information")
        st.write(f"**Database Path:** `{db_path}`")
        
        # Check if database exists
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / 1024  # KB
            st.write(f"**Database Size:** {db_size:.2f} KB")
            
            # Get record counts
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Count records
                cursor.execute("SELECT COUNT(*) FROM crm_companies")
                company_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM research_history")
                research_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM crm_activities")
                activity_count = cursor.fetchone()[0]
                
                conn.close()
                
                st.write(f"**Companies:** {company_count}")
                st.write(f"**Research History:** {research_count}")
                st.write(f"**Activities:** {activity_count}")
                
            except Exception as e:
                st.warning(f"Could not read database stats: {e}")
        else:
            st.warning("Database file not found. It will be created when you research companies.")
    
    with col2:
        st.markdown("#### Database Actions")
        
        # Backup database
        if st.button("💾 Backup Database", use_container_width=True):
            if os.path.exists(db_path):
                backup_path = f"data/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                import shutil
                shutil.copy2(db_path, backup_path)
                st.success(f"✅ Database backed up to: {backup_path}")
            else:
                st.warning("No database file to backup")
        
        # Export database
        if st.button("📤 Export Database (CSV)", use_container_width=True):
            try:
                conn = sqlite3.connect(db_path)
                
                # Export companies
                companies_df = pd.read_sql_query("SELECT * FROM crm_companies", conn)
                companies_csv = companies_df.to_csv(index=False)
                
                # Export research history
                research_df = pd.read_sql_query("SELECT * FROM research_history", conn)
                research_csv = research_df.to_csv(index=False)
                
                conn.close()
                
                # Provide download buttons
                st.download_button(
                    "Download Companies CSV",
                    companies_csv,
                    "companies_export.csv",
                    "text/csv"
                )
                
                st.download_button(
                    "Download Research History CSV",
                    research_csv,
                    "research_history_export.csv",
                    "text/csv"
                )
                
            except Exception as e:
                st.error(f"Export failed: {e}")
        
        # Clear all data (with confirmation)
        st.markdown("#### Danger Zone")
        if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
            st.session_state.confirm_clear = True
        
        if st.session_state.get('confirm_clear'):
            st.warning("⚠️ This will delete ALL data! Are you sure?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Clear All Data", use_container_width=True):
                    try:
                        if os.path.exists(db_path):
                            os.remove(db_path)
                            st.success("Database cleared! Restart the app to recreate it.")
                        else:
                            st.info("No database to clear")
                        st.session_state.confirm_clear = False
                    except Exception as e:
                        st.error(f"Error clearing database: {e}")
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.confirm_clear = False
                    st.rerun()
    
    # Database optimization
    st.markdown("#### Database Optimization")
    if st.button("🔄 Vacuum Database (Optimize)", use_container_width=True):
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("VACUUM")
            conn.close()
            st.success("Database optimized successfully!")
        except Exception as e:
            st.error(f"Optimization failed: {e}")

# Tab 2: Research Settings
with tab2:
    st.markdown("### Research Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### API Settings")
        
        # DuckDuckGo API
        use_ddg = st.checkbox("Enable DuckDuckGo Search", value=True)
        st.caption("Uses DuckDuckGo API for company information")
        
        # Timeout settings
        timeout = st.slider("Request Timeout (seconds)", 5, 30, 10)
        st.session_state['research_timeout'] = timeout
        
    with col2:
        st.markdown("#### Crawler Settings")
        
        # Crawl depth
        crawl_depth = st.slider("Website Crawl Depth", 1, 10, 3)
        st.session_state['crawl_depth'] = crawl_depth
        
        # Max pages
        max_pages = st.slider("Maximum Pages to Crawl", 1, 20, 5)
        st.session_state['max_pages'] = max_pages
    
    st.markdown("#### Lead Scoring Weights")
    st.caption("Adjust how lead scores are calculated")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        website_weight = st.slider("Website Presence", 0, 30, 25)
    with col2:
        email_weight = st.slider("Email Contact", 0, 20, 15)
    with col3:
        phone_weight = st.slider("Phone Contact", 0, 20, 10)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dns_weight = st.slider("DNS/Email Security", 0, 30, 25)
    with col2:
        social_weight = st.slider("Social Presence", 0, 20, 15)
    with col3:
        address_weight = st.slider("Physical Address", 0, 20, 10)
    
    if st.button("💾 Save Research Settings", type="primary", use_container_width=True):
        # Save to session state
        st.session_state['weights'] = {
            'website': website_weight,
            'email': email_weight,
            'phone': phone_weight,
            'dns': dns_weight,
            'social': social_weight,
            'address': address_weight
        }
        st.success("✅ Settings saved successfully!")

# Tab 3: Display Settings
with tab3:
    st.markdown("### Display Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Theme Settings")
        
        # Theme selection
        theme = st.selectbox("Theme", ["Dark", "Light", "System Default"])
        
        # Color scheme
        primary_color = st.color_picker("Primary Color", "#fbbf24")
        
        st.markdown("#### Dashboard Settings")
        
        # Default view
        default_view = st.selectbox("Default Dashboard View", ["Summary", "Detailed", "Compact"])
        
        # Items per page
        items_per_page = st.selectbox("Items per page", [10, 25, 50, 100])
    
    with col2:
        st.markdown("#### Chart Settings")
        
        # Chart theme
        chart_theme = st.selectbox("Chart Theme", ["Streamlit", "Plotly", "Altair"])
        
        # Show animations
        show_animations = st.checkbox("Show animations", value=True)
        
        st.markdown("#### Notification Settings")
        
        # Email notifications
        email_notifications = st.checkbox("Email notifications", value=False)
        
        # Browser notifications
        browser_notifications = st.checkbox("Browser notifications", value=True)
    
    if st.button("🎨 Apply Display Settings", type="primary", use_container_width=True):
        st.session_state['theme'] = theme
        st.session_state['primary_color'] = primary_color
        st.success("Display settings applied! Refresh to see changes.")
        st.rerun()

# Tab 4: About
with tab4:
    st.markdown("### About TechWokx Lead Intelligence")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Version:** 1.0.0
        
        **Features:**
        - 🔍 Company Research (Single & Bulk)
        - 📊 Lead Scoring & Intelligence
        - 👥 CRM Integration
        - 📄 Proposal Generator
        - 🌐 Website & SSL Audit
        - 📈 Analytics Dashboard
        
        **Technologies Used:**
        - Streamlit for UI
        - SQLite for database
        - DuckDuckGo API for research
        - Custom DNS audit tools
        
        **Support:**
        - Email: support@techwokx.com
        - Website: https://techwokx.com
        """)
    
    with col2:
        st.markdown("### System Info")
        
        import sys
        st.write(f"**Python:** {sys.version.split()[0]}")
        st.write(f"**Streamlit:** {st.__version__}")
        
        # Check module availability
        modules_status = {
            "SQLite": "✅",
            "Pandas": "✅" if 'pd' in dir() else "❌",
            "Requests": "✅" if 'requests' in sys.modules else "❌",
        }
        
        st.markdown("**Modules:**")
        for module, status in modules_status.items():
            st.write(f"{status} {module}")
    
    # Reset app button
    st.markdown("---")
    st.markdown("### Reset Application")
    
    if st.button("🔄 Reset All Settings", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.success("All settings reset! Please restart the app.")
        st.rerun()
    
    st.caption("© 2024 TechWokx Technologies. All rights reserved.")

# Footer
st.markdown("---")
st.caption(f"Settings last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

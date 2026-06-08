import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(page_title="Page Name", page_icon="📄", layout="wide")

from dotenv import load_dotenv
load_dotenv()

try:
    from modules.theme import THEME_CSS
    st.markdown(THEME_CSS, unsafe_allow_html=True)
except:
    pass
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.crm import get_dashboard_stats, get_all_companies
from modules.database import get_session, Company
from sqlalchemy import desc

st.title("📊 Dashboard")

stats = get_dashboard_stats()

# ── KPI Row ──
c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    ("Total Leads", stats["total"], "🏢"),
    ("Hot Leads", stats["hot"], "🔴"),
    ("Warm Leads", stats["warm"], "🟠"),
    ("Proposals Sent", stats["proposals"], "📄"),
    ("Won", stats["won"], "✅"),
    ("Lost", stats["lost"], "❌"),
]
for col, (label, val, icon) in zip([c1,c2,c3,c4,c5,c6], kpis):
    with col:
        st.metric(f"{icon} {label}", val)

st.markdown("---")

# ── Charts ──
all_companies = get_all_companies()
if all_companies:
    df = pd.DataFrame([{
        "Company": c.company_name,
        "Lead Score": c.lead_score or 0,
        "Status": c.lead_status or "Cold",
        "Stage": c.crm_stage or "New",
        "DNS Score": c.dns_score or 0,
        "Created": c.created_at,
    } for c in all_companies])

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Lead Status Distribution")
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        color_map = {"Hot": "#f87171", "Warm": "#fb923c", "Cold": "#60a5fa"}
        fig = px.pie(status_counts, names="Status", values="Count",
                     color="Status", color_discrete_map=color_map, hole=0.4)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("CRM Pipeline")
        stage_counts = df["Stage"].value_counts().reset_index()
        stage_counts.columns = ["Stage", "Count"]
        fig2 = px.bar(stage_counts, x="Stage", y="Count", color_discrete_sequence=["#EA580C"])
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)

    # Top opportunities
    st.subheader("🔥 Top Opportunities")
    top = df.nlargest(10, "Lead Score")[["Company", "Lead Score", "Status", "Stage", "DNS Score"]]
    st.dataframe(top, use_container_width=True, hide_index=True)

    # Recent activity
    st.subheader("🕐 Recent Research")
    recent = [{"Company": c.company_name, "Stage": c.crm_stage, "Score": c.lead_score,
               "Added": c.created_at.strftime("%d %b %Y") if c.created_at else "—"}
              for c in stats["recent"]]
    if recent:
        st.dataframe(pd.DataFrame(recent), use_container_width=True, hide_index=True)
else:
    st.info("No leads yet. Go to **Company Research** to get started.")

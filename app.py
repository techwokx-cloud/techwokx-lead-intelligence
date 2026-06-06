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

# ── Sidebar ──
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚡ TechWokx LIE</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sidebar-section">Main</div>', unsafe_allow_html=True)
    st.page_link("app.py",                          label="🏠  Dashboard")
    st.markdown('<div class="sidebar-section">Research</div>', unsafe_allow_html=True)
    st.page_link("pages/Company_Research.py",       label="🔍  Company Search")
    st.page_link("pages/Bulk_Research.py",          label="📋  Bulk Research")
    st.markdown('<div class="sidebar-section">Audits</div>', unsafe_allow_html=True)
    st.page_link("pages/IT_Audit.py",               label="🛡️  DNS & Email Audit")
    st.page_link("pages/Website_Audit.py",          label="🌐  Website & SSL Audit")
    st.markdown('<div class="sidebar-section">Intelligence</div>', unsafe_allow_html=True)
    st.page_link("pages/Lead_Intelligence.py",      label="🧠  AI Analysis")
    st.markdown('<div class="sidebar-section">Sales</div>', unsafe_allow_html=True)
    st.page_link("pages/Proposal_Generator.py",     label="📄  Proposals")
    st.page_link("pages/CRM.py",                    label="👥  CRM Pipeline")
    st.markdown("---")
    st.page_link("pages/Settings.py",               label="⚙️  Settings")

from modules.crm import get_dashboard_stats, get_all_companies
from modules.database import get_session, Activity
from sqlalchemy import desc
import pandas as pd

stats = get_dashboard_stats()

st.markdown("# 🏠 Dashboard")
st.caption("TechWokx Lead Intelligence Engine — your outreach command centre")
st.markdown("---")

# ── KPIs ──
k1,k2,k3,k4,k5,k6 = st.columns(6)
kpis = [
    ("🏢","Total Leads",    stats["total"],    "All time"),
    ("🔴","Hot Leads",      stats["hot"],      "Score 90+"),
    ("🟠","Warm Leads",     stats["warm"],     "Score 70–89"),
    ("📄","Proposals",      stats["proposals"],"Sent"),
    ("✅","Won",            stats["won"],      "Closed deals"),
    ("❌","Lost",           stats["lost"],     "Closed lost"),
]
for col,(icon,label,val,sub) in zip([k1,k2,k3,k4,k5,k6],kpis):
    with col:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns([1.6, 1])

with left:
    st.markdown("### 📊 Lead Pipeline")
    from modules.crm import CRM_STAGES
    all_cos = get_all_companies()
    stage_map = {s: [c for c in all_cos if c.crm_stage == s] for s in CRM_STAGES[:5]}
    cols = st.columns(5)
    stage_colors = {"New":"#6366f1","Researching":"#3b82f6","Contacted":"#f59e0b","Proposal Sent":"#f97316","Follow-up":"#ea580c"}
    for col,(stage,cos) in zip(cols, stage_map.items()):
        with col:
            color = stage_colors.get(stage,"#475569")
            st.markdown(f"""<div class="kanban-col">
                <div class="kanban-header">
                    <span style="color:{color}">{stage}</span>
                    <span style="background:rgba(255,255,255,0.05);padding:1px 7px;border-radius:10px;font-size:0.7rem">{len(cos)}</span>
                </div>""", unsafe_allow_html=True)
            for c in cos[:3]:
                badge_cls = "badge-hot" if c.lead_status=="Hot" else "badge-warm" if c.lead_status=="Warm" else "badge-cold"
                st.markdown(f"""<div class="kanban-card">
                    <div class="kanban-card-name">{(c.company_name or "")[:20]}</div>
                    <div class="kanban-card-meta"><span class="badge {badge_cls}">{c.lead_status or "Cold"}</span> &nbsp; {int(c.lead_score or 0)}/100</div>
                </div>""", unsafe_allow_html=True)
            if len(cos) > 3:
                st.markdown(f'<div style="font-size:0.72rem;color:#334155;text-align:center;padding:0.3rem">+{len(cos)-3} more</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("### 🕐 Recent Activity")
    db = get_session()
    acts = db.query(Activity).order_by(desc(Activity.created_at)).limit(8).all()
    db.close()
    if acts:
        for a in acts:
            ts = a.created_at.strftime("%d %b %H:%M") if a.created_at else ""
            st.markdown(f"""<div class="activity-item">
                <div class="activity-dot"></div>
                <div><div class="activity-text">{a.activity_type} — {(a.description or "")[:50]}</div>
                <div class="activity-time">{ts}</div></div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <div class="empty-state-title">No activity yet</div>
            <div class="empty-state-sub">Start by researching a company</div>
        </div>""", unsafe_allow_html=True)

# ── Top Opportunities ──
if all_cos:
    st.markdown("---")
    st.markdown("### 🔥 Top Opportunities")
    import pandas as pd
    rows = [{"Company":c.company_name,"Score":c.lead_score or 0,"Status":c.lead_status or "Cold",
             "Stage":c.crm_stage or "New","Email Provider":c.email_provider or "—","DNS":c.dns_score or 0} for c in sorted(all_cos,key=lambda x:-(x.lead_score or 0))[:8]]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

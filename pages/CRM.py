import streamlit as st
from dotenv import load_dotenv; load_dotenv()
st.set_page_config(page_title="CRM — TechWokx LIE", layout="wide")
from modules.theme import THEME_CSS; st.markdown(THEME_CSS, unsafe_allow_html=True)
import pandas as pd
from modules.crm import get_all_companies, get_company, update_stage, log_activity, CRM_STAGES
from modules.database import get_session, Company, Activity, Contact
from datetime import datetime, date
from sqlalchemy import desc

st.markdown("# 👥 CRM Pipeline")
st.caption("Manage your leads from first contact to closed deal.")
st.markdown("---")

# Filters
f1,f2,f3,f4 = st.columns([2,1,1,1])
with f1: search = st.text_input("", placeholder="🔍 Search company...", label_visibility="collapsed")
with f2: f_stage = st.selectbox("Stage", ["All"]+CRM_STAGES, label_visibility="collapsed")
with f3: f_status = st.selectbox("Status", ["All","Hot","Warm","Cold"], label_visibility="collapsed")
with f4: view = st.radio("", ["Cards","Table"], horizontal=True, label_visibility="collapsed")

companies = get_all_companies(stage=None if f_stage=="All" else f_stage, status=None if f_status=="All" else f_status)
if search: companies = [c for c in companies if search.lower() in (c.company_name or "").lower()]

st.markdown("---")

if view == "Cards":
    # Kanban with 5 stages
    kanban_stages = CRM_STAGES[:5]
    stage_colors = {"New":"#6366f1","Researching":"#3b82f6","Contacted":"#f59e0b","Proposal Sent":"#f97316","Follow-up":"#ea580c"}
    cols = st.columns(5)
    for col, stage in zip(cols, kanban_stages):
        stage_cos = [c for c in companies if c.crm_stage == stage]
        color = stage_colors.get(stage,"#475569")
        with col:
            st.markdown(f"""<div class="kanban-col">
                <div class="kanban-header">
                    <span style="color:{color};font-weight:700">{stage}</span>
                    <span style="background:rgba(255,255,255,0.06);padding:1px 8px;border-radius:10px">{len(stage_cos)}</span>
                </div>""", unsafe_allow_html=True)
            for c in stage_cos[:5]:
                badge_cls = "badge-hot" if c.lead_status=="Hot" else "badge-warm" if c.lead_status=="Warm" else "badge-cold"
                ssl_icon = "🔒" if c.ssl_valid else "🔓"
                st.markdown(f"""<div class="kanban-card">
                    <div class="kanban-card-name">{(c.company_name or "")[:22]}</div>
                    <div class="kanban-card-meta" style="margin-top:0.3rem">
                        <span class="badge {badge_cls}">{c.lead_status or "Cold"}</span>&nbsp;
                        <span style="color:#334155;font-size:0.7rem">{ssl_icon} {int(c.lead_score or 0)}/100</span>
                    </div>
                </div>""", unsafe_allow_html=True)
            if len(stage_cos) > 5:
                st.markdown(f'<div style="font-size:0.72rem;color:#334155;text-align:center;padding:0.4rem">+{len(stage_cos)-5} more</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # Won / Lost row
    st.markdown("<br>", unsafe_allow_html=True)
    wl1,wl2 = st.columns(2)
    for col,stage,color in [(wl1,"Won","#22c55e"),(wl2,"Lost","#ef4444")]:
        stage_cos = [c for c in get_all_companies(stage=stage)]
        with col:
            st.markdown(f"""<div class="kanban-col" style="border-color:rgba({('34,197,94' if stage=='Won' else '239,68,68')},0.2)">
                <div class="kanban-header"><span style="color:{color}">{stage}</span>
                <span style="background:rgba(255,255,255,0.06);padding:1px 8px;border-radius:10px">{len(stage_cos)}</span></div>""", unsafe_allow_html=True)
            for c in stage_cos[:3]:
                st.markdown(f'<div class="kanban-card"><div class="kanban-card-name">{(c.company_name or "")[:22]}</div></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

else:  # Table
    if companies:
        rows = [{"Company":c.company_name,"Status":f"{'🔴' if c.lead_status=='Hot' else '🟠' if c.lead_status=='Warm' else '🟢'} {c.lead_status or 'Cold'}","Score":int(c.lead_score or 0),"Stage":c.crm_stage or "New","Email":c.email or "—","Phone":c.phone or "—","DNS":int(c.dns_score or 0),"SSL":"✅" if c.ssl_valid else "❌","Website":"✅" if c.website_up else "❌","Added":c.created_at.strftime("%d %b %Y") if c.created_at else "—"} for c in companies]
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Export CSV", csv, file_name=f"leads_{datetime.now().strftime('%Y%m%d')}.csv")
    else:
        st.markdown('<div class="empty-state"><div class="empty-state-icon">👥</div><div class="empty-state-title">No leads yet</div><div class="empty-state-sub">Research companies to populate your pipeline</div></div>', unsafe_allow_html=True)

# ── Company Detail Panel ──
st.markdown("---")
st.markdown("### 📋 Company Detail")
if not companies:
    st.stop()

opts = {c.company_name: c.id for c in companies}
sel = st.selectbox("Select company", list(opts.keys()), label_visibility="collapsed")
selected = get_company(opts[sel])

if selected:
    d1,d2,d3 = st.columns([1.5,1,1])
    with d1:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        for l,v in [("Company",selected.company_name),("Website",selected.website or "—"),("Phone",selected.phone or "—"),("Email",selected.email or "—"),("Address",selected.address or "—"),("Provider",selected.email_provider or "—"),("Lead Score",f"{int(selected.lead_score or 0)}/100 ({selected.lead_status or 'Cold'})"),("DNS Score",f"{int(selected.dns_score or 0)}/100"),("SSL","✅ Valid" if selected.ssl_valid else "❌ Invalid"),("Website Up","✅ Yes" if selected.website_up else "❌ No")]:
            st.markdown(f'<div class="profile-row"><span class="profile-label">{l}</span><span class="profile-value">{v}</span></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with d2:
        st.markdown("**Update Stage**")
        new_stage = st.selectbox("", CRM_STAGES, index=CRM_STAGES.index(selected.crm_stage) if selected.crm_stage in CRM_STAGES else 0, label_visibility="collapsed")
        if st.button("✅ Update Stage", use_container_width=True):
            update_stage(selected.id, new_stage)
            log_activity(selected.id,"Stage Change",f"Moved to {new_stage}")
            st.success(f"Moved to {new_stage}"); st.rerun()
        st.markdown("**Add Note**")
        note = st.text_area("", placeholder="Type note...", height=100, label_visibility="collapsed")
        if st.button("💾 Save Note", use_container_width=True) and note:
            log_activity(selected.id,"Note",note); st.success("Saved")
    with d3:
        st.markdown("**Follow-up Date**")
        fu = st.date_input("", value=date.today(), label_visibility="collapsed")
        if st.button("📅 Set Follow-up", use_container_width=True):
            db = get_session()
            c2 = db.query(Company).filter(Company.id==selected.id).first()
            if c2: c2.follow_up_date = datetime.combine(fu,datetime.min.time()); db.commit()
            db.close(); st.success(f"Follow-up: {fu}")
        if selected.ai_summary:
            st.markdown("**AI Summary**")
            st.caption(selected.ai_summary[:200])

    # Activity log
    st.markdown("**Activity Log**")
    db = get_session()
    acts = db.query(Activity).filter(Activity.company_id==selected.id).order_by(desc(Activity.created_at)).limit(10).all()
    db.close()
    if acts:
        for a in acts:
            ts = a.created_at.strftime("%d %b %Y %H:%M") if a.created_at else "—"
            st.markdown(f'<div class="activity-item"><div class="activity-dot"></div><div><div class="activity-text"><strong>{a.activity_type}</strong> — {(a.description or "")[:60]}</div><div class="activity-time">{ts}</div></div></div>', unsafe_allow_html=True)
    else:
        st.caption("No activity yet")

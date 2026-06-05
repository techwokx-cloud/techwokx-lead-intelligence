import streamlit as st
import pandas as pd
from modules.crm import get_all_companies, get_company, update_stage, log_activity, CRM_STAGES
from modules.database import get_session, Company, Activity, Contact
from datetime import datetime, date
from sqlalchemy import desc

st.set_page_config(page_title="CRM — TechWokx LIE", layout="wide")
st.title("💼 CRM Pipeline")

# ── Filters ──
col1, col2, col3 = st.columns(3)
with col1:
    filter_stage = st.selectbox("Filter by Stage", ["All"] + CRM_STAGES)
with col2:
    filter_status = st.selectbox("Filter by Lead Status", ["All", "Hot", "Warm", "Cold"])
with col3:
    search_term = st.text_input("Search company", placeholder="Type to search...")

stage_arg = None if filter_stage == "All" else filter_stage
status_arg = None if filter_status == "All" else filter_status
companies = get_all_companies(stage=stage_arg, status=status_arg)

if search_term:
    companies = [c for c in companies if search_term.lower() in (c.company_name or "").lower()]

# ── Pipeline Board View ──
view_mode = st.radio("View", ["Table", "Kanban Board"], horizontal=True)

if view_mode == "Table":
    if companies:
        rows = []
        for c in companies:
            badge = "🔴" if c.lead_status == "Hot" else "🟠" if c.lead_status == "Warm" else "🟢"
            rows.append({
                "Company": c.company_name,
                "Status": f"{badge} {c.lead_status or 'Cold'}",
                "Score": c.lead_score or 0,
                "Stage": c.crm_stage or "New",
                "Email": c.email or "—",
                "Phone": c.phone or "—",
                "DNS Score": c.dns_score or 0,
                "SSL": "✅" if c.ssl_valid else "❌",
                "Website": "✅" if c.website_up else "❌",
                "Added": c.created_at.strftime("%d %b %Y") if c.created_at else "—",
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Export
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Export CSV", csv, file_name=f"techwokx_leads_{datetime.now().strftime('%Y%m%d')}.csv")
    else:
        st.info("No leads found. Run Company Research to populate the CRM.")

else:  # Kanban
    cols = st.columns(len(CRM_STAGES))
    stage_groups = {s: [c for c in companies if c.crm_stage == s] for s in CRM_STAGES}

    for col, stage in zip(cols, CRM_STAGES):
        with col:
            count = len(stage_groups[stage])
            st.markdown(f"**{stage}** `{count}`")
            st.markdown("---")
            for c in stage_groups[stage]:
                badge = "🔴" if c.lead_status == "Hot" else "🟠" if c.lead_status == "Warm" else "🟢"
                with st.container(border=True):
                    st.caption(f"{badge} Score: {c.lead_score or 0}")
                    st.write(c.company_name[:25])
                    if c.phone:
                        st.caption(f"📞 {c.phone}")

st.markdown("---")

# ── Company Detail ──
st.subheader("📋 Company Details & Actions")
if companies:
    selected_name = st.selectbox("Select Company", [c.company_name for c in companies])
    selected = next((c for c in companies if c.company_name == selected_name), None)
    if selected:
        left, right = st.columns([1, 1])
        with left:
            st.markdown(f"**Company:** {selected.company_name}")
            st.markdown(f"**Website:** {selected.website or '—'}")
            st.markdown(f"**Phone:** {selected.phone or '—'}")
            st.markdown(f"**Email:** {selected.email or '—'}")
            st.markdown(f"**Address:** {selected.address or '—'}")
            st.markdown(f"**Lead Score:** {selected.lead_score or 0}/100 ({selected.lead_status or 'Cold'})")
            st.markdown(f"**DNS Score:** {selected.dns_score or 0}/100")
            if selected.ai_summary:
                with st.expander("AI Summary"):
                    st.write(selected.ai_summary)

        with right:
            new_stage = st.selectbox("Update Stage", CRM_STAGES, index=CRM_STAGES.index(selected.crm_stage) if selected.crm_stage in CRM_STAGES else 0)
            if st.button("Update Stage", use_container_width=True):
                update_stage(selected.id, new_stage)
                log_activity(selected.id, "Stage Change", f"Stage changed to {new_stage}")
                st.success(f"Stage updated to {new_stage}")
                st.rerun()

            note = st.text_area("Add Note")
            if st.button("Save Note", use_container_width=True) and note:
                log_activity(selected.id, "Note", note)
                st.success("Note saved")

            follow_up = st.date_input("Set Follow-up Date", value=date.today())
            if st.button("Save Follow-up Date", use_container_width=True):
                db = get_session()
                c = db.query(Company).filter(Company.id == selected.id).first()
                if c:
                    c.follow_up_date = datetime.combine(follow_up, datetime.min.time())
                    db.commit()
                db.close()
                st.success(f"Follow-up set for {follow_up}")

        # Activity log
        st.subheader("📝 Activity Log")
        db = get_session()
        activities = db.query(Activity).filter(Activity.company_id == selected.id).order_by(desc(Activity.created_at)).limit(20).all()
        db.close()
        if activities:
            for act in activities:
                st.markdown(f"**{act.activity_type}** — {act.created_at.strftime('%d %b %Y %H:%M') if act.created_at else '—'}")
                st.caption(act.description)
                st.markdown("---")
        else:
            st.caption("No activity yet")

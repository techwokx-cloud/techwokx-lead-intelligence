import streamlit as st
from dotenv import load_dotenv; load_dotenv()
st.set_page_config(page_title="Bulk Research — TechWokx LIE", layout="wide")
from modules.theme import THEME_CSS; st.markdown(THEME_CSS, unsafe_allow_html=True)
from modules.company_research import research_company
from modules.lead_scoring import score_from_research
from modules.crm import save_research_to_crm
import pandas as pd, time

st.markdown("# 📋 Bulk Research")
st.caption("Upload a CSV of company names and research them all automatically.")
st.markdown("---")

st.markdown("""**Expected CSV format:**
```
company_name,website
Nyaho Medical Centre,nyahoclinic.com
Sealand Shipping,sealandltd.com
```
""")
uploaded = st.file_uploader("Upload CSV", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
    st.dataframe(df.head(5), use_container_width=True)
    st.caption(f"**{len(df)} companies** ready to research")
    if st.button("🚀 Start Bulk Research", type="primary"):
        results = []
        prog = st.progress(0)
        status = st.empty()
        for i, row in df.iterrows():
            name = str(row.get("company_name","")).strip()
            site = str(row.get("website","")).strip()
            if not name: continue
            status.info(f"Researching {i+1}/{len(df)}: **{name}**")
            try:
                r = research_company(company_name=name, website=site if site and site!="nan" else "")
                l = score_from_research(r)
                save_research_to_crm(r, r.dns_result, r.website_result, l)
                results.append({"Company":r.company_name,"Score":l.total,"Status":l.status,"Email":r.email or "—","Website":r.website or "—"})
            except Exception as e:
                results.append({"Company":name,"Score":0,"Status":"Error","Email":"—","Website":str(e)[:40]})
            prog.progress((i+1)/len(df))
            time.sleep(0.5)
        status.success(f"✅ Completed {len(results)} companies")
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
        csv_out = pd.DataFrame(results).to_csv(index=False)
        st.download_button("⬇️ Download Results", csv_out, file_name="bulk_results.csv")
else:
    st.markdown("""<div class="empty-state" style="margin-top:3rem"><div class="empty-state-icon">📋</div>
        <div class="empty-state-title">Upload a CSV to begin bulk research</div>
        <div class="empty-state-sub">Maximum recommended: 50 companies per batch</div>
    </div>""", unsafe_allow_html=True)

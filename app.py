
**Required field:** name
**Optional fields:** website, email, phone, address, lead_score
""")

st.markdown("---")

# File upload
uploaded_file = st.file_uploader("Choose file", type=['csv', 'json', 'txt'])

if uploaded_file is not None:
file_type = uploaded_file.name.split('.')[-1].lower()

if file_type == 'csv':
    success, message = import_leads_from_csv(uploaded_file)
elif file_type == 'json':
    success, message = import_leads_from_json(uploaded_file)
elif file_type == 'txt':
    success, message = import_leads_from_text(uploaded_file)
else:
    success, message = False, "Unsupported file type"

if success:
    st.success(message)
    st.rerun()
else:
    st.error(f"Import failed: {message}")

st.markdown("---")
st.markdown("### Manual Lead Entry")

with st.form("manual_lead_form"):
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Company Name*", placeholder="Required")
    website = st.text_input("Website", placeholder="https://example.com")
    email = st.text_input("Email", placeholder="info@example.com")
with col2:
    phone = st.text_input("Phone", placeholder="+233 XX XXX XXXX")
    address = st.text_input("Address", placeholder="City, Country")
    lead_score = st.slider("Lead Score", 0, 100, 50)

if st.form_submit_button("Add Lead Manually", type="primary"):
    if name:
        lead_data = {
            "name": name,
            "website": website,
            "email": email,
            "phone": phone,
            "address": address,
            "lead_score": lead_score,
            "source": "Manual Entry"
        }
        add_lead(lead_data)
        st.rerun()
    else:
        st.error("Company name is required")

# ============ EXPORT LEADS PAGE ============
elif st.session_state.page == 'export_leads':
st.markdown('<div class="section-header">Export Leads</div>', unsafe_allow_html=True)
st.caption("Export your leads to CSV or JSON format")
st.markdown("---")

if st.session_state.leads:
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Export to CSV")
    csv_data = export_leads_to_csv()
    if csv_data:
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

with col2:
    st.markdown("### Export to JSON")
    json_data = export_leads_to_json()
    if json_data:
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

st.markdown("---")
st.markdown(f"**Total Leads:** {len(st.session_state.leads)}")

with st.expander("Preview Export Data"):
    preview_df = pd.DataFrame(st.session_state.leads)
    st.dataframe(preview_df)
else:
st.info("No leads to export. Research or import leads first.")

# ============ COMPANY RESEARCH PAGE ============
elif st.session_state.page == 'company_research':
st.markdown('<div class="section-header">Deep Company Research</div>', unsafe_allow_html=True)
st.caption("Powered by Google Search - Finds real company data with website crawling")
st.markdown("---")

api_keys = get_api_keys()

if not api_keys["serp_api"]:
st.warning("SERP API key missing. Add to .streamlit/secrets.toml")
st.info("Get your key from https://serpapi.com/")

company_name = st.text_input("Company Name", placeholder="e.g. Prime Meridian Docks, MTN Ghana")

if st.button("Deep Research", type="primary"):
if company_name:
    with st.spinner(f"Researching {company_name}..."):
        result = deep_research_company(
            company_name, 
            serp_api_key=api_keys["serp_api"],
            openai_api_key=api_keys["openai"]
        )
        
        st.session_state.last_research = result
        
        # Company Information
        st.markdown(f"""
        <div class="data-card">
            <h4>Company Information</h4>
            <p><strong>Name:</strong> {result['name']}</p>
            <p><strong>Website:</strong> {result['website'] or 'Not found'}</p>
            <p><strong>Address:</strong> {result['address'] or 'Not found'}</p>
            <p><strong>Phone:</strong> {result['phone'] or 'Not found'}</p>
            <p><strong>Email:</strong> {result['email'] or 'Not found'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Deep crawl button
        if result['website'] and not result['email']:
            if st.button("Deep Crawl Website for Email"):
                with st.spinner(f"Deep crawling {result['website']}..."):
                    email_data = crawl_website_for_emails(result['website'])
                    if email_data and email_data.get('primary_email'):
                        result['email'] = email_data['primary_email']
                        st.success(f"Found email: {result['email']}")
                        st.rerun()
                    else:
                        st.warning("No email found after deep crawl")
        
        # Contacts Found
        if result['contacts']:
            st.markdown("### Contacts Found")
            for contact in result['contacts']:
                st.markdown(f"""
                <div class="data-card">
                    <strong>{contact.get('name', 'Name found')}</strong><br>
                    Title: {contact.get('title', 'Staff')}<br>
                    Source: {contact.get('source', 'Website')}
                </div>
                """, unsafe_allow_html=True)
        
        # LinkedIn Search
        st.markdown(f"""
        <div class="data-card">
            <h4>LinkedIn Search</h4>
            <a href="{result['linkedin_search_url']}" target="_blank">Search LinkedIn for {result['name']} -></a>
        </div>
        """, unsafe_allow_html=True)
        
        # Description
        if result['description']:
            st.markdown(f"""
            <div class="data-card">
                <h4>Business Description</h4>
                <p>{result['description'][:500]}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Website Status
        if result['website_status']:
            status_icon = "Yes" if result['website_status'].get('reachable') else "No"
            status_text = "Online" if result['website_status'].get('reachable') else "Down"
            response_time = result['website_status'].get('response_time')
            response_display = f"{response_time:.0f}ms" if response_time and isinstance(response_time, (int, float)) else "N/A"
            
            st.markdown(f"""
            <div class="data-card">
                <h4>Website Status</h4>
                <p><strong>Status:</strong> {status_icon} {status_text}</p>
                <p><strong>Response Time:</strong> {response_display}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Lead Score
        score_color = "#22c55e" if result['lead_score'] >= 70 else "#f97316" if result['lead_score'] >= 50 else "#ef4444"
        st.markdown(f"""
        <div class="data-card" style="text-align: center;">
            <h4>Lead Score</h4>
            <p style="font-size: 3rem; font-weight: 700; color: {score_color};">{result['lead_score']}/100</p>
            <p><strong>Data Sources:</strong> {', '.join(result['sources']) if result['sources'] else 'None'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Recommendations
        st.markdown(f"""
        <div class="data-card">
            <h4>Recommendations</h4>
            <ul>
                {''.join([f'<li>{rec}</li>' for rec in result['recommendations']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add to CRM", use_container_width=True, type="primary"):
                add_lead(result)
                st.rerun()
        
        with col2:
            if result.get('email'):
                if st.button("Send Email", use_container_width=True):
                    st.session_state.proposal_lead = result
                    st.session_state.page = 'send_email'
                    st.rerun()
else:
    st.warning("Please enter a company name")

# ============ LEAD CRM PAGE ============
elif st.session_state.page == 'crm':
st.markdown('<div class="section-header">Lead CRM</div>', unsafe_allow_html=True)
st.caption("All researched leads - " + str(len(st.session_state.leads)) + " total")
st.markdown("---")

if st.session_state.leads:
search = st.text_input("Search Leads", placeholder="Search by name, email, or website")

filtered_leads = st.session_state.leads
if search:
    filtered_leads = [
        l for l in filtered_leads 
        if search.lower() in l.get('name', '').lower() 
        or search.lower() in l.get('email', '').lower()
        or search.lower() in l.get('website', '').lower()
    ]

st.caption(f"Showing {len(filtered_leads)} of {len(st.session_state.leads)} leads")

for lead in filtered_leads:
    with st.expander(f"{lead['name']} - Score: {lead['lead_score']}/100 - {lead['status']}"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Website:** {lead.get('website', 'N/A')}")
            st.write(f"**Email:** {lead.get('email', 'N/A')}")
            st.write(f"**Phone:** {lead.get('phone', 'N/A')}")
        with col2:
            st.write(f"**Address:** {lead.get('address', 'N/A')}")
            st.write(f"**Source:** {lead.get('source', 'Unknown')}")
            st.write(f"**Added:** {lead['created_at'][:10]}")
        
        if lead.get('contacts'):
            st.write("**Contacts Found:**")
            for contact in lead['contacts']:
                st.write(f"- {contact.get('name', 'Name')} ({contact.get('title', 'Staff')})")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if lead.get('email'):
                if st.button(f"Send Email", key=f"email_{lead['id']}"):
                    st.session_state.proposal_lead = lead
                    st.session_state.page = 'send_email'
                    st.rerun()
        with col2:
            if st.button(f"Copy Name", key=f"copy_{lead['id']}"):
                st.write(f"Copied: {lead['name']}")
        with col3:
            if st.button(f"Delete", key=f"delete_{lead['id']}"):
                st.session_state.leads = [l for l in st.session_state.leads if l['id'] != lead['id']]
                save_leads()
                st.success(f"Deleted {lead['name']}")
                st.rerun()
else:
st.info("No leads yet. Use Company Research or Import Leads to add leads.")

col1, col2 = st.columns(2)
with col1:
    if st.button("Research Company", use_container_width=True):
        st.session_state.page = 'company_research'
        st.rerun()
with col2:
    if st.button("Import Leads", use_container_width=True):
        st.session_state.page = 'import_leads'
        st.rerun()

# ============ SEND EMAIL PAGE ============
elif st.session_state.page == 'send_email':
st.markdown('<div class="section-header">Send Email</div>', unsafe_allow_html=True)
st.markdown("---")

leads = st.session_state.leads
if leads:
lead_options = {f"{l['name']} (Score: {l['lead_score']}/100)": l for l in leads}

if st.session_state.get('proposal_lead'):
    default_lead = f"{st.session_state.proposal_lead['name']} (Score: {st.session_state.proposal_lead['lead_score']}/100)"
else:
    default_lead = list(lead_options.keys())[0] if lead_options else None

selected = st.selectbox("Select Lead", list(lead_options.keys()), index=0 if default_lead else None)
lead = lead_options[selected]

recipient_email = lead.get('email', '')
to_email = st.text_input("To Email", value=recipient_email)

if to_email:
    st.markdown("### Email Preview")
    contact_person = lead.get('contacts', [{}])[0] if lead.get('contacts') else None
    email_body = generate_proposal_email(lead, contact_person)
    st.markdown(email_body, unsafe_allow_html=True)
    
    if st.button("Send Email", type="primary"):
        subject = f"IT Assessment for {lead['name']} - Score: {lead['lead_score']}/100"
        success, msg = send_email(to_email, subject, email_body)
        if success:
            update_lead_email_status(lead['id'], "sent")
            st.session_state.email_log.append({
                "to": to_email,
                "company": lead['name'],
                "date": datetime.now().isoformat(),
                "status": "Sent"
            })
            save_email_log()
            st.success(f"Email sent to {to_email}!")
        else:
            st.error(f"Failed: {msg}")
else:
    st.warning("No email address for this lead. Add email or use LinkedIn search to find contacts.")
else:
st.info("No leads in CRM. Research or import leads first.")

# ============ EMAIL LOG PAGE ============
elif st.session_state.page == 'email_log':
st.markdown('<div class="section-header">Email Log</div>', unsafe_allow_html=True)
st.markdown("---")

if st.session_state.email_log:
for log in reversed(st.session_state.email_log):
    st.markdown(f"""
    <div class="data-card">
        <strong>To:</strong> {log['to']}<br>
        <strong>Company:</strong> {log['company']}<br>
        <strong>Status:</strong> {log['status']}<br>
        <strong>Date:</strong> {log['date'][:19]}
    </div>
    """, unsafe_allow_html=True)
else:
st.info("No emails sent yet")

# ============ FOLLOW-UPS PAGE ============
elif st.session_state.page == 'followups':
st.markdown('<div class="section-header">Follow-up Management</div>', unsafe_allow_html=True)
st.markdown("---")

needs_followup = get_leads_needing_followup()

if needs_followup:
st.warning(f"{len(needs_followup)} leads need follow-up")
for lead in needs_followup:
    with st.expander(f"{lead['name']} - Email sent on {lead.get('email_sent_date', '')[:10]}"):
        st.write(f"**Email:** {lead.get('email', 'N/A')}")
        st.write(f"**Phone:** {lead.get('phone', 'N/A')}")
        if st.button(f"Send Follow-up", key=f"followup_{lead['id']}"):
            st.session_state.proposal_lead = lead
            st.session_state.page = 'send_email'
            st.rerun()
else:
st.success("No leads need follow-up at this time")

# ============ SETTINGS PAGE ============
elif st.session_state.page == 'settings':
st.markdown('<div class="section-header">Settings</div>', unsafe_allow_html=True)
st.markdown("---")

st.markdown("### API Configuration")
st.code("""
# .streamlit/secrets.toml
SERP_API_KEY = "your_serp_api_key"
OPENAI_API_KEY = "your_openai_api_key"
""")

st.markdown("### Data Management")
col1, col2 = st.columns(2)
with col1:
if st.button("Clear All Leads", type="secondary"):
    st.session_state.leads = []
    save_leads()
    st.success("All leads cleared!")
    st.rerun()
with col2:
if st.button("Backup Leads"):
    if st.session_state.leads:
        backup_data = json.dumps(st.session_state.leads, default=str, indent=2)
        st.download_button("Download Backup", backup_data, f"leads_backup_{datetime.now().strftime('%Y%m%d')}.json", "application/json")
    else:
        st.warning("No leads to backup")

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("2024 TechWokx Enterprise Suite | Email: hello@techwokx.online")

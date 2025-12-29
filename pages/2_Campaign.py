import streamlit as st
from src.ui_styles import apply_ios_style
import pandas as pd
from src.database import Lead, LeadStatus, get_session
from src.scheduler import run_scheduler
from src.agent import generate_personalized_email, get_email_body
from src.mailer import send_outreach_email

st.set_page_config(page_title="Campaign Management", page_icon="🎯", layout="wide")
apply_ios_style()

st.title("🎯 Campaign Management")

# Initialize session state for email previews
if 'email_previews' not in st.session_state:
    st.session_state.email_previews = {}

session = get_session()
leads = session.query(Lead).all()

if leads:
    df = pd.DataFrame([{
        "ID": l.id,
        "Clinic": l.clinic_name,
        "Website": l.website,
        "Email": l.email,
        "Status": l.status,
        "Followups": l.follow_up_count,
        "Last Contacted": l.last_contacted
    } for l in leads])
    
    st.subheader("Manage Leads")
    
    # Filters
    status_filter = st.multiselect("Filter by Status", options=[status.value for status in LeadStatus], default=[])
    if status_filter:
        filtered_df = df[df['Status'].isin(status_filter)]
    else:
        filtered_df = df
        
    st.dataframe(filtered_df, use_container_width=True)
    
    # Create tabs for Individual and Bulk modes
    tab1, tab2, tab3 = st.tabs(["📧 Individual Emails", "📨 Bulk Send", "🔄 Follow-ups"])
    
    # ========== TAB 1: INDIVIDUAL EMAIL PREVIEW & SEND ==========
    with tab1:
        st.subheader("Preview & Send Individual Emails")
        st.write("Generate personalized emails for each lead, review and edit before sending.")
        
        # Get enriched leads
        enriched_leads = [l for l in leads if l.status == LeadStatus.ENRICHED.value]
        
        if enriched_leads:
            for lead in enriched_leads:
                with st.expander(f"📋 {lead.clinic_name} - {lead.email}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Website:** {lead.website}")
                        st.write(f"**Contact:** {lead.name if lead.name else 'N/A'}")
                    
                    with col2:
                        # Preview Email Button
                        if st.button(f"🔍 Preview Email", key=f"preview_{lead.id}"):
                            with st.spinner("Generating personalized email..."):
                                opening = generate_personalized_email(lead.name, lead.clinic_name)
                                subject = f"Question for {lead.clinic_name}"
                                body = get_email_body(lead, opening)
                                
                                # Store in session state
                                st.session_state.email_previews[lead.id] = {
                                    'subject': subject,
                                    'body': body
                                }
                                st.rerun()
                    
                    # Show email preview if generated
                    if lead.id in st.session_state.email_previews:
                        st.divider()
                        st.write("**✉️ Email Preview**")
                        
                        # Editable subject
                        subject = st.text_input(
                            "Subject Line:",
                            value=st.session_state.email_previews[lead.id]['subject'],
                            key=f"subject_{lead.id}"
                        )
                        
                        # Editable body
                        body = st.text_area(
                            "Email Body:",
                            value=st.session_state.email_previews[lead.id]['body'],
                            height=200,
                            key=f"body_{lead.id}"
                        )
                        
                        # Update session state with edits
                        st.session_state.email_previews[lead.id]['subject'] = subject
                        st.session_state.email_previews[lead.id]['body'] = body
                        
                        # Send button
                        col_send1, col_send2 = st.columns([1, 3])
                        with col_send1:
                            if st.button(f"📤 Send Email", key=f"send_{lead.id}", type="primary"):
                                with st.spinner(f"Sending email to {lead.clinic_name}..."):
                                    success = send_outreach_email(lead.id, subject, body)
                                    if success:
                                        st.success(f"✅ Email sent successfully to {lead.email}!")
                                        # Clear preview from session state
                                        del st.session_state.email_previews[lead.id]
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Failed to send email to {lead.email}")
                        
                        with col_send2:
                            if st.button(f"🗑️ Discard", key=f"discard_{lead.id}"):
                                del st.session_state.email_previews[lead.id]
                                st.rerun()
        else:
            st.info("No ENRICHED leads available. All leads have been contacted or are in other stages.")
    
    # ========== TAB 2: BULK SEND ==========
    with tab2:
        st.subheader("Bulk Email Campaign")
        st.write("Generate and send emails to all enriched leads at once.")
        
        enriched_leads = [l for l in leads if l.status == LeadStatus.ENRICHED.value]
        
        if enriched_leads:
            st.write(f"**{len(enriched_leads)} leads** ready for outreach")
            
            # Preview all emails button
            if st.button("🔍 Preview All Emails", key="preview_all"):
                with st.spinner("Generating personalized emails for all leads..."):
                    bulk_previews = {}
                    for lead in enriched_leads:
                        opening = generate_personalized_email(lead.name, lead.clinic_name)
                        subject = f"Question for {lead.clinic_name}"
                        body = get_email_body(lead, opening)
                        bulk_previews[lead.id] = {
                            'subject': subject,
                            'body': body,
                            'lead': lead
                        }
                    st.session_state.bulk_previews = bulk_previews
                    st.rerun()
            
            # Show bulk previews if generated
            if 'bulk_previews' in st.session_state and st.session_state.bulk_previews:
                st.divider()
                st.write("**📧 Email Previews**")
                
                # Checkboxes to select/deselect leads
                selected_leads = []
                for lead_id, preview_data in st.session_state.bulk_previews.items():
                    lead = preview_data['lead']
                    include = st.checkbox(
                        f"✅ {lead.clinic_name} ({lead.email})",
                        value=True,
                        key=f"bulk_select_{lead_id}"
                    )
                    
                    if include:
                        selected_leads.append(lead_id)
                        with st.expander(f"Preview: {lead.clinic_name}"):
                            st.write(f"**Subject:** {preview_data['subject']}")
                            st.write(f"**Body:**")
                            st.text(preview_data['body'])
                
                st.divider()
                st.write(f"**{len(selected_leads)} of {len(st.session_state.bulk_previews)} emails** will be sent")
                
                col_bulk1, col_bulk2 = st.columns([1, 3])
                with col_bulk1:
                    if st.button("📤 Confirm & Send All", type="primary", key="send_all"):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        sent_count = 0
                        failed_count = 0
                        
                        for idx, lead_id in enumerate(selected_leads):
                            preview_data = st.session_state.bulk_previews[lead_id]
                            lead = preview_data['lead']
                            
                            status_text.text(f"Sending to {lead.clinic_name}...")
                            success = send_outreach_email(
                                lead_id,
                                preview_data['subject'],
                                preview_data['body']
                            )
                            
                            if success:
                                sent_count += 1
                            else:
                                failed_count += 1
                            
                            progress_bar.progress((idx + 1) / len(selected_leads))
                        
                        status_text.empty()
                        progress_bar.empty()
                        
                        st.success(f"✅ Bulk send complete! Sent: {sent_count}, Failed: {failed_count}")
                        
                        # Clear bulk previews
                        del st.session_state.bulk_previews
                        st.rerun()
                
                with col_bulk2:
                    if st.button("🗑️ Discard All", key="discard_all"):
                        del st.session_state.bulk_previews
                        st.rerun()
        else:
            st.info("No ENRICHED leads available for bulk outreach.")
    
    # ========== TAB 3: FOLLOW-UPS ==========
    with tab3:
        st.subheader("Follow-up Management")
        
        if st.button("🔄 Run Follow-up Scheduler", help="Process pending follow-ups"):
            with st.spinner("Running follow-up sequence..."):
                run_scheduler()
                st.success("Follow-up sequence completed!")
                st.rerun()
        
        # Show leads in follow-up stages
        followup_leads = [l for l in leads if l.status in [
            LeadStatus.CONTACTED.value,
            LeadStatus.FOLLOWUP_1.value,
            LeadStatus.FOLLOWUP_2.value,
            LeadStatus.FOLLOWUP_3.value
        ]]
        
        if followup_leads:
            st.write(f"**{len(followup_leads)} leads** in follow-up stages")
            followup_df = pd.DataFrame([{
                "Clinic": l.clinic_name,
                "Email": l.email,
                "Status": l.status,
                "Followups": l.follow_up_count,
                "Last Contacted": l.last_contacted
            } for l in followup_leads])
            st.dataframe(followup_df, use_container_width=True)
        else:
            st.info("No leads currently in follow-up stages.")
else:
    st.info("No leads available. Go to the Scraper page first.")

session.close()

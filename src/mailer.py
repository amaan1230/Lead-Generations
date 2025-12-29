import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import datetime
from src.database import Lead, LeadStatus, get_session

def send_outreach_email(lead_id, subject, html_content):
    """Send email via SMTP and update lead status"""
    session = get_session()
    lead = session.query(Lead).filter_by(id=lead_id).first()
    
    if not lead or not lead.email:
        print(f"❌ Cannot send email - Lead {lead_id}: No email address")
        return False
    
    try:
        # Get SMTP credentials from secrets
        smtp_server = st.secrets["SMTP_SERVER"]
        smtp_port = st.secrets["SMTP_PORT"]
        smtp_username = st.secrets["SMTP_USERNAME"]
        smtp_password = st.secrets["SMTP_PASSWORD"]
        from_email = st.secrets["SMTP_FROM_EMAIL"]
        from_name = st.secrets.get("SMTP_FROM_NAME", "Lead Generation")
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{from_name} <{from_email}>"
        message["To"] = lead.email
        
        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        print(f"📧 Sending email to {lead.clinic_name} ({lead.email})...")
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_username, smtp_password)
            server.send_message(message)
        
        print(f"✅ Email sent successfully to {lead.email}")
        
        # Update lead status
        if lead.status == LeadStatus.ENRICHED.value:
            lead.status = LeadStatus.CONTACTED.value
        elif lead.status == LeadStatus.CONTACTED.value:
            lead.status = LeadStatus.FOLLOWUP_1.value
        elif lead.status == LeadStatus.FOLLOWUP_1.value:
            lead.status = LeadStatus.FOLLOWUP_2.value
        elif lead.status == LeadStatus.FOLLOWUP_2.value:
            lead.status = LeadStatus.FOLLOWUP_3.value
            
        lead.last_contacted = datetime.datetime.utcnow()
        lead.follow_up_count += 1
        session.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error sending email to {lead.clinic_name}: {e}")
        return False

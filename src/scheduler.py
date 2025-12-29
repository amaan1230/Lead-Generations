import datetime
from src.database import Lead, LeadStatus, get_session
from src.mailer import send_outreach_email
from src.agent import generate_personalized_email, get_email_body

def run_scheduler():
    session = get_session()
    now = datetime.datetime.utcnow()
    
    # Logic: 
    # 1. Contacted -> Followup_1 (Wait 3 days)
    # 2. Followup_1 -> Followup_2 (Wait 3 days)
    # 3. Followup_2 -> Followup_3 (Wait 3 days)
    # 4. Followup_3 and no reply after 7 days -> Closed
    
    leads_to_followup = session.query(Lead).filter(
        Lead.status.in_([
            LeadStatus.CONTACTED, 
            LeadStatus.FOLLOWUP_1, 
            LeadStatus.FOLLOWUP_2,
            LeadStatus.FOLLOWUP_3
        ])
    ).all()
    
    for lead in leads_to_followup:
        days_since_contact = (now - lead.last_contacted).days
        
        if lead.status == LeadStatus.FOLLOWUP_3:
            if days_since_contact >= 7:
                lead.status = LeadStatus.CLOSED
                session.commit()
            continue
            
        if days_since_contact >= 3:
            # Generate follow up email (simplified for now, could use Gemini again)
            subject = f"Following up: Helping {lead.clinic_name}"
            opening = f"Hi {lead.name}, just following up on my previous email."
            body = get_email_body(lead, opening)
            
            send_outreach_email(lead.id, subject, body)
            
    session.commit()

def process_initial_outreach():
    session = get_session()
    leads_to_contact = session.query(Lead).filter_by(status=LeadStatus.ENRICHED).all()
    
    count = 0
    for lead in leads_to_contact:
        opening = generate_personalized_email(lead.name, lead.clinic_name)
        subject = f"Question for {lead.clinic_name}"
        body = get_email_body(lead, opening)
        
        if send_outreach_email(lead.id, subject, body):
            count += 1
            
    return count

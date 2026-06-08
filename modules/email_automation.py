# modules/email_automation.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime, timedelta

def send_follow_up(lead, stage='initial'):
    """Send follow-up email based on lead score and stage"""
    
    # Templates
    templates = {
        'RED_initial': f"""
        Subject: URGENT: Your email security is at critical risk
        
        Dear {lead.name},
        
        Your email audit shows CRITICAL risks that need immediate attention:
        - Email security records missing
        - Your domain can be impersonated
        - Emails likely landing in spam
        
        Fix this in 48 hours: {os.getenv('CALENDLY_LINK')}
        
        Stay secure,
        TechWokx Security Team
        """,
        
        'ORANGE_nurture': f"""
        Subject: 3 ways to fix your email deliverability
        
        Hi {lead.name},
        
        Your audit shows several areas for improvement. Here's a quick guide:
        [Link to free resource]
        
        Want a personalised fix? Book 15 mins: {os.getenv('CALENDLY_LINK')}
        
        Best regards,
        TechWokx Team
        """,
        
        'GREEN_newsletter': f"""
        Subject: New: Email security features for growing businesses
        
        Hello {lead.name},
        
        Your email setup is good, but here's how to make it excellent:
        - Weekly security tips newsletter
        - Advanced DMARC reporting
        - Staff training guides
        
        Stay ahead of threats,
        TechWokx
        """
    }
    
    key = f"{lead.lead_status}_{stage}"
    if key not in templates:
        return False
    
    # Send email (configure SMTP in .env)
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv('SMTP_FROM')
        msg['To'] = lead.email
        msg['Subject'] = templates[key].split('\n')[0].replace('Subject: ', '')
        
        body = templates[key]
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT')))
        server.starttls()
        server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
        server.send_message(msg)
        server.quit()
        
        return True
    except:
        return False

def get_leads_due_for_followup():
    """Get leads needing follow-up based on last contact"""
    from modules.database import get_session, CRMCompany, CRMActivity
    db = get_session()
    
    # Leads with no activity in last 3 days
    cutoff = datetime.utcnow() - timedelta(days=3)
    leads = db.query(CRMCompany).filter(
        ~CRMCompany.activities.any(CRMActivity.created_at > cutoff)
    ).all()
    
    db.close()
    return leads

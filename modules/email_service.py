# modules/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st

def send_email(smtp_config, to_email, subject, body, from_name="TechWokx"):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{smtp_config['username']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        # Choose port based on security type
        if smtp_config.get('use_ssl', True):
            server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'])
        else:
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
            server.starttls()
        
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)
        server.quit()
        
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

def generate_proposal_email(company_data, contact_person=None):
    """Generate personalized proposal email"""
    
    # Get contact name or use fallback
    if contact_person and contact_person.get('name'):
        salutation = f"Dear {contact_person['name']}"
    elif company_data.get('contacts') and company_data['contacts'][0].get('name'):
        salutation = f"Dear {company_data['contacts'][0]['name']}"
    else:
        salutation = "Dear Management Team"
    
    # Build email body
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .score {{ font-size: 2rem; font-weight: bold; color: #667eea; text-align: center; }}
            .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🔍 TechWokx IT Assessment</h2>
            </div>
            <div class="content">
                {salutation},<br><br>
                
                <p>I recently reviewed <strong>{company_data['name']}</strong>'s online presence and identified several opportunities to improve your IT infrastructure and email security.</p>
                
                <div class="score">
                    Lead Score: {company_data['lead_score']}/100
                </div>
                
                <h3>📊 Key Findings:</h3>
                <ul>
                    <li><strong>Website:</strong> {company_data.get('website', 'Not found')}</li>
                    <li><strong>Business Email:</strong> {'Found' if company_data.get('email') else 'Not configured'}</li>
                    <li><strong>Contact Info:</strong> {'Complete' if company_data.get('phone') else 'Missing'}</li>
                </ul>
                
                <h3>🚀 Recommended Services:</h3>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in company_data.get('recommendations', [])[:3]])}
                </ul>
                
                <h3>💡 Next Steps:</h3>
                <ol>
                    <li>Schedule a 15-minute discovery call</li>
                    <li>Review detailed IT audit report</li>
                    <li>Receive custom proposal with pricing</li>
                </ol>
                
                <p>I'll follow up in a few days, but feel free to reply here or call me at +233 555 087 407.</p>
                
                <p>Best regards,<br>
                <strong>George Jabley</strong><br>
                Founder & IT Operations Lead<br>
                TechWokx Ghana<br>
                <a href="https://techwokx.online">techwokx.online</a>
                </p>
            </div>
            <div class="footer">
                <p>© 2024 TechWokx | IT Intelligence for African Businesses</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return body

def send_proposal_email(smtp_config, company_data, to_email, contact_person=None):
    """Send proposal email to lead"""
    subject = f"IT Assessment for {company_data['name']} - Score: {company_data['lead_score']}/100"
    body = generate_proposal_email(company_data, contact_person)
    return send_email(smtp_config, to_email, subject, body)

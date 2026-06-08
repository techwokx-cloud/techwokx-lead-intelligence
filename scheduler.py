# scheduler.py - Run via GitHub Actions or cron job
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from modules.email_automation import get_leads_due_for_followup, send_follow_up
from modules.database import get_session, CRMActivity
from datetime import datetime

def run_daily_followups():
    print(f"Running follow-ups at {datetime.utcnow()}")
    
    leads = get_leads_due_for_followup(days_since_contact=3)
    print(f"Found {len(leads)} leads due for follow-up")
    
    success_count = 0
    for lead in leads:
        if send_follow_up(lead):
            success_count += 1
            # Log activity
            db = get_session()
            activity = CRMActivity(
                company_id=lead.id,
                activity_type="Auto Email",
                description=f"Automated follow-up sent (Day {lead.followup_count or 1})"
            )
            db.add(activity)
            db.commit()
            db.close()
    
    print(f"Sent {success_count} emails")

if __name__ == "__main__":
    run_daily_followups()

import json
from datetime import datetime
from modules.database import get_session, CRMCompany, CRMActivity

def save_research_to_crm(research_result, dns_result, website_result, lead_score):
    """Save research results to CRM database"""
    session = get_session()
    
    # Check if company already exists
    existing = session.query(CRMCompany).filter_by(domain=research_result.domain).first()
    
    if existing:
        company_id = existing.id
        # Update existing record
        existing.name = research_result.company_name
        existing.website = research_result.website
        existing.phone = research_result.phone
        existing.email = research_result.email
        existing.address = research_result.address
        existing.lead_score = lead_score.total
        existing.lead_status = lead_score.status
        existing.last_research = datetime.utcnow()
        existing.research_data = json.dumps({
            "dns_score": dns_result.score if dns_result else None,
            "website_reachable": website_result.reachable if website_result else None,
            "confidence": research_result.confidence_score
        })
    else:
        # Create new record
        new_company = CRMCompany(
            name=research_result.company_name,
            domain=research_result.domain,
            website=research_result.website,
            phone=research_result.phone,
            email=research_result.email,
            address=research_result.address,
            lead_score=lead_score.total,
            lead_status=lead_score.status,
            created_at=datetime.utcnow(),
            last_research=datetime.utcnow(),
            research_data=json.dumps({
                "dns_score": dns_result.score if dns_result else None,
                "website_reachable": website_result.reachable if website_result else None,
                "confidence": research_result.confidence_score
            })
        )
        session.add(new_company)
        session.flush()
        company_id = new_company.id
    
    session.commit()
    session.close()
    
    return company_id

def log_activity(company_id, activity_type, description, user_id=None):
    """Log activity for a company"""
    session = get_session()
    
    activity = CRMActivity(
        company_id=company_id,
        activity_type=activity_type,
        description=description,
        created_at=datetime.utcnow(),
        user_id=user_id
    )
    
    session.add(activity)
    session.commit()
    session.close()

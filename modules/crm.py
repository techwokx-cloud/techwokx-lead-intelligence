# modules/crm.py
from modules.database import get_session, CRMCompany, CRMActivity
from datetime import datetime
import json
import hashlib

def save_research_to_crm(research_result, dns_result, website_result, lead_score):
    """Save research results to CRM database"""
    try:
        session = get_session()
        
        # Create email hash for unique identification
        email_hash = None
        if research_result.email:
            email_hash = hashlib.md5(research_result.email.lower().encode()).hexdigest()
        
        # Check if company already exists by domain or email hash
        existing = None
        if research_result.domain:
            existing = session.query(CRMCompany).filter_by(domain=research_result.domain).first()
        if not existing and email_hash:
            existing = session.query(CRMCompany).filter_by(email_hash=email_hash).first()
        
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
            
            # Update email hash if not set
            if not existing.email_hash and email_hash:
                existing.email_hash = email_hash
        else:
            # Create new record
            new_company = CRMCompany(
                name=research_result.company_name,
                domain=research_result.domain or "",
                website=research_result.website or "",
                phone=research_result.phone or "",
                email=research_result.email or "",
                address=research_result.address or "",
                lead_score=lead_score.total,
                lead_status=lead_score.status,
                email_hash=email_hash,
                created_at=datetime.utcnow(),
                last_research=datetime.utcnow()
            )
            session.add(new_company)
            session.flush()
            company_id = new_company.id
        
        session.commit()
        session.close()
        return company_id
    except Exception as e:
        print(f"Error saving to CRM: {e}")
        return None

def log_activity(company_id, activity_type, description, user_id=None):
    """Log activity for a company"""
    try:
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
        return True
    except Exception as e:
        print(f"Error logging activity: {e}")
        return False

def get_all_companies(limit=None, offset=0, sort_by='lead_score', sort_desc=True):
    """Get all companies from CRM with optional pagination"""
    try:
        session = get_session()
        query = session.query(CRMCompany)
        
        # Apply sorting
        if sort_by == 'lead_score':
            if sort_desc:
                query = query.order_by(CRMCompany.lead_score.desc())
            else:
                query = query.order_by(CRMCompany.lead_score.asc())
        elif sort_by == 'name':
            if sort_desc:
                query = query.order_by(CRMCompany.name.desc())
            else:
                query = query.order_by(CRMCompany.name.asc())
        elif sort_by == 'created_at':
            if sort_desc:
                query = query.order_by(CRMCompany.created_at.desc())
            else:
                query = query.order_by(CRMCompany.created_at.asc())
        elif sort_by == 'last_research':
            if sort_desc:
                query = query.order_by(CRMCompany.last_research.desc())
            else:
                query = query.order_by(CRMCompany.last_research.asc())
        
        # Apply limit and offset
        if limit:
            query = query.limit(limit)
        query = query.offset(offset)
        
        companies = query.all()
        session.close()
        return companies
    except Exception as e:
        print(f"Error getting companies: {e}")
        return []

def get_company(company_id):
    """Get a specific company by ID"""
    try:
        session = get_session()
        company = session.query(CRMCompany).filter_by(id=company_id).first()
        session.close()
        return company
    except Exception as e:
        print(f"Error getting company: {e}")
        return None

def get_company_by_email(email):
    """Get a company by email address"""
    try:
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        session = get_session()
        company = session.query(CRMCompany).filter_by(email_hash=email_hash).first()
        session.close()
        return company
    except Exception as e:
        print(f"Error getting company by email: {e}")
        return None

def get_company_by_domain(domain):
    """Get a company by domain"""
    try:
        session = get_session()
        company = session.query(CRMCompany).filter_by(domain=domain).first()
        session.close()
        return company
    except Exception as e:
        print(f"Error getting company by domain: {e}")
        return None

def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        session = get_session()
        companies = session.query(CRMCompany).all()
        
        total = len(companies)
        hot = sum(1 for c in companies if c.lead_score and c.lead_score >= 70)
        warm = sum(1 for c in companies if c.lead_score and 50 <= c.lead_score < 70)
        cold = sum(1 for c in companies if c.lead_score and c.lead_score < 50)
        no_score = sum(1 for c in companies if not c.lead_score)
        
        scores = [c.lead_score for c in companies if c.lead_score]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Get recent activity count
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_activities = session.query(CRMActivity).filter(CRMActivity.created_at >= week_ago).count()
        
        # Get leads by source
        sources = {}
        for c in companies:
            source = getattr(c, 'source', 'Audit')
            sources[source] = sources.get(source, 0) + 1
        
        session.close()
        
        return {
            'total_companies': total,
            'hot_leads': hot,
            'warm_leads': warm,
            'cold_leads': cold,
            'no_score': no_score,
            'avg_score': avg_score,
            'recent_activities': recent_activities,
            'sources': sources
        }
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return {
            'total_companies': 0,
            'hot_leads': 0,
            'warm_leads': 0,
            'cold_leads': 0,
            'no_score': 0,
            'avg_score': 0,
            'recent_activities': 0,
            'sources': {}
        }

def get_recent_activities(limit=10):
    """Get recent CRM activities"""
    try:
        session = get_session()
        activities = session.query(CRMActivity).order_by(CRMActivity.created_at.desc()).limit(limit).all()
        session.close()
        
        result = []
        for act in activities:
            # Get company name
            company = session.query(CRMCompany).filter_by(id=act.company_id).first()
            result.append({
                'id': act.id,
                'company_id': act.company_id,
                'company_name': company.name if company else 'Unknown',
                'activity_type': act.activity_type,
                'description': act.description,
                'created_at': act.created_at,
                'user_id': act.user_id
            })
        
        return result
    except Exception as e:
        print(f"Error getting recent activities: {e}")
        return []

def update_company(company_id, updates):
    """Update company information"""
    try:
        session = get_session()
        company = session.query(CRMCompany).filter_by(id=company_id).first()
        
        if company:
            for key, value in updates.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            
            session.commit()
            session.close()
            return True
        
        session.close()
        return False
    except Exception as e:
        print(f"Error updating company: {e}")
        return False

def delete_company(company_id):
    """Delete a company from CRM"""
    try:
        session = get_session()
        company = session.query(CRMCompany).filter_by(id=company_id).first()
        
        if company:
            # Delete related activities first
            session.query(CRMActivity).filter_by(company_id=company_id).delete()
            session.delete(company)
            session.commit()
            session.close()
            return True
        
        session.close()
        return False
    except Exception as e:
        print(f"Error deleting company: {e}")
        return False

def get_leads_by_status(status):
    """Get leads filtered by status (RED, ORANGE, GREEN)"""
    try:
        session = get_session()
        leads = session.query(CRMCompany).filter_by(lead_status=status).all()
        session.close()
        return leads
    except Exception as e:
        print(f"Error getting leads by status: {e}")
        return []

def get_leads_due_for_followup(days=3):
    """Get leads that need follow-up"""
    try:
        from datetime import timedelta
        session = get_session()
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Get leads with no recent activity
        from sqlalchemy import not_
        leads = session.query(CRMCompany).filter(
            not_(CRMCompany.activities.any(CRMActivity.created_at > cutoff))
        ).all()
        
        session.close()
        return leads
    except Exception as e:
        print(f"Error getting leads due for followup: {e}")
        return []

def search_companies(search_term):
    """Search companies by name, email, or domain"""
    try:
        session = get_session()
        search = f"%{search_term}%"
        companies = session.query(CRMCompany).filter(
            (CRMCompany.name.ilike(search)) |
            (CRMCompany.email.ilike(search)) |
            (CRMCompany.domain.ilike(search))
        ).all()
        session.close()
        return companies
    except Exception as e:
        print(f"Error searching companies: {e}")
        return []

def get_company_activities(company_id, limit=20):
    """Get activity history for a specific company"""
    try:
        session = get_session()
        activities = session.query(CRMActivity).filter_by(company_id=company_id).order_by(CRMActivity.created_at.desc()).limit(limit).all()
        session.close()
        return activities
    except Exception as e:
        print(f"Error getting company activities: {e}")
        return []

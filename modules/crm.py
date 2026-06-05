from datetime import datetime
from modules.database import get_session, Company, Contact, Activity, ResearchHistory
from sqlalchemy import desc


CRM_STAGES = ["New", "Researching", "Contacted", "Proposal Sent", "Follow-up", "Negotiation", "Won", "Lost"]


def save_company(data: dict) -> int:
    db = get_session()
    try:
        existing = db.query(Company).filter(Company.company_name == data.get("company_name")).first()
        if existing:
            for k, v in data.items():
                if hasattr(existing, k) and v is not None:
                    setattr(existing, k, v)
            existing.updated_at = datetime.utcnow()
            db.commit()
            return existing.id
        else:
            company = Company(**{k: v for k, v in data.items() if hasattr(Company, k)})
            db.add(company)
            db.commit()
            db.refresh(company)
            return company.id
    finally:
        db.close()


def save_contact(company_id: int, email: str, phone: str = "", name: str = "", source: str = "crawl"):
    db = get_session()
    try:
        existing = db.query(Contact).filter(Contact.company_id == company_id, Contact.email == email).first()
        if not existing:
            c = Contact(company_id=company_id, email=email, phone=phone, name=name, source=source)
            db.add(c)
            db.commit()
    finally:
        db.close()


def log_activity(company_id: int, activity_type: str, description: str):
    db = get_session()
    try:
        act = Activity(company_id=company_id, activity_type=activity_type, description=description)
        db.add(act)
        db.commit()
    finally:
        db.close()


def update_stage(company_id: int, stage: str):
    db = get_session()
    try:
        company = db.query(Company).filter(Company.id == company_id).first()
        if company:
            company.crm_stage = stage
            company.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


def get_all_companies(stage: str = None, status: str = None) -> list:
    db = get_session()
    try:
        q = db.query(Company)
        if stage:
            q = q.filter(Company.crm_stage == stage)
        if status:
            q = q.filter(Company.lead_status == status)
        return q.order_by(desc(Company.lead_score)).all()
    finally:
        db.close()


def get_company(company_id: int) -> Company:
    db = get_session()
    try:
        return db.query(Company).filter(Company.id == company_id).first()
    finally:
        db.close()


def get_dashboard_stats() -> dict:
    db = get_session()
    try:
        total = db.query(Company).count()
        hot = db.query(Company).filter(Company.lead_status == "Hot").count()
        warm = db.query(Company).filter(Company.lead_status == "Warm").count()
        proposals = db.query(Company).filter(Company.crm_stage == "Proposal Sent").count()
        won = db.query(Company).filter(Company.crm_stage == "Won").count()
        lost = db.query(Company).filter(Company.crm_stage == "Lost").count()
        recent = db.query(Company).order_by(desc(Company.created_at)).limit(5).all()
        return {"total": total, "hot": hot, "warm": warm, "proposals": proposals, "won": won, "lost": lost, "recent": recent}
    finally:
        db.close()


def save_research_to_crm(research, dns=None, web=None, lead_score=None, ai_data=None) -> int:
    tech_stack = ""
    if dns:
        tech_stack = f"Email: {dns.email_provider}"

    data = {
        "company_name": research.company_name,
        "website": research.website,
        "domain": research.domain if hasattr(research, "domain") else "",
        "phone": research.phone,
        "email": research.email,
        "address": research.address,
        "confidence_score": research.confidence_score,
        "lead_score": lead_score.total if lead_score else 0,
        "lead_status": lead_score.status if lead_score else "Cold",
        "crm_stage": "Researching",
        "ssl_valid": web.ssl.valid if (web and web.ssl) else False,
        "website_up": web.reachable if web else False,
        "has_spf": dns.has_spf if dns else False,
        "has_dmarc": dns.has_dmarc if dns else False,
        "has_mx": dns.has_mx if dns else False,
        "dns_score": dns.score if dns else 0,
        "email_provider": dns.email_provider if dns else "",
        "tech_stack": tech_stack,
        "ai_summary": (ai_data or {}).get("company_summary", ""),
        "description": research.description,
    }
    cid = save_company(data)
    if research.email:
        save_contact(cid, research.email, research.phone or "", source="crawl")
    log_activity(cid, "Research", f"Automated research completed. Lead score: {lead_score.total if lead_score else 0}/100")
    return cid

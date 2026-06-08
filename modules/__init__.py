# modules/__init__.py
# This file makes the modules directory a Python package

from modules.company_research import research_company, CompanyResearchResult
from modules.lead_scoring import score_from_research
from modules.technology_detector import detect_technologies
from modules.crm import save_research_to_crm, log_activity
from modules.database import get_session, ResearchHistory, CRMCompany, CRMActivity
from modules.theme import THEME_CSS

__all__ = [
    'research_company',
    'CompanyResearchResult',
    'score_from_research',
    'detect_technologies',
    'save_research_to_crm',
    'log_activity',
    'get_session',
    'ResearchHistory',
    'CRMCompany',
    'CRMActivity',
    'THEME_CSS'
]

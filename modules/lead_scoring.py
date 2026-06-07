from dataclasses import dataclass, field
from typing import List

@dataclass
class ScoringRule:
    name: str
    points: int
    reason: str
    triggered: bool = False

@dataclass
class LeadScore:
    total: int
    status: str
    rules: List[ScoringRule]
    opportunity_summary: str

def score_from_research(research_result):
    """Calculate lead score based on research results"""
    rules = []
    total = 0
    
    # Website presence and quality
    if research_result.website:
        rules.append(ScoringRule("website", 15, "Has website", True))
        total += 15
        
        if research_result.website_result and research_result.website_result.reachable:
            rules.append(ScoringRule("reachable", 10, "Website reachable", True))
            total += 10
            
            if research_result.website_result.https:
                rules.append(ScoringRule("https", 10, "Uses HTTPS", True))
                total += 10
    else:
        rules.append(ScoringRule("website", 0, "No website found", False))
    
    # Contact information
    if research_result.email:
        rules.append(ScoringRule("email", 15, "Has email contact", True))
        total += 15
    
    if research_result.phone:
        rules.append(ScoringRule("phone", 10, "Has phone number", True))
        total += 10
    
    if research_result.address:
        rules.append(ScoringRule("address", 10, "Has physical address", True))
        total += 10
    
    # DNS/Email security
    if research_result.dns_result:
        if research_result.dns_result.has_mx:
            rules.append(ScoringRule("mx_records", 10, "Has email infrastructure", True))
            total += 10
        
        if research_result.dns_result.has_dmarc:
            rules.append(ScoringRule("dmarc", 10, "Has DMARC (email security)", True))
            total += 10
    
    # Social presence
    if research_result.social:
        rules.append(ScoringRule("social", 10, "Has social media presence", True))
        total += 10
    
    # Determine status
    if total >= 70:
        status = "Hot Lead"
        summary = "High-quality lead with strong online presence and contact information."
    elif total >= 50:
        status = "Warm Lead"
        summary = "Moderate potential. Some information available for follow-up."
    elif total >= 30:
        status = "Cold Lead"
        summary = "Limited information. Requires further research."
    else:
        status = "Invalid"
        summary = "Minimal information found. Check company name/website."
    
    return LeadScore(total=total, status=status, rules=rules, opportunity_summary=summary)

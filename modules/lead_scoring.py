from dataclasses import dataclass, field
from typing import List


@dataclass
class ScoreRule:
    reason: str
    points: int
    triggered: bool = False


@dataclass
class LeadScore:
    total: int = 0
    status: str = "Cold"
    rules: List[ScoreRule] = field(default_factory=list)
    opportunity_summary: str = ""


def calculate_lead_score(
    has_dmarc: bool = False,
    has_spf: bool = False,
    has_mx: bool = False,
    has_dkim: bool = False,
    ssl_valid: bool = False,
    website_up: bool = True,
    has_business_email: bool = True,
    website_security_poor: bool = False,
    dns_score: int = 100,
) -> LeadScore:
    rules = [
        ScoreRule("No DMARC policy — email spoofing risk", 20, not has_dmarc),
        ScoreRule("No SPF record — impersonation possible", 20, not has_spf),
        ScoreRule("No SSL certificate", 20, not ssl_valid),
        ScoreRule("Website is down or unreachable", 25, not website_up),
        ScoreRule("No business email detected", 20, not has_business_email),
        ScoreRule("No MX records — cannot receive email", 15, not has_mx),
        ScoreRule("No DKIM signing", 10, not has_dkim),
        ScoreRule("Poor website security overall", 15, website_security_poor),
    ]

    total = sum(r.points for r in rules if r.triggered)
    total = min(total, 100)

    if total >= 90:
        status = "Hot"
    elif total >= 70:
        status = "Warm"
    else:
        status = "Cold"

    triggered = [r for r in rules if r.triggered]
    if total >= 70:
        opportunity = f"HIGH VALUE: {len(triggered)} critical issue(s) found. Strong opportunity for TechWokx services."
    elif total >= 50:
        opportunity = f"MEDIUM: {len(triggered)} issue(s) detected. Good opportunity for email or security fix."
    else:
        opportunity = f"LOW: {len(triggered)} minor issue(s). Monitor and nurture."

    return LeadScore(total=total, status=status, rules=rules, opportunity_summary=opportunity)


def score_from_research(research_result) -> LeadScore:
    dns = research_result.dns_result
    web = research_result.website_result
    has_dmarc = dns.has_dmarc if dns else False
    has_spf = dns.has_spf if dns else False
    has_mx = dns.has_mx if dns else False
    has_dkim = dns.has_dkim if dns else False
    ssl_valid = web.ssl.valid if (web and web.ssl) else False
    website_up = web.reachable if web else False
    has_business_email = bool(research_result.email and "@gmail" not in research_result.email)
    poor_security = (not has_dmarc and not has_spf and not ssl_valid)
    return calculate_lead_score(
        has_dmarc=has_dmarc, has_spf=has_spf, has_mx=has_mx, has_dkim=has_dkim,
        ssl_valid=ssl_valid, website_up=website_up, has_business_email=has_business_email,
        website_security_poor=poor_security
    )

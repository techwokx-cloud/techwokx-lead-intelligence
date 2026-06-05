import os
import json
from typing import Optional


def _build_context(research, dns, web, lead_score) -> str:
    lines = []
    lines.append(f"Company: {research.company_name}")
    lines.append(f"Domain: {research.domain}")
    lines.append(f"Website: {research.website}")
    lines.append(f"Address: {research.address or 'Unknown'}")
    lines.append(f"Phone: {research.phone or 'Unknown'}")
    lines.append(f"Email: {research.email or 'Unknown'}")
    lines.append(f"Description: {research.description or 'Not available'}")
    lines.append(f"Lead Score: {lead_score.total}/100 ({lead_score.status})")
    if dns:
        lines.append(f"Email Security Score: {dns.score}/100 (Grade: {dns.grade})")
        lines.append(f"Has MX: {dns.has_mx}, Has SPF: {dns.has_spf}, Has DMARC: {dns.has_dmarc}, Has DKIM: {dns.has_dkim}")
        lines.append(f"Email Provider: {dns.email_provider}")
    if web:
        lines.append(f"Website Reachable: {web.reachable}, HTTPS: {web.https}")
        lines.append(f"SSL Valid: {web.ssl.valid if web.ssl else False}")
    triggered = [r.reason for r in lead_score.rules if r.triggered]
    if triggered:
        lines.append("Issues Found: " + "; ".join(triggered))
    return "\n".join(lines)


def _call_claude(prompt: str) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"AI analysis unavailable: {e}"


def _call_openai(prompt: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI analysis unavailable: {e}"


def generate_ai_analysis(research, dns=None, web=None, lead_score=None, provider="claude") -> dict:
    context = _build_context(research, dns, web, lead_score)

    prompt = f"""You are a senior IT consultant at TechWokx Ghana. Analyze the following company data and provide a structured assessment.

COMPANY DATA:
{context}

Provide a JSON response with these exact keys:
- company_summary: 2-3 sentence overview of the company and their digital presence
- business_risks: list of 3-5 business risks based on findings (in plain English, no jargon)
- technology_risks: list of 3-5 technical risks found
- email_risks: list of specific email security risks
- recommended_services: list of TechWokx services that would help (from: Business Email Fix, Monthly IT Retainer, Infrastructure Audit, Process Automation)
- sales_opportunity: 1 paragraph sales opportunity summary for a cold outreach
- urgency: HIGH / MEDIUM / LOW

RULES:
- Only analyze facts provided. Do not invent company information.
- Write for a business audience, not a technical one.
- Keep each list item under 20 words.

Return valid JSON only, no markdown."""

    if provider == "claude" and os.getenv("ANTHROPIC_API_KEY"):
        raw = _call_claude(prompt)
    elif os.getenv("OPENAI_API_KEY"):
        raw = _call_openai(prompt)
    else:
        return _fallback_analysis(research, dns, web, lead_score)

    try:
        return json.loads(raw)
    except Exception:
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"company_summary": raw[:400], "error": "Parse error"}


def _fallback_analysis(research, dns, web, lead_score) -> dict:
    triggered = [r.reason for r in lead_score.rules if r.triggered] if lead_score else []
    risks = triggered[:5] if triggered else ["No critical issues detected"]
    return {
        "company_summary": f"{research.company_name} is a business based in Ghana. Digital presence assessment completed with {len(triggered)} issue(s) identified.",
        "business_risks": risks[:3],
        "technology_risks": risks[3:] or ["Manual processes may be in place"],
        "email_risks": [r for r in risks if "email" in r.lower() or "spf" in r.lower() or "dmarc" in r.lower()] or ["Email security not verified"],
        "recommended_services": ["Business Email Fix", "Infrastructure Audit"],
        "sales_opportunity": f"TechWokx can help {research.company_name} fix {len(triggered)} identified issues.",
        "urgency": "HIGH" if (lead_score and lead_score.total >= 70) else "MEDIUM"
    }

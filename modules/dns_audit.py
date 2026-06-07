import dns.resolver
import dns.exception
from dataclasses import dataclass, field
from typing import List

@dataclass
class DNSFinding:
    check: str
    status: str  # PASS, FAIL, WARNING
    detail: str
    value: str = ""

@dataclass
class DNSResult:
    domain: str
    score: int
    grade: str
    findings: List[DNSFinding] = field(default_factory=list)
    has_mx: bool = False
    has_dmarc: bool = False
    email_provider: str = "None"

def run_dns_audit(domain: str) -> DNSResult:
    """Run comprehensive DNS audit for a domain"""
    result = DNSResult(domain=domain, score=0, grade="F")
    total_score = 0
    max_score = 100
    
    # Check MX records
    mx_finding = check_mx_records(domain)
    result.findings.append(mx_finding)
    if mx_finding.status == "PASS":
        total_score += 30
        result.has_mx = True
        result.email_provider = detect_email_provider(mx_finding.value)
    
    # Check SPF
    spf_finding = check_spf(domain)
    result.findings.append(spf_finding)
    if spf_finding.status == "PASS":
        total_score += 25
    
    # Check DMARC
    dmarc_finding = check_dmarc(domain)
    result.findings.append(dmarc_finding)
    if dmarc_finding.status == "PASS":
        total_score += 25
        result.has_dmarc = True
    
    # Check DKIM (simplified - just checks if DKIM record exists)
    dkim_finding = check_dkim(domain)
    result.findings.append(dkim_finding)
    if dkim_finding.status == "PASS":
        total_score += 20
    
    # Calculate score and grade
    result.score = total_score
    
    if result.score >= 90:
        result.grade = "A+"
    elif result.score >= 80:
        result.grade = "A"
    elif result.score >= 70:
        result.grade = "B"
    elif result.score >= 60:
        result.grade = "C"
    elif result.score >= 50:
        result.grade = "D"
    else:
        result.grade = "F"
    
    return result

def check_mx_records(domain: str) -> DNSFinding:
    """Check MX records for the domain"""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_list = [str(mx.exchange).rstrip('.') for mx in mx_records]
        mx_str = ", ".join(mx_list)
        return DNSFinding(
            check="MX Records",
            status="PASS",
            detail=f"Found {len(mx_records)} MX record(s)",
            value=mx_str
        )
    except dns.resolver.NXDOMAIN:
        return DNSFinding(
            check="MX Records",
            status="FAIL",
            detail="Domain does not exist",
            value=""
        )
    except dns.resolver.NoAnswer:
        return DNSFinding(
            check="MX Records",
            status="FAIL",
            detail="No MX records found - email may not be configured",
            value=""
        )
    except Exception as e:
        return DNSFinding(
            check="MX Records",
            status="WARNING",
            detail=f"Error checking MX: {str(e)}",
            value=""
        )

def check_spf(domain: str) -> DNSFinding:
    """Check SPF record for the domain"""
    try:
        spf_records = dns.resolver.resolve(domain, 'TXT')
        for record in spf_records:
            if 'v=spf1' in str(record).lower():
                return DNSFinding(
                    check="SPF Record",
                    status="PASS",
                    detail="SPF record found",
                    value=str(record)[:200]
                )
        return DNSFinding(
            check="SPF Record",
            status="FAIL",
            detail="No SPF record found - email spoofing risk",
            value=""
        )
    except Exception as e:
        return DNSFinding(
            check="SPF Record",
            status="WARNING",
            detail=f"Error checking SPF: {str(e)}",
            value=""
        )

def check_dmarc(domain: str) -> DNSFinding:
    """Check DMARC record for the domain"""
    dmarc_domain = f"_dmarc.{domain}"
    try:
        dmarc_records = dns.resolver.resolve(dmarc_domain, 'TXT')
        for record in dmarc_records:
            if 'v=DMARC1' in str(record).upper():
                return DNSFinding(
                    check="DMARC Record",
                    status="PASS",
                    detail="DMARC record found - good email security",
                    value=str(record)[:200]
                )
        return DNSFinding(
            check="DMARC Record",
            status="FAIL",
            detail="No DMARC record found",
            value=""
        )
    except dns.resolver.NoAnswer:
        return DNSFinding(
            check="DMARC Record",
            status="FAIL",
            detail="No DMARC record found",
            value=""
        )
    except Exception as e:
        return DNSFinding(
            check="DMARC Record",
            status="WARNING",
            detail=f"Error checking DMARC: {str(e)}",
            value=""
        )

def check_dkim(domain: str) -> DNSFinding:
    """Check for DKIM records (simplified - checks common selectors)"""
    common_selectors = ['default', 'google', 'selector1', 'dkim', 'mail']
    
    for selector in common_selectors:
        dkim_domain = f"{selector}._domainkey.{domain}"
        try:
            dns.resolver.resolve(dkim_domain, 'TXT')
            return DNSFinding(
                check="DKIM Record",
                status="PASS",
                detail=f"DKIM record found with selector '{selector}'",
                value=""
            )
        except:
            continue
    
    return DNSFinding(
        check="DKIM Record",
        status="WARNING",
        detail="No DKIM records found with common selectors",
        value=""
    )

def detect_email_provider(mx_records_str: str) -> str:
    """Detect email provider from MX records"""
    mx_lower = mx_records_str.lower()
    
    if 'google' in mx_lower or 'gmail' in mx_lower:
        return "Google Workspace"
    elif 'microsoft' in mx_lower or 'outlook' in mx_lower or 'office365' in mx_lower:
        return "Microsoft 365"
    elif 'zoho' in mx_lower:
        return "Zoho"
    elif 'proton' in mx_lower:
        return "ProtonMail"
    elif 'icloud' in mx_lower:
        return "iCloud"
    else:
        return "Other/Unknown"

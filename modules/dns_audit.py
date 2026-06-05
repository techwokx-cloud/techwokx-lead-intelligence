import dns.resolver
import dns.exception
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DNSFinding:
    check: str
    status: str  # PASS / FAIL / WARN
    detail: str
    value: str = ""


@dataclass
class DNSAuditResult:
    domain: str
    score: int = 0
    grade: str = "F"
    findings: List[DNSFinding] = field(default_factory=list)
    has_mx: bool = False
    has_spf: bool = False
    has_dmarc: bool = False
    has_dkim: bool = False
    has_mta_sts: bool = False
    has_bimi: bool = False
    email_provider: str = "Unknown"


def _resolve(qname: str, rtype: str) -> Optional[list]:
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 4
        resolver.lifetime = 6
        answers = resolver.resolve(qname, rtype)
        return [str(r) for r in answers]
    except Exception:
        return None


def detect_email_provider(mx_records: list) -> str:
    if not mx_records:
        return "None"
    combined = " ".join(mx_records).lower()
    if "google" in combined or "aspmx" in combined:
        return "Google Workspace"
    if "outlook" in combined or "protection.outlook" in combined or "microsoft" in combined:
        return "Microsoft 365"
    if "zoho" in combined:
        return "Zoho Mail"
    if "mxroute" in combined:
        return "MXRoute"
    if "mailgun" in combined:
        return "Mailgun"
    if "sendgrid" in combined:
        return "SendGrid"
    if "cpanel" in combined or "secureserver" in combined:
        return "cPanel/Shared Hosting"
    return "Custom"


def run_dns_audit(domain: str) -> DNSAuditResult:
    domain = domain.lower().replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    result = DNSAuditResult(domain=domain)
    score = 0

    # MX
    mx = _resolve(domain, "MX")
    if mx:
        result.has_mx = True
        result.email_provider = detect_email_provider(mx)
        result.findings.append(DNSFinding("MX Records", "PASS", f"Mail server found: {mx[0]}", mx[0]))
        score += 15
    else:
        result.findings.append(DNSFinding("MX Records", "FAIL", f"No MX records — domain cannot receive email"))

    # SPF
    txt = _resolve(domain, "TXT")
    spf_record = None
    if txt:
        for t in txt:
            if "v=spf1" in t.lower():
                spf_record = t
                break
    if spf_record:
        result.has_spf = True
        result.findings.append(DNSFinding("SPF Record", "PASS", "SPF record found", spf_record[:80]))
        score += 20
    else:
        result.findings.append(DNSFinding("SPF Record", "FAIL", f"No SPF — anyone can send email as {domain}"))

    # DMARC
    dmarc = _resolve(f"_dmarc.{domain}", "TXT")
    dmarc_record = None
    if dmarc:
        for d in dmarc:
            if "v=dmarc1" in d.lower():
                dmarc_record = d
                break
    if dmarc_record:
        result.has_dmarc = True
        policy = "none"
        if "p=reject" in dmarc_record.lower():
            policy = "reject"
        elif "p=quarantine" in dmarc_record.lower():
            policy = "quarantine"
        if policy in ("reject", "quarantine"):
            result.findings.append(DNSFinding("DMARC Policy", "PASS", f"DMARC enforced (policy={policy})", dmarc_record[:80]))
            score += 25
        else:
            result.findings.append(DNSFinding("DMARC Policy", "WARN", f"DMARC exists but policy=none (not enforced)", dmarc_record[:80]))
            score += 10
    else:
        result.findings.append(DNSFinding("DMARC Policy", "FAIL", f"No DMARC — no spoofing protection policy"))

    # DKIM (common selectors)
    dkim_found = False
    for selector in ["default", "google", "mail", "selector1", "selector2", "dkim", "k1"]:
        dkim = _resolve(f"{selector}._domainkey.{domain}", "TXT")
        if dkim:
            dkim_found = True
            result.has_dkim = True
            result.findings.append(DNSFinding("DKIM Signing", "PASS", f"DKIM found (selector: {selector})", dkim[0][:60]))
            score += 15
            break
    if not dkim_found:
        result.findings.append(DNSFinding("DKIM Signing", "WARN", "No common DKIM selectors found — emails may not be signed"))

    # MTA-STS
    mta = _resolve(f"_mta-sts.{domain}", "TXT")
    if mta:
        result.has_mta_sts = True
        result.findings.append(DNSFinding("MTA-STS", "PASS", "MTA-STS found — mail transport encryption enforced"))
        score += 10
    else:
        result.findings.append(DNSFinding("MTA-STS", "WARN", "No MTA-STS — mail transport encryption not enforced"))

    # BIMI
    bimi = _resolve(f"default._bimi.{domain}", "TXT")
    if bimi:
        result.has_bimi = True
        result.findings.append(DNSFinding("BIMI (Brand Logo)", "PASS", "BIMI record found — brand logo in inboxes"))
        score += 5
    else:
        result.findings.append(DNSFinding("BIMI (Brand Logo)", "WARN", "No BIMI — no brand logo in recipient inboxes"))

    result.score = min(score, 100)
    if score >= 90:
        result.grade = "A"
    elif score >= 75:
        result.grade = "B"
    elif score >= 60:
        result.grade = "C"
    elif score >= 40:
        result.grade = "D"
    else:
        result.grade = "F"

    return result

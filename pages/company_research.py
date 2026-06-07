import requests
import re
import tldextract
from dataclasses import dataclass, field
from typing import List, Optional
from modules.website_verifier import verify_website
from modules.website_crawler import crawl_website
from modules.dns_audit import run_dns_audit
from modules.research_engine import research_company

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TechWokxBot/1.0)"}
TIMEOUT = 8


@dataclass
class CompanyResearchResult:
    search_term: str = ""
    company_name: str = ""
    website: str = ""
    domain: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    industry: str = ""
    description: str = ""
    social: dict = field(default_factory=dict)
    confidence_score: float = 0.0
    confidence_label: str = "Low Confidence"
    sources: List[str] = field(default_factory=list)
    website_result: object = None
    dns_result: object = None
    crawl_result: object = None
    error: str = ""


def _clean_domain(url: str) -> str:
    ext = tldextract.extract(url)
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}"
    return url.lower().replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]


def _duckduckgo_search(query: str) -> dict:
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            headers=HEADERS, timeout=TIMEOUT
        )
        return r.json()
    except Exception:
        return {}


def _extract_website_from_ddg(dd: dict) -> str:
    for key in ("OfficialWebsite", "AbstractURL"):
        val = dd.get(key, "")
        if val and "wikipedia" not in val:
            return val
    if dd.get("Infobox") and dd["Infobox"].get("content"):
        for item in dd["Infobox"]["content"]:
            lbl = (item.get("label") or "").lower()
            if "website" in lbl or "url" in lbl:
                return item.get("value", "")
    return ""


def _extract_phone_from_ddg(dd: dict) -> str:
    if dd.get("Infobox") and dd["Infobox"].get("content"):
        for item in dd["Infobox"]["content"]:
            lbl = (item.get("label") or "").lower()
            if "phone" in lbl or "tel" in lbl or "call" in lbl:
                return item.get("value", "")
    return ""


def _extract_address_from_ddg(dd: dict) -> str:
    if dd.get("Infobox") and dd["Infobox"].get("content"):
        for item in dd["Infobox"]["content"]:
            lbl = (item.get("label") or "").lower()
            if "address" in lbl or "location" in lbl:
                return item.get("value", "")
    return ""


def calculate_confidence(res: CompanyResearchResult) -> float:
    score = 0
    if res.website and res.website_result and res.website_result.reachable:
        if res.company_name and res.company_name.lower().split()[0] in (res.website_result.title or "").lower():
            score += 40
        else:
            score += 20
    if res.address:
        score += 20
    if res.phone:
        score += 20
    if res.email:
        score += 20
    return min(float(score), 100.0)


def research_company(company_name: str = "", website: str = "", progress_cb=None) -> CompanyResearchResult:
    result = CompanyResearchResult(search_term=company_name or website)

    def _progress(msg):
        if progress_cb:
            progress_cb(msg)

    # ── Step 1: DuckDuckGo lookup ──
    _progress("Searching company information...")
    query = f"{company_name} Ghana" if company_name else website
    dd = _duckduckgo_search(query)

    if dd.get("Heading"):
        result.company_name = dd["Heading"]
    else:
        result.company_name = company_name or website
    result.sources.append("DuckDuckGo")

    if dd.get("AbstractText"):
        result.description = dd["AbstractText"][:400]

    ddg_website = _extract_website_from_ddg(dd)
    if ddg_website and not website:
        website = ddg_website
        result.sources.append("DuckDuckGo Website")

    ddg_phone = _extract_phone_from_ddg(dd)
    if ddg_phone:
        result.phone = ddg_phone

    ddg_addr = _extract_address_from_ddg(dd)
    if ddg_addr:
        result.address = ddg_addr

    # ── Step 2: Resolve domain ──
    if website:
        result.website = website if website.startswith("http") else "https://" + website
        result.domain = _clean_domain(result.website)
    elif company_name:
        slug = re.sub(r"[^a-z0-9]", "", company_name.lower().replace("&", "and").replace(" ", ""))
        result.domain = slug + ".com"
        result.website = "https://www." + result.domain

    # ── Step 3: Verify website ──
    if result.website:
        _progress("Verifying website...")
        result.website_result = verify_website(result.website)
        if result.website_result.reachable:
            result.sources.append("Website")

    # ── Step 4: Crawl website ──
    if result.website and result.website_result and result.website_result.reachable:
        _progress("Crawling website for contacts...")
        result.crawl_result = crawl_website(result.website)
        if result.crawl_result.emails:
            result.email = result.crawl_result.emails[0]
        if result.crawl_result.phones and not result.phone:
            result.phone = result.crawl_result.phones[0]
        if result.crawl_result.social_links:
            result.social = result.crawl_result.social_links
        if result.crawl_result.address_hints and not result.address:
            result.address = result.crawl_result.address_hints[0]

    # ── Step 5: DNS audit ──
    if result.domain:
        _progress("Running DNS audit...")
        result.dns_result = run_dns_audit(result.domain)
        if result.dns_result.email_provider and result.dns_result.email_provider != "None":
            result.sources.append(f"DNS ({result.dns_result.email_provider})")

    # ── Step 6: Confidence score ──
    result.confidence_score = calculate_confidence(result)
    if result.confidence_score >= 90:
        result.confidence_label = "Excellent"
    elif result.confidence_score >= 80:
        result.confidence_label = "Good"
    elif result.confidence_score >= 70:
        result.confidence_label = "Review"
    else:
        result.confidence_label = "Low Confidence"

    return result

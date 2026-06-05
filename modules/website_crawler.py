import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
from typing import List, Set

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TechWokxBot/1.0)"}
TIMEOUT = 8
CRAWL_PATHS = ["/", "/about", "/contact", "/services", "/team", "/about-us", "/contact-us"]
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+?[\d\s\-().]{7,20})")
SOCIAL_RE = {
    "linkedin": re.compile(r"linkedin\.com/(?:company|in)/[\w-]+"),
    "twitter": re.compile(r"twitter\.com/[\w]+"),
    "facebook": re.compile(r"facebook\.com/[\w.]+"),
    "instagram": re.compile(r"instagram\.com/[\w.]+"),
}


@dataclass
class CrawlResult:
    base_url: str
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    social_links: dict = field(default_factory=dict)
    pages_crawled: List[str] = field(default_factory=list)
    has_contact_form: bool = False
    address_hints: List[str] = field(default_factory=list)


def _clean_phone(p: str) -> str:
    cleaned = re.sub(r"[\s\-().]", "", p).strip()
    if len(cleaned) >= 7:
        return cleaned
    return ""


def _fetch(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return ""


def crawl_website(base_url: str) -> CrawlResult:
    if not base_url.startswith("http"):
        base_url = "https://" + base_url
    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    result = CrawlResult(base_url=base_url)
    emails: Set[str] = set()
    phones: Set[str] = set()

    for path in CRAWL_PATHS:
        url = origin + path
        html = _fetch(url)
        if not html:
            continue
        result.pages_crawled.append(url)
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator=" ")

        # Emails
        found_emails = EMAIL_RE.findall(text)
        for e in found_emails:
            if not any(skip in e.lower() for skip in ["example", "test", "placeholder", ".png", ".jpg"]):
                emails.add(e.lower())

        # Phones
        for match in PHONE_RE.findall(text):
            cleaned = _clean_phone(match)
            if cleaned and len(cleaned) >= 7:
                phones.add(cleaned)

        # Social links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            for platform, pattern in SOCIAL_RE.items():
                if platform not in result.social_links and pattern.search(href):
                    result.social_links[platform] = href

        # Contact form
        if soup.find("form") and not result.has_contact_form:
            inputs = soup.find_all("input")
            if any(i.get("type") in ("email", "text") for i in inputs):
                result.has_contact_form = True

        # Address hints (look for Ghana addresses)
        addr_matches = re.findall(r"(?:Accra|Kumasi|Tema|Takoradi|Box|P\.O\.|Street|Avenue|Road|Lane|Close|Estate)[^<\n]{5,60}", text)
        result.address_hints.extend(addr_matches[:3])

    result.emails = sorted(emails)[:10]
    result.phones = sorted(phones, key=len, reverse=True)[:5]
    return result

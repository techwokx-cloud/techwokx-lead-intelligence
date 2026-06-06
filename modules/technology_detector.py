import requests
from dataclasses import dataclass, field
from typing import List

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TechWokxBot/1.0)"}

SIGNATURES = {
    "WordPress":         [("html", "wp-content"), ("html", "wp-includes"), ("html", "wordpress")],
    "Shopify":           [("html", "cdn.shopify.com"), ("header", "x-shopify")],
    "Wix":               [("html", "wix.com"), ("html", "wixstatic.com")],
    "Squarespace":       [("html", "squarespace.com"), ("html", "sqsp.net")],
    "Joomla":            [("html", "/components/com_"), ("meta", "joomla")],
    "Drupal":            [("header", "x-generator: drupal"), ("html", "drupal.js")],
    "Cloudflare":        [("header", "cf-ray"), ("header", "server: cloudflare")],
    "Google Analytics":  [("html", "google-analytics.com"), ("html", "gtag/js"), ("html", "UA-"), ("html", "G-")],
    "Meta Pixel":        [("html", "connect.facebook.net"), ("html", "fbq(")],
    "HubSpot":           [("html", "hs-scripts.com"), ("html", "hubspot")],
    "Mailchimp":         [("html", "mailchimp"), ("html", "list-manage.com")],
    "jQuery":            [("html", "jquery")],
    "Bootstrap":         [("html", "bootstrap")],
    "React":             [("html", "react"), ("html", "__REACT")],
    "Google Workspace":  [("mx", "google"), ("mx", "aspmx")],
    "Microsoft 365":     [("mx", "outlook"), ("mx", "protection.outlook")],
    "Zoho Mail":         [("mx", "zoho")],
    "cPanel Hosting":    [("mx", "secureserver"), ("header", "cpanel")],
    "Nginx":             [("header", "server: nginx")],
    "Apache":            [("header", "server: apache")],
}


@dataclass
class TechResult:
    detected: List[str] = field(default_factory=list)
    categories: dict = field(default_factory=dict)
    raw_headers: dict = field(default_factory=dict)


CATEGORIES = {
    "CMS": ["WordPress", "Shopify", "Wix", "Squarespace", "Joomla", "Drupal"],
    "CDN/Security": ["Cloudflare"],
    "Analytics": ["Google Analytics", "Meta Pixel", "HubSpot"],
    "Marketing": ["Mailchimp", "HubSpot"],
    "Email": ["Google Workspace", "Microsoft 365", "Zoho Mail", "cPanel Hosting"],
    "Framework": ["jQuery", "Bootstrap", "React"],
    "Server": ["Nginx", "Apache"],
}


def detect_technologies(url: str, mx_records: list = None) -> TechResult:
    result = TechResult()
    html = ""
    headers_lower = {}

    try:
        r = requests.get(url if url.startswith("http") else "https://" + url,
                         headers=HEADERS, timeout=8, allow_redirects=True)
        html = r.text.lower()
        headers_lower = {k.lower(): v.lower() for k, v in r.headers.items()}
        result.raw_headers = dict(r.headers)
    except Exception:
        pass

    mx_str = " ".join(mx_records or []).lower()
    detected = set()

    for tech, sigs in SIGNATURES.items():
        for source, pattern in sigs:
            if source == "html" and pattern in html:
                detected.add(tech)
            elif source == "header" and any(pattern in f"{k}: {v}" for k, v in headers_lower.items()):
                detected.add(tech)
            elif source == "mx" and pattern in mx_str:
                detected.add(tech)
            elif source == "meta" and f'name="{pattern}"' in html:
                detected.add(tech)

    result.detected = sorted(detected)
    for cat, techs in CATEGORIES.items():
        found = [t for t in techs if t in detected]
        if found:
            result.categories[cat] = found

    return result

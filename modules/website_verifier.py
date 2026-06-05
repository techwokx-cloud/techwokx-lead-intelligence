import requests
import ssl
import socket
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TechWokxBot/1.0)"}
TIMEOUT = 8


@dataclass
class SSLInfo:
    valid: bool = False
    expiry: Optional[str] = None
    issuer: str = ""
    days_remaining: int = 0
    error: str = ""


@dataclass
class WebsiteResult:
    url: str = ""
    reachable: bool = False
    https: bool = False
    ssl: SSLInfo = None
    status_code: int = 0
    title: str = ""
    redirects_to_https: bool = False
    response_time_ms: int = 0
    error: str = ""


def get_ssl_info(domain: str) -> SSLInfo:
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.create_connection((domain, 443), timeout=6), server_hostname=domain) as s:
            cert = s.getpeercert()
        expiry_str = cert.get("notAfter", "")
        expiry_dt = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z") if expiry_str else None
        days = (expiry_dt - datetime.utcnow()).days if expiry_dt else 0
        issuer_raw = dict(x[0] for x in cert.get("issuer", []))
        issuer = issuer_raw.get("organizationName", issuer_raw.get("commonName", "Unknown"))
        return SSLInfo(valid=True, expiry=expiry_str, issuer=issuer, days_remaining=days)
    except ssl.SSLError as e:
        return SSLInfo(valid=False, error=str(e))
    except Exception as e:
        return SSLInfo(valid=False, error=str(e))


def extract_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip()[:120] if m else ""


def verify_website(url: str) -> WebsiteResult:
    if not url:
        return WebsiteResult(error="No URL provided")
    if not url.startswith("http"):
        url = "https://" + url
    domain = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    result = WebsiteResult(url=url)

    try:
        import time
        t0 = time.time()
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        result.response_time_ms = int((time.time() - t0) * 1000)
        result.reachable = True
        result.status_code = r.status_code
        result.https = r.url.startswith("https://")
        result.title = extract_title(r.text)
        result.redirects_to_https = r.url.startswith("https://") and url.startswith("http://")
    except requests.exceptions.SSLError:
        result.https = False
        result.ssl = SSLInfo(valid=False, error="SSL error")
        try:
            r2 = requests.get(url.replace("https://", "http://"), headers=HEADERS, timeout=TIMEOUT)
            result.reachable = True
            result.status_code = r2.status_code
            result.title = extract_title(r2.text)
        except Exception as e2:
            result.error = str(e2)
    except Exception as e:
        result.error = str(e)[:120]

    if result.https and not result.ssl:
        result.ssl = get_ssl_info(domain)

    if not result.ssl:
        result.ssl = SSLInfo(valid=False, error="HTTP only")

    return result

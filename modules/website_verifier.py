import requests
import ssl
import socket
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SSLInfo:
    valid: bool = False
    issuer: str = ""
    expiry_date: str = ""
    error: str = ""

@dataclass
class WebsiteResult:
    url: str = ""
    reachable: bool = False
    https: bool = False
    response_time_ms: float = 0
    title: str = ""
    ssl: SSLInfo = None

def verify_website(url: str) -> WebsiteResult:
    """Verify if a website is reachable and get basic info"""
    result = WebsiteResult(url=url)
    
    # Check if URL uses HTTPS
    result.https = url.startswith("https://")
    
    try:
        # Make request with timeout
        start_time = datetime.now()
        response = requests.get(url, timeout=10, allow_redirects=True, 
                               headers={"User-Agent": "Mozilla/5.0"})
        end_time = datetime.now()
        
        result.reachable = response.status_code == 200
        result.response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        if result.reachable:
            # Extract title from HTML
            import re
            title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
            if title_match:
                result.title = title_match.group(1).strip()
            
            # Check SSL certificate
            result.ssl = check_ssl_certificate(url)
    
    except requests.RequestException as e:
        result.reachable = False
        result.title = f"Error: {str(e)[:50]}"
    
    return result

def check_ssl_certificate(url: str) -> SSLInfo:
    """Check SSL certificate validity"""
    ssl_info = SSLInfo()
    
    # Extract hostname from URL
    hostname = url.replace("https://", "").replace("http://", "").split("/")[0]
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                ssl_info.valid = True
                ssl_info.issuer = dict(x[0] for x in cert['issuer'])['organizationName']
                ssl_info.expiry_date = cert['notAfter']
                
    except Exception as e:
        ssl_info.valid = False
        ssl_info.error = str(e)
    
    return ssl_info

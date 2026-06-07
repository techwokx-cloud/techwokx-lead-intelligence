from dataclasses import dataclass, field
from typing import List, Dict
import re

@dataclass
class TechnologyResult:
    detected: List[str] = field(default_factory=list)
    categories: Dict[str, List[str]] = field(default_factory=dict)

def detect_technologies(website_url: str, mx_records: List[str] = None) -> TechnologyResult:
    """Detect technologies used by a company based on website and email"""
    result = TechnologyResult()
    
    # This is a simplified version - in production, you'd use Wappalyzer or similar
    # For now, we'll return some common patterns
    
    if website_url:
        # Check for common CMS patterns
        if "wordpress" in website_url.lower():
            result.detected.append("WordPress")
            result.categories.setdefault("CMS", []).append("WordPress")
        
        if "shopify" in website_url.lower():
            result.detected.append("Shopify")
            result.categories.setdefault("E-commerce", []).append("Shopify")
        
        # Common email providers from MX records
        if mx_records:
            for mx in mx_records:
                mx_lower = mx.lower()
                if "google" in mx_lower or "gmail" in mx_lower:
                    result.detected.append("Google Workspace")
                    result.categories.setdefault("Email", []).append("Google Workspace")
                elif "microsoft" in mx_lower or "outlook" in mx_lower or "office365" in mx_lower:
                    result.detected.append("Microsoft 365")
                    result.categories.setdefault("Email", []).append("Microsoft 365")
                elif "zoho" in mx_lower:
                    result.detected.append("Zoho")
                    result.categories.setdefault("Email", []).append("Zoho")
    
    # Remove duplicates while preserving order
    result.detected = list(dict.fromkeys(result.detected))
    
    return result

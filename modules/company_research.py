# modules/company_research.py
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def search_google_serp(api_key, business_name, location="Ghana"):
    """Search Google SERP for business information"""
    if not api_key:
        return None
    
    try:
        url = "https://serpapi.com/search"
        params = {
            "api_key": api_key,
            "q": f"{business_name} {location}",
            "location": location,
            "engine": "google"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        result = {
            "name": business_name,
            "website": None,
            "description": None,
            "address": None,
            "phone": None,
            "social_links": [],
            "people_also_search": []
        }
        
        # Get knowledge graph
        if "knowledge_graph" in data:
            kg = data["knowledge_graph"]
            result["name"] = kg.get("title", result["name"])
            result["website"] = kg.get("website", "")
            result["description"] = kg.get("description", "")
            result["address"] = kg.get("address", "")
            result["phone"] = kg.get("phone", "")
            
            # Get social profiles
            if "profile" in kg:
                for profile in kg.get("profile", []):
                    if isinstance(profile, dict):
                        result["social_links"].append(profile.get("link", ""))
                    elif isinstance(profile, str):
                        result["social_links"].append(profile)
        
        # Get organic results for additional info
        if "organic_results" in data:
            for org in data["organic_results"][:3]:
                if org.get("snippet") and not result["description"]:
                    result["description"] = org.get("snippet")
        
        # Get people also search for
        if "related_queries" in data:
            for query in data["related_queries"].get("top", [])[:5]:
                result["people_also_search"].append(query.get("query"))
        
        return result
    except Exception as e:
        return None

def find_contact_person(website):
    """Try to find contact person/management from website"""
    if not website:
        return None
    
    try:
        if not website.startswith("http"):
            website = "https://" + website
        
        response = requests.get(website, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for management team, about page, team members
        contacts = []
        
        # Find all text
        text = soup.get_text().lower()
        
        # Common job titles to look for
        titles = ['ceo', 'managing director', 'general manager', 'founder', 
                  'director', 'head of', 'manager', 'president', 'owner']
        
        # Find emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, response.text)
        business_emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'test', 'noreply'])]
        
        # Try to find team/about page link
        about_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if 'about' in href or 'team' in href or 'management' in href or 'leadership' in href:
                full_url = urljoin(website, link.get('href'))
                about_links.append(full_url)
        
        # If about page exists, scrape it
        if about_links:
            try:
                about_response = requests.get(about_links[0], timeout=10)
                about_soup = BeautifulSoup(about_response.text, 'html.parser')
                about_text = about_soup.get_text().lower()
                
                # Look for names with titles
                for title in titles:
                    pattern = rf'([A-Z][a-z]+ [A-Z][a-z]+).*?{title}'
                    matches = re.findall(pattern, about_response.text, re.IGNORECASE)
                    for match in matches[:3]:
                        contacts.append({"name": match, "title": title.upper(), "source": "About Page"})
            except:
                pass
        
        # Look for email signatures
        for email in business_emails[:3]:
            contacts.append({"email": email, "title": "Contact Email", "source": "Website"})
        
        return {
            "contacts": contacts[:5],
            "business_emails": business_emails[:3],
            "about_page": about_links[0] if about_links else None
        }
    except Exception as e:
        return None

def check_website_status(url):
    """Check if website is accessible"""
    if not url:
        return {"reachable": False, "error": "No website"}
    
    try:
        if not url.startswith("http"):
            url = "https://" + url
        
        response = requests.get(url, timeout=10, verify=True)
        return {
            "reachable": response.status_code == 200,
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds() * 1000,
            "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
        }
    except Exception as e:
        return {"reachable": False, "error": str(e)[:50]}

def analyze_with_ai(api_key, company_data):
    """Analyze company using OpenAI"""
    if not api_key:
        return None
    
    try:
        prompt = f"""Analyze this company and provide actionable insights:

Company: {company_data.get('name')}
Website: {company_data.get('website', 'N/A')}
Industry: {company_data.get('industry', 'Unknown')}

Provide a brief analysis (max 150 words):
1. What IT/email security services they likely need
2. Suggested initial outreach approach
3. Estimated budget range for services"""

        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return None
    except Exception as e:
        return None

def deep_research_company(company_name, serp_api_key=None, openai_api_key=None):
    """Perform deep research using Google Search (SERP API)"""
    
    result = {
        "name": company_name,
        "website": None,
        "email": None,
        "phone": None,
        "address": None,
        "description": None,
        "social_links": [],
        "contacts": [],
        "business_emails": [],
        "website_status": None,
        "ai_insights": None,
        "people_also_search": [],
        "lead_score": 0,
        "recommendations": [],
        "sources": []
    }
    
    # Step 1: Google Search via SERP API
    if serp_api_key:
        serp_data = search_google_serp(serp_api_key, company_name)
        if serp_data:
            result["name"] = serp_data.get("name", result["name"])
            result["website"] = serp_data.get("website")
            result["address"] = serp_data.get("address")
            result["phone"] = serp_data.get("phone")
            result["description"] = serp_data.get("description")
            result["social_links"] = serp_data.get("social_links", [])
            result["people_also_search"] = serp_data.get("people_also_search", [])
            result["sources"].append("Google Search")
    
    # Step 2: Check website status
    if result["website"]:
        result["website_status"] = check_website_status(result["website"])
        
        # Step 3: Find contact person from website
        contact_data = find_contact_person(result["website"])
        if contact_data:
            result["contacts"] = contact_data.get("contacts", [])
            result["business_emails"] = contact_data.get("business_emails", [])
            if result["business_emails"]:
                result["email"] = result["business_emails"][0]
                result["sources"].append("Website Scraping")
    
    # Step 4: AI Analysis
    if openai_api_key:
        ai_insights = analyze_with_ai(openai_api_key, result)
        if ai_insights:
            result["ai_insights"] = ai_insights
            result["sources"].append("AI Analysis")
    
    # Calculate lead score
    score = 0
    if result["website"]:
        score += 20
        if result["website_status"] and result["website_status"]["reachable"]:
            score += 15
    if result["address"]:
        score += 10
    if result["phone"]:
        score += 10
    if result["email"]:
        score += 15
    if result["contacts"]:
        score += 15
    if result["description"]:
        score += 5
    if result["social_links"]:
        score += 5
    if result["ai_insights"]:
        score += 5
    result["lead_score"] = min(score, 100)
    
    # Generate recommendations
    recs = []
    if not result["website"]:
        recs.append("🌐 No website found - Professional website needed")
    elif result["website_status"] and not result["website_status"]["reachable"]:
        recs.append("🔧 Website is DOWN - Emergency IT support required")
    if not result["email"]:
        recs.append("📧 No business email found - Setup Google Workspace/Microsoft 365")
    if not result["contacts"]:
        recs.append("👤 Find decision maker - LinkedIn search recommended")
    if result["phone"]:
        recs.append(f"📞 Call {result['phone']} - Ask for IT decision maker")
    if len(recs) < 3:
        recs.append("📊 Schedule free IT consultation")
    result["recommendations"] = recs[:5]
    
    return result

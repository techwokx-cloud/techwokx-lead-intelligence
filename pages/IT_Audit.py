# pages/Website_Audit.py
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from dotenv import load_dotenv
import requests
import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse

load_dotenv()

# Try to import theme safely
try:
    from modules.theme import THEME_CSS
    st.markdown(THEME_CSS, unsafe_allow_html=True)
except Exception:
    pass

st.set_page_config(
    page_title="Website & SSL Audit",
    page_icon="🌐",
    layout="wide"
)

st.markdown("# 🌐 Website & SSL Audit")
st.caption("Comprehensive security and performance audit for any website")
st.markdown("---")

# Input section
col1, col2 = st.columns([3, 1])
with col1:
    website_url = st.text_input(
        "Website URL",
        placeholder="https://example.com",
        help="Enter full URL including http:// or https://"
    )
with col2:
    run_audit = st.button("🔍 Run Audit", type="primary", use_container_width=True)

# Function to check SSL certificate
def check_ssl_certificate(hostname):
    """Check SSL certificate details"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Extract certificate info
                subject = dict(x[0] for x in cert['subject'])
                issuer = dict(x[0] for x in cert['issuer'])
                
                # Get expiry date
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (expiry_date - datetime.now()).days
                
                return {
                    'valid': True,
                    'issuer': issuer.get('organizationName', 'Unknown'),
                    'subject': subject.get('commonName', 'Unknown'),
                    'expiry_date': expiry_date,
                    'days_left': days_left,
                    'serial_number': cert.get('serialNumber', 'N/A'),
                    'version': cert.get('version', 'N/A')
                }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'issuer': 'N/A',
            'subject': 'N/A',
            'days_left': 0
        }

# Function to check website headers
def check_security_headers(url):
    """Check security headers"""
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        headers = response.headers
        
        security_checks = {
            'Strict-Transport-Security (HSTS)': headers.get('Strict-Transport-Security', 'Not Set'),
            'Content-Security-Policy': headers.get('Content-Security-Policy', 'Not Set'),
            'X-Frame-Options': headers.get('X-Frame-Options', 'Not Set'),
            'X-Content-Type-Options': headers.get('X-Content-Type-Options', 'Not Set'),
            'X-XSS-Protection': headers.get('X-XSS-Protection', 'Not Set'),
            'Referrer-Policy': headers.get('Referrer-Policy', 'Not Set'),
        }
        
        return {
            'status_code': response.status_code,
            'headers': security_checks,
            'server': headers.get('Server', 'Unknown'),
            'powered_by': headers.get('X-Powered-By', 'Not Disclosed')
        }
    except Exception as e:
        return {
            'status_code': 0,
            'error': str(e),
            'headers': {}
        }

# Function to check DNS records
def check_dns_records(domain):
    """Check DNS records"""
    import dns.resolver
    
    records = {}
    
    # Check A record
    try:
        a_records = dns.resolver.resolve(domain, 'A')
        records['A'] = [str(r) for r in a_records]
    except:
        records['A'] = ['Not found']
    
    # Check AAAA record (IPv6)
    try:
        aaaa_records = dns.resolver.resolve(domain, 'AAAA')
        records['AAAA'] = [str(r) for r in aaaa_records]
    except:
        records['AAAA'] = ['Not found']
    
    # Check MX records
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        records['MX'] = [f"{r.preference} {str(r.exchange).rstrip('.')}" for r in mx_records]
    except:
        records['MX'] = ['Not found']
    
    # Check TXT records
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        records['TXT'] = [str(r).strip('"')[:100] for r in txt_records][:3]
    except:
        records['TXT'] = ['Not found']
    
    return records

# Run audit
if run_audit and website_url:
    if not website_url.startswith(('http://', 'https://')):
        website_url = 'https://' + website_url
    
    # Parse domain
    parsed = urlparse(website_url)
    domain = parsed.netloc or parsed.path
    domain = domain.split(':')[0]  # Remove port if present
    
    with st.spinner(f"Auditing {domain}..."):
        # Create tabs for different audit sections
        tab1, tab2, tab3, tab4 = st.tabs(["🔒 SSL Certificate", "🛡️ Security Headers", "🌐 DNS Records", "📊 Performance"])
        
        # Tab 1: SSL Certificate
        with tab1:
            st.markdown("### SSL/TLS Certificate Analysis")
            
            if domain:
                ssl_info = check_ssl_certificate(domain)
                
                if ssl_info['valid']:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Status", "✅ Valid", delta="Secure")
                        st.metric("Days Until Expiry", ssl_info['days_left'], 
                                 delta="⚠️ Expiring soon" if ssl_info['days_left'] < 30 else "Good")
                    
                    with col2:
                        st.metric("Issuer", ssl_info['issuer'][:30])
                        st.metric("Common Name", ssl_info['subject'])
                    
                    with col3:
                        st.metric("Expiry Date", ssl_info['expiry_date'].strftime('%Y-%m-%d'))
                        st.metric("SSL Version", ssl_info['version'])
                    
                    # Warning if expiring soon
                    if ssl_info['days_left'] < 30:
                        st.warning(f"⚠️ SSL certificate expires in {ssl_info['days_left']} days! Renew immediately.")
                    elif ssl_info['days_left'] < 90:
                        st.info(f"ℹ️ SSL certificate expires in {ssl_info['days_left']} days. Plan for renewal.")
                    else:
                        st.success(f"✅ SSL certificate is valid for {ssl_info['days_left']} days")
                else:
                    st.error(f"❌ SSL Certificate Error: {ssl_info.get('error', 'Unknown error')}")
                    st.info("The website either doesn't have SSL or the certificate is invalid/insecure.")
        
        # Tab 2: Security Headers
        with tab2:
            st.markdown("### Security Headers Analysis")
            
            headers_info = check_security_headers(website_url)
            
            if headers_info.get('status_code') == 200:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("HTTP Status", f"{headers_info['status_code']} ✅")
                    st.metric("Server", headers_info.get('server', 'Unknown'))
                with col2:
                    st.metric("Powered By", headers_info.get('powered_by', 'Not disclosed'))
                
                st.markdown("#### Security Headers Status")
                
                for header, value in headers_info.get('headers', {}).items():
                    if value != 'Not Set':
                        st.success(f"✅ **{header}**: {value[:100]}")
                    else:
                        st.error(f"❌ **{header}**: {value}")
                
                st.info("""
                **Security Headers Explained:**
                - **HSTS**: Enforces HTTPS connection
                - **CSP**: Prevents XSS and data injection attacks
                - **X-Frame-Options**: Prevents clickjacking
                - **X-Content-Type-Options**: Prevents MIME type sniffing
                """)
            else:
                st.error(f"Failed to reach website. Status code: {headers_info.get('status_code', 'Unknown')}")
        
        # Tab 3: DNS Records
        with tab3:
            st.markdown("### DNS Records Analysis")
            
            dns_records = check_dns_records(domain)
            
            for record_type, records in dns_records.items():
                with st.expander(f"{record_type} Records"):
                    for record in records:
                        st.code(record)
            
            st.info("""
            **DNS Records Explained:**
            - **A Record**: Maps domain to IPv4 address
            - **AAAA Record**: Maps domain to IPv6 address
            - **MX Record**: Mail exchange servers for email
            - **TXT Record**: Text records (SPF, DKIM, etc.)
            """)
        
        # Tab 4: Performance
        with tab4:
            st.markdown("### Performance Analysis")
            
            # Check response time
            try:
                start_time = datetime.now()
                response = requests.get(website_url, timeout=10)
                end_time = datetime.now()
                
                response_time = (end_time - start_time).total_seconds() * 1000
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Response Time", f"{response_time:.0f}ms")
                    if response_time < 500:
                        st.success("✅ Excellent")
                    elif response_time < 1000:
                        st.warning("⚠️ Acceptable")
                    else:
                        st.error("❌ Slow")
                
                with col2:
                    st.metric("Content Size", f"{len(response.content):,} bytes")
                
                with col3:
                    st.metric("Final URL", response.url[:50] + "...")
                
                # Recommendations
                st.markdown("### Recommendations")
                recommendations = []
                
                if not ssl_info.get('valid', False):
                    recommendations.append("🔒 Install a valid SSL certificate")
                
                if response_time > 1000:
                    recommendations.append("⚡ Optimize website loading speed")
                
                for header, value in headers_info.get('headers', {}).items():
                    if value == 'Not Set':
                        if header == 'Strict-Transport-Security (HSTS)':
                            recommendations.append(f"🛡️ Enable {header} header")
                        elif header == 'Content-Security-Policy':
                            recommendations.append(f"🛡️ Implement {header} for better security")
                
                if recommendations:
                    for rec in recommendations:
                        st.warning(rec)
                else:
                    st.success("✅ No critical issues found!")
                    
            except Exception as e:
                st.error(f"Performance check failed: {str(e)}")
        
        # Overall Score
        st.markdown("---")
        st.markdown("### Overall Security Score")
        
        # Calculate score
        score = 0
        max_score = 100
        
        # SSL check (30 points)
        if ssl_info.get('valid', False):
            score += 30
        
        # Security headers (40 points)
        headers_set = sum(1 for v in headers_info.get('headers', {}).values() if v != 'Not Set')
        score += min(headers_set * 8, 40)
        
        # Response time (30 points)
        if 'response_time' in locals():
            if response_time < 500:
                score += 30
            elif response_time < 1000:
                score += 15
        
        # Display score
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if score >= 80:
                st.success(f"### Score: {score}/100 - Excellent! 🎉")
            elif score >= 60:
                st.warning(f"### Score: {score}/100 - Good, but needs improvement")
            else:
                st.error(f"### Score: {score}/100 - Critical issues found!")
            
            # Progress bar
            st.progress(score / 100)
        
        # Export report option
        if st.button("📥 Export Audit Report", use_container_width=True):
            report = f"""
WEBSITE AUDIT REPORT
====================
URL: {website_url}
Domain: {domain}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SSL CERTIFICATE
--------------
Status: {'Valid' if ssl_info.get('valid') else 'Invalid'}
Issuer: {ssl_info.get('issuer', 'N/A')}
Expiry: {ssl_info.get('expiry_date', 'N/A')}
Days Left: {ssl_info.get('days_left', 0)}

SECURITY HEADERS
---------------
{chr(10).join([f'{k}: {v}' for k, v in headers_info.get('headers', {}).items()])}

PERFORMANCE
----------
Response Time: {response_time:.0f}ms
Status Code: {headers_info.get('status_code')}

OVERALL SCORE: {score}/100
            """
            st.download_button("Download Report", report, f"audit_{domain}.txt", "text/plain")

elif run_audit and not website_url:
    st.warning("Please enter a website URL")

# Empty state
if not run_audit:
    st.info("👆 Enter a website URL above and click 'Run Audit' to begin")
    
    with st.expander("What gets audited?"):
        st.markdown("""
        **The audit checks:**
        - ✅ SSL/TLS certificate validity and details
        - ✅ Security headers (HSTS, CSP, X-Frame-Options, etc.)
        - ✅ DNS records (A, AAAA, MX, TXT)
        - ✅ Response time and performance
        - ✅ Security recommendations
        
        **Perfect for:**
        - Security assessments
        - Compliance checks
        - Pre-sales audits
        - Competitor analysis
        """)

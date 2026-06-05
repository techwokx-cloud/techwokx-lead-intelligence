import os
import io
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

TECHWOKX_ORANGE = colors.HexColor("#EA580C")
TECHWOKX_DARK = colors.HexColor("#0D1526")
TECHWOKX_BLUE = colors.HexColor("#1E3A5F")
AUDIT_URL = "https://techwokx.online/#audit"


def generate_qr_code() -> io.BytesIO:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=2)
    qr.add_data(AUDIT_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def generate_cold_email(company: str, contact: str, findings: list, risks: list, lead_score: int) -> dict:
    risk_word = "CRITICAL" if lead_score >= 90 else "HIGH" if lead_score >= 70 else "MEDIUM"
    emoji = "\U0001f534" if lead_score >= 90 else "\U0001f7e0" if lead_score >= 70 else "\U0001f7e1"
    subject = f"{emoji} {company}: Free 5-Step Email Security Audit \u2014 {risk_word} Risk Detected"

    findings_text = "\n".join(f"\u2022 {f}" for f in findings[:5])
    risks_text = "\n".join(f"\u2022 {r}" for r in risks[:4])

    body = f"""Re: Free 5-Step Email Security Audit for {company}

Dear {contact},

We are interested in doing business with {company}, so we took the time to research your current setup including your website, domain, and email infrastructure.

Here\u2019s what we discovered:

{emoji} Risk Assessment for {company}: {risk_word}

What We Found:
{findings_text}

Please note: This assessment was done outside {company}\u2019s network, so we may not have captured every detail. That is why we are sending this letter \u2014 to formally introduce TechWokx to {company} and find out if there is an opportunity to help.

What This Means For {company}:
{risks_text}

What We Can Do For You:
\u2713 Protect {company} from email impersonation and fraud
\u2713 Ensure all emails reach your clients\u2019 inboxes
\u2713 Stop business emails from landing in spam folders
\u2713 Secure your website so visitors trust your business
\u2713 Free Professional Email Signature for one staff member

\U0001f4de Next Step:
Take our FREE 5-Step Email Risk Audit:
1. Go to techwokx.online/#audit
2. Receive an instant personalised risk score for {company}

About TechWokx:
We provide professional IT support and email solutions for businesses in Ghana.
\u2022 Business Email Health Fix \u2014 Stop emails going to spam, protect from impersonation
\u2022 Monthly IT Retainer \u2014 On-call support for devices, networks, software
\u2022 IT Infrastructure Audit \u2014 Full review with clear report and action plan
\u2022 Process Automation \u2014 Eliminate repetitive tasks

We work on a \u201cdiagnose before prescribe\u201d basis.

Best regards,

George Jabley
TechWokx IT Solutions
hello@techwokx.online | techwokx.online
+233 264 375 628 | WhatsApp: +233 555 087 407"""

    return {"subject": subject, "body": body}


def generate_whatsapp_message(company: str, findings: list, lead_score: int) -> str:
    risk_word = "CRITICAL" if lead_score >= 90 else "HIGH" if lead_score >= 70 else "MEDIUM"
    top_issues = findings[:2] if findings else ["email security issues", "domain vulnerability"]
    issues_str = " and ".join(top_issues)
    return f"""Hi, I\u2019m George from TechWokx Ghana \ud83d\udc4b

We recently scanned *{company}*\u2019s email and web infrastructure and found *{risk_word}* risk issues including {issues_str}.

We\u2019d love to help fix this for free consultation. Can we have a 10-minute call this week?

\ud83d\udd17 Full risk report: techwokx.online/#audit
\ud83d\udce7 hello@techwokx.online"""


def generate_pdf_proposal(company_data: dict, findings: list, risks: list, recommendations: list, ai_summary: str = "") -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm, leftMargin=20*mm, rightMargin=20*mm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("title", parent=styles["Heading1"], fontSize=22, textColor=TECHWOKX_ORANGE, spaceAfter=4)
    h2_style = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, textColor=TECHWOKX_BLUE, spaceBefore=12, spaceAfter=4)
    body_style = ParagraphStyle("body", parent=styles["Normal"], fontSize=10, leading=15, spaceAfter=4)
    muted_style = ParagraphStyle("muted", parent=styles["Normal"], fontSize=9, textColor=colors.grey)

    story = []
    today = datetime.now().strftime("%d %B %Y")
    company = company_data.get("company_name", "Unknown Company")
    lead_score = company_data.get("lead_score", 0)
    risk_label = "CRITICAL" if lead_score >= 90 else "HIGH" if lead_score >= 70 else "MEDIUM"
    risk_color = colors.red if lead_score >= 90 else TECHWOKX_ORANGE if lead_score >= 70 else colors.green

    # Header
    story.append(Paragraph("TechWokx IT Solutions", title_style))
    story.append(Paragraph(f"IT Infrastructure & Email Security Report", h2_style))
    story.append(HRFlowable(width="100%", color=TECHWOKX_ORANGE, thickness=2))
    story.append(Spacer(1, 6))

    # Company + date table
    meta = [
        ["Prepared for:", company],
        ["Date:", today],
        ["Risk Level:", risk_label],
        ["Lead Score:", f"{lead_score}/100"],
    ]
    t = Table(meta, colWidths=[45*mm, 130*mm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("TEXTCOLOR", (1, 2), (1, 2), risk_color),
        ("FONTNAME", (1, 2), (1, 2), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    # AI Summary
    if ai_summary:
        story.append(Paragraph("Executive Summary", h2_style))
        story.append(Paragraph(ai_summary, body_style))

    # Findings
    story.append(Paragraph("What We Found", h2_style))
    for f in findings:
        icon = "\u2717" if any(bad in f.lower() for bad in ["no ", "fail", "down", "invalid"]) else "\u26a0"
        story.append(Paragraph(f"{icon} {f}", body_style))
    story.append(Spacer(1, 6))

    # Risks
    story.append(Paragraph("Business Risks", h2_style))
    for r in risks:
        story.append(Paragraph(f"\u2022 {r}", body_style))
    story.append(Spacer(1, 6))

    # Recommendations
    story.append(Paragraph("What TechWokx Can Do For You", h2_style))
    for rec in recommendations:
        story.append(Paragraph(f"\u2713 {rec}", body_style))
    story.append(Spacer(1, 10))

    # QR Code + CTA
    story.append(HRFlowable(width="100%", color=TECHWOKX_ORANGE, thickness=1))
    story.append(Spacer(1, 6))
    try:
        qr_buf = generate_qr_code()
        qr_img = Image(qr_buf, width=30*mm, height=30*mm)
        cta_data = [[qr_img, Paragraph(f"Take our FREE 5-Step Email Risk Audit\n\nScan the QR code or visit:\ntechwokx.online/#audit\n\nhello@techwokx.online | +233 264 375 628", body_style)]]
        cta_table = Table(cta_data, colWidths=[35*mm, 140*mm])
        story.append(cta_table)
    except Exception:
        story.append(Paragraph("Take our FREE audit at techwokx.online/#audit", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("George Jabley | TechWokx IT Solutions | hello@techwokx.online | techwokx.online", muted_style))

    doc.build(story)
    return buf.getvalue()

# TechWokx Lead Intelligence Engine v2

**Automated company research · DNS audit · AI analysis · Proposal generation · CRM**

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/techwokx-cloud/techwokx-lead-intelligence
cd techwokx-lead-intelligence
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 3. Run
streamlit run app.py
```

---

## Project Structure

```
techwokx-lead-intelligence/
├── app.py                        # Main entry point
├── pages/
│   ├── Dashboard.py              # KPIs and charts
│   ├── Company_Research.py       # Research + full audit
│   ├── IT_Audit.py               # Standalone DNS/SSL audit
│   ├── Lead_Intelligence.py      # AI analysis
│   ├── Proposal_Generator.py     # Email, WhatsApp, PDF
│   ├── CRM.py                    # Pipeline management
│   └── Settings.py               # API keys and config
├── modules/
│   ├── database.py               # SQLAlchemy models
│   ├── company_research.py       # DuckDuckGo + crawl + DNS
│   ├── website_verifier.py       # HTTP + SSL check
│   ├── website_crawler.py        # Contact extraction
│   ├── dns_audit.py              # MX, SPF, DMARC, DKIM, BIMI
│   ├── lead_scoring.py           # Rule-based scoring
│   ├── ai_analysis.py            # Claude / OpenAI analysis
│   ├── proposal_generator.py     # Email + WhatsApp + PDF
│   └── crm.py                    # CRM operations
├── data/
│   ├── leads.db                  # SQLite database (auto-created)
│   └── exports/
├── requirements.txt
├── .env.example
└── README.md
```

---

## Features

| Feature | Description |
|---|---|
| Company Research | DuckDuckGo lookup + website crawl + contact extraction |
| DNS Audit | MX, SPF, DKIM, DMARC, MTA-STS, BIMI checks |
| SSL Audit | Certificate validity, expiry, issuer |
| Lead Scoring | Rule-based 0–100 score (Hot/Warm/Cold) |
| AI Analysis | Claude or OpenAI — risks, opportunities, recommendations |
| Cold Email | Personalised outreach letter with company name |
| WhatsApp | Short WhatsApp pitch with deep link |
| PDF Proposal | Branded proposal with QR code (ReportLab) |
| CRM | Table + Kanban board, notes, follow-up dates |
| CSV Export | Export all leads to CSV |

---

## Lead Scoring Rules

| Issue | Points |
|---|---|
| Website down | +25 |
| No DMARC | +20 |
| No SPF | +20 |
| No SSL | +20 |
| No business email | +20 |
| No MX records | +15 |
| No DKIM | +10 |
| Poor overall security | +15 |

**90+ = Hot | 70–89 = Warm | <70 = Cold**

---

## Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_MAPS_API_KEY=AIza...
SERP_API_KEY=...
DB_PATH=data/leads.db
```

---

## Deployment (Streamlit Cloud)

1. Push to GitHub
2. Go to share.streamlit.io
3. Connect your repo
4. Add secrets in Streamlit Cloud settings (same as .env keys)
5. Deploy

---

**George Jabley | TechWokx IT Solutions**
**hello@techwokx.online | techwokx.online**

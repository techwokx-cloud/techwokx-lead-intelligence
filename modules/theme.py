THEME_CSS = """
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #060d1a !important;
    color: #e2e8f0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0a1628 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    min-width: 220px !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.06) !important; }
.sidebar-logo {
    padding: 1.25rem 1rem 0.5rem;
    font-size: 1rem;
    font-weight: 700;
    color: #EA580C !important;
    letter-spacing: -0.02em;
}
.sidebar-section {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #334155 !important;
    padding: 0.85rem 1rem 0.25rem;
}
.nav-item {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.55rem 1rem;
    border-radius: 0;
    font-size: 0.85rem;
    color: #64748b !important;
    cursor: pointer;
    transition: all 0.15s;
    border-left: 2px solid transparent;
    text-decoration: none;
}
.nav-item:hover { background: rgba(234,88,12,0.06); color: #e2e8f0 !important; }
.nav-item.active { color: #EA580C !important; border-left-color: #EA580C; background: rgba(234,88,12,0.08); }

/* ── KPI Cards ── */
.kpi-card {
    background: #0d1a2e;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #EA580C, #f97316);
}
.kpi-label { font-size: 0.72rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.5rem; }
.kpi-value { font-size: 2rem; font-weight: 700; color: #f1f5f9; line-height: 1; }
.kpi-sub { font-size: 0.75rem; color: #475569; margin-top: 0.4rem; }
.kpi-icon { position: absolute; right: 1.25rem; top: 1.25rem; font-size: 1.5rem; opacity: 0.3; }

/* ── Data Cards ── */
.data-card {
    background: #0d1a2e;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
}
.data-card h4 { font-size: 0.82rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; }

/* ── Score Ring ── */
.score-ring {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 90px; height: 90px;
    border-radius: 50%;
    border: 4px solid;
    font-weight: 700;
}
.score-hot  { border-color: #ef4444; color: #ef4444; }
.score-warm { border-color: #f97316; color: #f97316; }
.score-good { border-color: #22c55e; color: #22c55e; }

/* ── Badges ── */
.badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; font-weight: 700; }
.badge-hot    { background: rgba(239,68,68,0.15);   color: #f87171; }
.badge-warm   { background: rgba(249,115,22,0.15);  color: #fb923c; }
.badge-cold   { background: rgba(96,165,250,0.15);  color: #60a5fa; }
.badge-pass   { background: rgba(34,197,94,0.15);   color: #4ade80; }
.badge-fail   { background: rgba(239,68,68,0.15);   color: #f87171; }
.badge-warn   { background: rgba(234,179,8,0.15);   color: #fbbf24; }
.badge-info   { background: rgba(99,102,241,0.15);  color: #a5b4fc; }

/* ── Pipeline Kanban ── */
.kanban-col {
    background: #0a1628;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 0.75rem;
    min-height: 180px;
}
.kanban-header {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #475569;
    margin-bottom: 0.65rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.kanban-card {
    background: #0d1a2e;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 7px;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    font-size: 0.82rem;
}
.kanban-card-name { font-weight: 600; color: #e2e8f0; margin-bottom: 0.25rem; }
.kanban-card-meta { font-size: 0.72rem; color: #475569; }

/* ── Activity Feed ── */
.activity-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.82rem;
}
.activity-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #EA580C;
    margin-top: 4px;
    flex-shrink: 0;
}
.activity-text { color: #94a3b8; }
.activity-time { font-size: 0.7rem; color: #334155; margin-top: 0.15rem; }

/* ── Scorecard ── */
.scorecard {
    background: #0d1a2e;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1.25rem;
    text-align: center;
}
.scorecard-title { font-size: 0.75rem; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.75rem; }
.scorecard-score { font-size: 2.5rem; font-weight: 800; line-height: 1; }
.scorecard-grade { font-size: 0.8rem; color: #475569; margin-top: 0.25rem; }

/* ── Profile Row ── */
.profile-row { display: flex; align-items: center; gap: 0.5rem; padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.82rem; }
.profile-label { color: #475569; min-width: 90px; font-size: 0.75rem; }
.profile-value { color: #e2e8f0; }

/* ── Tech Chip ── */
.tech-chip {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.2);
    color: #a5b4fc; border-radius: 6px; padding: 0.25rem 0.65rem;
    font-size: 0.75rem; font-weight: 500; margin: 0.2rem;
}

/* ── Empty State ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #334155;
}
.empty-state-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.4; }
.empty-state-title { font-size: 1.1rem; font-weight: 600; color: #475569; margin-bottom: 0.5rem; }
.empty-state-sub { font-size: 0.85rem; color: #334155; }

/* ── Streamlit overrides ── */
div.stButton > button {
    background: #EA580C !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.25rem !important;
    transition: all 0.15s !important;
}
div.stButton > button:hover { background: #c2410c !important; }
div.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.05) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
[data-testid="stMetric"] {
    background: #0d1a2e;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1rem 1.25rem;
}
[data-testid="stMetricValue"] { font-size: 1.75rem !important; color: #f1f5f9 !important; }
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; color: #475569 !important; text-transform: uppercase; letter-spacing: 0.06em; }
.stProgress > div > div { background: linear-gradient(90deg, #EA580C, #f97316) !important; border-radius: 4px !important; }
.stProgress > div { background: rgba(255,255,255,0.05) !important; border-radius: 4px !important; height: 6px !important; }
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] select,
textarea, .stSelectbox > div > div {
    background: #0d1a2e !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
.stTabs [data-baseweb="tab-list"] { background: transparent; border-bottom: 1px solid rgba(255,255,255,0.06); gap: 0; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #475569; border-bottom: 2px solid transparent; font-size: 0.85rem; padding: 0.6rem 1.25rem; }
.stTabs [aria-selected="true"] { color: #EA580C !important; border-bottom-color: #EA580C !important; background: transparent !important; }
[data-testid="stExpander"] { background: #0d1a2e; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; }
.stDataFrame { background: #0d1a2e !important; }
h1 { font-size: 1.4rem !important; font-weight: 700 !important; color: #f1f5f9 !important; letter-spacing: -0.02em !important; }
h2 { font-size: 1.05rem !important; font-weight: 600 !important; color: #94a3b8 !important; }
h3 { font-size: 0.9rem !important; font-weight: 600 !important; color: #64748b !important; }
p, li, span { color: #94a3b8; font-size: 0.85rem; }
hr { border-color: rgba(255,255,255,0.05) !important; margin: 1rem 0 !important; }
</style>
"""

# modules/theme.py
# Simple theme CSS without any syntax errors

THEME_CSS = """
<style>
    /* Main container */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #fbbf24 !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #fbbf24 !important;
    }
    
    /* Success messages */
    .stAlert {
        background-color: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
    }
    
    /* Info messages */
    .stAlert[data-baseweb="notification"] {
        background-color: rgba(59, 130, 246, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: #0f172a;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        transform: translateY(-2px);
    }
    
    /* Text input */
    .stTextInput > div > div > input {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.7);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: rgba(30, 41, 59, 0.5);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        color: #fbbf24;
        border-bottom: 2px solid #fbbf24;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: #1e293b;
        border-radius: 8px;
    }
    
    /* Dataframe */
    .stDataFrame {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #fbbf24;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Cards */
    .data-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Score rings */
    .score-ring {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        background: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 16px;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .badge-info {
        background: #3b82f6;
        color: white;
    }
</style>
"""

# Optional: Add a simple function to get theme
def get_theme_css():
    """Return the theme CSS"""
    return THEME_CSS

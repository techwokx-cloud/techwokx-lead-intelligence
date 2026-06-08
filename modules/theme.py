# modules/theme.py
# Dark mode theme with better readability

THEME_CSS = """
<style>
    /* Main container - Dark background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Main content area */
    .main .block-container {
        background: transparent;
    }
    
    /* Headers - Bright and clear */
    h1, h2, h3, h4, h5, h6 {
        color: #fbbf24 !important;
        font-weight: 600 !important;
    }
    
    /* Regular text - Lighter for better contrast */
    p, li, .stMarkdown, .stCaption, .stText, div, span {
        color: #e2e8f0 !important;
    }
    
    /* Smaller text and captions */
    .stCaption, caption, .caption {
        color: #94a3b8 !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #fbbf24 !important;
        font-size: 1.8rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #22c55e !important;
    }
    
    /* Success messages */
    .stAlert {
        background-color: rgba(34, 197, 94, 0.15) !important;
        border-left: 4px solid #22c55e !important;
        color: #dcfce7 !important;
    }
    
    /* Info messages */
    .stAlert[data-baseweb="notification"]:has(.stAlertInfo) {
        background-color: rgba(59, 130, 246, 0.15) !important;
        border-left: 4px solid #3b82f6 !important;
        color: #bfdbfe !important;
    }
    
    /* Warning messages */
    .stAlert[data-baseweb="notification"]:has(.stAlertWarning) {
        background-color: rgba(245, 158, 11, 0.15) !important;
        border-left: 4px solid #f59e0b !important;
        color: #fef3c7 !important;
    }
    
    /* Error messages */
    .stAlert[data-baseweb="notification"]:has(.stAlertError) {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid #ef4444 !important;
        color: #fee2e2 !important;
    }
    
    /* Alert text */
    .stAlert p, .stAlert div {
        color: #f1f5f9 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: #0f172a !important;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white !important;
        transform: translateY(-2px);
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: rgba(51, 65, 85, 0.8);
        color: #cbd5e1 !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(71, 85, 105, 0.9);
        color: #fbbf24 !important;
    }
    
    /* Text input labels */
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }
    
    /* Text input fields */
    .stTextInput > div > div > input {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #f1f5f9 !important;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #fbbf24;
        box-shadow: 0 0 0 2px rgba(251, 191, 36, 0.2);
    }
    
    /* Placeholder text */
    .stTextInput > div > div > input::placeholder {
        color: #64748b !important;
    }
    
    /* Text area */
    .stTextArea > div > div > textarea {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #f1f5f9 !important;
        border-radius: 8px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #fbbf24;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #f1f5f9 !important;
    }
    
    /* Select box options */
    .stSelectbox > div > div > div {
        color: #f1f5f9 !important;
    }
    
    /* Multi select */
    .stMultiSelect > div > div {
        background: rgba(15, 23, 42, 0.8);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: rgba(30, 41, 59, 0.5);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
        background: transparent;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #fbbf24 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #fbbf24 !important;
        border-bottom: 2px solid #fbbf24;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 8px;
        color: #e2e8f0 !important;
        font-weight: 500;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(51, 65, 85, 0.7);
        color: #fbbf24 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(15, 23, 42, 0.4);
        border-radius: 0 0 8px 8px;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: #0f172a !important;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e2e8f0 !important;
    }
    
    code {
        color: #fbbf24 !important;
        background: rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
    }
    
    .dataframe {
        color: #e2e8f0 !important;
    }
    
    .dataframe th {
        background: #1e293b !important;
        color: #fbbf24 !important;
        font-weight: 600;
    }
    
    .dataframe td {
        background: #0f172a !important;
        color: #cbd5e1 !important;
    }
    
    .dataframe tr:hover td {
        background: #1e293b !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #fbbf24;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(255, 255, 255, 0.1);
        margin: 1rem 0;
    }
    
    /* Cards */
    .data-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .data-card h4 {
        color: #fbbf24 !important;
        margin-bottom: 0.8rem;
        font-size: 1rem;
    }
    
    /* Profile rows */
    .profile-row {
        display: flex;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .profile-label {
        width: 120px;
        font-weight: 600;
        color: #94a3b8 !important;
        font-size: 0.85rem;
    }
    
    .profile-value {
        flex: 1;
        color: #e2e8f0 !important;
        font-size: 0.85rem;
    }
    
    /* Score rings */
    .score-ring {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        background: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .score-hot {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white !important;
    }
    
    .score-warm {
        background: linear-gradient(135deg, #f97316, #ea580c);
        color: white !important;
    }
    
    .score-good {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: white !important;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 16px;
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .empty-state-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #e2e8f0 !important;
        margin-bottom: 0.5rem;
    }
    
    .empty-state-sub {
        font-size: 0.85rem;
        color: #94a3b8 !important;
    }
    
    /* Scorecards */
    .scorecard {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .scorecard-title {
        font-size: 0.75rem;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .scorecard-score {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .scorecard-grade {
        font-size: 0.75rem;
        color: #64748b !important;
    }
    
    /* Tech chips */
    .tech-chip {
        display: inline-block;
        background: #fbbf24;
        color: #0f172a !important;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        margin: 0.25rem;
        font-weight: 500;
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
        color: white !important;
    }
    
    /* Sidebar */
    .css-1d391kg, .css-163ttbj, .stSidebar {
        background: rgba(15, 23, 42, 0.9);
    }
    
    .sidebar .sidebar-content {
        background: rgba(15, 23, 42, 0.9);
    }
    
    /* Sidebar text */
    .stSidebar .stMarkdown, .stSidebar p, .stSidebar div {
        color: #e2e8f0 !important;
    }
    
    /* Links */
    a {
        color: #fbbf24 !important;
        text-decoration: none;
    }
    
    a:hover {
        color: #f59e0b !important;
        text-decoration: underline;
    }
    
    /* Download button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: white !important;
    }
    
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #16a34a, #15803d);
    }
    
    /* Number input */
    .stNumberInput input {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #f1f5f9 !important;
    }
    
    /* Slider */
    .stSlider label {
        color: #94a3b8 !important;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #e2e8f0 !important;
    }
    
    /* Radio */
    .stRadio label {
        color: #e2e8f0 !important;
    }
    
    /* Toggle */
    .stToggle label {
        color: #e2e8f0 !important;
    }
</style>
"""

def get_theme_css():
    """Return the theme CSS"""
    return THEME_CSS

THEME_CSS = """
<style>
    /* Main theme colors */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
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
        color: white;
    }
    
    .score-warm {
        background: linear-gradient(135deg, #f97316, #ea580c);
        color: white;
    }
    
    .score-good {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: white;
    }
    
    /* Data cards */
    .data-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .data-card h4 {
        color: #fbbf24;
        margin-bottom: 0.8rem;
        font-size: 1rem;
    }
    
    /* Profile rows */
    .profile-row {
        display: flex;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .profile-label {
        width: 120px;
        font-weight: 500;
        color: #94a3b8;
        font-size: 0.85rem;
    }
    
    .profile-value {
        flex: 1;
        color: #cbd5e1;
        font-size: 0.85rem;
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
        font-weight: 500;
        color: #cbd5e1;
        margin-bottom: 0.5rem;
    }
    
    .empty-state-sub {
        font-size: 0.85rem;
        color: #64748b;
    }
    
    /* Scorecards */
    .scorecard {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .scorecard-title {
        font-size: 0.75rem;
        color: #94a3b8;
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
        color: #64748b;
    }
    
    /* Tech chips */
    .tech-chip {
        display: inline-block;
        background: #fbbf24;
        color: #0f172a;
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
        color: white;
    }
    
    /* Custom input styling */
    .stTextInput > div > div > input {
        background: rgba(30, 41, 59, 0.7);
        border-color: rgba(255,255,255,0.1);
        color: white;
    }
    
    /* Button styling */
    .

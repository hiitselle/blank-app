import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the page
st.set_page_config(
    page_title="🧗‍♂️ IFSC 2025 World Championships",
    page_icon="🧗‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with mobile responsiveness and improved styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1);
        color: white;
        margin-bottom: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        animation: fadeIn 1s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .competition-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #4ecdc4;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .competition-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .athlete-row {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        font-weight: 500;
        border: 2px solid transparent;
        box-shadow: 0 3px 8px rgba(0,0,0,0.12);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .athlete-row::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        transition: transform 0.6s;
    }
    
    .athlete-row:hover::before {
        transform: translateX(100%);
    }
    
    .athlete-row:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }
    
    .athlete-row strong {
        font-size: 1.2rem;
        display: block;
        margin-bottom: 0.5rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .athlete-row small {
        font-size: 0.95rem;
        opacity: 0.9;
        line-height: 1.4;
    }
    
    .athlete-row .targets {
        background-color: rgba(0, 0, 0, 0.15);
        padding: 0.6rem 0.8rem;
        border-radius: 8px;
        margin-top: 0.6rem;
        display: inline-block;
        font-weight: 600;
        border: 2px solid rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(5px);
    }
    
    .podium-position {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 2px solid #28a745;
        color: #155724;
    }
    
    .podium-position .targets {
        background-color: rgba(40, 167, 69, 0.25);
        color: #155724;
        border: 2px solid #28a745;
    }
    
    .no-podium {
        background: linear-gradient(135deg, #f8d7da, #f1b0b7);
        border: 2px solid #dc3545;
        color: #721c24;
    }
    
    .no-podium .targets {
        background-color: rgba(220, 53, 69, 0.25);
        color: #721c24;
        border: 2px solid #dc3545;
    }
    
    .qualified {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 2px solid #28a745;
        color: #155724;
    }
    
    .qualified .targets {
        background-color: rgba(40, 167, 69, 0.25);
        color: #155724;
        border: 2px solid #28a745;
    }
    
    .podium-contention {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border: 2px solid #ffc107;
        color: #856404;
    }
    
    .podium-contention .targets {
        background-color: rgba(255, 193, 7, 0.25);
        color: #856404;
        border: 2px solid #ffc107;
    }
    
    .eliminated {
        background: linear-gradient(135deg, #f8d7da, #f1b0b7);
        border: 2px solid #dc3545;
        color: #721c24;
    }
    
    .eliminated .targets {
        background-color: rgba(220, 53, 69, 0.25);
        color: #721c24;
        border: 2px solid #dc3545;
    }
    
    .awaiting-result {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border: 2px solid #6c757d;
        color: #495057;
    }
    
    .awaiting-result .targets {
        background-color: rgba(108, 117, 125, 0.25);
        color: #495057;
        border: 2px solid #6c757d;
    }
    
    .metric-card {
        background: linear-gradient(135deg, white, #f8f9fa);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        color: #333333;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-card h4 {
        color: #666666;
        margin-bottom: 0.8rem;
        font-size: 0.95rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card h2 {
        color: #333333;
        margin: 0;
        font-size: 1.8rem;
        font-weight: bold;
        text-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-left: 0.5rem;
    }
    
    .badge-live {
        background: linear-gradient(45deg, #ff4757, #ff6b6b);
        color: white;
        animation: pulse 2s infinite;
    }
    
    .badge-completed {
        background: linear-gradient(45deg, #2ed573, #7bed9f);
        color: white;
    }
    
    .badge-upcoming {
        background: linear-gradient(45deg, #ffa502, #ff6348);
        color: white;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #4ecdc4;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .threshold-card {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border: 2px solid #2196f3;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #0d47a1;
    }
    
    .error-card {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border: 2px solid #f44336;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #c62828;
    }
    
    .success-card {
        background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
        border: 2px solid #4caf50;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #2e7d32;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem 0;
            margin-bottom: 1rem;
        }
        
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        .main-header h3 {
            font-size: 1rem;
        }
        
        .metric-card {
            margin-bottom: 1rem;
            padding: 1rem;
        }
        
        .metric-card h2 {
            font-size: 1.4rem;
        }
        
        .athlete-row {
            font-size: 0.9rem;
            padding: 0.8rem;
            margin: 0.3rem 0;
        }
        
        .athlete-row strong {
            font-size: 1rem;
        }
        
        .athlete-row small {
            font-size: 0.8rem;
        }
        
        .competition-card {
            padding: 1rem;
        }
        
        .targets {
            font-size: 0.8rem !important;
            padding: 0.4rem 0.6rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .main-header h1 {
            font-size: 1.2rem;
        }
        
        .main-header h3 {
            font-size: 0.9rem;
        }
        
        .metric-card h2 {
            font-size: 1.2rem;
        }
        
        .athlete-row {
            font-size: 0.8rem;
            padding: 0.6rem;
        }
        
        .athlete-row strong {
            font-size: 0.9rem;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background: linear-gradient(135deg, #2d3748, #4a5568);
            color: #e2e8f0;
            border: 1px solid #4a5568;
        }
        
        .metric-card h4 {
            color: #a0aec0;
        }
        
        .metric-card h2 {
            color: #e2e8f0;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #4ecdc4, #45b7d1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #45b7d1, #4ecdc4);
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets URLs
SHEETS_URLS = {
    "Male Boulder Semis": "https://docs.google.com/spreadsheets/d/1MwVp1mBUoFrzRSIIu4UdMcFlXpxHAi_R7ztp1E4Vgx0/export?format=csv&gid=911620167",
    "Female Boulder Semis": "https://docs.google.com/spreadsheets/d/1MwVp1mBUoFrzRSIIu4UdMcFlXpxHAi_R7ztp1E4Vgx0/export?format=csv&gid=920221506",
    "Male Boulder Final": "https://docs.google.com/spreadsheets/d/1MwVp1mBUoFrzRSIIu4UdMcFlXpxHAi_R7ztp1E4Vgx0/export?format=csv&gid=1415967322",
    "Female Boulder Final": "https://docs.google.com/spreadsheets/d/1MwVp1mBUoFrzRSIIu4UdMcFlXpxHAi_R7ztp1E4Vgx0/export?format=csv&gid=299577805",
    "Male Lead Semis": "https://docs.google.com/spreadsheets/d/1MwVp1mBUoFrzRSIIu4UdMcFlXpxHAi_R7ztp1E4Vgx0/export?format=csv&gid=0",
    "Female Lead Semis": "https://docs.google.com/spreadsheets/d/1MwVp1mBUoFrzRSIIu4UdMcFlXpxHAi_R7ztp1E4Vgx0/export?format=csv&gid=352924417",
    "Male Lead Final": "https://docs.google.com/spreadsheets/d/1MwVp1mBUoFrzRSIIu4UdMcFlXpxHAi_R7ztp1E4Vgx0/export?format=csv&gid=1091240908",
    "Female Lead Final": "https://docs.google.com/spreadsheets/d/1MwVp1mBUoFrzRSIIu4UdMcFlXpxHAi_R7ztp1E4Vgx0/export?format=csv&gid=528108640"
}

# Configuration
CONFIG = {
    'CACHE_TTL': 30,  # Cache time in seconds
    'AUTO_REFRESH_INTERVAL': 30,  # Auto refresh interval in seconds
    'MAX_RETRIES': 3,  # Maximum retry attempts for data loading
    'REQUEST_TIMEOUT': 15,  # Request timeout in seconds
}

def safe_numeric_conversion(value, default=0):
    """Safely convert value to numeric with proper error handling"""
    try:
        if pd.isna(value) or value == '' or value is None:
            return default
        return pd.to_numeric(value, errors='coerce')
    except Exception as e:
        logger.warning(f"Error converting {value} to numeric: {e}")
        return default

def clean_text(text):
    """Clean text by removing unwanted characters and normalizing"""
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    try:
        # Remove common encoding artifacts
        cleaned = text.replace('Ã¢', '').replace('Ã¡', '').replace('â€™', "'")
        cleaned = cleaned.replace('â€œ', '"').replace('â€', '"').replace('â€"', '-')
        
        return cleaned.strip()
    except Exception as e:
        logger.warning(f"Error cleaning text '{text}': {e}")
        return str(text) if text is not None else ""

def validate_dataframe(df, expected_columns):
    """Validate DataFrame has expected structure"""
    if df.empty:
        return False, ["DataFrame is empty"]
    
    missing_cols = [col for col in expected_columns if col not in df.columns]
    issues = []
    
    if missing_cols:
        issues.append(f"Missing columns: {', '.join(missing_cols)}")
    
    return len(issues) == 0, issues

def get_competition_status(df, competition_name):
    """Determine competition status based on data"""
    if df.empty:
        return "upcoming", "🔄"
    
    # Check if there are any scores/results
    if "Boulder" in competition_name:
        score_cols = [col for col in df.columns if 'Score' in str(col)]
        if score_cols:
            has_scores = df[score_cols].notna().any().any()
            if has_scores:
                # Check if all athletes have completed
                total_athletes = len(df[df.iloc[:, 0].notna() & (df.iloc[:, 0] != '')])
                completed_athletes = len(df[df[score_cols].notna().any(axis=1)])
                if completed_athletes >= total_athletes * 0.8:  # 80% completion threshold
                    return "completed", "✅"
                else:
                    return "live", "🔴"
            else:
                return "upcoming", "⏳"
    elif "Lead" in competition_name:
        if 'Manual Score' in df.columns:
            has_scores = df['Manual Score'].notna().any()
            if has_scores:
                total_athletes = len(df[df['Name'].notna() & (df['Name'] != '')])
                completed_athletes = len(df[df['Manual Score'].notna()])
                if completed_athletes >= total_athletes * 0.8:
                    return "completed", "✅"
                else:
                    return "live", "🔴"
            else:
                return "upcoming", "⏳"
    
    return "upcoming", "⏳"

@st.cache_data(ttl=CONFIG['CACHE_TTL'])
def load_sheet_data(url, retries=0):
    """Load data from Google Sheets CSV export URL with enhanced error handling"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(
            url, 
            timeout=CONFIG['REQUEST_TIMEOUT'],
            headers=headers
        )
        response.raise_for_status()
        
        # Read CSV data
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        # Clean up the dataframe
        df = df.dropna(how='all')  # Remove completely empty rows
        
        # Clean column names - strip whitespace and normalize
        df.columns = df.columns.str.strip()
        
        # Remove unnamed columns more safely
        if len(df.columns) > 0:
            unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed')]
            df = df.drop(columns=unnamed_cols, errors='ignore')
        
        # Clean text data
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(clean_text)
        
        logger.info(f"Successfully loaded data with {len(df)} rows and {len(df.columns)} columns")
        return df
        
    except requests.RequestException as e:
        error_msg = f"Network error loading data: {str(e)}"
        logger.error(error_msg)
        
        if retries < CONFIG['MAX_RETRIES']:
            logger.info(f"Retrying... attempt {retries + 1}")
            time.sleep(2 ** retries)  # Exponential backoff
            return load_sheet_data(url, retries + 1)
        
        st.error(f"🚫 {error_msg}")
        return pd.DataFrame()
        
    except pd.errors.EmptyDataError:
        st.warning("⚠️ The data source appears to be empty")
        return pd.DataFrame()
        
    except Exception as e:
        error_msg = f"Unexpected error loading data: {str(e)}"
        logger.error(error_msg)
        st.error(f"🚫 {error_msg}")
        return pd.DataFrame()

def get_status_emoji(status_text):
    """Get emoji based on status with enhanced detection"""
    if pd.isna(status_text):
        return "⏳"
    
    status_str = str(status_text).lower()
    
    if "qualified" in status_str or "✓✓" in status_str:
        return "✅"
    elif "eliminated" in status_str or "✗" in status_str:
        return "❌"
    elif "contention" in status_str or "⚠" in status_str:
        return "⚠️"
    elif "podium" in status_str and "no podium" not in status_str:
        return "🏆"
    elif "no podium" in status_str:
        return "💔"
    else:
        return "🔥"

def display_enhanced_metrics(df, competition_name):
    """Display enhanced metrics with better calculation"""
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics based on competition type
    if "Boulder" in competition_name:
        # Total athletes
        total_athletes = len(df[df['Athlete Name'].notna() & (df['Athlete Name'] != '')])
        
        # Completed problems across all boulders
        boulder_cols = [col for col in df.columns if 'Boulder' in str(col) and 'Score' in str(col)]
        completed_problems = 0
        if boulder_cols:
            for col in boulder_cols:
                completed_problems += df[col].notna().sum()
        
        # Average score
        score_col = None
        for col in df.columns:
            if 'Total Score' in str(col):
                score_col = col
                break
        
        avg_score = 0
        if score_col and score_col in df.columns:
            numeric_scores = pd.to_numeric(df[score_col], errors='coerce')
            avg_score = numeric_scores.mean() if not numeric_scores.isna().all() else 0
        
        # Leader
        leader = "TBD"
        if 'Current Position/Rank' in df.columns:
            try:
                leader_mask = pd.to_numeric(df['Current Position/Rank'], errors='coerce') == 1
                if leader_mask.any():
                    leader = clean_text(df.loc[leader_mask, 'Athlete Name'].iloc[0])
            except:
                pass
        
        with col1:
            st.markdown(f'<div class="metric-card"><h4>👥 Athletes</h4><h2>{total_athletes}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h4>🧗‍♂️ Completed Problems</h4><h2>{completed_problems}</h2></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><h4>📊 Avg Score</h4><h2>{avg_score:.1f}</h2></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><h4>🥇 Leader</h4><h2>{leader}</h2></div>', unsafe_allow_html=True)
            
    elif "Lead" in competition_name:
        # Filter active athletes
        active_df = df[
            df['Name'].notna() & 
            (df['Name'] != '') & 
            (~df['Name'].astype(str).str.contains('Hold for', na=False)) &
            (~df['Name'].astype(str).str.contains('Min to', na=False))
        ]
        
        total_athletes = len(active_df)
        completed = len(active_df[active_df['Manual Score'].notna() & (active_df['Manual Score'] != '')])
        
        # Average score
        if 'Manual Score' in active_df.columns:
            scores = pd.to_numeric(active_df['Manual Score'], errors='coerce')
            avg_score = scores.mean() if not scores.isna().all() else 0
        else:
            avg_score = 0
        
        # Leader
        leader = "TBD"
        if 'Current Rank' in active_df.columns:
            try:
                leader_idx = pd.to_numeric(active_df['Current Rank'], errors='coerce') == 1
                if leader_idx.any():
                    leader = clean_text(active_df.loc[leader_idx, 'Name'].iloc[0])
            except:
                pass
        
        with col1:
            st.markdown(f'<div class="metric-card"><h4>👥 Athletes</h4><h2>{total_athletes}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h4>✅ Completed</h4><h2>{completed}</h2></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><h4>📊 Avg Score</h4><h2>{avg_score:.1f}</h2></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><h4>🥇 Leader</h4><h2>{leader}</h2></div>', unsafe_allow_html=True)

def display_boulder_results(df, competition_name):
    """Display boulder competition results with enhanced formatting"""
    status, status_emoji = get_competition_status(df, competition_name)
    status_class = f"badge-{status}"
    
    st.markdown(f"""
    ### 🪨 {competition_name} 
    <span class="status-badge {status_class}">{status_emoji} {status.upper()}</span>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown('<div class="error-card">⚠️ No data available for this competition</div>', unsafe_allow_html=True)
        return
    
    # Validate required columns
    required_cols = ['Athlete Name', 'Current Position/Rank']
    is_valid, issues = validate_dataframe(df, required_cols)
    
    if not is_valid:
        st.markdown(f'<div class="error-card">❌ Data validation failed: {"; ".join(issues)}</div>', unsafe_allow_html=True)
        with st.expander("🔍 Raw Data"):
            st.dataframe(df, use_container_width=True, hide_index=True)
        return
    
    # Display enhanced metrics
    display_enhanced_metrics(df, competition_name)
    
    st.markdown("#### 📋 Current Standings")
    
    # Find the total score column
    score_col = None
    for col in df.columns:
        if 'Total Score' in str(col):
            score_col = col
            break
    
    # Sort and prepare data
    df_sorted = df.copy()
    
    # Convert rank to numeric
    if 'Current Position/Rank' in df.columns:
        df_sorted['Current Position/Rank'] = pd.to_numeric(df_sorted['Current Position/Rank'], errors='coerce')
    
    # Convert score to numeric if available
    if score_col is not None:
        df_sorted[score_col] = pd.to_numeric(df_sorted[score_col], errors='coerce')
    
    # Sort by position first (ascending), then by score (descending) as tiebreaker
    try:
        if 'Current Position/Rank' in df_sorted.columns:
            df_sorted = df_sorted.sort_values('Current Position/Rank', ascending=True).reset_index(drop=True)
        elif score_col is not None:
            df_sorted = df_sorted.sort_values(score_col, ascending=False).reset_index(drop=True)
    except Exception as e:
        logger.warning(f"Could not sort data: {e}")
        df_sorted = df.copy()
    
    # Display results with enhanced styling
    for idx, row in df_sorted.iterrows():
        if pd.isna(row.get('Athlete Name')) or row.get('Athlete Name') == '':
            continue
            
        rank = row.get('Current Position/Rank', 'N/A')
        athlete = clean_text(str(row.get('Athlete Name', 'Unknown')))
        total_score = row.get(score_col, 'N/A') if score_col else 'N/A'
        
        # Color coding based on position
        try:
            rank_num = safe_numeric_conversion(rank)
            if rank_num > 0 and rank_num <= 3:
                card_class = "podium-position"
                position_emoji = "🥇" if rank_num == 1 else "🥈" if rank_num == 2 else "🥉"

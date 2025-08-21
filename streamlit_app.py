import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time
from datetime import datetime, timedelta
import logging
import re

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
        background: linear-gradient(135deg, #d4edda, #c3e6cb) !important;
        border: 2px solid #28a745 !important;
        color: #155724 !important;
    }
    
    .podium-position .targets {
        background-color: rgba(40, 167, 69, 0.25) !important;
        color: #155724 !important;
        border: 2px solid #28a745 !important;
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
    'CACHE_TTL': 30,
    'AUTO_REFRESH_INTERVAL': 60,  # Increased to 60 seconds for better performance
    'MAX_RETRIES': 3,
    'REQUEST_TIMEOUT': 15,
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
        cleaned = text.replace('ÃƒÆ'Ã‚Â¢', '').replace('ÃƒÆ'Ã‚Â¡', '').replace('ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢', "'")
        cleaned = cleaned.replace('ÃƒÂ¢Ã¢â€šÂ¬Ã…"', '"').replace('ÃƒÂ¢Ã¢â€šÂ¬', '"').replace('ÃƒÂ¢Ã¢â€šÂ¬"', '-')
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
                total_athletes = len(df[df.iloc[:, 0].notna() & (df.iloc[:, 0] != '')])
                completed_athletes = len(df[df[score_cols].notna().any(axis=1)])
                if completed_athletes >= total_athletes * 0.8:
                    return "completed", "✅"
                else:
                    return "live", "🔴"

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
    
    return "upcoming", "🔄"

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
        df = df.dropna(how='all')
        
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
            time.sleep(2 ** retries)
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
    """Get emoji based on status text"""
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
        return "❌"
    else:
        return "🔄"

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
        # Filter active athletes (excluding threshold rows)
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
        
        # Boulder scores and completion check
        boulder_scores = []
        completed_boulders = 0
        for i in range(1, 5):
            col_name = f'Boulder {i} Score (0-25)'
            if col_name in df.columns:
                score = row.get(col_name, '-')
                if pd.notna(score) and str(score) != '-' and str(score) != '':
                    boulder_scores.append(f"B{i}: {score}")
                    completed_boulders += 1
                else:
                    boulder_scores.append(f"B{i}: -")
        
        boulder_display = " | ".join(boulder_scores) if boulder_scores else "No boulder data available"
        
        # Check for worst finish information
        worst_finish_display = ""
        if completed_boulders == 4:
            worst_finish_col = None
            
            if "Boulder" in competition_name and 'Worst Possible Finish' in df.columns:
                worst_finish_col = 'Worst Possible Finish'
            elif "Lead" in competition_name and 'Worst Finish' in df.columns:
                worst_finish_col = 'Worst Finish'
            else:
                # Try other variations as fallback
                for col in df.columns:
                    col_str = str(col).strip().lower()
                    if ('worst' in col_str and 'possible' in col_str and 'finish' in col_str) or ('worst' in col_str and 'finish' in col_str):
                        worst_finish_col = col
                        break
            
            if worst_finish_col and worst_finish_col in df.columns:
                worst_finish = row.get(worst_finish_col, 'N/A')
                if worst_finish not in ['N/A', '', None] and not pd.isna(worst_finish):
                    worst_finish_clean = clean_text(str(worst_finish))
                    if worst_finish_clean and worst_finish_clean != '-':
                        worst_finish_display = f" | Worst Finish: {worst_finish_clean}"

        # Color coding based on completion and competition type
        position_emoji = ""
        card_class = ""
        
        try:
            rank_num = safe_numeric_conversion(rank)
            
            # Get worst possible finish number
            worst_finish_num = None
            if worst_finish_display:
                worst_finish_match = re.search(r'Worst Finish: (\d+)', worst_finish_display)
                if worst_finish_match:
                    worst_finish_num = int(worst_finish_match.group(1))
            
            # Only apply coloring if athlete has completed all 4 boulders OR has a valid score
            if completed_boulders == 4 or (total_score not in ['N/A', '', None] and not pd.isna(total_score)):
                if "Final" in competition_name:
                    # For Finals, use podium-based coloring (top 3)
                    if rank_num > 0 and rank_num <= 3:
                        if worst_finish_num and worst_finish_num <= 3:
                            card_class = "podium-position"  # Green - safe podium
                            position_emoji = "🥇" if rank_num == 1 else "🥈" if rank_num == 2 else "🥉"
                        else:
                            card_class = "podium-contention"  # Yellow - could drop off podium
                            position_emoji = "⚠️"
                    elif rank_num > 3:
                        card_class = "no-podium"  # Red - out of podium positions
                        position_emoji = "❌"
                        
                elif "Semis" in competition_name:
                    # For Semis, use qualification-based coloring (top 8)
                    if rank_num > 0 and rank_num <= 8:
                        if worst_finish_num and worst_finish_num <= 8:
                            card_class = "qualified"  # Green - safe qualification
                            position_emoji = "✅"
                        else:
                            card_class = "podium-contention"  # Yellow - could drop out of top 8
                            position_emoji = "⚠️"
                    elif rank_num > 8:
                        card_class = "eliminated"  # Red - out of qualifying positions
                        position_emoji = "❌"
                
                else:
                    # For other competitions, use standard rank-based coloring
                    if rank_num > 0 and rank_num <= 3:
                        card_class = "podium-position"
                        position_emoji = "🥇" if rank_num == 1 else "🥈" if rank_num == 2 else "🥉"
                    elif rank_num > 0 and rank_num <= 8:
                        card_class = "qualified"
                        position_emoji = "✅"
                    elif rank_num > 0:
                        card_class = "eliminated"
                        position_emoji = "❌"
            
            # If no complete score, just show rank number without special coloring
            if not position_emoji and rank_num > 0:
                position_emoji = f"#{rank_num}"
                        
        except Exception as e:
            logger.warning(f"Error determining card class: {e}")
            if rank_num > 0:
                position_emoji = f"#{rank_num}"
        
        # Strategy display for boulder competitions after 3 boulders completed
        strategy_display = ""
        if ("Semis" in competition_name or "Final" in competition_name) and completed_boulders == 3:
            strategy_cols = {}
            for col in df.columns:
                col_str = str(col)
                if '1st Place Strategy' in col_str or '1st Place Strate' in col_str:
                    strategy_cols['1st'] = col
                elif '2nd Place Strategy' in col_str or '2nd Place Strate' in col_str:
                    strategy_cols['2nd'] = col
                elif '3rd Place Strategy' in col_str or '3rd Place Strate' in col_str:
                    strategy_cols['3rd'] = col
            
            if strategy_cols:
                strategies = []
                for place, col in strategy_cols.items():
                    strategy_value = row.get(col, '')
                    if strategy_value and str(strategy_value) not in ['', 'nan', 'N/A']:
                        strategy_clean = clean_text(str(strategy_value))
                        if strategy_clean:
                            if place == '1st':
                                strategies.append(f"🥇 1st: {strategy_clean}")
                            elif place == '2nd':
                                strategies.append(f"🥈 2nd: {strategy_clean}")
                            elif place == '3rd':
                                strategies.append(f"🥉 3rd: {strategy_clean}")
                
                if strategies:
                    comp_type = "Final" if "Final" in competition_name else "Semi"
                    strategy_display = f"<br><div class='targets'><strong>{comp_type} Boulder Strategy:</strong> {' | '.join(strategies)}</div>"
        
        # Create the display text
        if completed_boulders == 4:
            detail_text = f"Total: {total_score} | {boulder_display}{worst_finish_display}"
        elif completed_boulders == 3 and ("Semis" in competition_name or "Final" in competition_name):
            detail_text = f"Total: {total_score} | {boulder_display} | 1 boulder remaining"
        else:
            detail_text = f"Total: {total_score} | {boulder_display} | Progress: {completed_boulders}/4 boulders"
        
        st.markdown(f"""
        <div class="athlete-row {card_class}">
            <strong>{position_emoji} - {athlete}</strong><br>
            <small>{detail_text}</small>{strategy_display}
        </div>
        """, unsafe_allow_html=True)

def display_lead_results(df, competition_name):
    """Display lead competition results with enhanced formatting"""
    status, status_emoji = get_competition_status(df, competition_name)
    status_class = f"badge-{status}"
    
    st.markdown(f"""
    ### 🧗‍♀️ {competition_name}
    <span class="status-badge {status_class}">{status_emoji} {status.upper()}</span>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown('<div class="error-card">⚠️ No data available for this competition</div>', unsafe_allow_html=True)
        return
    
    # Validate Name column exists
    if 'Name' not in df.columns:
        st.markdown('<div class="error-card">❌ Name column not found in data</div>', unsafe_allow_html=True)
        with st.expander("🔍 Raw Data"):
            st.dataframe(df, use_container_width=True, hide_index=True)
        return
    
    # Extract qualification thresholds from the bottom rows
    qualification_info = {}
    try:
        for idx, row in df.iterrows():
            if pd.isna(row.get('Name')) or row.get('Name') == '':
                continue
            # Check if this row contains qualification thresholds
            threshold_cols = ['Hold for 1st', 'Hold for 2nd', 'Hold for 3rd', 'Hold to Qualify', 'Min to Qualify']
            for col in threshold_cols:
                if col in df.columns and pd.notna(row.get(col)):
                    qualification_info[col] = clean_text(str(row.get(col)))
    except Exception as e:
        logger.warning(f"Error extracting qualification thresholds: {e}")
    
    # Filter out empty rows and scoring reference rows safely
    try:
        active_df = df[
            df['Name'].notna() & 
            (df['Name'] != '') & 
            (~df['Name'].astype(str).str.isdigit()) &
            (~df['Name'].astype(str).str.contains('Hold for', na=False)) &
            (~df['Name'].astype(str).str.contains('Min to', na=False))
        ]
    except Exception as e:
        logger.error(f"Error filtering data: {e}")
        active_df = df[df['Name'].notna() & (df['Name'] != '')]
    
    # Display enhanced metrics
    display_enhanced_metrics(active_df, competition_name)
    
    st.markdown("#### 📋 Current Standings")
    
    # Show qualification thresholds if available
    if qualification_info:
        threshold_items = []
        threshold_mapping = {
            'Hold for 1st': ('🥇 1st', '#FFD700'),
            'Hold for 2nd': ('🥈 2nd', '#C0C0C0'),
            'Hold for 3rd': ('🥉 3rd', '#CD7F32'),
            'Hold to Qualify': ('✅ Qualify', '#28a745'),
            'Min to Qualify': ('⚠️ Min', '#ffc107')
        }
        
        for key, value in qualification_info.items():
            if key in threshold_mapping:
                label, color = threshold_mapping[key]
                threshold_items.append(f'<span style="color: {color}; font-weight: bold;">{label}: {value}</span>')
        
        if threshold_items:
            st.markdown(f"""
            <div class="threshold-card">
                <h5>🎯 Qualification Thresholds</h5>
                {' | '.join(threshold_items)}
            </div>
            """, unsafe_allow_html=True)
    
    # Sort by Current Rank if available
    try:
        if 'Current Rank' in active_df.columns:
            active_df['Current Rank'] = pd.to_numeric(active_df['Current Rank'], errors='coerce')
            active_df = active_df.sort_values('Current Rank', ascending=True).reset_index(drop=True)
    except Exception as e:
        logger.warning(f"Could not sort by rank: {e}")
    
    # Display results with enhanced formatting
    for idx, row in active_df.iterrows():
        name = clean_text(str(row.get('Name', 'Unknown')))
        score = row.get('Manual Score', 'N/A')
        rank = row.get('Current Rank', 'N/A')
        status = clean_text(str(row.get('Status', 'Unknown')))
        worst_finish = row.get('Worst Finish', 'N/A')
        
        # Determine if athlete has a score or is awaiting result
        has_score = score not in ['N/A', '', None] and not pd.isna(score)
        
        # If no score yet and we have qualification info, show thresholds
        threshold_display = ""
        if not has_score and qualification_info:
            thresholds = []
            if 'Hold for 1st' in qualification_info:
                thresholds.append(f'🥇 1st: {qualification_info["Hold for 1st"]}')
            if 'Hold for 2nd' in qualification_info:
                thresholds.append(f'🥈 2nd: {qualification_info["Hold for 2nd"]}')
            if 'Hold for 3rd' in qualification_info:
                thresholds.append(f'🥉 3rd: {qualification_info["Hold for 3rd"]}')
            if 'Hold to Podium' in qualification_info:
                thresholds.append(f'🏆 Podium: {qualification_info["Hold to Podium"]}')
            if 'Min to Podium' in qualification_info:
                thresholds.append(f'⚠️ Min: {qualification_info["Min to Podium"]}')
            
            if thresholds:
                threshold_display = f"<br><div class='targets'><strong>Targets:</strong> {' | '.join(thresholds)}</div>"
        
        # Get status styling
        status_emoji = get_status_emoji(status)
        
        # Determine card class based on status and score availability - only color if has score
        card_class = ""
        position_emoji = ""
        
        if has_score:
            if "Qualified" in status or "✓✓" in status:
                card_class = "qualified"
                status_emoji = "✅"
            elif "Eliminated" in status or "✗" in status:
                card_class = "eliminated"
                status_emoji = "❌"
            elif "Podium" in status and "No Podium" not in status and "Contention" not in status:
                card_class = "podium-position"
                status_emoji = "🏆"
            elif "Podium Contention" in status or "Contention" in status:
                card_class = "podium-contention"
                status_emoji = "⚠️"
            elif "No Podium" in status:
                card_class = "no-podium"
                status_emoji = "❌"
        
        # Set position emoji
        rank_num = safe_numeric_conversion(rank)
        if rank_num > 0:
            if has_score and card_class:
                position_emoji = status_emoji
            else:
                position_emoji = f"#{rank_num}"
        
        # Show score if available, otherwise show "Awaiting Result"
        score_display = score if has_score else "Awaiting Result"
        
        # Add worst finish info if athlete has a score
        worst_finish_display = ""
        if has_score and worst_finish not in ['N/A', '', None] and not pd.isna(worst_finish):
            worst_finish_clean = clean_text(str(worst_finish))
            if worst_finish_clean and worst_finish_clean != '-':
                worst_finish_display = f" | Worst Finish: {worst_finish_clean}"
        
        st.markdown(f"""
        <div class="athlete-row {card_class}">
            <strong>{position_emoji} #{rank} - {name}</strong><br>
            <small>Score: {score_display} | Status: {status}{worst_finish_display}</small>{threshold_display}
        </div>
        """, unsafe_allow_html=True)

def get_filtered_competitions(competition_type, gender_filter, round_filter):
    """Get filtered competitions based on user selection"""
    filtered_competitions = {}
    
    for name, url in SHEETS_URLS.items():
        include = True
        
        if competition_type != "All":
            if competition_type.lower() not in name.lower():
                include = False
        
        if gender_filter != "All":
            if gender_filter.lower() not in name.lower():
                include = False
                
        if round_filter != "All":
            if round_filter.lower() not in name.lower():
                include = False
        
        if include:
            filtered_competitions[name] = url
    
    return filtered_competitions

def main():
    """Main application function with enhanced features"""
    
    # Initialize session state for auto-refresh
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if 'auto_refresh_enabled' not in st.session_state:
        st.session_state.auto_refresh_enabled = True
    
    # Header with enhanced styling
    st.markdown("""
    <div class="main-header">
        <h1>🧗‍♂️ IFSC 2025 World Championships</h1>
        <h3>Live Competition Results Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with enhanced controls
    st.sidebar.title("🏆 Competition Control Center")
    
    # Auto-refresh controls
    st.sidebar.markdown("### 🔄 Auto-Refresh Settings")
    auto_refresh = st.sidebar.checkbox(
        "Enable Auto-Refresh", 
        value=st.session_state.auto_refresh_enabled,
        help=f"Automatically refresh data every {CONFIG['AUTO_REFRESH_INTERVAL']} seconds"
    )
    st.session_state.auto_refresh_enabled = auto_refresh
    
    # Manual refresh with enhanced feedback
    refresh_col1, refresh_col2 = st.sidebar.columns(2)
    with refresh_col1:
        if st.button("🔄 Refresh Now", type="primary"):
            st.cache_data.clear()
            st.session_state.last_refresh = datetime.now()
            st.sidebar.success("✅ Data refreshed!")
            time.sleep(1)
            st.rerun()
    
    with refresh_col2:
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.sidebar.success("✅ Cache cleared!")
    
    # Last refresh time
    time_since_refresh = datetime.now() - st.session_state.last_refresh
    st.sidebar.caption(f"🕐 Last refresh: {time_since_refresh.seconds}s ago")
    
    # Competition filters with enhanced UI
    st.sidebar.markdown("### 🎯 Competition Filters")
    
    competition_type = st.sidebar.selectbox(
        "🏔️ Competition Type",
        ["All", "Boulder", "Lead"],
        help="Filter by climbing discipline"
    )
    
    gender_filter = st.sidebar.selectbox(
        "👤 Gender Category",
        ["All", "Male", "Female"],
        help="Filter by gender category"
    )
    
    round_filter = st.sidebar.selectbox(
        "🎯 Competition Round",
        ["All", "Semis", "Final"],
        help="Filter by competition round"
    )
    
    # Filter competitions
    filtered_competitions = get_filtered_competitions(competition_type, gender_filter, round_filter)
    
    # Main content area
    if len(filtered_competitions) == 0:
        st.markdown("""
        <div class="error-card">
            <h3>⚠️ No Competitions Found</h3>
            <p>No competitions match your current filter settings. Please adjust your filters to see results.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Quick overview with enhanced metrics
    st.markdown("### 🚀 Competition Overview")
    
    # Calculate overview metrics
    total_competitions = len(filtered_competitions)
    live_competitions = 0
    completed_competitions = 0
    upcoming_competitions = 0
    
    for comp_name, url in filtered_competitions.items():
        df = load_sheet_data(url)
        status, _ = get_competition_status(df, comp_name)
        if status == "live":
            live_competitions += 1
        elif status == "completed":
            completed_competitions += 1
        else:
            upcoming_competitions += 1
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h4>🏆 Total Competitions</h4><h2>{total_competitions}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h4>🔴 Live</h4><h2>{live_competitions}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h4>✅ Completed</h4><h2>{completed_competitions}</h2></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><h4>🔄 Upcoming</h4><h2>{upcoming_competitions}</h2></div>', unsafe_allow_html=True)
    
    # Detailed results with enhanced presentation
    st.markdown("### 📊 Live Competition Results")
    
    # Handle single vs multiple competitions
    if len(filtered_competitions) > 1:
        # Create tabs for multiple competitions
        tab_names = list(filtered_competitions.keys())
        tabs = st.tabs(tab_names)
        
        for i, (comp_name, url) in enumerate(filtered_competitions.items()):
            with tabs[i]:
                with st.spinner(f"Loading {comp_name}..."):
                    df = load_sheet_data(url)
                    
                current_time = datetime.now().strftime("%H:%M:%S")
                st.caption(f"📡 Last updated: {current_time}")
                
                if "Boulder" in comp_name:
                    display_boulder_results(df, comp_name)
                elif "Lead" in comp_name:
                    display_lead_results(df, comp_name)
                else:
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.markdown('<div class="error-card">❌ No data available</div>', unsafe_allow_html=True)
    else:
        # Single competition view
        comp_name, url = list(filtered_competitions.items())[0]
        
        with st.spinner(f"Loading {comp_name}..."):
            df = load_sheet_data(url)
            
        current_time = datetime.now().strftime("%H:%M:%S")
        st.caption(f"📡 Last updated: {current_time}")
        
        if "Boulder" in comp_name:
            display_boulder_results(df, comp_name)
        elif "Lead" in comp_name:
            display_lead_results(df, comp_name)
        else:
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.markdown('<div class="error-card">❌ No data available</div>', unsafe_allow_html=True)
    
    # Footer with additional information
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🏔️ IFSC World Championships 2025**")
    with col2:
        st.markdown("**📊 Real-time Results Dashboard**")
    with col3:
        st.markdown("**🔄 Auto-updating data**")
    
    # Auto-refresh logic (improved)
    if st.session_state.auto_refresh_enabled:
        time_since_last = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_last >= CONFIG['AUTO_REFRESH_INTERVAL']:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"🚫 Application Error: {e}")
        st.markdown("Please refresh the page or contact support if the issue persists.")
        
        # Show debug information in expander
        with st.expander("🔧 Debug Information"):
            st.code(f"Error: {e}")
            st.code(f"Time: {datetime.now()}")
            import traceback
            st.code(traceback.format_exc())

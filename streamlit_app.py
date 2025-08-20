import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time

# Configure the page
st.set_page_config(
    page_title="🧗‍♂️ IFSC 2025 World Championships",
    page_icon="🧗‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        color: white;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    .competition-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4ecdc4;
        margin: 1rem 0;
    }
    .athlete-row {
        padding: 0.75rem;
        margin: 0.3rem 0;
        border-radius: 8px;
        font-weight: 500;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .athlete-row strong {
        font-size: 1.1rem;
        display: block;
        margin-bottom: 0.25rem;
    }
    .athlete-row small {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    .athlete-row .targets {
        background-color: rgba(0, 0, 0, 0.1);
        padding: 0.4rem 0.6rem;
        border-radius: 6px;
        margin-top: 0.4rem;
        display: inline-block;
        font-weight: 600;
        border: 1px solid rgba(0, 0, 0, 0.2);
    }
    .podium-position {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        color: #856404;
    }
    .podium-position .targets {
        background-color: rgba(255, 193, 7, 0.2);
        color: #856404;
        border: 1px solid #ffc107;
    }
    .qualified {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        color: #155724;
    }
    .qualified .targets {
        background-color: rgba(40, 167, 69, 0.2);
        color: #155724;
        border: 1px solid #28a745;
    }
    .eliminated {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        color: #721c24;
    }
    .eliminated .targets {
        background-color: rgba(220, 53, 69, 0.2);
        color: #721c24;
        border: 1px solid #dc3545;
    }
    .awaiting-result {
        background-color: #f8f9fa;
        border-left: 4px solid #6c757d;
        color: #495057;
    }
    .awaiting-result .targets {
        background-color: rgba(108, 117, 125, 0.2);
        color: #495057;
        border: 1px solid #6c757d;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        color: #333333;
    }
    .metric-card h4 {
        color: #666666;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .metric-card h2 {
        color: #333333;
        margin: 0;
        font-size: 1.5rem;
        font-weight: bold;
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

@st.cache_data(ttl=2)  # Cache data for 2 seconds
def load_sheet_data(url):
    """Load data from Google Sheets CSV export URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Read CSV data
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        # Clean up the dataframe
        df = df.dropna(how='all')  # Remove completely empty rows
        
        # Clean column names - strip whitespace
        df.columns = df.columns.str.strip()
        
        # Remove unnamed columns more safely
        if len(df.columns) > 0:
            unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed')]
            df = df.drop(columns=unnamed_cols, errors='ignore')
        
        return df
    except requests.RequestException as e:
        st.error(f"Network error loading data: {str(e)}")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.warning("The data source appears to be empty")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def get_status_emoji(status_text):
    """Get emoji based on status"""
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
    else:
        return "🔥"

def display_boulder_results(df, competition_name):
    """Display boulder competition results with enhanced formatting"""
    st.markdown(f"### 🪨 {competition_name}")
    
    if df.empty:
        st.warning("No data available")
        return
    
    # Ensure required columns exist
    required_cols = ['Athlete Name', 'Current Position/Rank']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><h4>👥 Athletes</h4><h2>{}</h2></div>'.format(len(df)), unsafe_allow_html=True)
    with col2:
        completed_boulders = df.iloc[:, 2:6].notna().sum().sum() if len(df.columns) > 6 else 0
        st.markdown(f'<div class="metric-card"><h4>🧗‍♂️ Completed Problems</h4><h2>{completed_boulders}</h2></div>', unsafe_allow_html=True)
    with col3:
        # Look for Total Score column (with or without trailing space)
        score_col = None
        for col in df.columns:
            if 'Total Score' in str(col):
                score_col = col
                break
        
        if score_col is not None and score_col in df.columns:
            # Convert to numeric, handling errors
            numeric_scores = pd.to_numeric(df[score_col], errors='coerce')
            avg_score = numeric_scores.mean()
            if not pd.isna(avg_score):
                st.markdown(f'<div class="metric-card"><h4>📊 Avg Score</h4><h2>{avg_score:.1f}</h2></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-card"><h4>📊 Avg Score</h4><h2>N/A</h2></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card"><h4>📊 Avg Score</h4><h2>N/A</h2></div>', unsafe_allow_html=True)
    with col4:
        if 'Current Position/Rank' in df.columns:
            try:
                leader_mask = pd.to_numeric(df['Current Position/Rank'], errors='coerce') == 1
                leader = df.loc[leader_mask, 'Athlete Name'].iloc[0] if leader_mask.any() else "TBD"
                st.markdown(f'<div class="metric-card"><h4>🥇 Leader</h4><h2>{leader}</h2></div>', unsafe_allow_html=True)
            except:
                st.markdown('<div class="metric-card"><h4>🥇 Leader</h4><h2>TBD</h2></div>', unsafe_allow_html=True)
    
    st.markdown("#### 📋 Current Standings")
    
    # Find the total score column
    score_col = None
    for col in df.columns:
        if 'Total Score' in str(col):
            score_col = col
            break
    
    # Sort by Current Position/Rank (ascending) first
    df_sorted = df.copy()
    
    # Convert rank to numeric
    if 'Current Position/Rank' in df.columns:
        try:
            df_sorted['Current Position/Rank'] = pd.to_numeric(df_sorted['Current Position/Rank'], errors='coerce')
        except:
            pass
    
    # Convert score to numeric if available
    if score_col is not None:
        try:
            df_sorted[score_col] = pd.to_numeric(df_sorted[score_col], errors='coerce')
        except:
            pass
    
    # Sort by position first (ascending), then by score (descending) as tiebreaker
    try:
        if 'Current Position/Rank' in df_sorted.columns:
            # Sort by position (ascending)
            df_sorted = df_sorted.sort_values('Current Position/Rank', ascending=True).reset_index(drop=True)
        elif score_col is not None:
            # Fallback: Sort by score only (descending)
            df_sorted = df_sorted.sort_values(score_col, ascending=False).reset_index(drop=True)
    except Exception as e:
        st.warning(f"Could not sort data: {e}")
        # Keep original order if sorting fails
        df_sorted = df.copy()
    
    # Display results table with enhanced formatting
    for idx, row in df_sorted.iterrows():
        if pd.isna(row.get('Athlete Name')) or row.get('Athlete Name') == '':
            continue
            
        rank = row.get('Current Position/Rank', 'N/A')
        athlete = row.get('Athlete Name', 'Unknown')
        total_score = row.get(score_col, 'N/A') if score_col else 'N/A'
        
        # Color coding based on position
        try:
            rank_num = pd.to_numeric(rank, errors='coerce')
            if not pd.isna(rank_num) and rank_num <= 3:
                card_class = "podium-position"
                position_emoji = "🥇" if rank_num == 1 else "🥈" if rank_num == 2 else "🥉"
            elif not pd.isna(rank_num) and rank_num <= 8:
                card_class = "qualified"
                position_emoji = "✅"
            else:
                card_class = "eliminated"
                position_emoji = "❌"
        except:
            card_class = "awaiting-result"
            position_emoji = "⏳"
        
        # Boulder scores
        boulder_scores = []
        for i in range(1, 5):
            col_name = f'Boulder {i} Score (0-25)'
            if col_name in df.columns:
                score = row.get(col_name, '-')
                boulder_scores.append(f"B{i}: {score}")
        
        boulder_display = " | ".join(boulder_scores) if boulder_scores else "No boulder data"
        
        st.markdown(f"""
        <div class="athlete-row {card_class}">
            <strong>{position_emoji} #{rank} - {athlete}</strong><br>
            <small>Total: {total_score} | {boulder_display}</small>
        </div>
        """, unsafe_allow_html=True)

def display_lead_results(df, competition_name):
    """Display lead competition results with enhanced formatting"""
    st.markdown(f"### 🧗‍♀️ {competition_name}")
    
    if df.empty:
        st.warning("No data available")
        return
    
    # Ensure 'Name' column exists
    if 'Name' not in df.columns:
        st.error("Name column not found in data")
        return
    
    # Extract qualification thresholds from the bottom rows
    qualification_info = {}
    try:
        # Look for qualification threshold rows at the bottom
        for idx, row in df.iterrows():
            if pd.isna(row.get('Name')) or row.get('Name') == '':
                continue
            # Check if this row contains qualification thresholds
            if any(col in ['Hold for 1st', 'Hold for 2nd', 'Hold for 3rd', 'Hold to Qualify', 'Min to Qualify'] for col in df.columns):
                for col in df.columns:
                    if col in ['Hold for 1st', 'Hold for 2nd', 'Hold for 3rd', 'Hold to Qualify', 'Min to Qualify']:
                        if pd.notna(row.get(col)):
                            qualification_info[col] = row.get(col)
    except Exception as e:
        pass  # If we can't extract thresholds, continue without them
    
    # Filter out empty rows and scoring reference rows
    try:
        active_df = df[
            df['Name'].notna() & 
            (df['Name'] != '') & 
            (~df['Name'].astype(str).str.isdigit()) &
            (~df['Name'].astype(str).str.contains(r'^\s*$', na=True)) &
            (~df['Name'].astype(str).str.contains('Hold for', na=False)) &
            (~df['Name'].astype(str).str.contains('Min to', na=False))
        ]
    except Exception as e:
        st.error(f"Error filtering data: {e}")
        active_df = df[df['Name'].notna() & (df['Name'] != '')]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h4>👥 Athletes</h4><h2>{len(active_df)}</h2></div>', unsafe_allow_html=True)
    with col2:
        completed = len(active_df[active_df['Manual Score'].notna() & (active_df['Manual Score'] != '')])
        st.markdown(f'<div class="metric-card"><h4>✅ Completed</h4><h2>{completed}</h2></div>', unsafe_allow_html=True)
    with col3:
        if 'Manual Score' in active_df.columns:
            scores = pd.to_numeric(active_df['Manual Score'], errors='coerce')
            avg_score = scores.mean()
            if not pd.isna(avg_score):
                st.markdown(f'<div class="metric-card"><h4>📊 Avg Score</h4><h2>{avg_score:.1f}</h2></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-card"><h4>📊 Avg Score</h4><h2>N/A</h2></div>', unsafe_allow_html=True)
    with col4:
        if 'Current Rank' in active_df.columns:
            try:
                leader_idx = pd.to_numeric(active_df['Current Rank'], errors='coerce') == 1
                leader = active_df.loc[leader_idx, 'Name'].iloc[0] if leader_idx.any() else "TBD"
                st.markdown(f'<div class="metric-card"><h4>🥇 Leader</h4><h2>{leader}</h2></div>', unsafe_allow_html=True)
            except:
                st.markdown('<div class="metric-card"><h4>🥇 Leader</h4><h2>TBD</h2></div>', unsafe_allow_html=True)
    
    st.markdown("#### 📋 Current Standings")
    
    # Show qualification thresholds if available
    if qualification_info and "Semis" in competition_name:
        st.markdown("##### 🎯 Qualification Thresholds:")
        threshold_text = []
        if 'Hold for 1st' in qualification_info:
            threshold_text.append(f"🥇 1st: {qualification_info['Hold for 1st']}")
        if 'Hold for 2nd' in qualification_info:
            threshold_text.append(f"🥈 2nd: {qualification_info['Hold for 2nd']}")
        if 'Hold for 3rd' in qualification_info:
            threshold_text.append(f"🥉 3rd: {qualification_info['Hold for 3rd']}")
        if 'Hold to Qualify' in qualification_info:
            threshold_text.append(f"✅ Qualify: {qualification_info['Hold to Qualify']}")
        if 'Min to Qualify' in qualification_info:
            threshold_text.append(f"⚠️ Min: {qualification_info['Min to Qualify']}")
        
        if threshold_text:
            st.markdown(" | ".join(threshold_text))
        st.markdown("---")
    
    # Sort by Current Rank if available
    try:
        if 'Current Rank' in active_df.columns:
            active_df['Current Rank'] = pd.to_numeric(active_df['Current Rank'], errors='coerce')
            active_df = active_df.sort_values('Current Rank', ascending=True).reset_index(drop=True)
    except Exception as e:
        st.warning(f"Could not sort by rank: {e}")
    
    # Display results
    for idx, row in active_df.iterrows():
        name = row.get('Name', 'Unknown')
        score = row.get('Manual Score', 'N/A')
        rank = row.get('Current Rank', 'N/A')
        status = row.get('Status', 'Unknown')
        
        # Determine if athlete has a score or is awaiting result
        has_score = score not in ['N/A', '', None] and not pd.isna(score)
        
        # If no score yet and we have qualification info, show thresholds
        threshold_display = ""
        if not has_score and qualification_info and "Semis" in competition_name:
            thresholds = []
            if 'Hold for 1st' in qualification_info:
                thresholds.append(f"🥇 1st: {qualification_info['Hold for 1st']}")
            if 'Hold for 2nd' in qualification_info:
                thresholds.append(f"🥈 2nd: {qualification_info['Hold for 2nd']}")
            if 'Hold for 3rd' in qualification_info:
                thresholds.append(f"🥉 3rd: {qualification_info['Hold for 3rd']}")
            if 'Hold to Qualify' in qualification_info:
                thresholds.append(f"✅ Qualify: {qualification_info['Hold to Qualify']}")
            if 'Min to Qualify' in qualification_info:
                thresholds.append(f"⚠️ Min: {qualification_info['Min to Qualify']}")
            
            if thresholds:
                threshold_display = f"<br><div class='targets'><strong>Targets:</strong> {' | '.join(thresholds)}</div>"
        
        # Get status styling
        status_emoji = get_status_emoji(status)
        
        # Determine card class based on status and score availability
        if not has_score:
            card_class = "awaiting-result"
        elif "Qualified" in str(status) or "✓✓" in str(status):
            card_class = "qualified"
        elif "Eliminated" in str(status) or "✗" in str(status):
            card_class = "eliminated"
        elif "Contention" in str(status) or "⚠" in str(status):
            card_class = "podium-position"
        else:
            card_class = "awaiting-result"
        
        # Show score if available, otherwise show "Awaiting Result"
        score_display = score if has_score else "Awaiting Result"
        
        st.markdown(f"""
        <div class="athlete-row {card_class}">
            <strong>{status_emoji} #{rank} - {name}</strong><br>
            <small>Score: {score_display} | Status: {status}</small>{threshold_display}
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧗‍♂️ IFSC 2025 World Championships</h1>
        <h3>Live Competition Results</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🏆 Competition Selection")
    
    # Manual refresh
    if st.sidebar.button("🔄 Refresh Now", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Competition type filter
    st.sidebar.markdown("### 🎯 Filter by:")
    competition_type = st.sidebar.selectbox(
        "Competition Type",
        ["All", "Boulder", "Lead"]
    )
    
    gender_filter = st.sidebar.selectbox(
        "Gender",
        ["All", "Male", "Female"]
    )
    
    round_filter = st.sidebar.selectbox(
        "Round",
        ["All", "Semis", "Final"]
    )
    
    # Filter competitions based on selection
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
    
    # Main content
    if len(filtered_competitions) == 0:
        st.warning("No competitions match your filters.")
        return
    
    # Quick overview cards
    st.markdown("### 🚀 Quick Overview")
    cols = st.columns(min(len(filtered_competitions), 4))
    
    for i, (comp_name, _) in enumerate(list(filtered_competitions.items())[:4]):
        with cols[i % 4]:
            df = load_sheet_data(filtered_competitions[comp_name])
            if not df.empty:
                athlete_count = len(df[df.iloc[:, 0].notna() & (df.iloc[:, 0] != '')])
                st.metric(
                    comp_name.replace(" ", "\n"),
                    f"{athlete_count} athletes",
                    delta=None
                )
    
    # Detailed results
    st.markdown("### 📊 Detailed Results")
    
    # Tabs for each competition
    if len(filtered_competitions) > 1:
        tabs = st.tabs(list(filtered_competitions.keys()))
        
        for i, (comp_name, url) in enumerate(filtered_competitions.items()):
            with tabs[i]:
                df = load_sheet_data(url)
                current_time = time.strftime("%H:%M:%S")
                st.caption(f"Last updated: {current_time}")
                
                if "Boulder" in comp_name:
                    display_boulder_results(df, comp_name)
                elif "Lead" in comp_name:
                    display_lead_results(df, comp_name)
                else:
                    st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        # Single competition view
        comp_name, url = list(filtered_competitions.items())[0]
        df = load_sheet_data(url)
        current_time = time.strftime("%H:%M:%S")
        st.caption(f"Last updated: {current_time}")
        
        if "Boulder" in comp_name:
            display_boulder_results(df, comp_name)
        elif "Lead" in comp_name:
            display_lead_results(df, comp_name)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Auto-refresh functionality - refresh every 2 seconds
    time.sleep(2)
    st.rerun()

if __name__ == "__main__":
    main()

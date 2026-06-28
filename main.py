import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random
import math
import pandas as pd
import json

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cuerden & Co WC26", page_icon="🏆", layout="wide")
ADMIN_PASSWORD = "Cuerden2026"

ALL_TEAMS = [
    "USA", "Mexico", "Canada", "Japan", "New Zealand", "Iran", "Argentina", "Uzbekistan", 
    "South Korea", "Jordan", "Australia", "Brazil", "Ecuador", "Uruguay", "Colombia", 
    "Paraguay", "Morocco", "Tunisia", "Egypt", "Algeria", "Ghana", "Cabo Verde", 
    "Saudi Arabia", "Qatar", "England", "Ivory Coast", "South Africa", "Senegal", 
    "France", "Croatia", "Portugal", "Norway", "Germany", "Netherlands", "Belgium", 
    "Switzerland", "Spain", "Austria", "Scotland", "Curaçao", "Haiti", "Panama", 
    "Sweden", "Türkiye", "Czechia", "Bosnia and Herzegovina", "DR Congo", "Iraq"
]

TEAM_FLAGS = {
    "USA": "🇺🇸", "Mexico": "🇲🇽", "Canada": "🇨🇦", "Japan": "🇯🇵", "New Zealand": "🇳🇿",
    "Iran": "🇮🇷", "Argentina": "🇦🇷", "Uzbekistan": "🇺🇿", "South Korea": "🇰🇷", "Jordan": "🇯🇴",
    "Australia": "🇦🇺", "Brazil": "🇧🇷", "Ecuador": "🇪🇨", "Uruguay": "🇺🇾", "Colombia": "🇨🇴",
    "Paraguay": "🇵🇾", "Morocco": "🇲🇦", "Tunisia": "🇹🇳", "Egypt": "🇪🇬", "Algeria": "🇩🇿",
    "Ghana": "🇬🇭", "Cabo Verde": "🇨🇻", "Saudi Arabia": "🇸🇦", "Qatar": "🇶🇦", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Ivory Coast": "🇨🇮", "South Africa": "🇿🇦", "Senegal": "🇸🇳", "France": "🇫🇷", "Croatia": "🇭🇷",
    "Portugal": "🇵🇹", "Norway": "🇳🇴", "Germany": "🇩🇪", "Netherlands": "🇳🇱", "Belgium": "🇧🇪",
    "Switzerland": "🇨🇭", "Spain": "🇪🇸", "Austria": "🇦🇹", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Curaçao": "🇨🇼",
    "Haiti": "🇭🇹", "Panama": "🇵🇦", "Sweden": "🇸🇪", "Türkiye": "🇹🇷", "Czechia": "🇨🇿",
    "Bosnia and Herzegovina": "🇧🇦", "DR Congo": "🇨🇩", "Iraq": "🇮🇶"
}

# --- CSS STYLING ---
st.markdown("""
<style>
.premium-card { background: rgba(30, 5, 45, 0.85) !important; border-left: 4px solid #C6FF00 !important; padding: 15px !important; margin-bottom: 10px !important; border-radius: 8px !important; }
.score-display { font-weight: 800 !important; color: #C6FF00 !important; }
.badge-ft { color: #E61D25 !important; border: 1px solid #E61D25 !important; padding: 2px 8px !important; border-radius: 4px !important; font-size: 0.75rem !important; }
.badge-live { color: #00E673 !important; border: 1px solid #00E673 !important; padding: 2px 8px !important; font-size: 0.75rem !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def load_db_from_sheets():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        if df.empty: return {"participants": [], "assignments": {}, "locked": False}
        assignments = {row["Name"]: json.loads(row["Teams"]) for _, row in df[df["Type"] == "Assignment"].iterrows()}
        return {"participants": df[df["Type"] == "Player"]["Name"].tolist(), "assignments": assignments, "locked": not df[df["Type"] == "Status"].empty}
    except: return {"participants": [], "assignments": {}, "locked": False}

def save_db_to_sheets(db_data):
    rows = [{"Type": "Player", "Name": p, "Teams": ""} for p in db_data["participants"]]
    rows.extend([{"Type": "Assignment", "Name": name, "Teams": json.dumps(teams)} for name, teams in db_data["assignments"].items()])
    if db_data["locked"]: rows.append({"Type": "Status", "Name": "Locked", "Teams": ""})
    conn.update(worksheet="Sheet1", data=pd.DataFrame(rows))

db = load_db_from_sheets()

def process_match_calculations():
    team_points = {team: 0 for team in ALL_TEAMS}
    activity_logs = []
    eliminated_teams_set = set()
    processed_fixtures_list = []
    
    try:
        sheet_df = conn.read(worksheet="Scores", ttl=0)
        if 'EliminatedTeam' in sheet_df.columns:
            eliminated_teams_set = set(sheet_df['EliminatedTeam'].dropna().astype(str).str.strip().unique())
            eliminated_teams_set.discard('')
    except: pass

    if not sheet_df.empty:
        for _, row in sheet_df.iterrows():
            home, away = str(row.get('HomeTeam', '')).strip(), str(row.get('AwayTeam', '')).strip()
            hg, ag = row.get('HomeScore'), row.get('AwayScore')
            status = str(row.get('Status', '')).lower()
            date = str(row.get('Date', 'TBD'))
            
            is_finished = status in ['final', 'ft', 'finished']
            processed_fixtures_list.append({"Date": date, "Match": f"{home} vs {away}", "Result": f"{hg}-{ag}" if pd.notna(hg) else "Scheduled", "Status": "FT" if is_finished else "Upcoming"})
            
            if pd.notna(hg) and pd.notna(ag):
                hp = (3 if hg > ag else 0) + (1 if hg == ag else 0) + hg
                ap = (3 if ag > hg else 0) + (1 if ag == hg else 0) + ag
                team_points[home] += hp
                team_points[away] += ap
                activity_logs.append({"Date": date, "Match": f"{home} {hg}-{ag} {away}", "Team": home, "Points": hp, "Status": "FT" if is_finished else "Live"})
                activity_logs.append({"Date": date, "Match": f"{home} {hg}-{ag} {away}", "Team": away, "Points": ap, "Status": "FT" if is_finished else "Live"})
    return team_points, activity_logs, eliminated_teams_set, processed_fixtures_list

team_scores, raw_activity_logs, eliminated_nations, full_calendar_schedule = process_match_calculations()

# --- APP INTERFACE ---
if not db["locked"]:
    st.write("Registration is open...")
else:
    tab1, tab2, tab3 = st.tabs(["🏆 Standings", "📊 Match Activity", "📅 Fixtures"])
    team_to_player = {t: p for p, teams in db["assignments"].items() for t in teams}

    with tab1:
        st.subheader("Leaderboard")
        data = [{"Player": p, "Points": sum([team_scores.get(t, 0) for t in teams])} for p, teams in db["assignments"].items()]
        for _, row in pd.DataFrame(data).sort_values("Points", ascending=False).iterrows():
            st.markdown(f"<div class='premium-card'>{row['Player']}: {row['Points']} PTS</div>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Match Activity")
        players = ["All Players"] + sorted(list(db["assignments"].keys()))
        selected_player = st.selectbox("Filter by Player:", players)
        
        logs = pd.DataFrame(raw_activity_logs).iloc[::-1]
        if selected_player != "All Players":
            relevant_teams = db["assignments"][selected_player]
            logs = logs[logs["Team"].isin(relevant_teams)]
        
        for _, row in logs.iterrows():
            st.markdown(f"<div class='premium-card'>{row['Match']} - {row['Points']} PTS</div>", unsafe_allow_html=True)

    with tab3:
        st.subheader("Tournament Calendar")
        dates = ["All Dates"] + sorted(list(set([str(d) for d in pd.DataFrame(full_calendar_schedule)["Date"]])))
        selected_date = st.selectbox("Filter by Date:", dates)
        
        cal = pd.DataFrame(full_calendar_schedule).iloc[::-1]
        if selected_date != "All Dates":
            cal = cal[cal["Date"] == selected_date]
            
        for _, row in cal.iterrows():
            st.markdown(f"<div class='premium-card'>{row['Date']} | {row['Match']} | {row['Result']}</div>", unsafe_allow_html=True)

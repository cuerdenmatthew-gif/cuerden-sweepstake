import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random
import math
import pandas as pd
import json
import os
import base64

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

# --- 1.5 PREMIUM THEME CSS ---
page_bg = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Inter:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { background: linear-gradient(-45deg, #1A0033, #5F00A8, #8000FF, #3A0066) !important; background-size: 400% 400% !important; animation: gradientBG 15s ease infinite !important; color: #FFFFFF !important; }
@keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
[data-testid="stAppViewContainer"] > .main { background: rgba(15, 5, 25, 0.65) !important; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background-color: #120024 !important; background-image: linear-gradient(180deg, #1C0038 0%, #0A0014 100%) !important; border-right: 1px solid rgba(255, 255, 255, 0.1) !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] li, [data-testid="stSidebar"] div { color: #FFFFFF !important; }
h1, h2, h3, h4, p, span, label, li, [data-testid="stMarkdownContainer"] p { color: #FFFFFF !important; }
div[data-baseweb="select"] > div { background-color: #1E052D !important; color: #FFFFFF !important; border: 1px solid rgba(198, 255, 0, 0.4) !important; }
div[data-baseweb="select"] input { pointer-events: none !important; caret-color: transparent !important; }
div[data-baseweb="select"] span, div[data-baseweb="select"] div { color: #FFFFFF !important; }
ul[role="listbox"], li[role="option"] { background-color: #1E052D !important; color: #FFFFFF !important; }
div[data-baseweb="input"] { background-color: #1E052D !important; border: 1px solid rgba(198, 255, 0, 0.4) !important; }
div[data-baseweb="input"] input { color: #FFFFFF !important; pointer-events: auto !important; }
div[data-testid="stExpander"] { background-color: #1E052D !important; border: 1px solid rgba(255, 255, 255, 0.15) !important; }
div[data-testid="stExpander"] summary { background-color: #1E052D !important; color: #FFFFFF !important; }
div.stButton > button { background-color: #4C0099 !important; color: #C6FF00 !important; border: 1px solid rgba(198, 255, 0, 0.3) !important; font-weight: 600 !important; box-shadow: 0 4px 12px rgba(128, 0, 255, 0.3) !important; }
.premium-title { font-family: 'Montserrat', sans-serif; font-size: 3.5rem; font-weight: 800; text-align: center; background: linear-gradient(to right, #FFFFFF, #C6FF00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; }
.premium-subtitle { font-family: 'Inter', sans-serif; text-align: center; color: #E61D25; font-weight: 600; letter-spacing: 3px; text-transform: uppercase; font-size: 0.9rem; margin-bottom: 40px; }
.sidebar-hint-text { position: fixed !important; top: 15px !important; left: 55px !important; z-index: 9999999 !important; font-family: 'Inter', sans-serif !important; font-size: 0.8rem !important; font-weight: 600 !important; color: #C6FF00 !important; background: rgba(40, 0, 80, 0.95) !important; padding: 4px 10px !important; border-radius: 6px !important; }
.premium-card { background: rgba(30, 5, 45, 0.85) !important; border: 1px solid rgba(255, 255, 255, 0.12) !important; border-left: 4px solid #C6FF00 !important; border-radius: 8px !important; padding: 15px 20px !important; margin-bottom: 12px !important; display: flex !important; justify-content: space-between !important; align-items: center !important; font-family: 'Inter', sans-serif !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important; }
.card-left { display: flex !important; flex-direction: column !important; gap: 4px !important; }
.card-title { font-size: 1.15rem !important; font-weight: 700 !important; color: #FFFFFF !important; }
.card-subtitle { font-size: 0.85rem !important; color: rgba(255, 255, 255, 0.6) !important; }
.card-right { text-align: right !important; display: flex !important; flex-direction: column !important; align-items: flex-end !important; gap: 4px !important; }
.badge-ft { background-color: rgba(230, 29, 37, 0.2) !important; color: #E61D25 !important; border: 1px solid #E61D25 !important; padding: 2px 8px !important; border-radius: 4px !important; font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase; }
.badge-upcoming { background-color: rgba(198, 255, 0, 0.1) !important; color: #C6FF00 !important; border: 1px solid #C6FF00 !important; padding: 2px 8px !important; border-radius: 4px !important; font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase; }
.badge-live { background-color: rgba(0, 230, 115, 0.15) !important; color: #00E673 !important; border: 1px solid #00E673 !important; padding: 2px 8px !important; border-radius: 4px !important; font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase; }
.score-display { font-family: 'Montserrat', sans-serif !important; font-size: 1.4rem !important; font-weight: 800 !important; color: #C6FF00 !important; letter-spacing: 1px; }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# --- 2. CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_db_from_sheets():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        if df.empty: return {"participants": [], "assignments": {}, "locked": False}
        participants = df[df["Type"] == "Player"]["Name"].tolist()
        locked = not df[df["Type"] == "Status"].empty
        assignments = {}
        assign_rows = df[df["Type"] == "Assignment"]
        for _, row in assign_rows.iterrows():
            assignments[row["Name"]] = json.loads(row["Teams"])
        return {"participants": participants, "assignments": assignments, "locked": locked}
    except: return {"participants": [], "assignments": {}, "locked": False}

def save_db_to_sheets(db_data):
    rows = []
    for p in db_data["participants"]: rows.append({"Type": "Player", "Name": p, "Teams": ""})
    for name, teams in db_data["assignments"].items(): rows.append({"Type": "Assignment", "Name": name, "Teams": json.dumps(teams)})
    if db_data["locked"]: rows.append({"Type": "Status", "Name": "Locked", "Teams": ""})
    new_df = pd.DataFrame(rows)
    conn.update(worksheet="Sheet1", data=new_df)

db = load_db_from_sheets()

# --- 3. MATCH CALCULATIONS ENGINE ---
def process_match_calculations():
    team_points = {team: 0 for team in ALL_TEAMS}
    activity_logs = []
    eliminated_teams_set = set()
    processed_fixtures_list = []
    
    try:
        sheet_df = conn.read(worksheet="Scores", ttl=0)
        if 'EliminatedTeam' in sheet_df.columns:
            eliminated_teams_set = set(sheet_df['EliminatedTeam'].dropna().unique())
    except: pass

    if not sheet_df.empty:
        for _, row in sheet_df.iterrows():
            home, away = str(row.get('HomeTeam', '')).strip(), str(row.get('AwayTeam', '')).strip()
            g_winner, g_runnerup = str(row.get('GroupWinner', '')).strip(), str(row.get('GroupRunnerUp', '')).strip()
            
            if g_winner in team_points: team_points[g_winner] += 2
            if g_runnerup in team_points: team_points[g_runnerup] += 1
            
            if not home or not away or pd.isna(home) or pd.isna(away): continue
            hg, ag = row.get('HomeScore'), row.get('AwayScore')
            is_finished = str(row.get('Status', '')).lower() in ['final', 'ft', 'finished']
            is_knockout = any(w in str(row.get('Stage', '')).lower() for w in ['knockout', 'round', 'quarter', 'semi', 'final'])
            
            multiplier = 2 if is_knockout else 1
            if hg is not None and ag is not None:
                if hg > ag: hp, ap = (3*multiplier)+(hg*multiplier), 0
                elif ag > hg: hp, ap = 0, (3*multiplier)+(ag*multiplier)
                else: hp, ap = 1*multiplier, 1*multiplier
                team_points[home] += hp; team_points[away] += ap
                processed_fixtures_list.append({"Match": f"{home} vs {away}", "Result": f"{hg}-{ag}", "Status": "FT" if is_finished else "Live"})
            else:
                processed_fixtures_list.append({"Match": f"{home} vs {away}", "Result": "📅", "Status": "Upcoming"})
                
    return team_points, activity_logs, eliminated_teams_set, processed_fixtures_list

team_scores, raw_activity_logs, eliminated_nations, full_calendar_schedule = process_match_calculations()

# --- 4. DISPLAY ---
st.markdown("<div style='text-align: center;'><div class='premium-title'>Cuerden & Co<br>WC26 Sweepstake</div><div class='premium-subtitle'>Official Match Tracker</div></div>", unsafe_allow_html=True)

st.sidebar.markdown("### 🏳️ Active Nations")
for team in ALL_TEAMS:
    if team not in eliminated_nations:
        st.sidebar.markdown(f"{TEAM_FLAGS.get(team, '🏳️')} {team}")

if not db["locked"]:
    # ... (Keep your existing registration code)
    pass
else:
    tab1, tab2, tab3 = st.tabs(["🏆 Standings & Teams", "📊 Match Activity", "📅 Fixtures Calendar"])
    with tab1:
        st.subheader("📋 Your Teams")
        for p, teams in db["assignments"].items():
            with st.expander(f"{p}'s Teams ({len(teams)})"):
                formatted_teams = []
                for t in teams:
                    if t in eliminated_nations:
                        formatted_teams.append(f"<s>{TEAM_FLAGS.get(t, '🏳️')} {t}</s>")
                    else:
                        formatted_teams.append(f"{TEAM_FLAGS.get(t, '🏳️')} {t}")
                st.write(", ".join(formatted_teams), unsafe_allow_html=True)
    # ... (Rest of your original code)

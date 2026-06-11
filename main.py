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

# 72 Group Match Calendar Schedule Matrix with Official Kickoff Times Included
FIXED_FIXTURES = [
    {"Date": "June 11", "Time": "Finished", "Home": "Mexico", "Away": "South Africa"},
    {"Date": "June 12", "Time": "03:00", "Home": "South Korea", "Away": "Czechia"},
    {"Date": "June 12", "Time": "20:00", "Home": "Canada", "Away": "Bosnia and Herzegovina"},
    {"Date": "June 13", "Time": "02:00", "Home": "USA", "Away": "Paraguay"},
    {"Date": "June 13", "Time": "20:00", "Home": "Qatar", "Away": "Switzerland"},
    {"Date": "June 13", "Time": "23:00", "Home": "Brazil", "Away": "Morocco"},
    {"Date": "June 14", "Time": "02:00", "Home": "Haiti", "Away": "Scotland"},
    {"Date": "June 14", "Time": "05:00", "Home": "Australia", "Away": "Türkiye"},
    {"Date": "June 14", "Time": "18:00", "Home": "Germany", "Away": "Curaçao"},
    {"Date": "June 14", "Time": "21:00", "Home": "Netherlands", "Away": "Japan"},
    {"Date": "June 15", "Time": "00:00", "Home": "Ivory Coast", "Away": "Ecuador"},
    {"Date": "June 15", "Time": "03:00", "Home": "Sweden", "Away": "Tunisia"},
    {"Date": "June 15", "Time": "17:00", "Home": "Spain", "Away": "Cabo Verde"},
    {"Date": "June 15", "Time": "20:00", "Home": "Belgium", "Away": "Egypt"},
    {"Date": "June 15", "Time": "23:00", "Home": "Saudi Arabia", "Away": "Uruguay"},
    {"Date": "June 16", "Time": "02:00", "Home": "Iran", "Away": "New Zealand"},
    {"Date": "June 16", "Time": "20:00", "Home": "France", "Away": "Senegal"},
    {"Date": "June 16", "Time": "23:00", "Home": "Iraq", "Away": "Norway"},
    {"Date": "June 17", "Time": "02:00", "Home": "Argentina", "Away": "Algeria"},
    {"Date": "June 17", "Time": "05:00", "Home": "Austria", "Away": "Jordan"},
    {"Date": "June 17", "Time": "18:00", "Home": "Portugal", "Away": "DR Congo"},
    {"Date": "June 17", "Time": "21:00", "Home": "England", "Away": "Croatia"},
    {"Date": "June 18", "Time": "00:00", "Home": "Ghana", "Away": "Panama"},
    {"Date": "June 18", "Time": "03:00", "Home": "Uzbekistan", "Away": "Colombia"},
    {"Date": "June 18", "Time": "17:00", "Home": "Czechia", "Away": "South Africa"},
    {"Date": "June 18", "Time": "20:00", "Home": "Switzerland", "Away": "Bosnia and Herzegovina"},
    {"Date": "June 18", "Time": "23:00", "Home": "Canada", "Away": "Qatar"},
    {"Date": "June 19", "Time": "02:00", "Home": "Mexico", "Away": "South Korea"},
    {"Date": "June 19", "Time": "20:00", "Home": "USA", "Away": "Australia"},
    {"Date": "June 19", "Time": "23:00", "Home": "Scotland", "Away": "Morocco"},
    {"Date": "June 20", "Time": "01:30", "Home": "Brazil", "Away": "Haiti"},
    {"Date": "June 20", "Time": "04:00", "Home": "Türkiye", "Away": "Paraguay"},
    {"Date": "June 20", "Time": "18:00", "Home": "Netherlands", "Away": "Sweden"},
    {"Date": "June 20", "Time": "21:00", "Home": "Germany", "Away": "Ivory Coast"},
    {"Date": "June 21", "Time": "01:00", "Home": "Ecuador", "Away": "Curaçao"},
    {"Date": "June 21", "Time": "05:00", "Home": "Tunisia", "Away": "Japan"},
    {"Date": "June 21", "Time": "17:00", "Home": "Spain", "Away": "Saudi Arabia"},
    {"Date": "June 21", "Time": "20:00", "Home": "Belgium", "Away": "Iran"},
    {"Date": "June 21", "Time": "23:00", "Home": "Uruguay", "Away": "Cabo Verde"},
    {"Date": "June 22", "Time": "02:00", "Home": "New Zealand", "Away": "Egypt"},
    {"Date": "June 22", "Time": "18:00", "Home": "Argentina", "Away": "Austria"},
    {"Date": "June 22", "Time": "22:00", "Home": "France", "Away": "Iraq"},
    {"Date": "June 23", "Time": "01:00", "Home": "Norway", "Away": "Senegal"},
    {"Date": "June 23", "Time": "04:00", "Home": "Jordan", "Away": "Algeria"},
    {"Date": "June 23", "Time": "18:00", "Home": "Portugal", "Away": "Uzbekistan"},
    {"Date": "June 23", "Time": "21:00", "Home": "England", "Away": "Ghana"},
    {"Date": "June 24", "Time": "00:00", "Home": "Panama", "Away": "Croatia"},
    {"Date": "June 24", "Time": "03:00", "Home": "Colombia", "Away": "DR Congo"},
    {"Date": "June 24", "Time": "20:00", "Home": "Switzerland", "Away": "Canada"},
    {"Date": "June 24", "Time": "20:00", "Home": "Bosnia and Herzegovina", "Away": "Qatar"},
    {"Date": "June 24", "Time": "23:00", "Home": "Morocco", "Away": "Haiti"},
    {"Date": "June 24", "Time": "23:00", "Home": "Scotland", "Away": "Brazil"},
    {"Date": "June 25", "Time": "02:00", "Home": "South Africa", "Away": "South Korea"},
    {"Date": "June 25", "Time": "02:00", "Home": "Czechia", "Away": "Mexico"},
    {"Date": "June 25", "Time": "21:00", "Home": "Curaçao", "Away": "Ivory Coast"},
    {"Date": "June 25", "Time": "21:00", "Home": "Ecuador", "Away": "Germany"},
    {"Date": "June 26", "Time": "00:00", "Home": "Tunisia", "Away": "Netherlands"},
    {"Date": "June 26", "Time": "00:00", "Home": "Japan", "Away": "Sweden"},
    {"Date": "June 26", "Time": "03:00", "Home": "Türkiye", "Away": "USA"},
    {"Date": "June 26", "Time": "03:00", "Home": "Paraguay", "Away": "Australia"},
    {"Date": "June 26", "Time": "20:00", "Home": "Norway", "Away": "France"},
    {"Date": "June 26", "Time": "20:00", "Home": "Senegal", "Away": "Iraq"},
    {"Date": "June 27", "Time": "01:00", "Home": "Cabo Verde", "Away": "Saudi Arabia"},
    {"Date": "June 27", "Time": "01:00", "Home": "Uruguay", "Away": "Spain"},
    {"Date": "June 27", "Time": "04:00", "Home": "New Zealand", "Away": "Belgium"},
    {"Date": "June 27", "Time": "04:00", "Home": "Egypt", "Away": "Iran"},
    {"Date": "June 27", "Time": "22:00", "Home": "Panama", "Away": "England"},
    {"Date": "June 27", "Time": "22:00", "Home": "Croatia", "Away": "Ghana"},
    {"Date": "June 28", "Time": "00:30", "Home": "Colombia", "Away": "Portugal"},
    {"Date": "June 28", "Time": "00:30", "Home": "DR Congo", "Away": "Uzbekistan"},
    {"Date": "June 28", "Time": "03:00", "Home": "Algeria", "Away": "Austria"},
    {"Date": "June 28", "Time": "03:00", "Home": "Jordan", "Away": "Argentina"}
]

# --- 1.5 PREMIUM THEME CSS ---
page_bg = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Inter:wght@400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #1A0033, #5F00A8, #8000FF, #3A0066) !important;
    background-size: 400% 400% !important;
    animation: gradientBG 15s ease infinite !important;
    color: #FFFFFF !important;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
[data-testid="stAppViewContainer"] > .main {
    background: rgba(15, 5, 25, 0.65) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}
[data-testid="stHeader"] { background: transparent !important; }

[data-testid="stSidebar"] {
    background-color: #120024 !important;
    background-image: linear-gradient(180deg, #1C0038 0%, #0A0014 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] li, [data-testid="stSidebar"] div {
    color: #FFFFFF !important;
}

h1, h2, h3, h4, p, span, label, li, [data-testid="stMarkdownContainer"] p { color: #FFFFFF !important; }

div[data-baseweb="select"] > div {
    background-color: #1E052D !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(198, 255, 0, 0.4) !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] div { color: #FFFFFF !important; }
ul[role="listbox"], li[role="option"] { background-color: #1E052D !important; color: #FFFFFF !important; }

div[data-baseweb="input"] {
    background-color: #1E052D !important;
    border: 1px solid rgba(198, 255, 0, 0.4) !important;
}
div[data-baseweb="input"] input { color: #FFFFFF !important; }

div[data-testid="stExpander"] {
    background-color: #1E052D !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
}
div[data-testid="stExpander"] summary { background-color: #1E052D !important; color: #FFFFFF !important; }

div.stButton > button {
    background-color: #4C0099 !important;
    color: #C6FF00 !important;
    border: 1px solid rgba(198, 255, 0, 0.3) !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(128, 0, 255, 0.3) !important;
}
.premium-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(to right, #FFFFFF, #C6FF00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.premium-subtitle {
    font-family: 'Inter', sans-serif;
    text-align: center;
    color: #E61D25;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-size: 0.9rem;
    margin-bottom: 40px;
}
.sidebar-hint-text {
    position: fixed !important;
    top: 15px !important;
    left: 55px !important;
    z-index: 9999999 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #C6FF00 !important;
    background: rgba(40, 0, 80, 0.95) !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
}

.premium-card {
    background: rgba(30, 5, 45, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-left: 4px solid #C6FF00 !important;
    border-radius: 8px !important;
    padding: 15px 20px !important;
    margin-bottom: 12px !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important;
}
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
    
    group_stats = {t: {"pts": 0, "gd": 0, "gf": 0, "mp": 0} for t in ALL_TEAMS}
    
    scores_dict = {}
    try:
        sheet_df = conn.read(worksheet="Scores", ttl=0)
        if not sheet_df.empty:
            for _, row in sheet_df.iterrows():
                h = str(row.get('HomeTeam', '')).strip()
                a = str(row.get('AwayTeam', '')).strip()
                if h and a:
                    scores_dict[f"{h} vs {a}"] = {
                        "HomeScore": row.get('HomeScore'),
                        "AwayScore": row.get('AwayScore'),
                        "Status": str(row.get('Status', '')).strip().lower(),
                        "Stage": str(row.get('Stage', '')).strip().lower()
                    }
    except: pass

    for f in FIXED_FIXTURES:
        home, away, match_date, match_time = f["Home"], f["Away"], f["Date"], f["Time"]
        key = f"{home} vs {away}"
        
        hg, ag, is_finished, stage_label = None, None, False, "group stage"
        
        if key in scores_dict:
            s_data = scores_dict[key]
            if not pd.isna(s_data["HomeScore"]) and not pd.isna(s_data["AwayScore"]):
                hg, ag = int(s_data["HomeScore"]), int(s_data["AwayScore"])
                is_finished = s_data["Status"] in ['final', 'ft', 'finished', 'complete']
                stage_label = s_data["Stage"]
                
        is_knockout = any(w in stage_label for w in ['knockout', 'round', 'quarter', 'semi', 'final'])
        multiplier = 2 if is_knockout else 1
        
        processed_fixtures_list.append({
            "Date": match_date,
            "Time": match_time,
            "Match": f"{TEAM_FLAGS.get(home, '🏳️')} {home} vs {away} {TEAM_FLAGS.get(away, '🏳️')}",
            "Result": f"{hg} - {ag}" if hg is not None else "📅 Scheduled",
            "Status": "FT" if is_finished else ("Live" if hg is not None else "Upcoming")
        })

        if hg is None or ag is None:
            continue

        if not is_knockout and is_finished:
            group_stats[home]["mp"] += 1; group_stats[home]["gf"] += hg; group_stats[home]["gd"] += (hg - ag)
            group_stats[away]["mp"] += 1; group_stats[away]["gf"] += ag; group_stats[away]["gd"] += (ag - hg)
            if hg > ag: group_stats[home]["pts"] += 3
            elif ag > hg: group_stats[away]["pts"] += 3
            else: group_stats[home]["pts"] += 1; group_stats[away]["pts"] += 1

        hp, ap = 0, 0
        h_break, a_break = [], []
        
        if hg > ag: hp += (3 * multiplier); h_break.append(f"Win (+{3 * multiplier})")
        elif hg == ag: hp += (1 * multiplier); h_break.append(f"Draw (+{1 * multiplier})")
        if hg > 0: hp += (hg * multiplier); h_break.append(f"{hg} Goal{'s' if hg>1 else ''} (+{hg * multiplier})")
        if ag == 0: hp += (1 * multiplier); h_break.append(f"Clean Sheet (+{1 * multiplier})")
        if ag >= 3: hp -= (1 * multiplier); h_break.append(f"Conceded 3+ (-{1 * multiplier})")

        if ag > hg: ap += (3 * multiplier); a_break.append(f"Win (+{3 * multiplier})")
        elif ag == hg: ap += (1 * multiplier); a_break.append(f"Draw (+{1 * multiplier})")
        if ag > 0: ap += (ag * multiplier); a_break.append(f"{ag} Goal{'s' if ag>1 else ''} (+{ag * multiplier})")
        if hg == 0: ap += (1 * multiplier); a_break.append(f"Clean Sheet (+{1 * multiplier})")
        if hg >= 3: ap -= (1 * multiplier); a_break.append(f"Conceded 3+ (-{1 * multiplier})")

        team_points[home] += hp
        team_points[away] += ap
        
        activity_logs.append({"Status": "FT" if is_finished else "Live", "Match": f"{home} {hg} - {ag} {away}", "Team": home, "Player": "", "Points Earned": hp, "Breakdown": " | ".join(h_break)})
        activity_logs.append({"Status": "FT" if is_finished else "Live", "Match": f"{home} {hg} - {ag} {away}", "Team": away, "Player": "", "Points Earned": ap, "Breakdown": " | ".join(a_break)})

    return team_points, activity_logs, eliminated_teams_set, processed_fixtures_list

team_scores, raw_activity_logs, eliminated_nations, full_calendar_schedule = process_match_calculations()

# --- 4. DISPLAY LAYOUT ---
if os.path.exists("logo.png"):
    try:
        with open("logo.png", "rb") as f:
            img_encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"<div style='display: flex; justify-content: center; width: 100%; padding-top: 10px;'><img src='data:image/png;base64,{img_encoded}' style='width: 130px;'></div>", unsafe_allow_html=True)
    except: pass

st.markdown("<div style='text-align: center;'><div class='premium-title'>Cuerden & Co<br>WC26 Sweepstake</div><div class='premium-subtitle'>Official Match Tracker</div></div>", unsafe_allow_html=True)
st.markdown("<div class='sidebar-hint-text'>👈 Rules & Teams</div>", unsafe_allow_html=True)

st.sidebar.markdown("### 📜 Point System\n* **Win:** 3 pts | **Draw:** 1 pt\n* **Goal Scored:** 1 pt\n* **Clean Sheet:** 1 pt\n* **3+ Goals Conceded:** -1 pt\n* 🥇 **Group Winner:** +2 pts\n* 🥈 **Group 2nd Place:** +1 pt\n* 🏆 **World Cup Champion:** +10 pts")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏳️ Active Nations")
for team in ALL_TEAMS:
    if team not in eliminated_nations: st.sidebar.markdown(f"{TEAM_FLAGS.get(team, '🏳️')} {team}")

st.sidebar.markdown("---")
admin_input = st.sidebar.text_input("Admin Password", type="password")
if admin_input == ADMIN_PASSWORD and st.sidebar.button("RESET SWEEPSTAKE"):
    save_db_to_sheets({"participants": [], "assignments": {}, "locked": False})
    st.rerun()

if not db["locked"]:
    st.header("Step 1: Registration Phase")
    player_name = st.text_input("Enter name to join:")
    if st.button("Register") and player_name and player_name not in db["participants"]:
        db["participants"].append(player_name)
        save_db_to_sheets(db)
        st.rerun()
    st.write(f"**Registered Players ({len(db['participants'])}):** " + ", ".join(db["participants"]))
    
    if len(db["participants"]) > 0:
        per_person = math.floor(48 / len(db["participants"]))
        prize_pot = len(db["participants"]) * 20
        st.success(f"**Current Prize Pot: £{prize_pot}**")
        
        if admin_input == ADMIN_PASSWORD and st.button("🔴 EXECUTE RANDOM DRAW"):
            TOP_13 = ["Spain", "France", "Argentina", "England", "Brazil", "Portugal", "Germany", "Netherlands", "Morocco", "Norway", "Belgium", "Colombia", "Senegal"]
            shuffled_top = TOP_13.copy(); random.shuffle(shuffled_top)
            
            db["assignments"] = {person: [] for person in db["participants"]}
            for person in db["participants"]:
                if shuffled_top: db["assignments"][person].append(shuffled_top.pop(0))
            
            remaining_pool = shuffled_top + [t for t in ALL_TEAMS if t not in TOP_13]; random.shuffle(remaining_pool)
            for person in db["participants"]:
                needed = per_person - len(db["assignments"][person])
                for _ in range(needed):
                    if remaining_pool: db["assignments"][person].append(remaining_pool.pop(0))
            
            if remaining_pool:
                lucky_players = db["participants"].copy(); random.shuffle(lucky_players)
                while remaining_pool and lucky_players: db["assignments"][lucky_players.pop(0)].append(remaining_pool.pop(0))
                        
            db["locked"] = True; save_db_to_sheets(db); st.rerun()
else:
    tab1, tab2, tab3 = st.tabs(["🏆 Standings & Teams", "📊 Match Activity", "📅 Fixtures Calendar"])
    team_to_player = {t: p for p, teams in db["assignments"].items() for t in teams}
            
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("📋 Your Teams")
            for p, teams in db["assignments"].items():
                with st.expander(f"{p}'s Teams ({len(teams)})"):
                    st.write(", ".join([f"{TEAM_FLAGS.get(t, '🏳️')} {t}" for t in teams]))
        with c2:
            st.subheader("📊 Leaderboard")
            table = [{"Player": p, "Total Points": sum([team_scores.get(t, 0) for t in teams])} for p, teams in db["assignments"].items()]
            if table: 
                df_leaderboard = pd.DataFrame(table).sort_values("Total Points", ascending=False)
                for idx, row in df_leaderboard.iterrows():
                    st.markdown(f"""
                    <div class="premium-card">
                        <div class="card-left">
                            <div class="card-title">🏆 {row['Player']}</div>
                            <div class="card-subtitle">Tournament Sweepstake Contender</div>
                        </div>
                        <div class="card-right">
                            <div class="score-display">{row['Total Points']} PTS</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            prize_pot = len(db["participants"]) * 20
            st.success(f"**Final Tournament Prize Pot: £{prize_pot}**")
            st.markdown(f"💰 **Official Cash Split Structure:**\n* 🥇 **1st Place:** £{prize_pot - 60}\n* 🥈 **2nd Place:** £40 *(Double your money!)*\n* 🥾 **Last Place:** £20 *(Money back)*")

    with tab2:
        st.subheader("⚽ Match Activity Points Breakdown")
        processed_logs = []
        for log in raw_activity_logs:
            log_copy = log.copy()
            log_copy["Player"] = team_to_player.get(log["Team"], "🍿 Unassigned")
            processed_logs.append(log_copy)
            
        activity_df = pd.DataFrame(processed_logs)
        if not activity_df.empty:
            filter_option = st.selectbox("Filter Match Activity by Player:", ["All Players"] + sorted(list(db["assignments"].keys())))
            filtered_df = activity_df if filter_option == "All Players" else activity_df[activity_df["Player"] == filter_option]
            
            for _, row in filtered_df.iterrows():
                badge_style = "badge-ft" if row['Status'] == "FT" else "badge-live"
                st.markdown(f"""
                <div class="premium-card">
                    <div class="card-left">
                        <div class="card-title">{TEAM_FLAGS.get(row['Team'], '🏳️')} {row['Match']}</div>
                        <div class="card-subtitle"><b>Owner:</b> {row['Player']} | {row['Breakdown']}</div>
                    </div>
                    <div class="card-right">
                        <div style="margin-bottom: 4px;"><span class="{badge_style}">{row['Status']}</span></div>
                        <div class="score-display">{'+' if row['Points Earned'] >= 0 else ''}{row['Points Earned']} PTS</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Log final scores in your Google Sheet spreadsheet under the 'Scores' tab to populate updates!")

    with tab3:
        st.subheader("📅 Group Stage Tournament Calendar")
        cal_df = pd.DataFrame(full_calendar_schedule)
        filter_date = st.selectbox("Filter Calendar by Date:", ["All Dates"] + sorted(list(set(cal_df["Date"].tolist()))))
        display_cal = cal_df if filter_date == "All Dates" else cal_df[cal_df["Date"] == filter_date]
        
        for _, row in display_cal.iterrows():
            badge_style = "badge-ft" if row['Status'] == "FT" else ("badge-live" if row['Status'] == "Live" else "badge-upcoming")
            time_label = f"⏱️ Kickoff: {row['Time']}" if row['Status'] == "Upcoming" else "🏁 Match Concluded"
            st.markdown(f"""
            <div class="premium-card">
                <div class="card-left">
                    <div class="card-title">{row['Match']}</div>
                    <div class="card-subtitle">📅 Date: {row['Date']} | {time_label}</div>
                </div>
                <div class="card-right">
                    <div style="margin-bottom: 4px;"><span class="{badge_style}">{row['Status']}</span></div>
                    <div class="score-display">{row['Result']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

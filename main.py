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

FIXED_FIXTURES = [
    {"Date": "June 11", "Home": "Mexico", "Away": "South Africa"},
    {"Date": "June 11", "Home": "Canada", "Away": "Switzerland"},
    {"Date": "June 12", "Home": "USA", "Away": "Paraguay"},
    {"Date": "June 12", "Home": "Brazil", "Away": "Morocco"},
    {"Date": "June 13", "Home": "Germany", "Away": "Curaçao"},
    {"Date": "June 13", "Home": "Spain", "Away": "Cabo Verde"},
    {"Date": "June 13", "Home": "Argentina", "Away": "Algeria"},
    {"Date": "June 14", "Home": "Netherlands", "Away": "Japan"},
    {"Date": "June 14", "Home": "Belgium", "Away": "Egypt"},
    {"Date": "June 14", "Home": "France", "Away": "Senegal"},
    {"Date": "June 14", "Home": "Portugal", "Away": "Uzbekistan"},
    {"Date": "June 15", "Home": "England", "Away": "Croatia"},
    {"Date": "June 15", "Home": "South Korea", "Away": "Czechia"},
    {"Date": "June 15", "Home": "Qatar", "Away": "Bosnia and Herzegovina"},
    {"Date": "June 16", "Home": "Haiti", "Away": "Scotland"},
    {"Date": "June 16", "Home": "Australia", "Away": "Türkiye"},
    {"Date": "June 16", "Home": "Ivory Coast", "Away": "Ecuador"},
    {"Date": "June 17", "Home": "Tunisia", "Away": "Sweden"},
    {"Date": "June 17", "Home": "Iran", "Away": "New Zealand"},
    {"Date": "June 17", "Home": "Saudi Arabia", "Away": "Uruguay"},
    {"Date": "June 17", "Home": "Norway", "Away": "Iraq"},
    {"Date": "June 18", "Home": "Austria", "Away": "Jordan"},
    {"Date": "June 18", "Home": "Colombia", "Away": "DR Congo"},
    {"Date": "June 18", "Home": "Ghana", "Away": "Panama"},
    {"Date": "June 19", "Home": "Canada", "Away": "Qatar"},
    {"Date": "June 19", "Home": "Mexico", "Away": "South Korea"},
    {"Date": "June 20", "Home": "Switzerland", "Away": "Bosnia and Herzegovina"},
    {"Date": "June 20", "Home": "USA", "Away": "Australia"},
    {"Date": "June 20", "Home": "Brazil", "Away": "Haiti"},
    {"Date": "June 21", "Home": "South Africa", "Away": "Czechia"},
    {"Date": "June 21", "Home": "Paraguay", "Away": "Türkiye"},
    {"Date": "June 21", "Home": "Morocco", "Away": "Scotland"},
    {"Date": "June 22", "Home": "Germany", "Away": "Ivory Coast"},
    {"Date": "June 22", "Home": "Netherlands", "Away": "Tunisia"},
    {"Date": "June 22", "Home": "Belgium", "Away": "Iran"},
    {"Date": "June 23", "Home": "Curaçao", "Away": "Ecuador"},
    {"Date": "June 23", "Home": "Japan", "Away": "Sweden"},
    {"Date": "June 23", "Home": "Egypt", "Away": "New Zealand"},
    {"Date": "June 24", "Home": "Spain", "Away": "Saudi Arabia"},
    {"Date": "June 24", "Home": "France", "Away": "Norway"},
    {"Date": "June 24", "Home": "Argentina", "Away": "Austria"},
    {"Date": "June 25", "Home": "Cabo Verde", "Away": "Uruguay"},
    {"Date": "June 25", "Home": "Senegal", "Away": "Iraq"},
    {"Date": "June 25", "Home": "Algeria", "Away": "Jordan"},
    {"Date": "June 26", "Home": "Portugal", "Away": "Colombia"},
    {"Date": "June 26", "Home": "England", "Away": "Ghana"},
    {"Date": "June 26", "Home": "Uzbekistan", "Away": "DR Congo"},
    {"Date": "June 27", "Home": "Croatia", "Away": "Panama"},
    {"Date": "June 27", "Home": "Mexico", "Away": "Czechia"},
    {"Date": "June 27", "Home": "South Africa", "Away": "South Korea"},
    {"Date": "June 28", "Home": "Canada", "Away": "Bosnia and Herzegovina"},
    {"Date": "June 28", "Home": "Switzerland", "Away": "Qatar"},
    {"Date": "June 28", "Home": "Brazil", "Away": "Scotland"},
    {"Date": "June 29", "Home": "Morocco", "Away": "Haiti"},
    {"Date": "June 29", "Home": "USA", "Away": "Türkiye"},
    {"Date": "June 29", "Home": "Paraguay", "Away": "Australia"},
    {"Date": "June 30", "Home": "Germany", "Away": "Ecuador"},
    {"Date": "June 30", "Home": "Curaçao", "Away": "Ivory Coast"},
    {"Date": "July 01", "Home": "Netherlands", "Away": "Sweden"},
    {"Date": "July 01", "Home": "Japan", "Away": "Tunisia"},
    {"Date": "July 01", "Home": "Belgium", "Away": "New Zealand"},
    {"Date": "July 02", "Home": "Egypt", "Away": "Iran"},
    {"Date": "July 02", "Home": "Spain", "Away": "Uruguay"},
    {"Date": "July 02", "Home": "Cabo Verde", "Away": "Saudi Arabia"},
    {"Date": "July 03", "Home": "France", "Away": "Iraq"},
    {"Date": "July 03", "Home": "Senegal", "Away": "Norway"},
    {"Date": "July 03", "Home": "Argentina", "Away": "Jordan"},
    {"Date": "July 04", "Home": "Algeria", "Away": "Austria"},
    {"Date": "July 04", "Home": "Portugal", "Away": "DR Congo"},
    {"Date": "July 04", "Home": "Uzbekistan", "Away": "Colombia"},
    {"Date": "July 05", "Home": "England", "Away": "Panama"},
    {"Date": "July 05", "Home": "Croatia", "Away": "Ghana"}
]

# --- 1.5 ANTI-LIGHT-MODE CSS OVERRIDES ---
page_bg = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Inter:wght@400;600&display=swap');

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

/* HARD COMPONENT COLOR LOCKDOWN (IMMUNE TO DEVICE CHASSIS TOGGLES) */
div[data-baseweb="select"] > div {
    background-color: #1E052D !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(198, 255, 0, 0.4) !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] div {
    color: #FFFFFF !important;
}
div[data-baseweb="popover"] ul, ul[role="listbox"] {
    background-color: #1E052D !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(198, 255, 0, 0.4) !important;
}
li[role="option"], li[role="option"] span, li[role="option"] div {
    background-color: #1E052D !important;
    color: #FFFFFF !important;
}
li[role="option"]:hover {
    background-color: #4C0099 !important;
    color: #C6FF00 !important;
}

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
div[data-testid="stExpander"] p, div[data-testid="stExpander"] span, div[data-testid="stExpander"] label { color: #FFFFFF !important; }

/* STATIC TABLE DATA OVERRIDES */
div[data-testid="stDataFrame"], div[data-testid="stDataFrame"] * {
    background-color: #12051C !important;
    color: #FFFFFF !important;
}

div.stButton > button {
    background-color: #4C0099 !important;
    color: #C6FF00 !important;
    border: 1px solid rgba(198, 255, 0, 0.3) !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(128, 0, 255, 0.3) !important;
    transition: all 0.2s ease-in-out !important;
}
div.stButton > button:hover {
    background-color: #8000FF !important;
    color: #FFFFFF !important;
    border-color: #C6FF00 !important;
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
    letter-spacing: -1px;
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
    box-shadow: 0 4px 15px rgba(0,0,0,0.6);
}
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
    eliminated_teams = set()
    processed_fixtures_list = []
    
    group_stats = {t: {"pts": 0, "gd": 0, "gf": 0, "mp": 0} for t in ALL_TEAMS}
    
    scores_dict = {}
    try:
        sheet_df = conn.read(worksheet="Scores", ttl=0)
        if not sheet_df.empty:
            for _, row in sheet_df.iterrows():
                h = str(row.get('HomeTeam', '')).strip()
                a = str(row.get('AwayTeam', '')) .strip()
                if h and a:
                    scores_dict[f"{h} vs {a}"] = {
                        "HomeScore": row.get('HomeScore'),
                        "AwayScore": row.get('AwayScore'),
                        "Status": str(row.get('Status', '')).strip().lower(),
                        "Stage": str(row.get('Stage', '')).strip().lower()
                    }
    except: pass

    for f in FIXED_FIXTURES:
        home, away, match_date = f["Home"], f["Away"], f["Date"]
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
            "Match": f"{TEAM_FLAGS.get(home, '🏳️')} {home} vs {away} {TEAM_FLAGS.get(away, '🏳️')}",
            "Result": f"{hg} - {ag}" if hg is not None else "📅 Scheduled",
            "Status": "⏱️ FT" if is_finished else ("🟢 Live" if hg is not None else "Upcoming")
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
        
        activity_logs.append({"Status": "⏱️ FT" if is_finished else "🟢 Live", "Match": f"{home} {hg} - {ag} {away}", "Team": home, "Points Earned": hp, "Breakdown": " | ".join(h_break)})
        activity_logs.append({"Status": "⏱️ FT" if is_finished else "🟢 Live", "Match": f"{home} {hg} - {ag} {away}", "Team": away, "Points Earned": ap, "Breakdown": " | ".join(a_break)})

    return team_points, activity_logs, eliminated_teams, processed_fixtures_list

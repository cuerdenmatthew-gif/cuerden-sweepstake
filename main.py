import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random
import math
import requests
import pandas as pd
import json
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cuerden & Co WC26", page_icon="🏆", layout="wide")
ADMIN_PASSWORD = "Cuerden2026"

# BALLDONTLIE API Setup
API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
API_URL = "https://api.balldontlie.io/worldcup/v1/matches" 

ALL_TEAMS = [
    "USA", "Mexico", "Canada", "Japan", "New Zealand", "Iran", "Argentina", "Uzbekistan", 
    "South Korea", "Jordan", "Australia", "Brazil", "Ecuador", "Uruguay", "Colombia", 
    "Paraguay", "Morocco", "Tunisia", "Egypt", "Algeria", "Ghana", "Cabo Verde", 
    "Saudi Arabia", "Qatar", "England", "Ivory Coast", "South Africa", "Senegal", 
    "France", "Croatia", "Portugal", "Norway", "Germany", "Netherlands", "Belgium", 
    "Switzerland", "Spain", "Austria", "Scotland", "Curaçao", "Haiti", "Panama", 
    "Sweden", "Türkiye", "Czechia", "Bosnia and Herzegovina", "DR Congo", "Iraq"
]

# --- 1.5 PREMIUM WC26 UI THEME ---
page_bg = """
<style>
/* Import premium modern fonts */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Inter:wght@400;600&display=swap');

/* Deep, rich animated gradient background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #0A0012, #290038, #4D0011, #081100);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Glassmorphism blur overlay for the main app */
[data-testid="stAppViewContainer"] > .main {
    background: rgba(15, 10, 20, 0.70);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

/* Make header transparent */
[data-testid="stHeader"] {
    background: transparent;
}

/* Premium Typography for Title */
.premium-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(to right, #FFFFFF, #C6FF00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
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
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# --- 2. CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_db_from_sheets():
    try:
        df = conn.read(ttl=0) 
        if df.empty:
            return {"participants": [], "assignments": {}, "locked": False}
        participants = df[df["Type"] == "Player"]["Name"].tolist()
        locked = not df[df["Type"] == "Status"].empty
        assignments = {}
        assign_rows = df[df["Type"] == "Assignment"]
        for _, row in assign_rows.iterrows():
            assignments[row["Name"]] = json.loads(row["Teams"])
        return {"participants": participants, "assignments": assignments, "locked": locked}
    except:
        return {"participants": [], "assignments": {}, "locked": False}

def save_db_to_sheets(db_data):
    rows = []
    for p in db_data["participants"]:
        rows.append({"Type": "Player", "Name": p, "Teams": ""})
    for name, teams in db_data["assignments"].items():
        rows.append({"Type": "Assignment", "Name": name, "Teams": json.dumps(teams)})
    if db_data["locked"]:
        rows.append({"Type": "Status", "Name": "Locked", "Teams": ""})
    new_df = pd.DataFrame(rows)
    conn.update(data=new_df)

db = load_db_from_sheets()

# --- 3. LIVE API & MATCH ACTIVITY CALCULATION ---
@st.cache_data(ttl=900) 
def fetch_live_points_and_activity(_key):
    team_points = {team: 0 for team in ALL_TEAMS}
    activity_logs = []
    if not _key: return team_points, activity_logs
    
    headers = {'Authorization': _key}
    try:
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            matches = response.json().get('data', [])
            for m in matches:
                if m['status'] not in ['Final', 'In Progress', 'Halftime']: continue
                
                home_name = m['home_team']['name']
                away_name = m['visitor_team']['name']
                
                home = next((t for t in ALL_TEAMS if t in home_name), home_name)
                away = next((t for t in ALL_TEAMS if t in away_name), away_name)
                
                hg = m.get('home_team_score')
                ag = m.get('visitor_team_score')
                
                if hg is None or ag is None: continue

                # Automatic Knockout Detection (Matches from June 28th onwards)
                match_date = m.get('date', '2026-01-01')[:10]
                multiplier = 2 if match_date >= '2026-06-28' else 1
                
                # --- Home Team Points ---
                hp = 0
                home_breakdown = []
                if hg > ag: 
                    hp += (3 * multiplier)
                    home_breakdown.append(f"Win (+{3 * multiplier})")
                elif hg == ag: 
                    hp += (1 * multiplier)
                    home_breakdown.append(f"Draw (+{1 * multiplier})")
                    
                if hg > 0: 
                    hp += (hg * multiplier)
                    home_breakdown.append(f"{hg} Goal{'s' if hg>1 else ''} (+{hg * multiplier})")
                    
                if ag == 0: 
                    hp += (1 * multiplier)
                    home_breakdown.append(f"Clean Sheet (+{1 * multiplier})")
                    
                if ag >= 3: 
                    hp -= (1 * multiplier)
                    home_breakdown.append(f"Conceded 3+ (-{1 * multiplier})")
                
                # --- Away Team Points ---
                ap = 0
                away_breakdown = []
                if ag > hg: 
                    ap += (3 * multiplier)
                    away_breakdown.append(f"Win (+{3 * multiplier})")
                elif ag == hg: 
                    ap += (1 * multiplier)
                    away_breakdown.append(f"Draw (+{1 * multiplier})")
                    
                if ag > 0: 
                    ap += (ag * multiplier)
                    away_breakdown.append(f"{ag} Goal{'s' if ag>1 else ''} (+{ag * multiplier})")
                    
                if hg == 0: 
                    ap += (1 * multiplier)
                    away_breakdown.append(f"Clean Sheet (+{1 * multiplier})")
                    
                if hg >= 3: 
                    ap -= (1 * multiplier)
                    away_breakdown.append(f"Conceded 3+ (-{1 * multiplier})")
                
                if home in team_points: team_points[home] += hp
                if away in team_points: team_points[away] += ap
                
                status_emoji = "🟢 Live" if m['status'] != 'Final' else "⏱️ FT"
                knockout_tag = " 🏆 (2x Pts)" if multiplier == 2 else ""
                
                activity_logs.append({
                    "Status": status_emoji,
                    "Match": f"{home} {hg} - {ag} {away}{knockout_tag}",
                    "Team": home,
                    "Points Earned": hp,
                    "Breakdown": " | ".join(home_breakdown) if home_breakdown else "0 pts"
                })
                activity_logs.append({
                    "Status": status_emoji,
                    "Match": f"{home} {hg} - {ag} {away}{knockout_tag}",
                    "Team": away,
                    "Points Earned": ap,
                    "Breakdown": " | ".join(away_breakdown) if away_breakdown else "0 pts"
                })
    except:
        pass
    return team_points, activity_logs

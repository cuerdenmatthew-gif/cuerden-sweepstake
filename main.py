import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random
import math
import requests
import pandas as pd
import json

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cuerden & Co Sweepstake", page_icon="🏆", layout="wide")
ADMIN_PASSWORD = "Cuerden2026"

# API Setup
API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
API_URL = "https://api.football-data.org/v4/competitions/WC/matches"

# Official 48 Teams
ALL_TEAMS = [
    "USA", "Mexico", "Canada", "Japan", "New Zealand", "Iran", "Argentina", "Uzbekistan", 
    "South Korea", "Jordan", "Australia", "Brazil", "Ecuador", "Uruguay", "Colombia", 
    "Paraguay", "Morocco", "Tunisia", "Egypt", "Algeria", "Ghana", "Cabo Verde", 
    "Saudi Arabia", "Qatar", "England", "Ivory Coast", "South Africa", "Senegal", 
    "France", "Croatia", "Portugal", "Norway", "Germany", "Netherlands", "Belgium", 
    "Switzerland", "Spain", "Austria", "Scotland", "Curaçao", "Haiti", "Panama", 
    "Sweden", "Türkiye", "Czechia", "Bosnia and Herzegovina", "DR Congo", "Iraq"
]

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

# --- 3. LIVE API CALCULATION ---
@st.cache_data(ttl=900) 
def fetch_live_points(_key):
    team_points = {team: 0 for team in ALL_TEAMS}
    if not _key: return team_points
    
    headers = {'X-Auth-Token': _key}
    try:
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            matches = response.json().get('matches', [])
            for m in matches:
                if m['status'] not in ['FINISHED', 'IN_PLAY', 'PAUSED']: continue
                home = next((t for t in ALL_TEAMS if t in m['homeTeam']['name']), m['homeTeam']['name'])
                away = next((t for t in ALL_TEAMS if t in m['awayTeam']['name']), m['awayTeam']['name'])
                hg, ag = m['score']['fullTime']['home'], m['score']['fullTime']['away']
                if hg is None or ag is None: continue
                
                if home in team_points:
                    team_points[home] += hg
                    if hg > ag: team_points[home] += 3
                    elif hg == ag: team_points[home] += 1
                    if ag == 0: team_points[home] += 1
                    if ag >= 3: team_points[home] -= 1
                if away in team_points:
                    team_points[away] += ag
                    if ag > hg: team_points[away] += 3
                    elif ag == hg: team_points[away] += 1
                    if hg == 0: team_points[away] += 1
                    if hg >= 3: team_points[away] -= 1
    except:
        pass
    return team_points

# --- 4. DISPLAY LAYOUT ---
st.title("🏆 Cuerden and Co World Cup Sweepstake")

st.sidebar.markdown("""
### 📜 Point System
* **Win:** 3 pts | **Draw:** 1 pt
* **Goal Scored:** 1 pt
* **Clean Sheet:** 1 pt
* **3+ Goals Conceded:** -1 pt
""")

admin_input = st.sidebar.text_input("Admin Password", type="password")
if admin_input == ADMIN_PASSWORD and st.sidebar.button("RESET SWEEPSTAKE"):
    save_db_to_sheets({"participants": [], "assignments": {}, "locked": False})
    st.rerun()

if not db["locked"]:
    st.header("Step 1: Registration Phase")
    player_name = st.text_input("Enter name to join:")
    if st.button("Register"):
        if player_name and player_name not in db["participants"]:
            db["participants"].append(player_name)
            save_db_to_sheets(db)
            st.success(f"{player_name} added!")
            st.rerun()
            
    st.write(f"**Registered Players ({len(db['participants'])}):** " + ", ".join(db["participants"]))
    
    if len(db["participants"]) > 0:
        per_person = math.floor(48 / len(db["participants"]))
        st.info(f"Each person will receive **{per_person} teams** randomly.")
        if admin_input == ADMIN_PASSWORD and st.button("🔴 EXECUTE RANDOM DRAW"):
            random.shuffle(ALL_TEAMS)
            for i, person in enumerate(db["participants"]):
                start, end = i * per_person, (i * per_person) + per_person
                db["assignments"][person] = ALL_TEAMS[start:end]
            db["locked"] = True
            save_db_to_sheets(db)
            st.rerun()
else:
    st.header("Step 2: Live Leaderboard")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("📋 Your Teams")
        for p, teams in db["assignments"].items():
            with st.expander(f"{p}'s Teams"):
                st.write(", ".join(teams))
    with c2:
        st.subheader("📊 Standing")
        scores = fetch_live_points(API_KEY)
        table = []
        for p, teams in db["assignments"].items():
            pts = sum([scores.get(t, 0) for t in teams])
            table.append({"Player": p, "Total Points": pts})
        st.dataframe(pd.DataFrame(table).sort_values("Total Points", ascending=False), use_container_width=True, hide_index=True)

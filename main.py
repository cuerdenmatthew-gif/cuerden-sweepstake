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

# --- 1.5 OFFICIAL 2026 BRAND THEME ---
page_bg = """
<style>
/* Animated Gradient using the official 2026 colors */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #5200FF, #8E001C, #E61D25, #C6FF00);
    background-size: 300% 300%;
    animation: WorldCupGradient 18s ease infinite;
}

@keyframes WorldCupGradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 92% opaque white overlay so the app remains clean and readable */
[data-testid="stAppViewContainer"] > .main {
    background-color: rgba(255, 255, 255, 0.92);
}

/* Hide the default header background */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
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
                
                # --- Home Team Points ---
                hp = 0
                home_breakdown = []
                if hg > ag: hp += 3; home_breakdown.append("Win (+3)")
                elif hg == ag: hp += 1; home_breakdown.append("Draw (+1)")
                if hg > 0: hp += hg; home_breakdown.append(f"{hg} Goal{'s' if hg>1 else ''} (+{hg})")
                if ag == 0: hp += 1; home_breakdown.append("Clean Sheet (+1)")
                if ag >= 3: hp -= 1; home_breakdown.append("Conceded 3+ (-1)")
                
                # --- Away Team Points ---
                ap = 0
                away_breakdown = []
                if ag > hg: ap += 3; away_breakdown.append("Win (+3)")
                elif ag == hg: ap += 1; away_breakdown.append("Draw (+1)")
                if ag > 0: ap += ag; away_breakdown.append(f"{ag} Goal{'s' if ag>1 else ''} (+{ag})")
                if hg == 0: ap += 1; away_breakdown.append("Clean Sheet (+1)")
                if hg >= 3: ap -= 1; away_breakdown.append("Conceded 3+ (-1)")
                
                if home in team_points: team_points[home] += hp
                if away in team_points: team_points[away] += ap
                
                status_emoji = "🟢 Live" if m['status'] != 'Final' else "⏱️ FT"
                activity_logs.append({
                    "Status": status_emoji,
                    "Match": f"{home} {hg} - {ag} {away}",
                    "Team": home,
                    "Points Earned": hp,
                    "Breakdown": " | ".join(home_breakdown) if home_breakdown else "0 pts"
                })
                activity_logs.append({
                    "Status": status_emoji,
                    "Match": f"{home} {hg} - {ag} {away}",
                    "Team": away,
                    "Points Earned": ap,
                    "Breakdown": " | ".join(away_breakdown) if away_breakdown else "0 pts"
                })
    except:
        pass
    return team_points, activity_logs

# --- 4. DISPLAY LAYOUT ---
# Centered Logo and Title
st.markdown("""
<div style='text-align: center; padding-bottom: 20px;'>
    <img src='https://upload.wikimedia.org/wikipedia/en/thumb/f/fa/2026_FIFA_World_Cup_logo.svg/800px-2026_FIFA_World_Cup_logo.svg.png' width='160' style='margin-bottom: 15px;'>
    <h1 style='color: #111111; font-weight: 800; font-size: 2.5rem; margin: 0;'>Cuerden and Co World Cup Sweepstake</h1>
</div>
""", unsafe_allow_html=True)

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
    # Beautiful two-tab interface
    tab1, tab2 = st.tabs(["🏆 Standings & Teams", "📊 Match Activity"])
    
    team_scores, raw_activity_logs = fetch_live_points_and_activity(API_KEY)
    
    team_to_player = {}
    for player, teams in db["assignments"].items():
        for t in teams:
            team_to_player[t] = player
            
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("📋 Your Teams")
            for p, teams in db["assignments"].items():
                with st.expander(f"{p}'s Teams"):
                    st.write(", ".join(teams))
        with c2:
            st.subheader("📊 Leaderboard")
            table = []
            for p, teams in db["assignments"].items():
                pts = sum([team_scores.get(t, 0) for t in teams])
                table.append({"Player": p, "Total Points": pts})
            st.dataframe(pd.DataFrame(table).sort_values("Total Points", ascending=False), use_container_width=True, hide_index=True)
            st.caption("Scores update automatically every 15 minutes during live matches.")

    with tab2:
        st.subheader("⚽ Match Activity Points Breakdown")
        
        processed_logs = []
        for log in raw_activity_logs:
            log_copy = log.copy()
            log_copy["Player"] = team_to_player.get(log["Team"], "🍿 Unassigned Team")
            processed_logs.append(log_copy)
            
        activity_df = pd.DataFrame(processed_logs)
        
        if not activity_df.empty:
            filter_option = st.selectbox("Filter Match Activity by Player:", ["All Players"] + sorted(list(db["assignments"].keys())))
            
            if filter_option != "All Players":
                filtered_df = activity_df[activity_df["Player"] == filter_option]
            else:
                filtered_df = activity_df
                
            display_df = filtered_df[["Status", "Match", "Team", "Player", "Points Earned", "Breakdown"]]
            
            st.dataframe(
                display_df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Points Earned": st.column_config.NumberColumn(format="%+d"),
                    "Status": st.column_config.TextColumn(width="small")
                }
            )
        else:
            st.info("The tournament hasn't started yet! Once games kick off, live match updates and breakdowns will appear right here.")

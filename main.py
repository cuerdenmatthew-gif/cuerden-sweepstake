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

# --- 1.5 PREMIUM WC26 UI THEME ---
page_bg = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Inter:wght@400;600&display=swap');

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

[data-testid="stAppViewContainer"] > .main {
    background: rgba(15, 10, 20, 0.70);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

[data-testid="stHeader"] {
    background: transparent;
}

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

.stImage, [data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    width: 100% !important;
}

[data-testid="stImage"] img {
    width: 130px !important;
    max-width: 130px !important;
    height: auto !important;
    margin-left: auto !important;
    margin-right: auto !important;
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
    eliminated_teams = set()
    if not _key: return team_points, activity_logs, eliminated_teams
    
    TEAM_GROUPS = {
        "Mexico": "A", "South Africa": "A", "South Korea": "A", "Czechia": "A",
        "Canada": "B", "Switzerland": "B", "Qatar": "B", "Bosnia and Herzegovina": "B",
        "Brazil": "C", "Morocco": "C", "Haiti": "C", "Scotland": "C",
        "USA": "D", "Paraguay": "D", "Australia": "D", "Türkiye": "D",
        "Germany": "E", "Curaçao": "E", "Ivory Coast": "E", "Ecuador": "E",
        "Netherlands": "F", "Japan": "F", "Tunisia": "F", "Sweden": "F",
        "Belgium": "G", "Egypt": "G", "Iran": "G", "New Zealand": "G",
        "Spain": "H", "Cabo Verde": "H", "Saudi Arabia": "H", "Uruguay": "H",
        "France": "I", "Senegal": "I", "Norway": "I", "Iraq": "I",
        "Argentina": "J", "Algeria": "J", "Austria": "J", "Jordan": "J",
        "Portugal": "K", "Uzbekistan": "K", "Colombia": "K", "DR Congo": "K",
        "England": "L", "Croatia": "L", "Ghana": "L", "Panama": "L"
    }
    
    group_teams = {}
    for t, g in TEAM_GROUPS.items():
        if g not in group_teams: group_teams[g] = []
        group_teams[g].append(t)
        
    group_stats = {t: {"pts": 0, "gd": 0, "gf": 0, "mp": 0} for t in ALL_TEAMS}
    headers = {'Authorization': _key}
    
    try:
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            matches = response.json().get('data', [])
            
            has_knockouts_started = False
            knockout_participants = set()
            
            for m in matches:
                if m['status'] not in ['Final', 'In Progress', 'Halftime']: continue
                
                home_name = m['home_team']['name']
                away_name = m['visitor_team']['name']
                
                home = next((t for t in ALL_TEAMS if t in home_name), home_name)
                away = next((t for t in ALL_TEAMS if t in away_name), away_name)
                
                hg = m.get('home_team_score')
                ag = m.get('visitor_team_score')
                
                if hg is None or ag is None: continue

                raw_date = m.get('date')
                match_date = str(raw_date)[:10] if raw_date else '2026-01-01'
                
                multiplier = 2 if match_date >= '2026-06-28' else 1
                
                if match_date < '2026-06-28' and m['status'] == 'Final':
                    if home in group_stats:
                        group_stats[home]["mp"] += 1
                        group_stats[home]["gf"] += hg
                        group_stats[home]["gd"] += (hg - ag)
                    if away in group_stats:
                        group_stats[away]["mp"] += 1
                        group_stats[away]["gf"] += ag
                        group_stats[away]["gd"] += (ag - hg)
                    
                    if hg > ag:
                        if home in group_stats: group_stats[home]["pts"] += 3
                    elif ag > hg:
                        if away in group_stats: group_stats[away]["pts"] += 3
                    else:
                        if home in group_stats: group_stats[home]["pts"] += 1
                        if away in group_stats: group_stats[away]["pts"] += 1
                
                if match_date >= '2026-06-28':
                    has_knockouts_started = True
                    knockout_participants.add(home)
                    knockout_participants.add(away)
                    if m['status'] == 'Final':
                        if hg > ag: eliminated_teams.add(away)
                        elif ag > hg: eliminated_teams.add(home)
                
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
                
            for g, teams in group_teams.items():
                if all(group_stats[t]["mp"] == 3 for t in teams):
                    sorted_teams = sorted(teams, key=lambda x: (group_stats[x]["pts"], group_stats[x]["gd"], group_stats[x]["gf"]), reverse=True)
                    top_team = sorted_teams[0]
                    second_team = sorted_teams[1]
                    
                    team_points[top_team] += 2
                    team_points[second_team] += 1
                    
                    activity_logs.append({
                        "Status": "⏱️ Finished",
                        "Match": f"Group {g} Final Placement",
                        "Team": top_team,
                        "Points Earned": 2,
                        "Breakdown": "Group Stage Winner Bonus (+2)"
                    })
                    activity_logs.append({
                        "Status": "⏱️ Finished",
                        "Match": f"Group {g} Final Placement",
                        "Team": second_team,
                        "Points Earned": 1,
                        "Breakdown": "Group Stage 2nd Place Bonus (+1)"
                    })

            if has_knockouts_started:
                for team in ALL_TEAMS:
                    if team not in knockout_participants:
                        eliminated_teams.add(team)
                        
    except:
        pass
    return team_points, activity_logs, eliminated_teams

# Load active parameters
team_scores, raw_activity_logs, eliminated_nations = fetch_live_points_and_activity(API_KEY)

# --- 4. DISPLAY LAYOUT ---

if os.path.exists("logo.png"):
    st.image("logo.png")

st.markdown("""
<div style='text-align: center; padding-bottom: 10px;'>
    <div class='premium-title'>Cuerden & Co<br>WC26 Sweepstake</div>
    <div class='premium-subtitle'>Official Match Tracker</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
### 📜 Point System
* **Win:** 3 pts | **Draw:** 1 pt
* **Goal Scored:** 1 pt
* **Clean Sheet:** 1 pt
* **3+ Goals Conceded:** -1 pt
* 🥇 **Group Winner:** +2 pts
* 🥈 **Group 2nd Place:** +1 pt
* 🏆 **KNOCKOUTS:** All match metrics double (2x) from Round of 32 onwards!
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏳️ Active Nations")
active_count = 0
for team in ALL_TEAMS:
    if team not in eliminated_nations:
        flag = TEAM_FLAGS.get(team, "🏳️")
        st.sidebar.markdown(f"{flag} {team}")
        active_count += 1
if active_count == 0:
    st.sidebar.caption("All team data sync tracking is pending kickoff.")

st.sidebar.markdown("---")
admin_input = st.sidebar.text_input("Admin Password", type="password")
if admin_input == ADMIN_PASSWORD and st.sidebar.button("RESET SWEEPSTAKE"):
    save_db_to_sheets({"participants": [], "assignments": {}, "locked": False})
    st.rerun()

if not db["locked"]:
    st.header("Step 1: Registration Phase (Closes June 9th!)")
    st.markdown("### 💷 Entry Fee: £20 per person")
    
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
        prize_pot = len(db["participants"]) * 20
        st.success(f"**Current Total Prize Pot: £{prize_pot}**")
        
        if len(db["participants"]) >= 3:
            st.markdown(f"""
            💰 **Prize Money Breakdown:**
            * 🥇 **1st Place:** £{prize_pot - 40}
            * 🥈 **2nd Place:** £20 *(Money back)*
            * 🥾 **Last Place:** £20 *(Money back)*
            """)
        else:
            st.caption("A minimum of 3 registered players is required to activate the layered payout tier display.")
            
        st.info(f"Each person will receive **{per_person} teams** randomly. (Guaranteed at least 1 Top 13 Nation).")
        
        if admin_input == ADMIN_PASSWORD and st.button("🔴 EXECUTE RANDOM DRAW"):
            TOP_13 = ["Spain", "France", "Argentina", "England", "Brazil", "Portugal", "Germany", "Netherlands", "Morocco", "Norway", "Belgium", "Colombia", "Senegal"]
            
            shuffled_top = TOP_13.copy()
            random.shuffle(shuffled_top)
            regular_teams = [t for t in ALL_TEAMS if t not in TOP_13]
            
            for person in db["participants"]:
                db["assignments"][person] = []
                if shuffled_top:
                    db["assignments"][person].append(shuffled_top.pop(0))
            
            regular_teams.extend(shuffled_top)
            random.shuffle(regular_teams)
            
            for person in db["participants"]:
                needed = per_person - len(db["assignments"][person])
                for _ in range(needed):
                    if regular_teams:
                        db["assignments"][person].append(regular_teams.pop(0))
                        
            db["locked"] = True
            save_db_to_sheets(db)
            st.rerun()
else:
    tab1, tab2 = st.tabs(["🏆 Standings & Teams", "📊 Match Activity"])
    
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
                    team_list_with_flags = [f"{TEAM_FLAGS.get(t, '🏳️')} {t}" for t in teams]
                    st.write(", ".join(team_list_with_flags))
        with c2:
            st.subheader("📊 Leaderboard")
            table = []
            for p, teams in db["assignments"].items():
                pts = sum([team_scores.get(t, 0) for t in teams])
                table.append({"Player": p, "Total Points": pts})
            
            if table:
                st.dataframe(pd.DataFrame(table).sort_values("Total Points", ascending=False), use_container_width=True, hide_index=True)
            
            prize_pot = len(db["participants"]) * 20
            st.success(f"**Final Tournament Prize Pot: £{prize_pot}**")
            if len(db["participants"]) >= 3:
                st.markdown(f"""
                💰 **Official Cash Split Structure:**
                * 🥇 **1st Place:** £{prize_pot - 40}
                * 🥈 **2nd Place:** £20 *(Money back)*
                * 🥾 **Last Place:** £20 *(Money back)*
                """)
            st.caption("Scores update automatically every 15 minutes during live matches. Penalty shootouts do not count towards goals.")

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

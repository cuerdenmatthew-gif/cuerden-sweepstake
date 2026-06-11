import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random
import math
import requests
import pandas as pd
import json
import os
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cuerden & Co WC26", page_icon="🏆", layout="wide")
ADMIN_PASSWORD = "Cuerden2026"

# BALLDONTLIE API Setup - Hardcoded Key Configuration
API_KEY = "deea4eaa-fd4a-4eb9-8191-dcb568c2b88d"
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

# --- 1.5 PREMIUM WC26 UI THEME (VIBRANT PURPLE & SECURE CONTRAST) ---
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

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stSidebar"] {
    background-color: #120024 !important;
    background-image: linear-gradient(180deg, #1C0038 0%, #0A0014 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
}

[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span, 
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] div {
    color: #FFFFFF !important;
}

h1, h2, h3, h4, p, span, label, li, [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
}

div[data-baseweb="input"] {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(198, 255, 0, 0.4) !important;
    border-radius: 6px !important;
}
div[data-baseweb="input"] input {
    color: #FFFFFF !important;
}

/* HARD-LOCK EXPANDER STYLING FOR LIGHT MODE IMMUNITY */
div[data-testid="stExpander"] {
    background-color: #1E052D !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
}

div[data-testid="stExpander"] summary {
    background-color: #1E052D !important;
    color: #FFFFFF !important;
}

div[data-testid="stExpander"] p, 
div[data-testid="stExpander"] span,
div[data-testid="stExpander"] label,
div[data-testid="stExpander"] summary text {
    color: #FFFFFF !important;
}

/* Dataframe and table light-mode visibility corrections */
div[data-testid="stDataFrame"] {
    background-color: rgba(15, 5, 25, 0.8) !important;
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
    border: 1px solid rgba(198, 255, 0, 0.5) !important;
    white-space: nowrap !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.6) !important;
    text-shadow: 0 0 8px rgba(198, 255, 0, 0.6) !important;
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
                # Direct Multi-Tier Safety Extractors
                home_obj = m.get('home_team', {})
                away_obj = m.get('visitor_team', {})
                
                raw_home = home_obj.get('name', '') if isinstance(home_obj, dict) else str(home_obj)
                raw_away = away_obj.get('name', '') if isinstance(away_obj, dict) else str(away_obj)
                
                if not raw_home or not raw_away:
                    continue
                
                # Match names dynamically using partial lowercase matching loops
                home = next((t for t in ALL_TEAMS if t.lower() in raw_home.lower() or raw_home.lower() in t.lower()), None)
                away = next((t for t in ALL_TEAMS if t.lower() in raw_away.lower() or raw_away.lower() in t.lower()), None)
                
                if not home or not away:
                    continue
                
                hg = m.get('home_team_score')
                if hg is None: hg = m.get('scores', {}).get('home')
                if hg is None: hg = home_obj.get('score')
                
                ag = m.get('visitor_team_score')
                if ag is None: ag = m.get('scores', {}).get('away')
                if ag is None: ag = away_obj.get('score')
                
                if hg is None or ag is None:
                    continue

                hg, ag = int(hg), int(ag)

                raw_date = m.get('date', '')
                date_str = str(raw_date)
                stage_str = str(m.get('stage', '')).lower()
                
                is_knockout = ('2026-06-28' in date_str or '2026-07' in date_str) or any(w in stage_str for w in ['knockout', 'round', 'quarter', 'semi', 'final'])
                is_world_cup_final = ('2026-07-19' in date_str) or ('final' in stage_str and 'semi' not in stage_str)
                
                multiplier = 2 if is_knockout else 1
                
                status_raw = str(m.get('status', '')).strip().lower()
                is_finished = any(w in status_raw for w in ['final', 'ft', 'end', 'finish', 'complete', 'closed']) or m.get('time') == 'Full Time'
                
                if not is_knockout and is_finished:
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
                
                if is_knockout:
                    has_knockouts_started = True
                    knockout_participants.add(home)
                    knockout_participants.add(away)
                    if is_finished:
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
                
                team_points[home] += hp
                team_points[away] += ap
                
                status_emoji = "⏱️ FT" if is_finished else "🟢 Live"
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

                if is_world_cup_final and is_finished:
                    winner = home if hg > ag else away
                    team_points[winner] += 10
                    activity_logs.append({
                        "Status": "⏱️ Finished",
                        "Match": "World Cup Final - Tournament Champion",
                        "Team": winner,
                        "Points Earned": 10,
                        "Breakdown": "World Cup Winner Bonus (+10 Flat)"
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

# Load core metrics
team_scores, raw_activity_logs, eliminated_nations = fetch_live_points_and_activity(API_KEY)

# --- 4. DISPLAY LAYOUT ---

if os.path.exists("logo.png"):
    try:
        with open("logo.png", "rb") as f:
            img_encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style='display: flex; justify-content: center; align-items: center; width: 100%; padding-top: 10px; margin-bottom: -10px;'>
                <img src='data:image/png;base64,{img_encoded}' style='width: 130px; height: auto;'>
            </div>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

st.markdown("""
<div style='text-align: center; padding-bottom: 10px;'>
    <div class='premium-title'>Cuerden & Co<br>WC26 Sweepstake</div>
    <div class='premium-subtitle'>Official Match Tracker</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='sidebar-hint-text'>👈 Rules & Teams</div>", unsafe_allow_html=True)

st.sidebar.markdown("""
### 📜 Point System
* **Win:** 3 pts | **Draw:** 1 pt
* **Goal Scored:** 1 pt
* **Clean Sheet:** 1 pt
* **3+ Goals Conceded:** -1 pt
* 🥇 **Group Winner:** +2 pts
* 🥈 **Group 2nd Place:** +1 pt
* 🏆 **World Cup Champion:** +10 pts *(Flat)*
* 💥 **KNOCKOUTS:** Match performance metrics double (2x) from Round of 32 onwards!
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
        leftovers = 48 % len(db["participants"])
        prize_pot = len(db["participants"]) * 20
        st.success(f"**Current Total Prize Pot: £{prize_pot}**")
        
        if len(db["participants"]) >= 3:
            st.markdown(f"""
            💰 **Prize Money Breakdown:**
            * 🥇 **1st Place:** £{prize_pot - 60}
            * 🥈 **2nd Place:** £40 *(Double your money!)*
            * 🥾 **Last Place:** £20 *(Money back)*
            """)
        else:
            st.caption("A minimum of 3 registered players is required to activate the layered payout tier display.")
            
        if leftovers > 0:
            st.info(f"Each person gets **{per_person} teams** baseline. The remaining **{leftovers} teams** will be randomly distributed out so that {leftovers} lucky players get 1 extra team! (Guaranteed at least 1 Top 13 Nation).")
            st.caption("🛡️ Fairness Buff Active: Any players who end up receiving fewer teams total will get first priority over the leftover elite Top 13 seeds!")
        else:
            st.info(f"Each person will receive exactly **{per_person} teams** randomly. (Guaranteed at least 1 Top 13 Nation).")
        
        if admin_input == ADMIN_PASSWORD and st.button("🔴 EXECUTE RANDOM DRAW"):
            TOP_13 = ["Spain", "France", "Argentina", "England", "Brazil", "Portugal", "Germany", "Netherlands", "Morocco", "Norway", "Belgium", "Colombia", "Senegal"]
            
            shuffled_top = TOP_13.copy()
            random.shuffle(shuffled_top)
            
            db["assignments"] = {person: [] for person in db["participants"]}
            
            for person in db["participants"]:
                if shuffled_top:
                    db["assignments"][person].append(shuffled_top.pop(0))
            
            remaining_pool = shuffled_top + [t for t in ALL_TEAMS if t not in TOP_13]
            random.shuffle(remaining_pool)
            
            for person in db["participants"]:
                needed = per_person - len(db["assignments"][person])
                for _ in range(needed):
                    if remaining_pool:
                        db["assignments"][person].append(remaining_pool.pop(0))
            
            if remaining_pool:
                lucky_players = db["participants"].copy()
                random.shuffle(lucky_players)
                while remaining_pool and lucky_players:
                    recipient = lucky_players.pop(0)
                    db["assignments"][recipient].append(remaining_pool.pop(0))
                        
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
                with st.expander(f"{p}'s Teams ({len(teams)} teams)"):
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
                * 🥇 **1st Place:** £{prize_pot - 60}
                * 🥈 **2nd Place:** £40 *(Double your money!)*
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

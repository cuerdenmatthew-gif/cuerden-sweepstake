import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random
import math
import pandas as pd
import json
import os
import base64

# --- CONFIG & TEAMS ---
st.set_page_config(page_title="Cuerden & Co WC26", page_icon="🏆", layout="wide")
ADMIN_PASSWORD = "Cuerden2026"
ALL_TEAMS = ["USA", "Mexico", "Canada", "Japan", "New Zealand", "Iran", "Argentina", "Uzbekistan", "South Korea", "Jordan", "Australia", "Brazil", "Ecuador", "Uruguay", "Colombia", "Paraguay", "Morocco", "Tunisia", "Egypt", "Algeria", "Ghana", "Cabo Verde", "Saudi Arabia", "Qatar", "England", "Ivory Coast", "South Africa", "Senegal", "France", "Croatia", "Portugal", "Norway", "Germany", "Netherlands", "Belgium", "Switzerland", "Spain", "Austria", "Scotland", "Curaçao", "Haiti", "Panama", "Sweden", "Türkiye", "Czechia", "Bosnia and Herzegovina", "DR Congo", "Iraq"]
TEAM_FLAGS = {"USA": "🇺🇸", "Mexico": "🇲🇽", "Canada": "🇨🇦", "Japan": "🇯🇵", "New Zealand": "🇳🇿", "Iran": "🇮🇷", "Argentina": "🇦🇷", "Uzbekistan": "🇺🇿", "South Korea": "🇰🇷", "Jordan": "🇯🇴", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Ecuador": "🇪🇨", "Uruguay": "🇺🇾", "Colombia": "🇨🇴", "Paraguay": "🇵🇾", "Morocco": "🇲🇦", "Tunisia": "🇹🇳", "Egypt": "🇪🇬", "Algeria": "🇩🇿", "Ghana": "🇬🇭", "Cabo Verde": "🇨🇻", "Saudi Arabia": "🇸🇦", "Qatar": "🇶🇦", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Ivory Coast": "🇨🇮", "South Africa": "🇿🇦", "Senegal": "🇸🇳", "France": "🇫🇷", "Croatia": "🇭🇷", "Portugal": "🇵🇹", "Norway": "🇳🇴", "Germany": "🇩🇪", "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Switzerland": "🇨🇭", "Spain": "🇪🇸", "Austria": "🇦🇹", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Curaçao": "🇨🇼", "Haiti": "🇭🇹", "Panama": "🇵🇦", "Sweden": "🇸🇪", "Türkiye": "🇹🇷", "Czechia": "🇨🇿", "Bosnia and Herzegovina": "🇧🇦", "DR Congo": "🇨🇩", "Iraq": "🇮🇶"}

# --- CSS ---
st.markdown("<style>.premium-card { background: rgba(30,5,45,0.85); border-left: 4px solid #C6FF00; padding: 15px; margin-bottom: 10px; border-radius: 8px; } .score-display { font-weight: 800; color: #C6FF00; } s { color: #888; }</style>", unsafe_allow_html=True)

# --- DATA LOADING ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_all_data():
    # Load Players/Assignments
    df_players = conn.read(worksheet="Sheet1", ttl=0)
    participants = df_players[df_players["Type"] == "Player"]["Name"].tolist()
    assignments = {row["Name"]: json.loads(row["Teams"]) for _, row in df_players[df_players["Type"] == "Assignment"].iterrows()}
    
    # Load Scores & Eliminations
    df_scores = conn.read(worksheet="Scores", ttl=0)
    eliminated_nations = set(df_scores['EliminatedTeam'].dropna().unique()) if 'EliminatedTeam' in df_scores.columns else set()
    
    return participants, assignments, eliminated_nations, df_scores

participants, assignments, eliminated_nations, df_scores = load_all_data()

# --- SIDEBAR ---
st.sidebar.markdown("### 🏳️ Active Nations")
for team in ALL_TEAMS:
    if team not in eliminated_nations:
        st.sidebar.markdown(f"{TEAM_FLAGS.get(team, '🏳️')} {team}")

# --- MAIN CONTENT ---
st.title("🏆 Cuerden & Co WC26")

tab1, tab2 = st.tabs(["📋 My Teams", "📊 Activity"])

with tab1:
    st.subheader("Your Teams")
    for p, teams in assignments.items():
        with st.expander(f"{p}'s Teams"):
            display_teams = []
            for t in teams:
                flag = TEAM_FLAGS.get(t, '🏳️')
                if t in eliminated_nations:
                    display_teams.append(f"<s>{flag} {t}</s>")
                else:
                    display_teams.append(f"{flag} {t}")
            st.write(", ".join(display_teams), unsafe_allow_html=True)

with tab2:
    st.info("Ensure 'EliminatedTeam' column is filled in your 'Scores' sheet to update statuses!")

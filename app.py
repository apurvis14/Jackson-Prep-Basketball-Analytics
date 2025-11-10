# app.py
import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import os
from functionsapp import plot_zone_chart, calc_zone_stats, styled_text, split_name, centered_metric
# -----------------------------
# Page Config
# --------------------------
st.set_page_config(layout="centered", page_title="Jackson Prep Basketball Dashboard")

st.markdown(
    """
    <style>
    /* Shrink top bar */
    header[data-testid="stHeader"] {
        height: 40px !important;
        padding: 0 !important;
        min-height: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True)

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.username = None

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def hash_credentials(username: str, password: str) -> str:
    """Return a SHA256 hash of 'username:password'."""
    combo = f"{username}:{password}"
    return hashlib.sha256(combo.encode()).hexdigest()

def do_login():
    """Callback to validate and set session state."""
    hashed = hash_credentials(st.session_state.u, st.session_state.p)
    if hashed in st.secrets["auth"]:
        st.session_state.auth = True
        st.session_state.username = st.secrets["auth"][hashed]
    else:
        st.session_state.login_error = "Invalid username or password"

def do_logout():
    """Log out and clear session state."""
    st.session_state.auth = False
    st.session_state.username = None
    st.session_state.login_error = None

# -----------------------------
# LOGIN UI
# -----------------------------
if not st.session_state.auth:
    st.sidebar.header("Login")

    st.sidebar.text_input("Username", key="u")
    st.sidebar.text_input("Password", type="password", key="p")
    st.sidebar.button("Login", on_click=do_login)

    if st.session_state.get("login_error"):
        st.sidebar.error(st.session_state.login_error)

    st.stop()  # Halt app execution until logged in

# -----------------------------
# PROTECTED CONTENT
# -----------------------------
st.sidebar.success(f"Welcome **{st.session_state.username}**!")
st.sidebar.button("Logout", on_click=do_logout)


# -----------------------------
# Load Data
# -----------------------------
# Direct CSV URL
@st.cache_data
def load_data():
    csv_url = st.secrets["data"]["shooting_url"]
    csv_url_hustle = st.secrets["data"]["hustle_url"]
    practice_url = st.secrets["data"]["practice_url"]
    game_url = st.secrets["data"]["game_url"]

# Set DF Variable
    df = pd.read_csv(csv_url)
    df_hustle = pd.read_csv(csv_url_hustle)
    stats_df = pd.read_csv(practice_url)
    game_df = pd.read_csv(game_url)
    practice_df = pd.read_csv(practice_url)
    return df, df_hustle, stats_df, game_df, practice_df

df, df_hustle, stats_df, game_df, practice_df = load_data()

# Sidebar filters
st.sidebar.header("Shot/Player Filters")

# --- Player Dropdown ---
players = df["PLAYER"].dropna().unique().tolist()
players.sort()
players = ["Team"] + players  # Add "Team" option at top
selected_player = st.sidebar.selectbox("Select Player", players)

# --- Week Filter (TRUMPS ALL) ---
weeks_shot = df["WEEK"].dropna().unique().tolist()
weeks_shot.sort()
weeks_shot = ["Season"] + weeks_shot
selected_week_shot = st.sidebar.selectbox("Select Week", weeks_shot)

# --- Type Dropdown ---
selected_type = st.sidebar.selectbox("Select Type", options=["Game", "Practice", "Season", "All Including Pickup", "Pickup"], index=2)

# --- Game Dropdown ---
if selected_player == "Team":
    games = df["GAME"].dropna().unique().tolist()
else:
    games = df["GAME"].dropna().unique().tolist()
games.sort()
games = ["Season"] + games  # Add "Season" option at top
selected_game = st.sidebar.selectbox("Select Game/Practice", games)

# --- Define filter for game types ---
if selected_type == "Season":
    game_types = ["Game", "Practice"]  # Combine both
elif selected_type == "All Including Pickup":
    game_types = ["Pickup", "Practice", "Game"]
else:
    game_types = [selected_type]

# -----------------------------
# Apply week filter first (OVERRIDE)
# -----------------------------
if selected_week_shot != "Season":
    filtered = df[df["WEEK"] == selected_week_shot]
    if "Week" in stats_df.columns:
        week_values = stats_df["Week"].astype(str).unique().tolist()
        if str(selected_week_shot) in week_values:
            stats_df = stats_df[stats_df["Week"].astype(str) == str(selected_week_shot)]
        else:
            stats_df = stats_df.iloc[0:0]  # Empty DF if week not found
    else:
        stats_df = stats_df.iloc[0:0]  # Empty DF if week not found

    if "Week" in game_df.columns:
        week_values_game = game_df["Week"].astype(str).unique().tolist()
        if str(selected_week_shot) in week_values_game:
            game_df = game_df[game_df["Week"].astype(str) == str(selected_week_shot)]
        else:
            game_df = game_df.iloc[0:0]  # Empty DF if week not found
    else:
        game_df = game_df.iloc[0:0]  # Empty DF if week not found

else:
    # --- Regular filtering logic ---
    if selected_player == "Team" and selected_game == "Season":
        filtered = df[df["TYPE"].isin(game_types)]
    elif selected_player == "Team":
        filtered = df[(df["GAME"] == selected_game) & (df["TYPE"].isin(game_types))]
    elif selected_game == "Season":
        filtered = df[(df["PLAYER"] == selected_player) & (df["TYPE"].isin(game_types))]
    else:
        filtered = df[
            (df["PLAYER"] == selected_player)
            & (df["GAME"] == selected_game)
            & (df["TYPE"].isin(game_types))
        ]
    stats_df = stats_df.copy() 

st.sidebar.header("Lunch Pail Week Filter")
weeks = df_hustle["Week"].dropna().unique().tolist()
weeks.sort()
weeks = ["Season"] + weeks
selected_week = st.sidebar.selectbox("Select Week", weeks)

# --- Filtering Logic ---
if selected_week == "Season":
    if selected_game != "Season":
        df_hustle = df_hustle[
            (df_hustle["Game/Practice"] == str(selected_game))]
    else:
        df_hustle = df_hustle

else:
    if selected_game != "Season":
        df_hustle = df_hustle[
            (df_hustle["Game/Practice"] == str(selected_game))
            & (df_hustle["Week"] == selected_week)]
    else:
        df_hustle = df_hustle[
            (df_hustle["Week"] == selected_week)]



# Create Tabs
tab1, tab7, tab6, tab3, tab2, tab4, tab5 = st.tabs(["Shot Chart", "Team Practice Stats", "Team Game Stats", 'Lunch Pail Stats', "Player Game Dashboard", "Player Practice Dashboard", "Pickup Dashboard"])

st.markdown(
    """
    <style>
    @media print {
        /* Hide the tab buttons/headers only */
        .stTabs [role="tablist"] {
            display: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Tab 1: Original Shot Chart
# -----------------------------
with tab1:
    # Left + Right columns for image and stats
        left_col, right_col = st.columns([1, 2])

        with left_col:
            col_empty, col_img, col_empty2 = st.columns([0.25,3.5,0.25])
            with col_img:
                photo_path = f"photos/{selected_player}.JPG"
                if selected_player == "Team":
                    st.image("photos/team_logo.png", width=175)
                elif os.path.exists(photo_path):
                    st.image(photo_path, width=175)
                else:
                    st.image("photos/team_logo.png", width=175)  # fallback image

        with right_col:
            if selected_player == "Team":
                st.markdown(styled_text("Jackson Prep Team", size=28, weight='bold', margin="8px",underline=False, center=True), unsafe_allow_html=True)
            else:
                st.markdown(styled_text(f"{selected_player}", size=28, weight='bold', margin="8px",underline=False, center=True), unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            # Layup, Midrange, 3PT metrics
                # --- Layup ---
            makesL, attL, pctL = calc_zone_stats(filtered, "Layup")
            col1.markdown(styled_text("Layup", size=22, margin="0px 0px 0px 0px", underline=True, center=True), unsafe_allow_html=True)
            col1.markdown(styled_text(f"{makesL}/{attL}", size=18, weight="normal", margin="0px 0px 16px 0px",underline=False, center=True), unsafe_allow_html=True)
            col1.markdown(styled_text(f"{pctL:.1f}%", size=18, weight="normal", margin="-10px",underline=False, center=True), unsafe_allow_html=True)

            # --- Midrange ---
            makesM, attM, pctM = calc_zone_stats(filtered, "Midrange")
            col2.markdown(styled_text("Midrange", size=22, margin="0px 0px 0px 0px", underline=True, center=True), unsafe_allow_html=True)
            col2.markdown(styled_text(f"{makesM}/{attM}", size=18, weight="normal", margin="0px 0px 16px 0px",underline=False, center=True), unsafe_allow_html=True)
            col2.markdown(styled_text(f"{pctM:.1f}%", size=18, weight="normal", margin="-10px",underline=False, center=True), unsafe_allow_html=True)

            # --- 3PT ---
            makes3, att3, pct3 = calc_zone_stats(filtered, "3PT")
            col3.markdown(styled_text("3PT", size=22, margin="0px 0px 0px 0px", underline=True, center=True), unsafe_allow_html=True)
            col3.markdown(styled_text(f"{makes3}/{att3}", size=18, weight="normal", margin="0px 0px 16px 0px",underline=False, center=True), unsafe_allow_html=True)
            col3.markdown(styled_text(f"{pct3:.1f}%", size=18, weight="normal", margin="-10px",underline=False, center=True), unsafe_allow_html=True)

        # Shot chart
        fig = plot_zone_chart(filtered, df)
        st.pyplot(fig, use_container_width=True)

player_info = {
    "Asher Reynolds": {"number": 4, "position": "Guard"},
    "Ben Roberts Smith": {"number": 12, "position": "Guard"},
    "Clark Smith": {"number": 11, "position": "Guard"},
    "Cray Luckett": {"number": 3, "position": "Guard/Forward"},
    "Ejay Napier": {"number": 2, "position": "Guard"},
    "Hemming Williamson": {"number": 5, "position": "Forward"},
    "Joseph Chaney": {"number": 0, "position": "Center"},
    "Judson Colley": {"number": 15, "position": "Center"},
    "Kaden Griffin": {"number": 22, "position": "Forward"},
    "Kendrick Rogers": {"number": 14, "position": "Forward"},
    "Manning Parks": {"number": 34, "position": "Center"},
    "Miles Burkhalter": {"number": 20, "position": "Guard"},
    "William Thornton": {"number": 1, "position": "Forward"},
    "Abney Moss": {"number": 21, "position": "Forward"},
    "Bennett Rooker": {"number": 35, "position": "Center"},
    "Garrett Bridgers": {"number": 23, "position": "Forward"},
    "Henry Russ": {"number": 25, "position": "Guard"},
    "Herrin Goodman": {"number": 24, "position": "Guard"},
    "IV Davidson": {"number": 20, "position": "Guard"},
    "Johnny Fondren": {"number": 30, "position": "Guard"},
    "Sam Milner": {"number": 13, "position": "Guard"},
    "Knox Hassell": {"number": 99, "position": "Forward"},
    "Hayes Grenfell": {"number": 98, "position": "Guard"},
    "Bowen Jones": {"number": 97, "position": "Forward"},

}

selected_player_info = (lambda x: f"#{player_info[x]['number']} — {player_info[x]['position']}" 
                        if x in player_info else x)(selected_player)

if selected_game != "Season":
    game_df = game_df[game_df["Game"] == str(selected_game)]

if selected_player != "Team":
    player_df = game_df[game_df["Player"] == selected_player]

    if player_df.empty:
        game_total_assists = 0
        game_total_turnovers = 0
        game_total_off_rebs = 0
        game_total_def_rebs = 0
        game_ast_to_ratio = 0
    else:
        # Sum the stats for that player
        game_total_assists = player_df["Ast"].sum()
        game_total_turnovers = player_df["TO"].sum()
        game_total_off_rebs = player_df["OFF_Reb"].sum()
        game_total_def_rebs = player_df["DEF_Reb"].sum()

        # Derived metric
        game_ast_to_ratio = round(game_total_assists / game_total_turnovers, 2) if game_total_turnovers != 0 else game_total_assists
else:
    # For "Team", sum all players
    game_total_assists = game_df["Ast"].sum()
    game_total_turnovers = game_df["TO"].sum()
    game_total_off_rebs = game_df["OFF_Reb"].sum()
    game_total_def_rebs = game_df["DEF_Reb"].sum()
    game_ast_to_ratio = round(game_total_assists / game_total_turnovers, 2) if game_total_turnovers != 0 else game_total_assists

# -----------------------------
# Tab 2: Player Stats Dashboard
# -----------------------------
with tab2:
        st.markdown(
        """
        <div style="
            border: 3px solid red;
            border-radius: 15px;
            padding: 5px 5px;
            width: 350px;              /* fixed width to ensure centering */
            margin: 10px auto;         /* auto horizontal margin centers the div */
            text-align: center;
        ">
            <h1 style='margin: 0; font-size: 48px; text-decoration: underline; font-weight: bold;'>Game Stats</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

            # Left + Right columns for image and stats
        left_col, right_col = st.columns([1, 2])

        with left_col:
            col_empty, col_img, col_empty2 = st.columns([0.25,3.5,0.25])
            with col_img:
                photo_path = f"photos/{selected_player}.JPG"
                if selected_player == "Team":
                    st.image("photos/team_logo.png", width=175)
                elif os.path.exists(photo_path):
                    st.image(photo_path, width=175)
                else:
                    st.image("photos/team_logo.png", width=175)  # fallback image

        with right_col:
            if selected_player == "Team":
                st.markdown(styled_text("Jackson Prep Team", size=32, weight='normal', margin="8px 0px 16px 0px",underline=False, center=True, vertical=True), unsafe_allow_html=True)
                st.markdown(styled_text("3-4 (0-0)", size=24, weight='normal', margin="0px", underline=False, center=True, vertical=True), unsafe_allow_html=True)
            else:
                st.markdown(styled_text(f"{selected_player}", size=32, weight='normal', margin="8px 0px 16px 0px",underline=False, center=True, vertical=True), unsafe_allow_html=True)
                st.markdown(styled_text(f"{selected_player_info}", size=24, weight='normal', margin="0px", underline=False, center=True, vertical=True), unsafe_allow_html=True)


        st.markdown(
            "<hr style='border: 2px solid #0033A0; margin-top: 0.25rem; margin-bottom: 0rem;'>",
            unsafe_allow_html=True) 
        
        st.markdown(styled_text("Per-Game Stats", size=28, weight='normal', margin="0px 0px 0px 0px", underline=False, center=False, vertical=False), unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            centered_metric("Points Per Game", "N/A")

        with col2:
            centered_metric("Assists Per Game", "N/A")

        with col3:
            centered_metric("Rebs. Per Game", "N/A")

        st.markdown(
            "<hr style='border: 1px solid #0033A0; margin-top: 1rem; margin-bottom: 0rem;'>",
            unsafe_allow_html=True)  

        st.markdown(styled_text("Efficiency Ratings", size=28, weight='normal', margin="2px 0px 0px 0px", underline=False, center=False, vertical=False), unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            centered_metric("OFF Efficiency", "N/A")

        with col2:
            centered_metric("DEF Efficiency", "N/A")

        with col3:
            centered_metric("Net Efficiency", "N/A")

        st.markdown(
            "<hr style='border: 1px solid #0033A0; margin-top: 1rem; margin-bottom: 0rem;'>",
            unsafe_allow_html=True)

        st.markdown(styled_text("Shooting %", size=28, weight='normal', margin="2px 0px 0px 0px", underline=False, center=False, vertical=False), unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            centered_metric("eFG %", "N/A")

        with col2:
            centered_metric("3PT %", "N/A")

        with col3:
            centered_metric("2PT %", "N/A")
        
        with col4:
            centered_metric("FT %", "N/A")

        st.markdown(
            "<hr style='border: 1px solid #0033A0; margin-top: 1rem; margin-bottom: 0rem;'>",
            unsafe_allow_html=True)

        st.markdown(styled_text("Totals AST, TO, Rebs", size=28, weight='normal', margin="2px 0px 0px 0px", underline=False, center=False, vertical=False), unsafe_allow_html=True) 

        col1, col2, col3 = st.columns(3)

        with col1:
            centered_metric("ASTs", game_total_assists)

        with col2:
            centered_metric("TOs", game_total_turnovers)

        with col3:
            centered_metric("AST/TO", game_ast_to_ratio)

        col4, col5, col6 = st.columns(3)

        with col4:
            centered_metric("DEF Rebs", game_total_def_rebs)

        with col5:
            centered_metric("OFF Rebs", game_total_off_rebs)

        with col6:
            centered_metric("Total Rebs", game_total_def_rebs + game_total_off_rebs)

with tab3:

    hustle = df_hustle.groupby('Player').agg(
            {'Charges': 'sum',
            'Steals/Deflections': 'sum',
            'Ball Secured': 'sum',
            'Wallups': 'sum',
            'Floor Dives': 'sum',
            'Blocks': 'sum',
            'Screen Ast': 'sum',
            'Help Ups': 'sum',
            'O Rebs': 'sum',
            'Daggers': 'sum'}
        ).reset_index()
    
    hustle['Hustle Score'] = (hustle['Charges']* 3 
                        + hustle['Steals/Deflections'] * 1
                       + hustle['Ball Secured'] * 1
                       + hustle['Wallups'] * 1
                       + hustle['Floor Dives'] * 1
                       + hustle['Blocks'] * 1
                       + hustle['Screen Ast'] * 1
                       + hustle['Help Ups'] * 1
                       + hustle['O Rebs'] * 1
                       + hustle['Daggers'] * 1)
    
    hustle = hustle.rename(columns={
    "Steals/Deflections": "Steals\nDEFs",
    "Ball Secured": "Ball\nSecured",
    "Floor Dives": "Floor\nDives",
    "Screen Ast": "Screen\nAst",
    "Hustle Score": "Hustle\nScore",
    "Help Ups": "Help\nUps",
    "O Rebs": 'OFF\nRebs'
    })

    hustle = hustle.sort_values(by='Hustle\nScore', ascending=False)
    
    cols = hustle.columns.tolist()
    cols.insert(1, cols.pop(cols.index('Hustle\nScore')))
    hustle = hustle[cols]

    hustle['Player'] = hustle['Player'].apply(split_name)

    # Create a copy for display purposes
    hustle_display = hustle.copy()

    # Replace 0s with empty strings for display
    cols_to_replace = hustle_display.columns[1:]  # skip 'Player' column
    hustle_display[cols_to_replace] = hustle_display[cols_to_replace].replace(0, "")


    if selected_week == "Season":
        title = "Season Lunch Pail Stats"
    else:
        title = f"Week {selected_week} Lunch Pail Stats"

    fig, ax = plt.subplots(figsize=(32, 40))
    fig.suptitle(title, fontsize=36, color='#0033A0', fontweight='bold', y=0.975)
    ax.axis('off')

    # Create table with Formatted DataFrame
    table = plt.table(
        cellText=hustle_display.values,
        colLabels=hustle_display.columns,
        cellLoc='center',
        bbox=[-0.05, 0.13, 1.05, 0.95]
    )

    # Resize to ensure fit and readability
    table.auto_set_font_size(False)
    table.set_fontsize(28)
    table.scale(1.4, 2.5)

    # Change Color the header row
    for key, cell in table.get_celld().items():
        row, col = key
        if row == 0:  # header row
            cell.set_facecolor('#da1a32')
            cell.set_linewidth(2.5)
            cell.set_edgecolor('#0033A0')
            cell.get_text().set_fontweight('bold')
            cell.get_text().set_color('#0033A0')
            cell.set_fontsize(30)
        else:
            cell.get_text().set_color('#0033A0')
            cell.set_edgecolor('#0033A0')
    
            if row % 2 == 0:
                cell.set_facecolor('#f2f2f2')  # light gray
            else:
                cell.set_facecolor('white')    # default white

    st.pyplot(fig)

player_info = {
    "Asher Reynolds": {"number": 4, "position": "Guard"},
    "Ben Roberts Smith": {"number": 12, "position": "Guard"},
    "Clark Smith": {"number": 11, "position": "Guard"},
    "Cray Luckett": {"number": 3, "position": "Guard/Forward"},
    "Ejay Napier": {"number": 2, "position": "Guard"},
    "Hemming Williamson": {"number": 5, "position": "Forward"},
    "Joseph Chaney": {"number": 0, "position": "Center"},
    "Judson Colley": {"number": 15, "position": "Center"},
    "Kaden Griffin": {"number": 22, "position": "Forward"},
    "Kendrick Rogers": {"number": 14, "position": "Forward"},
    "Manning Parks": {"number": 34, "position": "Center"},
    "Miles Burkhalter": {"number": 20, "position": "Guard"},
    "William Thornton": {"number": 1, "position": "Forward"},
    "Abney Moss": {"number": 21, "position": "Forward"},
    "Bennett Rooker": {"number": 35, "position": "Center"},
    "Garrett Bridgers": {"number": 23, "position": "Forward"},
    "Henry Russ": {"number": 25, "position": "Guard"},
    "Herrin Goodman": {"number": 24, "position": "Guard"},
    "IV Davidson": {"number": 20, "position": "Guard"},
    "Johnny Fondren": {"number": 30, "position": "Guard"},
    "Sam Milner": {"number": 13, "position": "Guard"},
    "Knox Hassell": {"number": 99, "position": "Forward"},
    "Hayes Grenfell": {"number": 98, "position": "Guard"},
    "Bowen Jones": {"number": 97, "position": "Forward"},

}

selected_player_info = (lambda x: f"#{player_info[x]['number']} — {player_info[x]['position']}" 
                        if x in player_info else x)(selected_player)

# Apply Game filter (if not "Season")
if selected_game != "Season":
    stats_df = stats_df[stats_df["Practice"] == str(selected_game)]

if selected_player != "Team":
    player_df = stats_df[stats_df["Player"] == selected_player]

    if player_df.empty:
        total_assists = 0
        total_turnovers = 0
        total_off_rebs = 0
        total_def_rebs = 0
        ast_to_ratio = 0
    else:
        # Sum the stats for that player
        total_assists = player_df["Ast"].sum()
        total_turnovers = player_df["TO"].sum()
        total_off_rebs = player_df["OFF_Reb"].sum()
        total_def_rebs = player_df["DEF_Reb"].sum()

            # Derived metric
        ast_to_ratio = round(total_assists / total_turnovers, 2) if total_turnovers != 0 else total_assists
else:
    # For "Team", sum all players
    total_assists = stats_df["Ast"].sum()
    total_turnovers = stats_df["TO"].sum()
    total_off_rebs = stats_df["OFF_Reb"].sum()
    total_def_rebs = stats_df["DEF_Reb"].sum()
    ast_to_ratio = round(total_assists / total_turnovers, 2) if total_turnovers != 0 else total_assists

with tab4:
        st.markdown(
        """
        <div style="
            border: 3px solid red;
            border-radius: 15px;
            padding: 5px 5px;
            width: 350px;              /* fixed width to ensure centering */
            margin: 10px auto;         /* auto horizontal margin centers the div */
            text-align: center;
        ">
            <h1 style='margin: 0; font-size: 48px; text-decoration: underline; font-weight: bold;'>Practice Stats</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

            # Left + Right columns for image and stats
        left_col, right_col = st.columns([1, 2])

        with left_col:
            col_empty, col_img, col_empty2 = st.columns([0.25,3.5,0.25])
            with col_img:
                photo_path = f"photos/{selected_player}.JPG"
                if selected_player == "Team":
                    st.image("photos/team_logo.png", width=175)
                elif os.path.exists(photo_path):
                    st.image(photo_path, width=175)
                else:
                    st.image("photos/team_logo.png", width=175)  # fallback image

        with right_col:
            if selected_player == "Team":
                st.markdown(styled_text("Jackson Prep Team", size=32, weight='normal', margin="8px 0px 16px 0px",underline=False, center=True, vertical=True), unsafe_allow_html=True)
                st.markdown(styled_text("0-0 (0-0)", size=24, weight='normal', margin="0px", underline=False, center=True, vertical=True), unsafe_allow_html=True)
            else:
                st.markdown(styled_text(f"{selected_player}", size=32, weight='normal', margin="8px 0px 16px 0px",underline=False, center=True, vertical=True), unsafe_allow_html=True)
                st.markdown(styled_text(f"{selected_player_info}", size=24, weight='normal', margin="0px", underline=False, center=True, vertical=True), unsafe_allow_html=True)


        st.markdown(
            "<hr style='border: 2px solid #0033A0; margin-top: 0.25rem; margin-bottom: 0rem;'>",
            unsafe_allow_html=True) 
        
        st.markdown(styled_text("Playmaking Stats", size=28, weight='normal', margin="0px 0px 0px 0px", underline=False, center=False, vertical=False), unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            centered_metric("Total Assists", total_assists)

        with col2:
            centered_metric("Total Turnovers", total_turnovers)

        with col3:
            centered_metric("Ast/TO Ratio", ast_to_ratio)

        st.markdown(
            "<hr style='border: 1px solid #0033A0; margin-top: 1rem; margin-bottom: 0rem;'>",
            unsafe_allow_html=True)  

        st.markdown(styled_text("Rebound Stats", size=28, weight='normal', margin="2px 0px 0px 0px", underline=False, center=False, vertical=False), unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            centered_metric("OFF Rebs", total_off_rebs)

        with col2:
            centered_metric("DEF Rebs", total_def_rebs)

        with col3:
            centered_metric("Total Rebs", total_off_rebs + total_def_rebs)

pickup_url = st.secrets["data"]["pickup_url"]
pickup_df = pd.read_csv(pickup_url)

player_info = {
    "Asher Reynolds": {"number": 4, "position": "Guard"},
    "Ben Roberts Smith": {"number": 12, "position": "Guard"},
    "Clark Smith": {"number": 11, "position": "Guard"},
    "Cray Luckett": {"number": 3, "position": "Guard/Forward"},
    "Ejay Napier": {"number": 2, "position": "Guard"},
    "Hemming Williamson": {"number": 5, "position": "Forward"},
    "Joseph Chaney": {"number": 0, "position": "Center"},
    "Judson Colley": {"number": 15, "position": "Center"},
    "Kaden Griffin": {"number": 22, "position": "Forward"},
    "Kendrick Rogers": {"number": 14, "position": "Forward"},
    "Manning Parks": {"number": 34, "position": "Center"},
    "Miles Burkhalter": {"number": 20, "position": "Guard"},
    "William Thornton": {"number": 1, "position": "Forward"},
    "Abney Moss": {"number": 21, "position": "Forward"},
    "Bennett Rooker": {"number": 35, "position": "Center"},
    "Garrett Bridgers": {"number": 23, "position": "Forward"},
    "Henry Russ": {"number": 25, "position": "Guard"},
    "Herrin Goodman": {"number": 24, "position": "Guard"},
    "IV Davidson": {"number": 20, "position": "Guard"},
    "Johnny Fondren": {"number": 30, "position": "Guard"},
    "Sam Milner": {"number": 13, "position": "Guard"},
    "Knox Hassell": {"number": 99, "position": "Forward"},
    "Hayes Grenfell": {"number": 98, "position": "Guard"},
    "Bowen Jones": {"number": 97, "position": "Forward"},

}

selected_player_info = (lambda x: f"#{player_info[x]['number']} — {player_info[x]['position']}" 
                        if x in player_info else x)(selected_player)

if selected_player != "Team":
    player_df = pickup_df[pickup_df["Player"] == selected_player]

            # Sum the stats for that player
    total_assists = player_df["Ast"].sum()
    total_turnovers = player_df["TO"].sum()
    total_off_rebs = player_df["OFF_Reb"].sum()
    total_def_rebs = player_df["DEF_Reb"].sum()

            # Derived metric
    ast_to_ratio = round(total_assists / total_turnovers, 2) if total_turnovers != 0 else total_assists
else:
    # For "Team", sum all players
    total_assists = pickup_df["Ast"].sum()
    total_turnovers = pickup_df["TO"].sum()
    total_off_rebs = pickup_df["OFF_Reb"].sum()
    total_def_rebs = pickup_df["DEF_Reb"].sum()
    ast_to_ratio = round(total_assists / total_turnovers, 2) if total_turnovers != 0 else total_assists

with tab5:
        st.markdown(
        """
        <div style="
            border: 3px solid red;
            border-radius: 15px;
            padding: 5px 5px;
            width: 350px;              /* fixed width to ensure centering */
            margin: 10px auto;         /* auto horizontal margin centers the div */
            text-align: center;
        ">
            <h1 style='margin: 0; font-size: 48px; text-decoration: underline; font-weight: bold;'>Pickup Stats</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

            # Left + Right columns for image and stats
        left_col, right_col = st.columns([1, 2])

        with left_col:
            col_empty, col_img, col_empty2 = st.columns([0.25,3.5,0.25])
            with col_img:
                photo_path = f"photos/{selected_player}.JPG"
                if selected_player == "Team":
                    st.image("photos/team_logo.png", width=175)
                elif os.path.exists(photo_path):
                    st.image(photo_path, width=175)
                else:
                    st.image("photos/team_logo.png", width=175)  # fallback image

        with right_col:
            if selected_player == "Team":
                st.markdown(styled_text("Jackson Prep Team", size=32, weight='normal', margin="8px 0px 16px 0px",underline=False, center=True, vertical=True), unsafe_allow_html=True)
                st.markdown(styled_text("0-0 (0-0)", size=24, weight='normal', margin="0px", underline=False, center=True, vertical=True), unsafe_allow_html=True)
            else:
                st.markdown(styled_text(f"{selected_player}", size=32, weight='normal', margin="8px 0px 16px 0px",underline=False, center=True, vertical=True), unsafe_allow_html=True)
                st.markdown(styled_text(f"{selected_player_info}", size=24, weight='normal', margin="0px", underline=False, center=True, vertical=True), unsafe_allow_html=True)


        st.markdown(
            "<hr style='border: 2px solid #0033A0; margin-top: 0.25rem; margin-bottom: 0rem;'>",
            unsafe_allow_html=True) 
        
        st.markdown(styled_text("Playmaking Stats", size=28, weight='normal', margin="0px 0px 0px 0px", underline=False, center=False, vertical=False), unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            centered_metric("Total Assists", total_assists)

        with col2:
            centered_metric("Total Turnovers", total_turnovers)

        with col3:
            centered_metric("Ast/TO Ratio", ast_to_ratio)

        st.markdown(
            "<hr style='border: 1px solid #0033A0; margin-top: 1rem; margin-bottom: 0rem;'>",
            unsafe_allow_html=True)  

        st.markdown(styled_text("Rebound Stats", size=28, weight='normal', margin="2px 0px 0px 0px", underline=False, center=False, vertical=False), unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            centered_metric("OFF Rebs", total_off_rebs)

        with col2:
            centered_metric("DEF Rebs", total_def_rebs)

        with col3:
            centered_metric("Total Rebs", total_off_rebs + total_def_rebs)


with tab6:
    st.markdown(
        """
        <div style="
            border: 3px solid red;
            border-radius: 15px;
            padding: 5px 5px;
            width: 500px;              /* fixed width to ensure centering */
            margin: 10px auto;         /* auto horizontal margin centers the div */
            text-align: center;
        ">
            <h1 style='margin: 0; font-size: 48px; text-decoration: underline; font-weight: bold;'>Team Game Stats</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(styled_text("Coming Soon!", size=32, weight='bold', margin="200px 0px", underline=False, center=True), unsafe_allow_html=True)

if selected_game != "Season":
    practice_df = practice_df[practice_df["Practice"] == str(selected_game)]

with tab7:
    st.markdown(
        """
        <div style="
            border: 3px solid red;
            border-radius: 10px;
            padding: 2px 2px;
            width: 400px;              /* fixed width to ensure centering */
            margin: 10px auto;         /* auto horizontal margin centers the div */
            text-align: center;
        ">
            <h1 style='margin: 0; font-size: 36px; text-decoration: underline; font-weight: bold;'>Team Practice Stats</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if practice_df.empty:
        st.markdown(
        styled_text(
            f"No Practice Stats Available for {selected_game}",
            size=32,
            weight='bold',
            margin="200px 0px",
            underline=False,
            center=True
        ),
        unsafe_allow_html=True
    )
    else:
        practice = practice_df.groupby('Player').agg(
            {
                'Ast': 'sum',
                'TO': 'sum',
                'OFF_Reb': 'sum',
                'DEF_Reb': 'sum'
            }
        ).reset_index()

        # Fill all NaN with 0
        practice = practice.fillna(0)

        practice['AST/TO Ratio'] = round(practice['Ast'] / practice['TO'].replace(0, np.nan), 2).fillna(0)
        practice['Total Rebs'] = practice['OFF_Reb'] + practice['DEF_Reb']

        practice = practice.rename(columns={
            "Ast": "Assists",
            "TO": "Turnovers",
            "OFF_Reb": "OFF Rebs",
            "DEF_Reb": "DEF Rebs",
        })

        cols = practice.columns.tolist()
        cols.insert(3, cols.pop(cols.index('AST/TO Ratio')))
        cols.insert(6, cols.pop(cols.index('Total Rebs')))
        practice = practice[cols]

        practice['Practice Score'] = practice['Assists'] - practice['Turnovers'] + practice['Total Rebs']

        # Sort Practice DataFrame
        practice = practice.sort_values(by=['Practice Score'], ascending=False)

        practice['Player'] = practice['Player'].apply(split_name)

        # Create display version (without Practice Score)
        practice_display = practice.drop(columns=['Practice Score']).copy()

        fig, ax = plt.subplots(figsize=(32, 40))
        ax.axis('off')

        # Create table
        table = plt.table(
            cellText=practice_display.values,
            colLabels=practice_display.columns,
            cellLoc='center',
            bbox=[-0.05, 0.13, 1.05, 0.95]
        )

        # Style table
        table.auto_set_font_size(False)
        table.set_fontsize(28)
        table.scale(1.4, 2.5)

        for key, cell in table.get_celld().items():
            row, col = key
            if row == 0:
                cell.set_facecolor('#da1a32')
                cell.set_linewidth(2.5)
                cell.set_edgecolor('#0033A0')
                cell.get_text().set_fontweight('bold')
                cell.get_text().set_color('#0033A0')
                cell.set_fontsize(30)
            else:
                cell.get_text().set_color('#0033A0')
                cell.set_edgecolor('#0033A0')
                cell.set_facecolor('#f2f2f2' if row % 2 == 0 else 'white')

        st.pyplot(fig)
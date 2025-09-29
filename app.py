# app.py
import streamlit as st
import pandas as pd
import base64
import matplotlib as matplotlib
import matplotlib.pyplot as plt
from functionsapp import plot_zone_chart, calc_zone_stats, styled_text, split_name
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
# Simple base64 authentication
# -----------------------------
ENCODED_USERS = {
    "Y29hY2g6MTIzNDU=": "coach",
    "YXNzaXN0YW50OmxldG1laW4=": "assistant"
}

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.username = None

if not st.session_state.auth:
    st.sidebar.header("Coach Login")
    username_input = st.sidebar.text_input("Username")
    password_input = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        combined = f"{username_input}:{password_input}"
        encoded = base64.b64encode(combined.encode()).decode()
        if encoded in ENCODED_USERS:
            st.session_state.auth = True
            st.session_state.username = username_input
            st.sidebar.success(f"Logged in as {username_input}")
        else:
            st.sidebar.error("Invalid username or password")
    st.stop()

if st.session_state.auth:
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.session_state.username = None
        st.experimental_rerun()


# -----------------------------
# Load Data
# -----------------------------
# Direct CSV URL
csv_url = "https://drive.google.com/uc?export=download&id=1ANJJdJJpgiwECxwXIKXTkt_KPOmqRemY"
csv_url_hustle = "https://drive.google.com/uc?export=download&id=1Hyf7kpSVtHk4tT9H3BrpFUI04giMRPYj"

# Load CSV into DataFrame
df = pd.read_csv(csv_url)
df_hustle = pd.read_csv(csv_url_hustle)

# Sidebar filters
st.sidebar.header("Filters")

# --- Player Dropdown ---
players = df["PLAYER"].dropna().unique().tolist()
players.sort()
players = ["Team"] + players  # Add "Team" option at top
selected_player = st.sidebar.selectbox("Select Player", players)

# --- Game Dropdown ---
if selected_player == "Team":
    games = df["GAME"].dropna().unique().tolist()
else:
    games = df[df["PLAYER"] == selected_player]["GAME"].dropna().unique().tolist()
games.sort()
games = ["Season"] + games  # Add "Season" option at top
selected_game = st.sidebar.selectbox("Select Game", games)

# --- Type Dropdown ---
game_types = st.sidebar.multiselect("Select Type", options=["Game", "Practice"], default=["Game"])

# --- Filtering Logic ---
if selected_player == "Team" and selected_game == "Season":
    filtered = df[df["TYPE"].isin(game_types)]
elif selected_player == "Team":
    filtered = df[(df["GAME"] == selected_game) & (df["TYPE"].isin(game_types))]
elif selected_game == "Season":
    filtered = df[(df["PLAYER"] == selected_player) & (df["TYPE"].isin(game_types))]
else:
    filtered = df[
        (df["PLAYER"] == selected_player) &
        (df["GAME"] == selected_game) &
        (df["TYPE"].isin(game_types))
    ]

# -----------------------------
# Layout: Image + Info + Scoreboard
# -----------------------------
# Create three tabs
tab1, tab2, tab3 = st.tabs(["Shot Chart", "Player Stats", 'Hustle Stats'])

# -----------------------------
# Tab 1: Original Shot Chart
# -----------------------------
with tab1:
    # Left + Right columns for image and stats
        left_col, right_col = st.columns([1, 2])

        with left_col:
            col_empty, col_img, col_empty2 = st.columns([0.25,3.5,0.25])
            with col_img:
                if selected_player == "Team":
                    st.image('photos/team_logo.png', width=175)
                else:
                    st.image(f"photos/{selected_player}.JPG", width=200)

        with right_col:
            if selected_player == "Team":
                st.markdown(styled_text("Jackson Prep Team", size=28, weight='bold', margin="8px",underline=False, center=True), unsafe_allow_html=True)
            else:
                st.markdown(styled_text(f"{selected_player}", size=28, weight='bold', margin="8px",underline=False, center=True), unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            # Layup, Midrange, 3PT metrics
                # --- Layup ---
            makesL, attL, pctL = calc_zone_stats(filtered, "Layup")
            col1.markdown(styled_text("Layup", size=22, margin="0px", underline=True, center=True), unsafe_allow_html=True)
            col1.markdown(styled_text(f"{makesL}/{attL}", size=18, weight="normal", margin="0px",underline=False, center=True), unsafe_allow_html=True)
            col1.markdown(styled_text(f"{pctL:.1f}%", size=18, weight="normal", margin="-10px",underline=False, center=True), unsafe_allow_html=True)

            # --- Midrange ---
            makesM, attM, pctM = calc_zone_stats(filtered, "Midrange")
            col2.markdown(styled_text("Midrange", size=22, margin="0px", underline=True, center=True), unsafe_allow_html=True)
            col2.markdown(styled_text(f"{makesM}/{attM}", size=18, weight="normal", margin="0px",underline=False, center=True), unsafe_allow_html=True)
            col2.markdown(styled_text(f"{pctM:.1f}%", size=18, weight="normal", margin="-10px",underline=False, center=True), unsafe_allow_html=True)

            # --- 3PT ---
            makes3, att3, pct3 = calc_zone_stats(filtered, "3PT")
            col3.markdown(styled_text("3PT", size=22, margin="0px", underline=True, center=True), unsafe_allow_html=True)
            col3.markdown(styled_text(f"{makes3}/{att3}", size=18, weight="normal", margin="0px",underline=False, center=True), unsafe_allow_html=True)
            col3.markdown(styled_text(f"{pct3:.1f}%", size=18, weight="normal", margin="-10px",underline=False, center=True), unsafe_allow_html=True)

        # Shot chart
        fig = plot_zone_chart(filtered, df)
        st.markdown("<div style='margin-top:-1000px'></div>", unsafe_allow_html=True)
        st.pyplot(fig, use_container_width=True)

# -----------------------------
# Tab 2: Player Stats Dashboard
# -----------------------------
with tab2:
        st.header("Additional Player Stats")
        
        # Example: show a table of season stats
        season_stats = filtered.groupby("PLAYER").agg(
            Total_Makes=('SHOT_MADE_FLAG', 'sum'),
            Total_Attempts=('SHOT_MADE_FLAG', 'count'),
            FG_Pct=('SHOT_MADE_FLAG', 'mean')
        ).reset_index()
        
        st.dataframe(season_stats)

        # You can also add new charts, metrics, or text here
        st.markdown("### Top 3PT Shooters")
        top_3pt = filtered[filtered["SHOT_TYPE"].str.contains("3PT")].groupby("PLAYER")["SHOT_MADE_FLAG"].mean().sort_values(ascending=False).head(5)
        st.bar_chart(top_3pt)

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


    # st.table(hustle)
    # st.dataframe(hustle, use_container_width=True, height=775)

    fig, ax = plt.subplots(figsize=(32, 40))
    fig.suptitle("Jackson Prep Basketball Hustle Stats", fontsize=36, color='#0033A0', fontweight='bold', y=0.975)
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
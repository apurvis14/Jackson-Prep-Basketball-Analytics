# app.py
import streamlit as st
import pandas as pd
import base64
from functionsapp import plot_zone_chart, calc_zone_stats, styled_text
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

# Load CSV into DataFrame
df = pd.read_csv(csv_url)

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
# left_col, right_col = st.columns([1, 2])

# with left_col:
#     if selected_player == "Team":
#         st.image("photos/team_logo.JPG", width=225)
#     else:
#         st.image(f"photos/{selected_player}.JPG", width=225)

# with right_col:
#     if selected_player == "Team":
#         st.header("Jackson Prep Team")
#     else:
#         st.header(selected_player)

#     col1, col2, col3 = st.columns(3)

#     # --- Layup ---
#     makesL, attL, pctL = calc_zone_stats(filtered, "Layup")
#     col1.markdown(styled_text("Layup", size=24, margin="2px", underline=True), unsafe_allow_html=True)
#     col1.markdown(styled_text(f"{makesL}/{attL}", size=20, weight="normal", margin="0px"), unsafe_allow_html=True)
#     col1.markdown(styled_text(f"{pctL:.1f}%", size=20, weight="normal", margin="4px"), unsafe_allow_html=True)

#     # --- Midrange ---
#     makesM, attM, pctM = calc_zone_stats(filtered, "Midrange")
#     col2.markdown(styled_text("Midrange", size=24, margin="2px", underline=True), unsafe_allow_html=True)
#     col2.markdown(styled_text(f"{makesM}/{attM}", size=20, weight="normal", margin="0px"), unsafe_allow_html=True)
#     col2.markdown(styled_text(f"{pctM:.1f}%", size=20, weight="normal", margin="4px"), unsafe_allow_html=True)

#     # --- 3PT ---
#     makes3, att3, pct3 = calc_zone_stats(filtered, "3PT")
#     col3.markdown(styled_text("3PT", size=24, margin="2px", underline=True), unsafe_allow_html=True)
#     col3.markdown(styled_text(f"{makes3}/{att3}", size=20, weight="normal", margin="0px"), unsafe_allow_html=True)
#     col3.markdown(styled_text(f"{pct3:.1f}%", size=20, weight="normal", margin="4px"), unsafe_allow_html=True)

# # st.markdown("---")

# # Shot chart
# fig = plot_zone_chart(filtered, df)
# st.markdown("<div style='margin-top:-1000px'></div>", unsafe_allow_html=True)
# st.pyplot(fig, use_container_width=True)

# Create two tabs
tab1, tab2 = st.tabs(["Shot Chart", "Player Stats"])

# -----------------------------
# Tab 1: Original Shot Chart
# -----------------------------
with tab1:
    # Left + Right columns for image and stats
    left_col, right_col = st.columns([1, 2])

    with left_col:
        if selected_player == "Team":
            st.image("photos/team_logo.png", width=150)
        else:
            st.image(f"photos/{selected_player}.JPG", width=150)

    with right_col:
        if selected_player == "Team":
            st.markdown(styled_text("Jackson Prep Team", size=28, weight='bold', margin="0px"), unsafe_allow_html=True)
        else:
            st.markdown(styled_text(f"{selected_player}", size=28, weight='bold', margin="0px"), unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        # Layup, Midrange, 3PT metrics
            # --- Layup ---
        makesL, attL, pctL = calc_zone_stats(filtered, "Layup")
        col1.markdown(styled_text("Layup", size=22, margin="0px", underline=True), unsafe_allow_html=True)
        col1.markdown(styled_text(f"{makesL}/{attL}", size=18, weight="normal", margin="0px"), unsafe_allow_html=True)
        col1.markdown(styled_text(f"{pctL:.1f}%", size=18, weight="normal", margin="-10px"), unsafe_allow_html=True)

        # --- Midrange ---
        makesM, attM, pctM = calc_zone_stats(filtered, "Midrange")
        col2.markdown(styled_text("Midrange", size=22, margin="0px", underline=True), unsafe_allow_html=True)
        col2.markdown(styled_text(f"{makesM}/{attM}", size=18, weight="normal", margin="0px"), unsafe_allow_html=True)
        col2.markdown(styled_text(f"{pctM:.1f}%", size=18, weight="normal", margin="-10px"), unsafe_allow_html=True)

        # --- 3PT ---
        makes3, att3, pct3 = calc_zone_stats(filtered, "3PT")
        col3.markdown(styled_text("3PT", size=22, margin="0px", underline=True), unsafe_allow_html=True)
        col3.markdown(styled_text(f"{makes3}/{att3}", size=18, weight="normal", margin="0px"), unsafe_allow_html=True)
        col3.markdown(styled_text(f"{pct3:.1f}%", size=18, weight="normal", margin="-10px"), unsafe_allow_html=True)

    # Shot chart
    fig = plot_zone_chart(filtered, df)
    st.markdown("<div style='margin-top:-1000px'></div>", unsafe_allow_html=True)
    st.pyplot(fig, use_container_width=True)

# -----------------------------
# Tab 2: New Information
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
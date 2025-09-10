# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc, Polygon
import numpy as np
import math
import base64
import os

# -----------------------------
# Page Config
# --------------------------
st.set_page_config(layout="centered", page_title="HS Basketball Dashboard")

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

df['ZONE'] = df['ZONE'].str.strip()
df['SHOT_TYPE'] = df['SHOT_TYPE'].str.strip()

# Sidebar filters
st.sidebar.header("Filters")
players = df["PLAYER"].unique()
selected_player = st.sidebar.selectbox("Select Player", players)
games = df[df["PLAYER"] == selected_player]["GAME"].unique()
selected_game = st.sidebar.selectbox("Select Game", games)
game_types = st.sidebar.multiselect("Select Type", options=["Game", "Practice"], default=["Game"])

filtered = df[
    (df["PLAYER"] == selected_player) &
    (df["GAME"] == selected_game) &
    (df["TYPE"].isin(game_types))
]

# -----------------------------
# Court Drawing Functions
# -----------------------------
def draw_hs_half_court(ax=None, color='blue', lw=2):
    if ax is None:
        ax = plt.gca()
    hoop = Circle((0, -15), radius=7.5, linewidth=lw, color=color, fill=False)
    backboard = Rectangle((-30, -22.5), 60, 0, linewidth=lw, color=color)
    paint = Rectangle((-72, -47.5), 144, 190, linewidth=lw, color=color, fill=False)
    top_free_throw = Arc((0, 142.5), 144, 144, theta1=0, theta2=180, linewidth=lw, color=color)

    # Free Throw Side Dash 
    free_throw_dash_a = Rectangle((-72, 90), -10, 0, linewidth=lw, color=color) 
    free_throw_dash_b = Rectangle((72, 90), 10, 0, linewidth=lw, color=color) 

    free_throw_dash_c = Rectangle((-72, 60), -10, 0, linewidth=lw, color=color) 
    free_throw_dash_d = Rectangle((72, 60), 10, 0, linewidth=lw, color=color) 

    free_throw_dash_e = Rectangle((-72, 120), -10, 0, linewidth=lw, color=color)
    free_throw_dash_f = Rectangle((72, 120), 10, 0, linewidth=lw, color=color)

    # Free Throw Blocks near bottom of Paint 
    free_throw_block = Rectangle((-72, 5), -10, 20, linewidth=lw, color=color, fill=color) 
    free_throw_block_2 = Rectangle((72, 5), 10, 20, linewidth=lw, color=color, fill=color)

    restricted = Arc((0, -15), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)
    baseline = Rectangle((-250, -47.5), 500, 0, linewidth=lw, color=color)
    corner_three_a = Rectangle((-220, -47.5), 0, 114, linewidth=lw, color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 114, linewidth=lw, color=color)
    three_arc = Arc((0, -22.5), 474, 474, theta1=22, theta2=158, linewidth=lw, color=color)
    sideline_a = Rectangle((-250, -47.5), 0, 422.5, linewidth=lw, color=color)
    sideline_b = Rectangle((250, -47.5), 0, 422.5, linewidth=lw, color=color)
    half_court = Rectangle((-375, 375), 700, 0, linewidth=lw, color=color)
    center_circle = Arc((0, 375), 120, 120, theta1=180, theta2=360, linewidth=lw, color=color)
    court_elements = [hoop, backboard, paint, top_free_throw, restricted, three_arc, baseline,
                      corner_three_a, corner_three_b, sideline_a, sideline_b, half_court, center_circle,
                      free_throw_dash_a, free_throw_dash_b, free_throw_dash_c, free_throw_dash_d, free_throw_dash_e, free_throw_dash_f,
                      free_throw_block, free_throw_block_2]
    for el in court_elements:
        ax.add_patch(el)
    return ax

# -----------------------------
# Zones
# -----------------------------
def get_updated_zones():
    ARC_CX, ARC_CY = 0.0, -22.5
    ARC_R = 237.0
    R_OUT = ARC_R + 140.0

    def polar_to_xy(angle_deg, radius, cx=ARC_CX, cy=ARC_CY):
        a = math.radians(angle_deg)
        return (cx + radius*math.cos(a), cy + radius*math.sin(a))

    def arc_points(angle_start, angle_end, radius=ARC_R, n=60):
        angles = np.linspace(angle_start, angle_end, n)
        return [polar_to_xy(a, radius) for a in angles]

    def arc_y_at_x(x):
        dx = x - ARC_CX
        if abs(dx) > ARC_R:
            dx = max(min(dx, ARC_R), -ARC_R)
        return ARC_CY + math.sqrt(ARC_R**2 - dx**2)

    def threept_sector(start_ang, end_ang, inner_radius=ARC_R, outer_radius=None):
        if outer_radius is None:
            outer_radius = R_OUT - 15
        inner = arc_points(start_ang, end_ang, radius=inner_radius)
        outer = arc_points(end_ang, start_ang, radius=outer_radius)
        return inner + outer

    def midrange_arc_top_polygon_fixed(x_min, x_max, y_bottom, n_points=50):
        angles = np.linspace(0, 180, n_points*2)
        arc_pts = [polar_to_xy(a, ARC_R) for a in angles]
        top_pts = [(x, y) for x, y in arc_pts if x_min <= x <= x_max and y >= y_bottom]
        top_pts.append((x_min, arc_y_at_x(x_min)))
        top_pts.append((x_max, arc_y_at_x(x_max)))
        top_pts = sorted(top_pts, key=lambda p: p[0])
        bottom_left_y = min(y_bottom, arc_y_at_x(x_min))
        bottom_right_y = min(y_bottom, arc_y_at_x(x_max))
        polygon = [(x_min, bottom_left_y), (x_max, bottom_right_y)] + sorted(top_pts, key=lambda p: p[0], reverse=True)
        return polygon

    def midrange_center_arc_top_polygon(x_min, x_max, y_bottom, n_points=30):
        angles = np.linspace(0, 180, n_points*2)
        arc_pts = [polar_to_xy(a, ARC_R) for a in angles]
        top_pts = [(x, y) for x, y in arc_pts if x_min < x < x_max]
        top_pts.append((x_min, arc_y_at_x(x_min)))
        top_pts.append((x_max, arc_y_at_x(x_max)))
        top_pts = sorted(top_pts, key=lambda p: p[0], reverse=True)
        polygon = [(x_min, y_bottom), (x_max, y_bottom)] + top_pts
        return polygon

    zones = {}

    # Corners
    y_leftcorner = arc_y_at_x(-220)
    y_rightcorner = arc_y_at_x(220)
    zones['Left Corner 3'] = [(-250, -47.5), (-220, -47.5), (-220, y_leftcorner), (-250, y_leftcorner)]
    zones['Right Corner 3'] = [(220, -47.5), (250, -47.5), (250, y_rightcorner), (220, y_rightcorner)]

    # 3PT wings/top
    A_right_corner = math.degrees(math.atan2(y_rightcorner - ARC_CY, 220 - ARC_CX))
    A_left_corner = math.degrees(math.atan2(y_leftcorner - ARC_CY, -220 - ARC_CX))
    zones['Left Wing 3'] = threept_sector(110, A_left_corner)
    zones['Right Wing 3'] = threept_sector(A_right_corner, 70)
    zones['Top of Key 3'] = threept_sector(70, 110)

    # Baseline midrange
    zones['Left Midrange BL'] = [(-220, -47.5), (-72, -47.5), (-72, y_leftcorner), (-220, y_leftcorner)]
    zones['Right Midrange BL'] = [(72, -47.5), (220, -47.5), (220, y_rightcorner), (72, y_rightcorner)]

    # Layups
    zones['Left Layup'] = [(-72, -47.5), (0, -47.5), (0, 60), (-72, 60)]
    zones['Right Layup'] = [(0, -47.5), (72, -47.5), (72, 60), (0, 60)]

    # Wing midrange
    top_of_6_7 = max(max(y for x,y in zones['Left Midrange BL']), max(y for x,y in zones['Right Midrange BL']))
    zones['LW Midrange'] = midrange_arc_top_polygon_fixed(-220, -72, top_of_6_7)
    zones['RW Midrange'] = midrange_arc_top_polygon_fixed(72, 220, top_of_6_7)

    # Center midrange
    zones['Left Center Midrange'] = midrange_center_arc_top_polygon(-72, 0, -47.5)
    zones['Right Center Midrange'] = midrange_center_arc_top_polygon(0, 72, -47.5)

    # Convert to Polygon objects
    poly_zones = {name: Polygon(coords, closed=True) for name, coords in zones.items()}
    return poly_zones

# -----------------------------
# Plot Zones
# -----------------------------
def plot_zone_chart(df):
    zone_stats = df.groupby('ZONE').agg(
        makes=('SHOT_MADE_FLAG', 'sum'),
        attempts=('SHOT_MADE_FLAG', 'count')
    ).reset_index()
    zone_stats['FG%'] = (zone_stats['makes'] / zone_stats['attempts']) * 100
    overall_fg = df['SHOT_MADE_FLAG'].mean() * 100

    zone_polys = get_updated_zones()

    fig, ax = plt.subplots(figsize=(18, 14), dpi = 200)
    draw_hs_half_court(ax)
    ax.set_xlim(-250, 250)
    ax.set_ylim(-47.5, 422.5)
    ax.axis('off')

    for zone_name, poly in zone_polys.items():
        if zone_name not in zone_stats['ZONE'].values:
            continue
        stats = zone_stats[zone_stats['ZONE'] == zone_name].iloc[0]
        color = 'green' if stats['FG%'] >= overall_fg else 'red'
        ax.add_patch(Polygon(poly.get_xy(), closed=True, facecolor=color, alpha=0.4, edgecolor='black', linestyle = '--'))
        xs = poly.get_xy()[:, 0]
        ys = poly.get_xy()[:, 1]
        cx,cy = np.mean(xs), np.mean(ys)


        # Offset LW and RW Midrange text slightly
        if zone_name in ['LW Midrange', 'RW Midrange']:
            cy -= 30 

        if zone_name in ['RW Midrange']:
            cx -= 20 
        
        if zone_name in ['LW Midrange']:
            cx += 20

        if zone_name in ['Left Midrange BL']:
            cx +=20

        if zone_name in ['Top of Key 3','Left Center Midrange', 'Right Center Midrange']:
            cy -= 10

        if zone_name in ['Left Layup']:
            cx += 10

        if zone_name in ['Right Layup']:
            cx += 10
        
        if zone_name in ['Left Corner 3', 'Right Corner 3']:
            cx += 3

        ax.text(cx, cy+20, f"{int(stats['makes'])}/{int(stats['attempts'])}",
                ha='center', va='center', fontsize=16, weight='bold',
                bbox=dict(facecolor='lightgray', alpha=0.6, edgecolor='none', pad=2))

        ax.text(cx, cy, f"{stats['FG%']:.1f}%",
                ha='center', va='center', fontsize=16,
                bbox=dict(facecolor='lightgray', alpha=0.6, edgecolor='none', pad=2))

    return fig

# -----------------------------
# Layout: Image + Info + Scoreboard
# -----------------------------
# left_col, right_col = st.columns([1,2])

# with left_col:
#     st.image(f"photos/{selected_player}.JPG", width=250)

# with right_col:
#     st.header(selected_player)
#     col1, col2, col3 = st.columns(3)

#     def calc_zone_pct(df: pd.DataFrame, type: str) -> str:
#         """
#         Calculate the field goal percentage for a specific zone.
#         Returns a string with percentage formatted to 1 decimal place.
#         """
#         # Filter shots in the given zone
#         zone: pd.DataFrame = df[df["SHOT_TYPE"].str.contains(type, case=False, na=False)]
#         if zone.empty:
#             return "0%"
        
#         fg_pct: float = zone['SHOT_MADE_FLAG'].mean() * 100
#         return f"{fg_pct:.1f}%"

#     # Display metrics
#     col1.metric("3PT %", calc_zone_pct(filtered, "3PT"))
#     col2.metric("Midrange %", calc_zone_pct(filtered, "Midrange"))
#     col3.metric("Layup %", calc_zone_pct(filtered, "Layup"))

# st.markdown("---")

# # Shot chart
# fig = plot_zone_chart(filtered)
# st.markdown("<div style='margin-top:-1000px'></div>", unsafe_allow_html=True)
# st.pyplot(fig, use_container_width=True)

with st.container():
    left_col, right_col = st.columns([1, 2])

    # -----------------------------
    # Left Column: Player Image
    # -----------------------------
    with left_col:
        image_path = f"photos/{selected_player}.JPG"
        if os.path.exists(image_path):
            st.image(image_path, width=250)
        else:
            st.warning(f"No image found for {selected_player}")
            placeholder_url = "https://via.placeholder.com/250x250.png?text=No+Image"
            st.image(placeholder_url, width=250)

    # -----------------------------
    # Right Column: Player Name + Metrics
    # -----------------------------
    with right_col:
        st.header(selected_player)

        col1, col2, col3 = st.columns(3)

        def calc_zone_pct(df: pd.DataFrame, type: str) -> str:
            zone: pd.DataFrame = df[df["SHOT_TYPE"].str.contains(type, case=False, na=False)]
            if zone.empty:
                return "0%"
            fg_pct: float = zone['SHOT_MADE_FLAG'].mean() * 100
            return f"{fg_pct:.1f}%"

        col1.metric("3PT %", calc_zone_pct(filtered, "3PT"))
        col2.metric("Midrange %", calc_zone_pct(filtered, "Midrange"))
        col3.metric("Layup %", calc_zone_pct(filtered, "Layup"))

    # st.markdown(
    #     "<hr style='margin-top:10px; margin-bottom:0px; border:1px solid #ddd;'>",
    #     unsafe_allow_html=True
    # )

    # -----------------------------
    # Shot Chart
    # -----------------------------
    fig = plot_zone_chart(filtered)
    st.pyplot(fig, use_container_width=True)

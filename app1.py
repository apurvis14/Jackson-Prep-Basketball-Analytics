# save this as app.py and run with:  streamlit run app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc, Polygon
import numpy as np
import math

# ---------------------------------------------------
# Your existing court-drawing function
# ---------------------------------------------------
def draw_hs_half_court(ax=None, color='black', lw=2):
    if ax is None:
        ax = plt.gca()
    hoop = Circle((0, -15), radius=7.5, linewidth=lw, color=color, fill=False)
    backboard = Rectangle((-30, -22.5), 60, 0, linewidth=lw, color=color)
    paint = Rectangle((-72, -47.5), 144, 190, linewidth=lw, color=color, fill=False)
    top_free_throw = Arc((0, 142.5), 144, 144, theta1=0, theta2=180, linewidth=lw, color=color)
    free_throw_dash_a = Rectangle((-72, 90), -10, 0, linewidth=lw, color=color) 
    free_throw_dash_b = Rectangle((72, 90), 10, 0, linewidth=lw, color=color) 
    free_throw_dash_c = Rectangle((-72, 60), -10, 0, linewidth=lw, color=color) 
    free_throw_dash_d = Rectangle((72, 60), 10, 0, linewidth=lw, color=color) 
    free_throw_dash_e = Rectangle((-72, 120), -10, 0, linewidth=lw, color=color)
    free_throw_dash_f = Rectangle((72, 120), 10, 0, linewidth=lw, color=color)
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

# ---------------------------------------------------
# Your existing zone function (unchanged)
# ---------------------------------------------------
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
        bottom_left_y = min(y_bottom, arc_y_at_x(x_min))
        bottom_right_y = min(y_bottom, arc_y_at_x(x_max))
        top_pts = sorted(top_pts, key=lambda p: p[0])
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
    y_leftcorner = arc_y_at_x(-220)
    y_rightcorner = arc_y_at_x(220)
    zones['Left Corner 3'] = [(-250, -47.5), (-220, -47.5), (-220, y_leftcorner), (-250, y_leftcorner)]
    zones['Right Corner 3'] = [(220, -47.5), (250, -47.5), (250, y_rightcorner), (220, y_rightcorner)]

    A_right_corner = math.degrees(math.atan2(y_rightcorner - ARC_CY, 220 - ARC_CX))
    A_left_corner = math.degrees(math.atan2(y_leftcorner - ARC_CY, -220 - ARC_CX))
    zones['Left Wing 3'] = threept_sector(110, A_left_corner)
    zones['Right Wing 3'] = threept_sector(A_right_corner, 70)
    zones['Top of Key 3'] = threept_sector(70, 110)

    zones['Left Midrange BL'] = [(-220, -47.5), (-72, -47.5), (-72, y_leftcorner), (-220, y_leftcorner)]
    zones['Right Midrange BL'] = [(72, -47.5), (220, -47.5), (220, y_rightcorner), (72, y_rightcorner)]

    zones['Left Layup'] = [(-72, -47.5), (0, -47.5), (0, 60), (-72, 60)]
    zones['Right Layup'] = [(0, -47.5), (72, -47.5), (72, 60), (0, 60)]

    top_of_6_7 = max(max(y for x,y in zones['Left Midrange BL']), max(y for x,y in zones['Right Midrange BL']))
    zones['LW Midrange'] = midrange_arc_top_polygon_fixed(-220, -72, top_of_6_7)
    zones['RW Midrange'] = midrange_arc_top_polygon_fixed(72, 220, top_of_6_7)

    zones['Left Center Midrange'] = midrange_center_arc_top_polygon(-72, 0, -47.5)
    zones['Right Center Midrange'] = midrange_center_arc_top_polygon(0, 72, -47.5)

    poly_zones = {name: Polygon(coords, closed=True) for name, coords in zones.items()}
    return poly_zones

# ---------------------------------------------------
# Shot chart plotting with zones
# ---------------------------------------------------
def plot_zone_chart(df, ax):
    zone_stats = df.groupby('ZONE').agg(
        makes=('SHOT_MADE_FLAG', 'sum'),
        attempts=('SHOT_MADE_FLAG', 'count')
    ).reset_index()
    zone_stats['FG%'] = (zone_stats['makes'] / zone_stats['attempts']) * 100
    overall_fg = df['SHOT_MADE_FLAG'].mean() * 100

    zone_polys = get_updated_zones()
    draw_hs_half_court(ax)
    ax.set_xlim(-250, 250)
    ax.set_ylim(-47.5, 422.5)
    ax.axis('off')

    for zone_name, poly in zone_polys.items():
        if zone_name not in zone_stats['ZONE'].values:
            continue
        stats = zone_stats[zone_stats['ZONE'] == zone_name].iloc[0]
        color = 'green' if stats['FG%'] >= overall_fg else 'red'
        ax.add_patch(Polygon(poly.get_xy(), closed=True, facecolor=color, alpha=0.3, edgecolor='black', linestyle='--'))

        xs = poly.get_xy()[:, 0]
        ys = poly.get_xy()[:, 1]
        cx, cy = np.mean(xs), np.mean(ys)

        if zone_name in ['LW Midrange', 'RW Midrange']:
            cy -= 30 
        if zone_name == 'RW Midrange':
            cx -= 20 
        if zone_name == 'LW Midrange':
            cx += 20
        if zone_name == 'Left Midrange BL':
            cx += 20
        if zone_name in ['Top of Key 3','Left Center Midrange', 'Right Center Midrange']:
            cy -= 10
        if zone_name == 'Left Layup':
            cx += 10
        if zone_name == 'Right Layup':
            cx += 10

        ax.text(cx, cy+20, f"{int(stats['makes'])}/{int(stats['attempts'])}",
                ha='center', va='center', fontsize=10, weight='bold',
                bbox=dict(facecolor='lightgray', alpha=0.6, edgecolor='none', pad=2))
        ax.text(cx, cy, f"{stats['FG%']:.1f}%",
                ha='center', va='center', fontsize=10,
                bbox=dict(facecolor='lightgray', alpha=0.6, edgecolor='none', pad=2))

# ---------------------------------------------------
# Streamlit App
# ---------------------------------------------------
st.set_page_config(layout="wide")
st.title("High School Basketball Shot Dashboard")

# Load shot data
df = pd.read_csv("shot_data.csv")

# Sidebar filters
st.sidebar.header("Filters")
players = df["PLAYER"].unique()
selected_player = st.sidebar.selectbox("Select Player", players)
games = df[df["PLAYER"] == selected_player]["GAME"].unique()
selected_game = st.sidebar.selectbox("Select Game", games)
game_types = st.sidebar.multiselect("Select Type", options=["Game", "Practice"], default=["Game","Practice"])

# Filtered dataset
filtered = df[
    (df["PLAYER"] == selected_player) &
    (df["GAME"] == selected_game) &
    (df["TYPE"].isin(game_types))
]

# Player info
st.image(f"photos/{selected_player}.jpg", width=150)
st.header(selected_player)

# Mini scoreboard
def calc_zone_pct(df, zone_name):
    zone = df[df["ZONE"].str.contains(zone_name, case=False, na=False)]
    if len(zone) == 0:
        return "0%"
    return f"{100 * zone['SHOT_MADE_FLAG'].mean():.1f}%"

col1, col2, col3 = st.columns(3)
col1.metric("3PT %", calc_zone_pct(filtered, "3"))
col2.metric("Midrange %", calc_zone_pct(filtered, "Midrange"))
col3.metric("Layup %", calc_zone_pct(filtered, "Layup"))

# Shot chart
fig, ax = plt.subplots(figsize=(12, 11))
plot_zone_chart(filtered, ax)
st.pyplot(fig)
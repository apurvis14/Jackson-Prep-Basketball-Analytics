# save this as app.py and run with:  streamlit run app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc, Polygon
import numpy as np
import math
import streamlit_authenticator as stauth

# ==============================================
# AUTHENTICATION SETUP
# ==============================================
# Everyone shares the same name and password
names = ["Coach Smith"]
usernames = ["coach"]
shared_password = "letmein"

# Hash the single password once
hashed_pw = stauth.Hasher(['letmein']).generate()

# Duplicate the hashed password for each user
hashed_pw_list = [hashed_pw[0]] * len(usernames)

# Set up the authenticator
authenticator = stauth.Authenticate(
    dict(zip(usernames, names)),
    usernames,
    hashed_pw_list,
    "shot_dashboard", "abcdef", cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")

# ==============================================
# MAIN APP (only shows if authenticated)
# ==============================================
if authentication_status:

    # ----------------------------
    # Court drawing function
    # ----------------------------
    def draw_hs_half_court(ax=None, color='black', lw=2):
        if ax is None:
            ax = plt.gca()
        hoop = Circle((0, -15), radius=7.5, linewidth=lw, color=color, fill=False)
        backboard = Rectangle((-30, -22.5), 60, 0, linewidth=lw, color=color)
        paint = Rectangle((-72, -47.5), 144, 190, linewidth=lw, color=color, fill=False)
        top_free_throw = Arc((0, 142.5), 144, 144, theta1=0, theta2=180, linewidth=lw, color=color)
        restricted = Arc((0, -15), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)
        baseline = Rectangle((-250, -47.5), 500, 0, linewidth=lw, color=color)
        corner_three_a = Rectangle((-220, -47.5), 0, 114, linewidth=lw, color=color)
        corner_three_b = Rectangle((220, -47.5), 0, 114, linewidth=lw, color=color)
        three_arc = Arc((0, -22.5), 474, 474, theta1=22, theta2=158, linewidth=lw, color=color)
        sideline_a = Rectangle((-250, -47.5), 0, 422.5, linewidth=lw, color=color)
        sideline_b = Rectangle((250, -47.5), 0, 422.5, linewidth=lw, color=color)
        half_court = Rectangle((-375, 375), 700, 0, linewidth=lw, color=color)
        center_circle = Arc((0, 375), 120, 120, theta1=180, theta2=360, linewidth=lw, color=color)

        for el in [hoop, backboard, paint, top_free_throw, restricted, baseline,
                   corner_three_a, corner_three_b, three_arc,
                   sideline_a, sideline_b, half_court, center_circle]:
            ax.add_patch(el)
        return ax

    # ----------------------------
    # Your zones + plotting functions (shortened here, keep your full ones!)
    # ----------------------------
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

    # ----------------------------
    # PAGE CONFIG
    # ----------------------------
    st.set_page_config(layout="wide")
    st.title("High School Basketball Shot Dashboard")

    # ----------------------------
    # Load shot data
    # ----------------------------
    df = pd.read_csv("shot_data.csv")

    # ----------------------------
    # Sidebar filters
    # ----------------------------
    st.sidebar.header("Filters")
    players = df["PLAYER"].unique()
    selected_player = st.sidebar.selectbox("Select Player", players)
    games = df[df["PLAYER"] == selected_player]["GAME"].unique()
    selected_game = st.sidebar.selectbox("Select Game", games)
    game_types = st.sidebar.multiselect("Select Type", options=["Game", "Practice"],
                                        default=["Game", "Practice"])

    filtered = df[
        (df["PLAYER"] == selected_player) &
        (df["GAME"] == selected_game) &
        (df["TYPE"].isin(game_types))
    ]

    # ----------------------------
    # Layout: photo + name + metrics side by side
    # ----------------------------
    col_img, col_info = st.columns([1, 3])

    with col_img:
        st.image(f"photos/{selected_player}.jpg", width=180)

    with col_info:
        st.header(selected_player)

        def calc_zone_pct(df, zone_name):
            zone = df[df["ZONE"].str.contains(zone_name, case=False, na=False)]
            if len(zone) == 0:
                return "0%"
            return f"{100 * zone['SHOT_MADE_FLAG'].mean():.1f}%"

        mcol1, mcol2, mcol3 = st.columns(3)
        mcol1.metric("3PT %", calc_zone_pct(filtered, "3"))
        mcol2.metric("Midrange %", calc_zone_pct(filtered, "Midrange"))
        mcol3.metric("Layup %", calc_zone_pct(filtered, "Layup"))

    # ----------------------------
    # Shot chart
    # ----------------------------
    fig, ax = plt.subplots(figsize=(10, 9))
    plot_zone_chart(filtered, ax)
    st.pyplot(fig)

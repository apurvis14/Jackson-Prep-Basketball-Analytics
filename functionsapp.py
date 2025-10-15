import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc, Polygon
import numpy as np
import math
import base64
import streamlit as st

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
    zones['Right Wing 3'] = threept_sector(110, A_left_corner)
    zones['Left Wing 3'] = threept_sector(A_right_corner, 70)
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
# Final Plot
# -----------------------------
def plot_zone_chart(filtered_df, df_team):
    """
    Plot a basketball shot chart by zone with:
    - Red/green color based on relative FG% vs team benchmark
    - Multi-thresholds
    - Alpha scaled by attempts
    """
    # -----------------------------
    # Calculate per-zone stats for the player/game selection
    # -----------------------------
    zone_stats = filtered_df.groupby('ZONE').agg(
        makes=('SHOT_MADE_FLAG', 'sum'),
        attempts=('SHOT_MADE_FLAG', 'count')
    ).reset_index()
    zone_stats['FG%'] = (zone_stats['makes'] / zone_stats['attempts']) * 100

    # -----------------------------
    # Calculate team benchmarks per zone type
    # -----------------------------
    # Map zones to 3 categories
    def get_zone_type(zone_name):
        if "3" in zone_name:
            return "3PT"
        elif "Midrange" in zone_name:
            return "Midrange"
        else:
            return "Layup"

    df_team['ZONE_TYPE'] = df_team['ZONE'].apply(get_zone_type)
    team_benchmarks = df_team.groupby('ZONE_TYPE')['SHOT_MADE_FLAG'].mean() * 100  # FG% per type

    # -----------------------------
    # Prepare polygons
    # -----------------------------
    zone_polys = get_updated_zones()

    fig, ax = plt.subplots(figsize=(18, 18), dpi=200)
    draw_hs_half_court(ax)
    ax.set_xlim(-250, 250)
    ax.set_ylim(-47.5, 422.5)
    ax.axis('off')

    # Alpha scaling
    min_alpha = 0.2
    max_alpha = 0.8
    max_attempts = zone_stats['attempts'].max() if not zone_stats.empty else 1

    for zone_name, poly in zone_polys.items():
        if zone_name not in zone_stats['ZONE'].values:
            continue

        stats = zone_stats[zone_stats['ZONE'] == zone_name].iloc[0]
        zone_fg = stats['FG%']
        attempts = stats['attempts']

        # Determine zone type
        z_type = get_zone_type(zone_name)
        benchmark = team_benchmarks[z_type]

        # -----------------------------
        # Multi-threshold color logic
        # -----------------------------
        # thresholds (relative to benchmark)
        ratio = zone_fg / benchmark if benchmark > 0 else 0
        if ratio < 0.5:
            color = 'red'
        elif ratio < 0.7: 
            color = 'orange'
        elif ratio < 1.0:
            color = 'yellowgreen'
        elif ratio < 1.2:
            color = 'green'
        else:
            color = 'darkgreen'

        # -----------------------------
        # Alpha scaling based on attempts
        # -----------------------------
        alpha = min_alpha + (attempts / max_attempts) * (max_alpha - min_alpha)

        # Draw zone
        ax.add_patch(Polygon(
            poly.get_xy(), closed=True,
            facecolor=color, alpha=alpha, edgecolor='black', linestyle='--'
        ))

        # -----------------------------
        # Text placement
        # -----------------------------
        xs = poly.get_xy()[:, 0]
        ys = poly.get_xy()[:, 1]
        cx, cy = np.mean(xs), np.mean(ys)

        # Offset LW and RW Midrange text slightly
        if zone_name in ['LW Midrange', 'RW Midrange']:
            cy -= 30
        if zone_name == 'RW Midrange':
            cx -= 20
        if zone_name == 'LW Midrange':
            cx += 20
        if zone_name == 'Left Midrange BL':
            cx += 20
        if zone_name in ['Top of Key 3', 'Left Center Midrange', 'Right Center Midrange']:
            cy -= 10
        if zone_name == 'Left Layup':
            cx += 10
        if zone_name == 'Right Layup':
            cx += 10
        if zone_name in ['Left Corner 3', 'Right Corner 3']:
            cx += 3

        ax.text(cx, cy + 20, f"{int(stats['makes'])}/{int(stats['attempts'])}",
                ha='center', va='center', fontsize=20, weight='bold',
                bbox=dict(facecolor='lightgray', alpha=0.6, edgecolor='none', pad=2))
        ax.text(cx, cy, f"{zone_fg:.1f}%",
                ha='center', va='center', fontsize=20,
                bbox=dict(facecolor='lightgray', alpha=0.6, edgecolor='none', pad=2))
    plt.tight_layout()
    fig.subplots_adjust(top=1, bottom=0.05)

    return fig


def calc_zone_stats(df: pd.DataFrame, shot_type: str):
    zone = df[df["SHOT_TYPE"].str.contains(shot_type, case=False, na=False)]
    makes = int(zone["SHOT_MADE_FLAG"].sum())
    attempts = int(zone.shape[0])
    pct = makes / attempts * 100 if attempts > 0 else 0
    return makes, attempts, pct

# def styled_text(text, size=22, weight="bold", margin="0px", underline=False, center=False, vertical=False):
#     underline_css = "text-decoration: underline;" if underline else ""
#     center_css = "text-align: center;" if center else ""
#     vertical_css = "display: flex; align-items: center; justify-content: center;" if vertical else ""
#     return f"<div style='font-size:{size}px; font-weight:{weight}; margin-bottom:{margin};,{center_css} {underline_css } {vertical_css}'>{text}</div>"

def styled_text(
    text, 
    size=22, 
    weight="bold", 
    margin="0px 0px 8px 0px",  # top right bottom left
    underline=False, 
    center=False, 
    vertical=False
):
    underline_css = "text-decoration: underline;" if underline else ""
    center_css = "text-align: center;" if center else ""
    vertical_css = "display: flex; align-items: center; justify-content: center;" if vertical else ""

    return f"""
    <div style='
        font-size:{size}px; 
        font-weight:{weight}; 
        margin:{margin}; 
        {center_css} {underline_css} {vertical_css}'
    >
        {text}
    </div>
    """

def split_name(name):
    parts = name.split()  # split by spaces
    if len(parts) == 2:
        # First and Last
        return f"{parts[0]}\n{parts[1]}"
    elif len(parts) > 2:
        # More than 2 parts, put everything except last on first line
        first_line = " ".join(parts[:-1])
        last_line = parts[-1]
        return f"{first_line}\n{last_line}"
    else:
        # Single name
        return name
    
def centered_metric(label, value, delta=None):
    html = f"""
    <div style='
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 3px solid #da1a32;      /* equal border width */
        border-radius: 12px;
        padding: 12px;
        margin: 0 auto;             /* centers inside column */
        width: 150px;               /* fixed width so all are equal */
        text-align: center;
        margin-top: 8px;
    '>
        <div style='font-size: 16px; font-weight: bold;'>{label}</div>
        <div style='font-size: 26px; font-weight: bold; color: black;'>{value}</div>
        {f"<div style='font-size:14px; color: gray;'>{delta}</div>" if delta else ""}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def set_active_tab(tab_name):
    st.session_state.active_tab = tab_name
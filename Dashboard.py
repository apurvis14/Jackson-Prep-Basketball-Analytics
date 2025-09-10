import pandas as pd
import numpy as np
import math
import streamlit as st
import plotly.graph_objects as go

# -----------------------------
# Court + zone constants
# -----------------------------
ARC_CX, ARC_CY = 0.0, -22.5
ARC_R = 237.0
R_OUT = ARC_R + 140.0

# -----------------------------
# Geometry helpers
# -----------------------------
def polar_to_xy(angle_deg, radius, cx=ARC_CX, cy=ARC_CY):
    a = math.radians(angle_deg)
    return (cx + radius * math.cos(a), cy + radius * math.sin(a))

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

# -----------------------------
# Zones (13 zones)
# -----------------------------
def get_updated_zones():
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
    return zones

# -----------------------------
# Streamlit App
# -----------------------------
st.title("Interactive HS Basketball Zone Shot Chart with Full Court")

# Load CSV directly
data_file = "shot_data.csv"  # replace with your path
df = pd.read_csv(data_file)

# Compute zone stats
zone_stats = df.groupby('ZONE').agg(
    makes=('SHOT_MADE_FLAG', 'sum'),
    attempts=('SHOT_MADE_FLAG', 'count')
).reset_index()
zone_stats['FG%'] = (zone_stats['makes'] / zone_stats['attempts']) * 100
overall_fg = df['SHOT_MADE_FLAG'].mean() * 100

# -----------------------------
# Create Plotly figure
# -----------------------------
fig = go.Figure()

# -----------------------------
# Court layout (converted from draw_hs_half_court)
# -----------------------------
# Baseline & sidelines
fig.add_shape(type="line", x0=-250, y0=-47.5, x1=250, y1=-47.5, line=dict(color="black"))
fig.add_shape(type="line", x0=-250, y0=-47.5, x1=-250, y1=350, line=dict(color="black"))
fig.add_shape(type="line", x0=250, y0=-47.5, x1=250, y1=350, line=dict(color="black"))
# Hoop
fig.add_shape(type="circle", x0=-7.5, y0=-22.5, x1=7.5, y1=-7.5, line=dict(color="black"))
# Backboard
fig.add_shape(type="line", x0=-30, y0=-22.5, x1=30, y1=-22.5, line=dict(color="black"))
# Paint
fig.add_shape(type="rect", x0=-72, y0=-47.5, x1=72, y1=142.5, line=dict(color="black"))
# Free throw arcs
theta = np.linspace(0, 180, 100)
ft_arc_x = 72*np.cos(np.radians(theta))
ft_arc_y = 142.5 - 72 + 72*np.sin(np.radians(theta))
fig.add_trace(go.Scatter(x=ft_arc_x, y=ft_arc_y, mode="lines", line=dict(color="black"), showlegend=False))
# Restricted area
theta = np.linspace(0, 180, 50)
ra_x = 40*np.cos(np.radians(theta))
ra_y = -15 + 40*np.sin(np.radians(theta))
fig.add_trace(go.Scatter(x=ra_x, y=ra_y, mode="lines", line=dict(color="black"), showlegend=False))
# Three-point arc
theta = np.linspace(22, 158, 100)
tp_x = ARC_CX + ARC_R*np.cos(np.radians(theta))
tp_y = ARC_CY + ARC_R*np.sin(np.radians(theta))
fig.add_trace(go.Scatter(x=tp_x, y=tp_y, mode="lines", line=dict(color="black"), showlegend=False))

# -----------------------------
# Add zones
# -----------------------------
zones = get_updated_zones()
for zone_name, coords in zones.items():
    xs, ys = zip(*coords)
    if zone_name in zone_stats['ZONE'].values:
        stats = zone_stats[zone_stats['ZONE'] == zone_name].iloc[0]
        color = "rgba(0,200,0,0.3)" if stats['FG%'] >= overall_fg else "rgba(200,0,0,0.3)"
        hovertext = f"{zone_name}<br>{int(stats['makes'])}/{int(stats['attempts'])} ({stats['FG%']:.1f}%)"
    else:
        color = "rgba(150,150,150,0.2)"
        hovertext = f"{zone_name}<br>No shots"
    fig.add_trace(go.Scatter(
        x=xs, y=ys, fill="toself",
        fillcolor=color, line=dict(color="black", dash="dash"),
        name=zone_name,
        hovertext=hovertext,
        hoverinfo="text"
    ))

# -----------------------------
# Layout settings
# -----------------------------
fig.update_layout(
    title="HS Basketball Zone Shot Chart",
    xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-250, 250]),
    yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-47.5, 422.5]),
    height=800, width=700
)

st.plotly_chart(fig, use_container_width=True)

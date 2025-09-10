# basketball_zones_html.py
import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# Court / geometry parameters
# -----------------------------
ARC_CX, ARC_CY = 0.0, -22.5
ARC_R = 237.0

def polar_to_xy(angle_deg, radius, cx=ARC_CX, cy=ARC_CY):
    a = math.radians(angle_deg)
    return (cx + radius*math.cos(a), cy + radius*math.sin(a))

def arc_points(angle_start, angle_end, radius=ARC_R, n=100):
    angles = np.linspace(angle_start, angle_end, n)
    return [polar_to_xy(a, radius) for a in angles]

def arc_y_at_x(x):
    dx = x - ARC_CX
    if abs(dx) > ARC_R:
        dx = max(min(dx, ARC_R), -ARC_R)
    return ARC_CY + math.sqrt(ARC_R**2 - dx**2)

def midrange_center_arc_top_polygon(x_min, x_max, y_bottom, n_points=30):
    angles = np.linspace(0, 180, n_points*2)
    arc_pts = [polar_to_xy(a, ARC_R) for a in angles]
    top_pts = [(x, y) for x, y in arc_pts if x_min < x < x_max]
    top_pts.append((x_min, arc_y_at_x(x_min)))
    top_pts.append((x_max, arc_y_at_x(x_max)))
    top_pts = sorted(top_pts, key=lambda p: p[0], reverse=True)
    polygon = [(x_min, y_bottom), (x_max, y_bottom)] + top_pts
    return polygon

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

# -----------------------------
# Build zones
# -----------------------------
zones = {}

# Corners
y_leftcorner = arc_y_at_x(-220)
y_rightcorner = arc_y_at_x(220)
zones[1] = ("Left Corner 3", [(-250, -47.5), (-220, -47.5), (-220, y_leftcorner), (-250, y_leftcorner)])
zones[2] = ("Right Corner 3", [(220, -47.5), (250, -47.5), (250, y_rightcorner), (220, y_rightcorner)])

# Wing & top 3PT (simplified as polygon for visualization)
zones[3] = ("Left Wing 3", [(-220, y_leftcorner), (-72, 142.5), (-72, y_leftcorner)])
zones[4] = ("Right Wing 3", [(72, y_rightcorner), (220, 142.5), (72, y_rightcorner)])
zones[5] = ("Top of Key 3", [(-72, 142.5), (72, 142.5), (0, 237)])

# Midrange baseline rectangles
x_mid_left_start, x_mid_left_end = -220, -72
x_mid_right_start, x_mid_right_end = 72, 220
baseline_y = -47.5
zones[6] = ("Left Midrange BL", [(x_mid_left_start, baseline_y), (x_mid_left_end, baseline_y),
                                (x_mid_left_end, y_leftcorner), (x_mid_left_start, y_leftcorner)])
zones[7] = ("Right Midrange BL", [(x_mid_right_start, baseline_y), (x_mid_right_end, baseline_y),
                                 (x_mid_right_end, y_rightcorner), (x_mid_right_start, y_rightcorner)])

# Layups
zones[8] = ("Left Layup", [(-72, -47.5), (0, -47.5), (0, 60), (-72, 60)])
zones[9] = ("Right Layup", [(0, -47.5), (72, -47.5), (72, 60), (0, 60)])

# Top of 6-7 for wing midrange
top_of_6_7 = max(max(y for x,y in zones[6][1]), max(y for x,y in zones[7][1]))
x_left_center, x_right_center = -72, 72

# Wing midrange zones
zones[10] = ("LW Midrange", midrange_arc_top_polygon_fixed(x_min=-220, x_max=x_left_center, y_bottom=top_of_6_7))
zones[11] = ("RW Midrange", midrange_arc_top_polygon_fixed(x_min=x_right_center, x_max=220, y_bottom=top_of_6_7))

# Center midrange zones
y_bottom_midrange = -47.5
zones[12] = ("Left Center Midrange", midrange_center_arc_top_polygon(x_min=x_left_center, x_max=0, y_bottom=y_bottom_midrange))
zones[13] = ("Right Center Midrange", midrange_center_arc_top_polygon(x_min=0, x_max=x_right_center, y_bottom=y_bottom_midrange))

# -----------------------------
# Build Plotly Figure
# -----------------------------
fig = go.Figure()

colors = ['#FF6666','#66FF66','#6666FF','#FFCC66','#66CCFF','#CC66FF','#FF66CC','#66FFCC','#CCCC66','#CC9966','#9966CC','#66CC99','#99CC66']

for zid, (zname, coords) in zones.items():
    xs, ys = zip(*coords)
    fig.add_trace(go.Scatter(
        x=xs, y=ys, fill="toself", name=f"{zid}: {zname}",
        hoverinfo="text", text=[f"Zone {zid}: {zname}"]*len(xs),
        line=dict(color='black'), fillcolor=colors[(zid-1)%len(colors)], opacity=0.5
    ))

fig.update_layout(
    title="High School Basketball Shot Zones",
    xaxis=dict(range=[-250, 250], showgrid=False, zeroline=False),
    yaxis=dict(range=[-47.5, 422.5], showgrid=False, zeroline=False),
    width=900, height=1000,
    showlegend=True
)

fig.write_html("basketball_zones.html", include_plotlyjs="cdn")
print("Saved basketball_zones.html! You can send this file to your coach.")

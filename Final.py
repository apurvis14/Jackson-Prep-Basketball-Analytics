# updated_zones_for_tableau.py
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc, Polygon

# -----------------------------
# Court-drawing function
# -----------------------------
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
    sideline_a = Rectangle((-250, -47.5), 0, 397.5, linewidth=lw, color=color)
    sideline_b = Rectangle((250, -47.5), 0, 397.5, linewidth=lw, color=color)
    half_court = Rectangle((-350, 350), 700, 0, linewidth=lw, color=color)
    center_circle = Arc((0, 350), 120, 120, theta1=180, theta2=360, linewidth=lw, color=color)
    court_elements = [hoop, backboard, paint, top_free_throw, restricted, three_arc, baseline,
                      corner_three_a, corner_three_b, sideline_a, sideline_b, half_court, center_circle]
    for el in court_elements:
        ax.add_patch(el)
    return ax

# -----------------------------
# Arc / geometry parameters
# -----------------------------
ARC_CX, ARC_CY = 0.0, -22.5
ARC_R = 237.0
ARC_RES = 120
R_OUT = ARC_R + 140.0
R_IN = 100.0

# -----------------------------
# Helper functions
# -----------------------------
def polar_to_xy(angle_deg, radius, cx=ARC_CX, cy=ARC_CY):
    a = math.radians(angle_deg)
    return (cx + radius*math.cos(a), cy + radius*math.sin(a))

def arc_points(angle_start, angle_end, radius=ARC_R, n=ARC_RES):
    angles = np.linspace(angle_start, angle_end, n)
    return [polar_to_xy(a, radius) for a in angles]

def arc_y_at_x(x):
    dx = x - ARC_CX
    if abs(dx) > ARC_R:
        dx = max(min(dx, ARC_R), -ARC_R)
    return ARC_CY + math.sqrt(ARC_R**2 - dx**2)

def threept_sector(start_ang, end_ang, arc_res=ARC_RES):
    inner = arc_points(start_ang, end_ang, radius=ARC_R, n=arc_res)
    outer = arc_points(end_ang, start_ang, radius=R_OUT, n=arc_res)
    return inner + outer

def midrange_center_arc_top_polygon(x_min, x_max, y_bottom, n_points=30):
    angles = np.linspace(0, 180, n_points*2)
    arc_pts = [polar_to_xy(a, ARC_R, ARC_CX, ARC_CY) for a in angles]
    top_pts = [(x, y) for x, y in arc_pts if x_min < x < x_max]
    top_pts.append((x_min, arc_y_at_x(x_min)))
    top_pts.append((x_max, arc_y_at_x(x_max)))
    top_pts = sorted(top_pts, key=lambda p: p[0], reverse=True)
    polygon = [(x_min, y_bottom), (x_max, y_bottom)] + top_pts
    return polygon

def midrange_arc_top_polygon_fixed(x_min, x_max, y_bottom, n_points=50):
    angles = np.linspace(0, 180, n_points*2)
    arc_pts = [polar_to_xy(a, ARC_R, ARC_CX, ARC_CY) for a in angles]
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

# 3PT outside-arc
A_right_corner = math.degrees(math.atan2(y_rightcorner - ARC_CY, 220 - ARC_CX))
A_left_corner = math.degrees(math.atan2(y_leftcorner - ARC_CY, -220 - ARC_CX))
A2, A4 = 60.0, 120.0
zones[3] = ("Left Wing 3", threept_sector(A4, A_left_corner))
zones[4] = ("Right Wing 3", threept_sector(A_right_corner, A2))
zones[5] = ("Top of Key 3", threept_sector(A2, A4))

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
# Export CSV for Tableau
# -----------------------------
rows = []
for zid, (zname, coords) in zones.items():
    for i, (x, y) in enumerate(coords):
        if y is None:
            continue
        rows.append({"ZoneID": zid, "ZoneName": zname, "X": float(x), "Y": float(y), "Order": i})

df = pd.DataFrame(rows)
df.to_csv("zones_updated.csv", index=False)
print("Saved zones_updated.csv (polygon vertices).")

# -----------------------------
# Preview with zones
# -----------------------------
fig2, ax2 = plt.subplots(figsize=(12,11))
draw_hs_half_court(ax2)
colors = plt.cm.tab20.colors
for zid, (zname, coords) in zones.items():
    poly = Polygon(coords, closed=True, facecolor=colors[zid % len(colors)], alpha=0.35, edgecolor='black')
    ax2.add_patch(poly)
    xs, ys = zip(*coords)
    ax2.text(sum(xs)/len(xs), sum(ys)/len(ys), str(zid), ha='center', va='center', fontsize=10, weight='bold')
ax2.set_xlim(-250,250)
ax2.set_ylim(-47.5,422.5)
ax2.axis('off')
plt.savefig("court_with_zones_updated.png", dpi=300, bbox_inches='tight')
print("Saved court_with_zones_updated.png (preview).")

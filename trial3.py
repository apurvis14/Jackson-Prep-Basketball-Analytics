# updated_zones_for_tableau.py
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc, Polygon

# -----------------------------
# Your court-drawing function (unchanged)
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
# Arc / geometry parameters (edit these if your court uses different numbers)
# -----------------------------
ARC_CX, ARC_CY = 0.0, -22.5   # center used by your three_arc
ARC_R = 237.0                 # radius (half of 474)
ARC_RES = 120                 # smoothness (increase for smoother arc)
R_OUT = ARC_R + 140.0         # how far 3pt zones extend outward (visual)
R_IN = 100.0                  # inner radius for midrange ring sectors (adjustable)

# helper conversions
def polar_to_xy(angle_deg, radius, cx=ARC_CX, cy=ARC_CY):
    a = math.radians(angle_deg)
    return (cx + radius*math.cos(a), cy + radius*math.sin(a))

def arc_points(angle_start, angle_end, radius=ARC_R, n=ARC_RES):
    angles = np.linspace(angle_start, angle_end, n)
    return [polar_to_xy(a, radius) for a in angles]

def arc_y_at_x(x):
    dx = x - ARC_CX
    if abs(dx) > ARC_R:
        return None
    return ARC_CY + math.sqrt(ARC_R**2 - dx**2)

# exact corner intersection angles (x = +/-220)
y_leftcorner = arc_y_at_x(-220)
y_rightcorner = arc_y_at_x(220)
angle_left_corner = math.degrees(math.atan2(y_leftcorner - ARC_CY, -220 - ARC_CX))
angle_right_corner = math.degrees(math.atan2(y_rightcorner - ARC_CY, 220 - ARC_CX))

# choose split angles for sectors (I've chosen symmetric splits: 60 & 90 degrees)
A_right_corner = angle_right_corner     # ~21.833°
A2 = 60.0
A3 = 90.0
A4 = 120.0
A_left_corner = angle_left_corner       # ~158.167°

# -----------------------------
# Build zones
# -----------------------------
zones = {}

# 1-2 corners (rectangles up to exact arc y)
zones[1] = ("Left Corner 3", [(-250, -47.5), (-220, -47.5), (-220, y_leftcorner), (-250, y_leftcorner)])
zones[2] = ("Right Corner 3", [(220, -47.5), (250, -47.5), (250, y_rightcorner), (220, y_rightcorner)])

# helper: 3pt sector (outer: R_OUT, inner: ARC_R)
def threept_sector(start_ang, end_ang, arc_res=ARC_RES):
    inner = arc_points(start_ang, end_ang, radius=ARC_R, n=arc_res)
    outer = arc_points(end_ang, start_ang, radius=R_OUT, n=arc_res)  # reversed to form closed poly
    return inner + outer

# 3pt outside-arc zones
zones[3] = ("Left Wing 3", threept_sector(A4, A_left_corner))
zones[4] = ("Right Wing 3", threept_sector(A_right_corner, A2))
zones[5] = ("Top of Key 3", threept_sector(A2, A4))

# 6-7 left/right midrange baseline rectangles (bottom at corner top, top at arc y at x=±150)
# Get y-top of zones 1 & 2 (already computed)
y_top_6 = y_leftcorner   # top of zone 1
y_top_7 = y_rightcorner  # top of zone 2
baseline_y = -47.5       # bottom = baseline

# Define the width so it extends from corners to layup zones
x_mid_left_start = -220   # right edge of zone 1
x_mid_left_end = -72      # left edge of zone 8
x_mid_right_start = 72    # right edge of zone 9
x_mid_right_end = 220     # left edge of zone 2

# Zone 6 – Left Midrange
zones[6] = ("Left Midrange BL", [
    (x_mid_left_start, baseline_y),  # bottom-left
    (x_mid_left_end, baseline_y),    # bottom-right
    (x_mid_left_end, y_top_6),       # top-right
    (x_mid_left_start, y_top_6)      # top-left
])

# Zone 7 – Right Midrange
zones[7] = ("Right Midrange BL", [
    (x_mid_right_start, baseline_y), # bottom-left
    (x_mid_right_end, baseline_y),   # bottom-right
    (x_mid_right_end, y_top_7),      # top-right
    (x_mid_right_start, y_top_7)     # top-left
])


# 8-9 layups (unchanged small boxes inside paint)
zones[8] = ("Left Layup", [(-72, -47.5), (0, -47.5), (0, 60), (-72, 60)])
zones[9] = ("Right Layup", [(0, -47.5), (72, -47.5), (72, 60), (0, 60)])

# -----------------------------
# Midrange Polygon Helpers
# -----------------------------
def arc_y_at_x(x):
    dx = x - ARC_CX
    if abs(dx) > ARC_R:
        dx = max(min(dx, ARC_R), -ARC_R)  # clip to circle
    return ARC_CY + math.sqrt(ARC_R**2 - dx**2)

def midrange_arc_top_polygon(x_min, x_max, y_bottom, n_points=50):
    """
    Polygon for midrange zones (10-11) with:
    - top following 3-point arc
    - vertical sides at x_min/x_max
    - flat bottom at y_bottom
    """
    angles = np.linspace(0, 180, n_points*2)
    arc_pts = [polar_to_xy(a, ARC_R, ARC_CX, ARC_CY) for a in angles]
    top_pts = [(x, y) for x, y in arc_pts if x_min < x < x_max]

    # include edges to prevent gaps
    top_pts.append((x_min, arc_y_at_x(x_min)))
    top_pts.append((x_max, arc_y_at_x(x_max)))

    # sort from right to left
    top_pts = sorted(top_pts, key=lambda p: p[0], reverse=True)

    polygon = [(x_min, y_bottom), (x_max, y_bottom)] + top_pts
    return polygon

def midrange_center_arc_top_polygon(x_min, x_max, y_bottom, n_points=30):
    """
    Polygon for center midrange zones (12-13):
    - top follows 3-point arc
    - vertical sides
    - flat bottom
    - ensures top edges meet at x=0 without gaps
    """
    angles = np.linspace(0, 180, n_points*2)
    arc_pts = [polar_to_xy(a, ARC_R, ARC_CX, ARC_CY) for a in angles]
    top_pts = [(x, y) for x, y in arc_pts if x_min < x < x_max]

    # include exact edges
    top_pts.append((x_min, arc_y_at_x(x_min)))
    top_pts.append((x_max, arc_y_at_x(x_max)))

    top_pts = sorted(top_pts, key=lambda p: p[0], reverse=True)
    polygon = [(x_min, y_bottom), (x_max, y_bottom)] + top_pts
    return polygon

# -----------------------------
# Midrange zones 6-13
# -----------------------------
y_bottom_midrange = -47.5  # flat bottom aligned with layup baseline
x_left_center = -72
x_right_center = 72

# # Zones 6 & 7 – baseline midrange rectangles
# zones[6] = ("Left Midrange BL", [(-250, y_bottom_midrange), (x_left_center, y_bottom_midrange), 
#                                  (x_left_center, 60), (-250, 60)])
# zones[7] = ("Right Midrange BL", [(x_right_center, y_bottom_midrange), (250, y_bottom_midrange), 
#                                   (250, 60), (x_right_center, 60)])

# # Zones 8 & 9 – layups (unchanged)
# zones[8] = ("Left Layup", [(-72, -47.5), (0, -47.5), (0, 60), (-72, 60)])
# zones[9] = ("Right Layup", [(0, -47.5), (72, -47.5), (72, 60), (0, 60)])

top_of_6 = max(y for x,y in zones[6][1])
top_of_7 = max(y for x,y in zones[7][1]) # top of baseline midrange (zones 6 & 7)

top_of_6_7 = max(top_of_6, top_of_7)


x_left_center = -72        # separation for center zones
x_right_center = 72

def midrange_arc_top_polygon_fixed(x_min, x_max, y_bottom, n_points=50):
    """
    Polygon for midrange wing zones (10-11):
    - bottom aligned with zones 6-7 (y_bottom)
    - top follows 3-point arc
    - x_min/x_max vertical sides
    """
    # Sample points along the arc
    angles = np.linspace(0, 180, n_points*2)
    arc_pts = [polar_to_xy(a, ARC_R, ARC_CX, ARC_CY) for a in angles]

    # Only take points that are above y_bottom and within x_min/x_max
    top_pts = [(x, y) for x, y in arc_pts if x_min <= x <= x_max and y >= y_bottom]

    # Add vertical edges to prevent gaps
    top_pts.append((x_min, arc_y_at_x(x_min)))
    top_pts.append((x_max, arc_y_at_x(x_max)))

    # Bottom corners (clipped to arc if needed)
    bottom_left_y = min(y_bottom, arc_y_at_x(x_min))
    bottom_right_y = min(y_bottom, arc_y_at_x(x_max))

    # Sort left-to-right
    top_pts = sorted(top_pts, key=lambda p: p[0])

    # Polygon: bottom-left -> bottom-right -> arc top pts
    polygon = [(x_min, bottom_left_y), (x_max, bottom_right_y)] + sorted(top_pts, key=lambda p: p[0], reverse=True)
    return polygon

def zone10_top_arc_polygon(x_min, x_max, y_bottom, n_pts=30):
    """
    Build polygon for left wing midrange (Zone 10)
    - bottom aligned with top of Zone 6
    - top exactly follows 3PT arc
    """
    # Sample points along 3PT arc
    angles = np.linspace(0, 180, n_pts*2)
    arc_pts = [polar_to_xy(a, ARC_R, ARC_CX, ARC_CY) for a in angles]
    
    # Only keep points within x_min and x_max
    top_pts = [(x, y) for x, y in arc_pts if x_min <= x <= x_max]

    # Sort from right to left to close polygon correctly
    top_pts = sorted(top_pts, key=lambda p: p[0], reverse=True)

    # Polygon: bottom-left -> bottom-right -> arc top points
    polygon = [(x_min, y_bottom), (x_max, y_bottom)] + top_pts
    return polygon

# Apply to Zone 10
zones[10] = ("LW Midrange", midrange_arc_top_polygon_fixed(x_min=-220, x_max=x_left_center, y_bottom=top_of_6_7))
zones[11] = ("RW Midrange", midrange_arc_top_polygon_fixed(x_min=x_right_center, x_max=220, y_bottom=top_of_6_7))

zones[12] = ("Left Center Midrange", midrange_center_arc_top_polygon(x_min=x_left_center, x_max=0, y_bottom=y_bottom_midrange))
zones[13] = ("Right Center Midrange", midrange_center_arc_top_polygon(x_min=0, x_max=x_right_center, y_bottom=y_bottom_midrange))

# -----------------------------
# Export CSV for Tableau
# -----------------------------
rows = []
for zid, (zname, coords) in zones.items():
    for i, (x, y) in enumerate(coords):
        if y is None:  # skip invalid points
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
ax2.set_xlim(-250,250); ax2.set_ylim(-47.5,422.5); ax2.axis('off')
plt.savefig("court_with_zones_updated.png", dpi=300, bbox_inches='tight')
print("Saved court_with_zones_updated.png (preview).")
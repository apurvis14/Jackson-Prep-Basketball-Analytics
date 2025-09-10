import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc, Polygon
import numpy as np

# -----------------------------
# Draw High School Half Court
# -----------------------------
def draw_hs_half_court(ax=None, color='black', lw=2): 
    if ax is None: 
        ax = plt.gca() 
    # Hoop 
    hoop = Circle((0, -15), radius=7.5, linewidth=lw, color=color, fill=False) 

    # Backboard 
    backboard = Rectangle((-30, -22.5), 60, 0, linewidth=lw, color=color) 
    
    # Paint 
    paint = Rectangle((-72, -47.5), 144, 190, linewidth=lw, color=color, fill=False)
    
    # Free throw arcs 
    top_free_throw = Arc((0, 142.5), 144, 144, theta1=0, theta2=180, linewidth=lw, color=color)
    # Free Throw Side Dash 
    free_throw_dash_a = Rectangle((-72, 115), -10, 0, linewidth=lw, color=color) 
    free_throw_dash_b = Rectangle((72, 115), 10, 0, linewidth=lw, color=color) 
    free_throw_dash_c = Rectangle((-72, 60), -10, 0, linewidth=lw, color=color) 
    free_throw_dash_d = Rectangle((72, 60), 10, 0, linewidth=lw, color=color) 

    # Free Throw Blocks near bottom of Paint 
    free_throw_block = Rectangle((-72, -5), -10, 20, linewidth=lw, color=color, fill=color) 
    free_throw_block_2 = Rectangle((72, -5), 10, 20, linewidth=lw, color=color, fill=color) 
    # Restricted area
    restricted = Arc((0, -15), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color) 
    # Baseline 
    baseline = Rectangle((-250, -47.5), 500, 0, linewidth=lw, color=color)
    # Three point line (HS 19'9" radius) 
    corner_three_a = Rectangle((-220, -47.5), 0, 114, linewidth=lw, color=color) 
    corner_three_b = Rectangle((220, -47.5), 0, 114, linewidth=lw, color=color) 
    three_arc = Arc((0, -22.5), 474, 474, theta1=22, theta2=158, linewidth=lw, color=color) 
    # Sidelines 
    sideline_a = Rectangle((-250, -47.5), 0, 397.5, linewidth=lw, color=color) 
    sideline_b = Rectangle((250, -47.5), 0, 397.5, linewidth=lw, color=color) 
    # Half Court Line and center circle (half) 
    half_court = Rectangle((-350, 350), 700, 0, linewidth=lw, color=color) 
    center_circle = Arc((0, 350), 120, 120, theta1=180, theta2=360, linewidth=lw, color=color) 
    court_elements = [hoop, backboard, paint, top_free_throw, restricted, 
                      three_arc, baseline, corner_three_a, corner_three_b, 
                      free_throw_dash_a, free_throw_dash_b, free_throw_dash_c, free_throw_dash_d, 
                      free_throw_block, free_throw_block_2, sideline_a, sideline_b, 
                      half_court, center_circle] 
    
    for element in court_elements: 
        ax.add_patch(element) 
    return ax

fig, ax = plt.subplots(figsize=(12, 11))
draw_hs_half_court(ax)
ax.set_xlim(-250, 250)
ax.set_ylim(-47.5, 422.5)
ax.axis('off')
plt.savefig("high_school_basketball_half_court.png")
plt.show()



# -----------------------------
# Define Zones as Polygons
# -----------------------------
def get_zone_polygons():
    def quarter_circle_polygon(center_x, center_y, width, height, theta1, theta2,steps=30):
        angles = np.linspace(np.radians(theta1), np.radians(theta2), steps)

        x = center_x + (width / 2) * np.cos(angles)
        y = center_y + (height / 2) * np.sin(angles)
        coords = [(center_x, center_y)] + list(zip(x, y))
        return Polygon(coords, closed=True)

    zones = {
        # Layups
        'Layup Right': Polygon([(-72, -47.5), (-72, 65), (0, 65), (0, -47.5)], closed=True),
        'Layup Left': Polygon([(0, -47.5), (0, 65), (72, 65), (72, -47.5)], closed=True),

        # Corner 3s
        'Corner 3 Right': Polygon([(220, -47.5), (220, 65), (250, 65), (250, -47.5)], closed=True),
        'Corner 3 Left': Polygon([(-250, -47.5), (-250, 65), (-220, 65), (-220, -47.5)], closed=True),

        # Baseline Mid-Range
        'Baseline Mid Right': Polygon([(72, -47.5), (72, 65), (220, 65), (220, -47.5)], closed=True),
        'Baseline Mid Left': Polygon([(-220, -47.5), (-220, 65), (-72, 65), (-72, -47.5)], closed=True),

        # Mid-Range Wing (Quarter Circle)
        'Mid Right Wing': quarter_circle_polygon(-72, 65, 300, 280, 90, 180),
        'Mid Left Wing': quarter_circle_polygon(72, 65, 280, 300, 0, 90)
    }
    return zones

# -----------------------------
# Plot Zone Chart from Zone Names
# -----------------------------
def plot_zone_chart(df):
    zone_stats = df.groupby('ZONE').agg(
        makes=('SHOT_MADE_FLAG', 'sum'),
        attempts=('SHOT_MADE_FLAG', 'count')
    ).reset_index()
    zone_stats['FG%'] = (zone_stats['makes'] / zone_stats['attempts']) * 100
    overall_fg = df['SHOT_MADE_FLAG'].mean() * 100

    zone_polys = get_zone_polygons()

    fig, ax = plt.subplots(figsize=(12, 11))
    draw_hs_half_court(ax)
    ax.set_xlim(-250, 250)
    ax.set_ylim(-47.5, 422.5)
    ax.axis('off')

    for zone, poly in zone_polys.items():
        if zone not in zone_stats['ZONE'].values:
            continue
        stats = zone_stats[zone_stats['ZONE'] == zone].iloc[0]
        color = 'green' if stats['FG%'] >= overall_fg else 'red'
        ax.add_patch(Polygon(poly.get_xy(), closed=True, facecolor=color, alpha=0.3, edgecolor='black'))
        cx = np.mean(poly.get_xy()[:, 0])
        cy = np.mean(poly.get_xy()[:, 1])
        ax.text(cx, cy+10, f"{int(stats['makes'])}/{int(stats['attempts'])}", ha='center', fontsize=10, weight='bold')
        ax.text(cx, cy-10, f"{stats['FG%']:.1f}%", ha='center', fontsize=10)

    plt.title("High School Basketball Zone Shot Chart", fontsize=18)
    plt.savefig("high_school_basketball_zone_shot_chart.png")
    plt.show()

# -----------------------------
data = pd.read_csv("shot_data.csv")
plot_zone_chart(data)
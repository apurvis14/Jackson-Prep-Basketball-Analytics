from Functions import plot_zone_chart
import pandas as pd

data = pd.read_csv("shot_data.csv")
plot_zone_chart(data)
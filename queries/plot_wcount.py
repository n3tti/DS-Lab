import matplotlib.pyplot as plt
import numpy as np
import json
import matplotlib.ticker as ticker


count_html = dict(sorted(count_html.items()))
# Extract keys and values
wcount = list(count_html.keys())
counts1 = list(count_html.values())
#counts2 = list(lang_pdf.values())

# Set the width of the bars and positions
bar_width = 0.35
#x = np.arange(len(wcount))
x = wcount
y= counts1
plt.figure(figsize=(10, 6))
plt.scatter(x, y, color='#3358ff', label='Data Points')  # Scatter plot for (x, y)

# Add labels and title
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Scatter Plot of (x, y) Points")
plt.legend()
ax = plt.gca()  # Get current axis
ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))  # Adjust number of x-axis labels

# Show grid and save the plot
plt.grid(axis='both', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("./xy_points_scatter.png")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

# Define parameters
a, b = 0, 10  # Range for the x-axis
N = 50  # Number of points between each integer

# Generate data
x = np.linspace(a, b, N * (b - a))  # Evenly sample N points between each integer
y1 = 10**(-x / 10)  # Sample line
y2 = 10**(-x / 8)   # Another sample line

# Extract integer x-values and corresponding y-values for markers
integer_x = np.arange(a, b + 1)  # Integer values from a to b
marker_y1 = 10**(-integer_x / 10)  # y-values of y1 at integer x
marker_y2 = 10**(-integer_x / 8)   # y-values of y2 at integer x

# Create the plot
fig, ax = plt.subplots()

# Plot multiple lines with markers at integer x-values
ax.plot(x, y1, label='Line 1')
ax.plot(x, y2, label='Line 2')
ax.scatter(integer_x, marker_y1, color='blue', marker='o', label='Markers Line 1')
ax.scatter(integer_x, marker_y2, color='orange', marker='s', label='Markers Line 2')

# Set the y-axis to logarithmic scale
ax.set_yscale('log')
ax.set_ylim(1e-4, 1e0)  # From 10^-4 to 10^0

# Adjust x-axis ticks to show at every integer
ax.xaxis.set_major_locator(MultipleLocator(1))  # Major ticks at every integer

# Add grid for better readability
ax.grid(which="both", linestyle='--', linewidth=0.5)

# Add labels and title
ax.set_xlabel('X-axis (event sampled, integer markers)')
ax.set_ylabel('Y-axis (log scale)')
ax.set_title('Logarithmic Y-axis with Markers on Integer X-values')

# Add legend
ax.legend()

# Show the plot
plt.show()

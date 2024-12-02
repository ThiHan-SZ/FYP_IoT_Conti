import matplotlib.pyplot as plt
import numpy as np

# Example data
x = np.linspace(0, 1, 500)
y = x**3

# Create the plot
fig, ax = plt.subplots()
ax.plot(x, y)

# Set y-axis to symlog scale
ax.set_yscale('symlog', linthresh=1e-5)

# Custom ticks to include 0 and log-scale values
ticks = [0, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1]
ax.set_yticks(ticks)

# Add grid for clarity
ax.grid(True, which="both", linestyle="--", linewidth=0.5)

plt.show()

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig, ax = plt.subplots()
t = np.linspace(0, 2, 50, endpoint=False)
g = -9.81
v01 = 12
bbSymbols = g * t**2 / 2 + v01 * t
v02 = 5
pbSymbols = g * t**2 / 2 + v02 * t

scatter = ax.scatter(t[0], bbSymbols[0], label='BB Symbols', c='b')
scatter_pb = ax.scatter(t[0], pbSymbols[0], label='PB Symbols', c='r')
ax.legend()
ax.set(xlim=[0, 3], ylim=[-4, 10], xlabel='Time [s]', ylabel='Z [m]')


# Function to update the scatter plot
def update(frame):
    x = t[:frame]
    bb_symbols = bbSymbols[:frame]
    pb_symbols = pbSymbols[:frame]
    bb_symbols = np.stack((x, bb_symbols))
    pb_symbols = np.stack((x, pb_symbols))
    
    scatter.set_offsets(bb_symbols.T)
    scatter_pb.set_offsets(pb_symbols.T)
    
    return scatter, scatter_pb

# Create the animation (blit=False for scatter plot)
ani = animation.FuncAnimation(fig, update, frames=len(bbSymbols), interval=20, blit=False)
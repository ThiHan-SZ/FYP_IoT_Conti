from matplotlib.figure import Figure
import numpy as np

class SimpleModulator:
    def __init__(self, carrier_freq):
        self.carrier_freq = carrier_freq  # Carrier frequency for the sine wave

    def generate_sine_wave(self):
        """Generate a sine wave plot."""
        # Create time and sine wave data
        t = np.linspace(0, 1, 500)  # Time axis
        y = np.sin(2 * np.pi * self.carrier_freq * t)  # Sine wave

        # Create a matplotlib Figure object
        fig = Figure()
        ax = fig.add_subplot(111)
        ax.plot(t, y, label=f"Sine Wave ({self.carrier_freq} Hz)")
        ax.set_title("Sine Wave")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.legend()

        return fig  # Return the figure object

import numpy as np
import matplotlib.pyplot as plt

def simulate_frequency_drift(f0, drift, fs, duration):
    """
    Simulates frequency drift where the instantaneous frequency changes over time.
    
    f0: Initial frequency in Hz
    drift: Frequency drift rate (Hz per second)
    fs: Sampling frequency in Hz
    duration: Signal duration in seconds
    """
    t = np.arange(0, duration, 1/fs)  # Time vector
    phase = 2 * np.pi * (f0 * t + 0.5 * drift * t**2)  # Integral of frequency over time
    signal = np.exp(1j * phase)  # Generate complex exponential
    return t, signal

def stable_frequency_shift(f0, fs, duration):
    """
    Applies a constant frequency shift without drift using incremental phase updates.
    
    f0: Frequency shift in Hz
    fs: Sampling frequency in Hz
    duration: Signal duration in seconds
    """
    t = np.arange(0, duration, 1/fs)  # Time vector
    N = len(t)
    Ts = 1 / fs  # Sampling period
    phase_inc = 2 * np.pi * f0 * Ts  # Constant phase increment
    phase = 0  # Initialize phase
    
    signal = np.zeros(N, dtype=complex)
    
    for n in range(N):
        signal[n] = np.exp(1j * phase)
        phase += phase_inc  # Increment phase
        if phase > np.pi:  # Keep phase bounded
            phase -= 2 * np.pi
    
    return t, signal

# Simulation Parameters
fs = 1000  # Sampling rate in Hz
duration = 1  # Signal duration in seconds
f0 = 50  # Initial frequency in Hz
drift = 15  # Frequency drift (Hz per second)

# Generate signals
t1, drift_signal = simulate_frequency_drift(f0, drift, fs, duration)
t2, stable_signal = stable_frequency_shift(f0, fs, duration)


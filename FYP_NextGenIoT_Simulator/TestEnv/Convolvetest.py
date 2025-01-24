import numpy as np
from scipy.signal import fftconvolve
import time
import commpy
import pickle
import gc
# Parameters

TS = 1/4e3
FS = (2e5*2*10)
samples_per_symbol = int(TS * FS)
num_symbols = int(1.6e6)


# Generate random complex I and Q arrays
np.random.seed(1337)  # For reproducibility


I = np.random.choice([-3,-1,1,3], size=num_symbols)
Q = np.random.choice([-3,-1,1,3], size=num_symbols)

# Simulated RRC filter
RRC_delay = 3 * TS
_, rrc = commpy.filters.rrcosfilter(
            N=int(2 * FS * RRC_delay),
            alpha=0.35,
            Ts=TS,
            Fs=FS
        )

signal_length = int(num_symbols * samples_per_symbol + len(rrc) - 1)

# Benchmark Lazy Convolution
#@profile
def LUT_convolution2(I, Q, rrc, samples_per_symbol, signal_length):
    impulses = I + 1j * Q

    # Precompute unique pulse shapes for the LUT
    unique_impulses, unique_indices = np.unique(impulses, return_inverse=True)
    pulseLUT = unique_impulses[:, None] * rrc  # Broadcasting over RRC filter

    # Create a sparse Dirac comb using broadcasting
    dirac_indices = np.arange(len(I)) * samples_per_symbol
    Dirac_Comb = np.zeros(signal_length, dtype=complex)
    Dirac_Comb[dirac_indices] = impulses

    # Construct the shaped pulse using broadcasting
    Shaped_Pulse = np.zeros(signal_length, dtype=complex)

    # Add contributions from each pulse (broadcast the RRC filter)
    for idx, impulse_idx in enumerate(unique_indices):
        start_idx = idx * samples_per_symbol
        Shaped_Pulse[start_idx:start_idx + len(rrc)] += pulseLUT[impulse_idx]
        
    return Shaped_Pulse, Dirac_Comb
        
#@profile
def LUT_convolution(I, Q, rrc, samples_per_symbol, signal_length):
    pulseLUT = {}
    Shaped_Pulse = np.zeros(signal_length, dtype=complex)
    Dirac_Comb = np.zeros(signal_length, dtype=complex)
    
    for idx, (i_val, q_val) in enumerate(zip(I, Q)):
        if (i_val, q_val) not in pulseLUT:
            pulseLUT[(i_val, q_val)] = (i_val + 1j * q_val) * rrc
        start_idx = idx * samples_per_symbol
        Shaped_Pulse[start_idx:start_idx + len(rrc)] += pulseLUT[(i_val, q_val)]
        Dirac_Comb[start_idx] = i_val + 1j * q_val  # Place only at start of each symbol
        
    return Shaped_Pulse

#@profile
def lazy_convolution(I, Q, rrc, samples_per_symbol, signal_length):
    Shaped_Pulse = np.zeros(signal_length, dtype=complex)
    Dirac_Comb = np.zeros(signal_length, dtype=complex)
    
    for idx, (i_val, q_val) in enumerate(zip(I, Q)):
        start_idx = idx * samples_per_symbol
        Shaped_Pulse[start_idx:start_idx + len(rrc)] += (i_val + 1j * q_val) * rrc
        Dirac_Comb[start_idx] = i_val + 1j * q_val  # Place only at start of each symbol
        
    return Shaped_Pulse, Dirac_Comb

# Benchmark FFT-Based Convolution
def fft_convolution(I, Q, rrc, samples_per_symbol, signal_length):
    # Create sparse Dirac Comb
    Dirac_Comb = np.zeros(signal_length, dtype=complex)
    dirac_indices = np.arange(0, len(I) * samples_per_symbol, samples_per_symbol)
    Dirac_Comb[dirac_indices] = I + 1j * Q
    # Perform FFT-based convolution
    Shaped_Pulse = fftconvolve(Dirac_Comb, rrc, mode='full')[:signal_length]
    return Shaped_Pulse

# Run Benchmarks
print("Running benchmarks...")

start_time = time.time()
Shaped_Pulse_LUT, Dirac_Comb1 = lazy_convolution(I, Q, rrc, samples_per_symbol, signal_length)
LUT_time = time.time() - start_time
print(f"LUT Convolution Time: {LUT_time:.6f} seconds")

# FFT Convolution Benchmark
start_time = time.time()
Shaped_Pulse_LUT2, Dirac_Comb2 = LUT_convolution2(I, Q, rrc, samples_per_symbol, signal_length)
LUT_time = time.time() - start_time
print(f"LUT2 Convolution Time: {LUT_time:.6f} seconds")

# Verify Results
difference = np.max(np.abs(Shaped_Pulse_LUT - Shaped_Pulse_LUT2))
print(f"Maximum Difference Between Results: {difference:.6e}")

# Verify Results
difference = np.max(np.abs(Dirac_Comb1 - Dirac_Comb2))
print(f"Maximum Difference Between Results: {difference:.6e}")
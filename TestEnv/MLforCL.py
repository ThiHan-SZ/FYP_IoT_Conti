import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
import scipy.signal as sig

# Load data
mod_type = 'BPSK'
fs, mod_signal = wav.read(rf'WaveFiles\test_file__I_Love_Gaming!__200kHz_16kbps_{mod_type}.wav')

# Parameters
symbol_rate = 16000  # Symbol rate of 16 kbps
symbol_period = 1 / (symbol_rate / 2)
nyquist_bandwidth = 1 / (2 * symbol_period)
low_pass_cutoff = 0.9 * nyquist_bandwidth
low_pass_order = 101
low_pass_filter = sig.firwin(low_pass_order, low_pass_cutoff / (fs / 2))

# Downconversion parameters
carrier_freq = 2e5
freq_offset = 4800  # Initial frequency offset for simulation
t = np.arange(len(mod_signal)) / fs

# Coarse frequency correction with FFT
def coarse_freq_estimation(signal, fs, N_coarse=2):
    downconverted_buffer = signal ** N_coarse
    fftlen = 4 * len(signal)
    freqs = np.fft.fftfreq(fftlen, d=1/fs)
    spectrum = np.abs(np.fft.fftshift(np.fft.fft(downconverted_buffer, n=fftlen))) / len(downconverted_buffer)
    max_freq_idx = np.argmax(spectrum)
    coarse_freq = freqs[max_freq_idx] / N_coarse
    return coarse_freq

# Downconvert the signal with estimated coarse frequency
mod_signal_downconverted = mod_signal * np.exp(-1j * 2 * np.pi * (carrier_freq + freq_offset) * t)
coarse_freq = coarse_freq_estimation(mod_signal_downconverted, fs)
print(f"Coarse Frequency Adjustment: {coarse_freq:.2f} Hz")

mod_signal_downconverted *= np.exp(-1j * 2 * np.pi * t * coarse_freq)

# Initialize Costas loop parameters
N = len(mod_signal_downconverted)
phase_estimate = 0
freq_estimate = 0
alpha = 0.005  # Phase adjustment gain
beta = 0.00001  # Frequency adjustment gain

# Containers for logging
I_signal = np.zeros(N)
Q_signal = np.zeros(N)
freq_log = []
phase_log = []

# Costas loop implementation
for i in range(N):
    # Apply current phase estimate
    adjusted_sample = mod_signal_downconverted[i] * np.exp(-1j * phase_estimate)
    
    # Separate I (in-phase) and Q (quadrature) components
    I_signal[i] = np.real(adjusted_sample)
    Q_signal[i] = np.imag(adjusted_sample)
    
    # Calculate phase error based on I and Q for BPSK
    phase_error = I_signal[i] * Q_signal[i]
    
    # Update frequency and phase estimates
    freq_estimate += beta * phase_error
    phase_estimate += freq_estimate + alpha * phase_error
    
    # Log frequency and phase estimates for visualization
    freq_log.append(freq_estimate * fs / (2 * np.pi))  # Convert to Hz
    phase_log.append(np.mod(phase_estimate, 2 * np.pi))

# Low-pass filter the output I and Q components
I_filtered = sig.lfilter(low_pass_filter, 1, I_signal)
Q_filtered = sig.lfilter(low_pass_filter, 1, Q_signal)

# Plotting
fig, axs1 = plt.subplots(2, 1, constrained_layout=True)
fig.suptitle(f'{mod_type} Modulated Signal (Received) Costas Loop - Improved Implementation')
axs1[0].plot(t, I_filtered, label='I')
axs1[1].plot(t, Q_filtered, label='Q')
axs1[0].set_title(f'{mod_type} Costas Loop I Component')
axs1[0].set_xlabel('Time (s)')
axs1[0].set_ylabel('Amplitude')
axs1[1].set_title(f'{mod_type} Costas Loop Q Component')
axs1[1].set_xlabel('Time (s)')
axs1[1].set_ylabel('Amplitude')

fig, axs2 = plt.subplots(2, 1, constrained_layout=True)
axs2[0].plot(freq_log, label='Frequency Estimate (Hz)')
axs2[0].set_title(f'{mod_type} Costas Loop Frequency Tracking')
axs2[0].set_ylabel('Frequency (Hz)')
axs2[1].plot(phase_log)
axs2[1].set_title(f'{mod_type} Costas Loop Phase Tracking')
axs2[1].set_xlabel('Samples')
axs2[1].set_ylabel('Phase (radians)')

plt.show()

import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav




fs1,mod1 = wav.read(r'test_file__I_Love_Gaming!__200kHz_16kbps_qam64.wav')
fs2,mod2 = wav.read(r'test_file__I_Love_Gaming!__200kHz_16kbps_qam64_-44.1kHz_-3rad.wav')


spectrum = lambda x: np.fft.fftshift(np.abs(np.fft.fft(x[::],n=len(x))))/len(x)

f_spec_x_axis = np.linspace(-fs1/2,fs1/2,len(mod1),endpoint=False)

freq_range = fs1/20 * 1.25
range_indices = np.where((f_spec_x_axis >= -freq_range) & (f_spec_x_axis <= freq_range))

f_spec_x_axis = f_spec_x_axis[range_indices]

mod1_spec = spectrum(mod1)[range_indices]

mod2_spec = spectrum(mod2)[range_indices]


t = np.linspace(0,len(mod1)/fs1,len(mod1))
m1d_i = mod1 * np.cos(2 * np.pi * 2e5 * t)
m1d_q = mod1 * -np.sin(2 * np.pi * 2e5 * t)

basem1 = m1d_i + 1j*m1d_q
basem1_spec = spectrum(basem1)[range_indices]

fig, axs = plt.subplots(3,1)
fig.suptitle('QAM16 Modulated Signal')
axs[0].plot(t, m1d_i, label='I')
axs[1].plot(t, m1d_q, label='Q')
axs[0].set_title('QAM16 Modulated Signal (Original) I Component')
axs[0].set_xlabel('Time (s)')
axs[0].set_ylabel('Amplitude')
axs[1].set_title('QAM16 Modulated Signal (Original) Q Component')
axs[1].set_xlabel('Time (s)')
axs[2].plot(f_spec_x_axis, basem1_spec)
axs[2].set_title('QAM16 Modulated Signal (Original) Spectrum')
axs[2].set_xlabel('Frequency (Hz)')
axs[2].set_ylabel('Magnitude')


# initial local oscillator approximate downcoversion
m2d_i = mod2 * np.cos(2 * np.pi * 2e5 * t)
m2d_q = mod2 * -np.sin(2 * np.pi * 2e5 * t)

basem2_complex = m2d_i + 1j * m2d_q

#coarse tuning
basem2_complex_buff = basem2_complex**(2) # 2nd power to find the residual frequency offset

basem2_complex_buff_spec = spectrum(basem2_complex_buff)[range_indices]

coarse_freq = f_spec_x_axis[np.argmax(basem2_complex_buff_spec)]/2


# Remove the coarse offset
basem2_complex = basem2_complex * np.exp(-1j * 2 * np.pi * t * coarse_freq)
print(coarse_freq)

# Costas Fine tuning
N = len(basem2_complex)
phase = 0
freq = 0
# These next two params is what to adjust, to make the feedback loop faster or slower (which impacts stability)
alpha = 0.064
beta = 0.02
out = np.zeros(N, dtype=np.complex64)
freq_log = []
for i in range(N):
    out[i] = basem2_complex[i] * np.exp(-1j*phase) # adjust the input sample by the inverse of the estimated phase offset
    error = np.real(out[i]) * np.imag(out[i]) # This is the error formula for 2nd order Costas Loop (e.g. for BPSK)

    # Advance the loop (recalc phase and freq offset)
    freq += (beta * error)
    freq_log.append(freq * fs2 / (2*np.pi)) # convert from angular velocity to Hz for loggingq
    phase += freq + (alpha * error)

    # Optional: Adjust phase so its always between 0 and 2pi, recall that phase wraps around every 2pi
    while phase >= 2*np.pi:
        phase -= 2*np.pi
    while phase < 0:
        phase += 2*np.pi

fine_freq = freq_log[-1]

# Remove the residual fine offset
basem2_complex = basem2_complex * np.exp(-1j * 2 * np.pi * t * fine_freq)
print(fine_freq)

total_freq = coarse_freq + fine_freq
print(f'Total Frequency Offset: {total_freq} Hz')

m2d_i = mod2 *  np.cos(2 * np.pi * (2e5 + total_freq) * t)
m2d_q = mod2 * -np.sin(2 * np.pi * (2e5 + total_freq) * t)

m2d_i_c = mod2 * np.cos(2 * np.pi * (2e5-44.1e3) * t)
m2d_q_c = mod2 * -np.sin(2 * np.pi * (2e5-44.1e3) * t)

fig, axs2 = plt.subplots(2,2)
fig.suptitle('QAM16 Modulated Signal')
axs2[0,0].plot(t, m2d_i, label='I')
axs2[1,0].plot(t, m2d_q, label='Q')
axs2[0,0].set_title('QAM16 Modulated Signal (Offset) I Component')
axs2[0,0].set_xlabel('Time (s)')
axs2[0,0].set_ylabel('Amplitude')
axs2[1,0].set_title('QAM16 Modulated Signal (Offset) Q Component')
axs2[1,0].set_xlabel('Time (s)')
axs2[1,0].set_ylabel('Amplitude')

axs2[0,1].plot(t, m2d_i_c, label='I')
axs2[1,1].plot(t, m2d_q_c, label='Q')
axs2[0,1].set_title('QAM16 Modulated Signal (Offset) I Component (Corrected)')
axs2[0,1].set_xlabel('Time (s)')
axs2[0,1].set_ylabel('Amplitude')
axs2[1,1].set_title('QAM16 Modulated Signal (Offset) Q Component (Corrected)')
axs2[1,1].set_xlabel('Time (s)')
axs2[1,1].set_ylabel('Amplitude')



plt.show()





''' # PLOTTING Differences
fig, axs = plt.subplots(2,3)
fig.suptitle('QAM16 Modulated Signal')
axs[0,0].plot(t, m1d_i, label='I')
axs[0,1].plot(t, m1d_q, label='Q')
axs[0,0].set_title('QAM16 Modulated Signal (Original)')
axs[0,0].set_xlabel('Time (s)')
axs[0,0].set_ylabel('Amplitude')
axs[0,0].legend()


basem1 = m1d_i + m1d_q
basem2 = m2d_i + m2d_q

basem1_spec = spectrum(basem1)[range_indices]
basem2_spec = spectrum(basem2)[range_indices]

axs[0,2].plot(f_spec_x_axis, basem1_spec)
axs[0,2].set_title('QAM16 Modulated Signal (Original)')
axs[0,2].set_xlabel('Frequency (Hz)')
axs[0,2].set_ylabel('Magnitude')

axs[1,0].plot(t, m2d_i, label='I')
axs[1,1].plot(t, m2d_q, label='Q')
axs[1,0].set_title('QAM16 Modulated Signal (Modified)')
axs[1,0].set_xlabel('Time (s)')
axs[1,0].set_ylabel('Amplitude')
axs[1,0].legend()

axs[1,2].plot(f_spec_x_axis, basem2_spec)
axs[1,2].set_title('QAM16 Modulated Signal (Modified)')
axs[1,2].set_xlabel('Frequency (Hz)')
axs[1,2].set_ylabel('Magnitude')'''

''' # COSTAS LOOP SINGLE RUN
N = len(basem2_complex)
phase = 0
freq = 0
# These next two params is what to adjust, to make the feedback loop faster or slower (which impacts stability)
alpha = 0.15
beta = 0.01
out = np.zeros(N, dtype=np.complex64)
freq_log = []
for i in range(N):
    out[i] = basem2_complex[i] * np.exp(-1j*phase) # adjust the input sample by the inverse of the estimated phase offset
    error = np.real(out[i]) * np.imag(out[i]) # This is the error formula for 2nd order Costas Loop (e.g. for BPSK)

    # Advance the loop (recalc phase and freq offset)
    freq += (beta * error)
    freq_log.append(freq * fs2 / (2*np.pi)) # convert from angular velocity to Hz for loggingq
    phase += freq + (alpha * error)

    # Optional: Adjust phase so its always between 0 and 2pi, recall that phase wraps around every 2pi
    while phase >= 2*np.pi:
        phase -= 2*np.pi
    while phase < 0:
        phase += 2*np.pi

# Plot freq over time to see how long it takes to hit the right offset
fig2 = plt.figure(2)
fig2.add_subplot(111).plot(freq_log, '.-')
'''


''' # COSTAS LOOP MULTIPLE RUNS
alpha = np.linspace(0.01, 0.02, 3)
beta = np.linspace(0.001, 0.002, 3)
for i in range(len(alpha)):
    for j in range(len(beta)):
        out = np.zeros(N, dtype=np.complex64)
        freq_log = []
        for k in range(N):
            out[k] = basem2_complex[k] * np.exp(-1j*phase) # adjust the input sample by the inverse of the estimated phase offset
            error = np.real(out[k]) * np.imag(out[k]) # This is the error formula for 2nd order Costas Loop (e.g. for BPSK)

            # Advance the loop (recalc phase and freq offset)
            freq += (beta[j] * error)
            freq_log.append(freq * fs2 / (2*np.pi)) # convert from angular velocity to Hz for loggingq
            phase += freq + (alpha[i] * error)

            # Optional: Adjust phase so its always between 0 and 2pi, recall that phase wraps around every 2pi
            while phase >= 2*np.pi:
                phase -= 2*np.pi
            while phase < 0:
                phase += 2*np.pi

        # Plot freq over time to see how long it takes to hit the right offset
        fig = plt.figure(i+j*2)
        fig.add_subplot(111).plot(freq_log, '.-')
'''
plt.show()
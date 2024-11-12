import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as sig
import commpy

fs ,modc = wav.read(r'WaveFiles\test_file__I_Love_Gaming!__200kHz_16kbps_BPSK.wav')
_  ,modr = wav.read(r'WaveFiles\test_file__I_Love_Gaming!__200kHz_16kbps_BPSK.wav')

mod_type = 'BPSK'

symbol_period = 1/(16000/2)

Nyquist_Bandwidth = 1/(2*symbol_period)
low_pass_filter_cutoff = 5*Nyquist_Bandwidth
low_pass_filter_order = 77
low_pass_delay = (low_pass_filter_order // 2) / fs
low_pass_filter = sig.firwin(low_pass_filter_order, low_pass_filter_cutoff/(fs/2), fs = fs)

RRC_delay = 3*symbol_period
_, rrc = commpy.filters.rrcosfilter(N=int(2*fs*RRC_delay),alpha=0.5,Ts=symbol_period, Fs=fs)

assert modc.shape == modr.shape

fftlen = 4 * len(modc)

f_spec_x_axis = np.linspace(-fs/2,fs/2,fftlen,endpoint=False)

freq_range = fs/20 * 1.25
range_indices = np.where((f_spec_x_axis >= -freq_range) & (f_spec_x_axis <= freq_range))

f_spec_x_axis = f_spec_x_axis[range_indices]
spectrum = lambda x: (np.fft.fftshift(np.abs(np.fft.fft(x[::],n=fftlen)))/len(x))[range_indices]

#Downconversion
t = np.linspace(0,len(modc)/fs,len(modc))
m1d_i = modc * np.cos(2 * np.pi * 2e5 * t)
m1d_q = modc * -np.sin(2 * np.pi * 2e5 * t)

basem1 = m1d_i + 1j*m1d_q

RC_signal = sig.convolve(basem1, rrc) / np.sum(rrc**2) * 2

basem1_spec = spectrum(basem1)

fig, axs = plt.subplots(5,1)
fig.suptitle(f'{mod_type} Modulated Signal (Original)')
axs[0].plot(t, m1d_i, label='I')
axs[1].plot(t, m1d_q, label='Q')
axs[1].set_title(f'{mod_type} Modulated Signal (Original) I Component')
axs[0].set_xlabel('Time (s)')
axs[0].set_ylabel('Amplitude')
axs[1].set_title(f'{mod_type} Modulated Signal (Original) Q Component')
axs[1].set_xlabel('Time (s)')
axs[2].plot(f_spec_x_axis, basem1_spec)
axs[2].set_title(f'{mod_type} Modulated Signal (Original) Spectrum IQ')
axs[2].set_xlabel('Frequency (Hz)')
axs[2].set_ylabel('Magnitude')
axs[3].plot(RC_signal.real)
axs[3].set_title(f'{mod_type} Modulated Signal (Original) I Component (RC)')
axs[3].set_xlabel('Time (s)')
axs[3].set_ylabel('Amplitude')
axs[4].plot(RC_signal.imag)
axs[4].set_title(f'{mod_type} Modulated Signal (Original) Q Component (RC)')
axs[4].set_xlabel('Time (s)')
axs[4].set_ylabel('Amplitude')



deltaF = 1000
m2d_i = modr * np.cos(2 * np.pi * (2e5+deltaF) * t)
m2d_q = modr * -np.sin(2 * np.pi * (2e5+deltaF) * t)

basem2_complex = m2d_i + 1j * m2d_q

N = 2
basem2_complex_buff = basem2_complex**(N) # 2nd power to find the residual frequency offset
basem2_complex_buff_spec = spectrum(basem2_complex_buff)
coarse_freq = f_spec_x_axis[np.argmax(basem2_complex_buff_spec)]/N

print(f'Coarse Frequency: {coarse_freq}')

basem2_complex = basem2_complex * np.exp(-1j * 2 * np.pi * t * (coarse_freq-10))

'''fig, axs2 = plt.subplots(3,1)
fig.suptitle(f'{mod_type} Modulated Signal (Coarse)')
axs2[0].plot(t, basem2_complex.real, label='I')
axs2[1].plot(t, basem2_complex.imag, label='Q')
axs2[1].set_title(f'{mod_type} Modulated Signal (Coarse) I Component')
axs2[0].set_xlabel('Time (s)')
axs2[0].set_ylabel('Amplitude')
axs2[1].set_title(f'{mod_type} Modulated Signal (Coarse) Q Component')
axs2[1].set_xlabel('Time (s)')
axs2[2].plot(f_spec_x_axis, spectrum(basem2_complex))
axs2[2].set_title(f'{mod_type} Modulated Signal (Coarse) Spectrum')
axs2[2].set_xlabel('Frequency (Hz)')
axs2[2].set_ylabel('Magnitude')'''

modr_shift = modr * np.exp(-1j * 2 * np.pi * t * (1e3))

N = len(modr_shift)
phase = 0
freq = 0
# These next two params is what to adjust, to make the feedback loop faster or slower (which impacts stability)
alpha = 0.15
beta = 0.01
out = np.zeros(N, dtype=np.complex64)
freq_log = []
for i in range(N):
    out[i] = modr_shift[i] * np.exp(-1j*phase) # adjust the input sample by the inverse of the estimated phase offset
    error = np.real(out[i]) * np.imag(out[i]) # This is the error formula for 2nd order Costas Loop (e.g. for BPSK)

    # Advance the loop (recalc phase and freq offset)
    freq += (beta * error)
    freq_log.append(freq * fs / (2*np.pi)) # convert from angular velocity to Hz for loggingq
    phase += freq + (alpha * error)

    # Optional: Adjust phase so its always between 0 and 2pi, recall that phase wraps around every 2pi
    while phase >= 2*np.pi:
        phase -= 2*np.pi
    while phase < 0:
        phase += 2*np.pi

# Plot freq over time to see how long it takes to hit the right offset
fig, axs4 = plt.subplots(1,1)
fig.suptitle(f'{mod_type} Modulated Signal (Fine)')
axs4.plot(freq_log)

fig, axs3 = plt.subplots(3,1)
fig.suptitle(f'{mod_type} Modulated Signal (fine)')
axs3[0].plot(t, out.real, label='I')
axs3[1].plot(t, out.imag, label='Q')
axs3[1].set_title(f'{mod_type} Modulated Signal (fine) I Component')
axs3[0].set_xlabel('Time (s)')
axs3[0].set_ylabel('Amplitude')
axs3[1].set_title(f'{mod_type} Modulated Signal (fine) Q Component')
axs3[1].set_xlabel('Time (s)')
axs3[2].plot(f_spec_x_axis, spectrum(out))
axs3[2].set_title(f'{mod_type} Modulated Signal (fine) Spectrum')
axs3[2].set_xlabel('Frequency (Hz)')
axs3[2].set_ylabel('Magnitude')

plt.show()
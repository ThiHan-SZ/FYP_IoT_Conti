import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as sig
import commpy


mod_type = 'BPSK'

fs ,modc = wav.read(rf'WaveFiles\test_file__I_Love_Gaming!__200kHz_16kbps_{mod_type}.wav')
_  ,modr = wav.read(rf'WaveFiles\test_file__I_Love_Gaming!__200kHz_16kbps_{mod_type}.wav')

symbol_period = 1/(16000/2)

Nyquist_Bandwidth = 1/(2*symbol_period)
low_pass_filter_cutoff = 0.9*Nyquist_Bandwidth
low_pass_filter_order = 77
low_pass_filter = sig.firwin(low_pass_filter_order, low_pass_filter_cutoff / (fs / 2), fs=fs)


RRC_delay = 3*symbol_period
_, rrc = commpy.filters.rrcosfilter(N=int(2*fs*RRC_delay),alpha=0.5,Ts=symbol_period, Fs=fs)

assert modc.shape == modr.shape

fftlen = 1 * len(modc)

f_spec_x_axis = np.linspace(-fs/2,fs/2,fftlen,endpoint=False)

freq_range = fs/20 * 1.25
range_indices = np.where((f_spec_x_axis >= -freq_range) & (f_spec_x_axis <= freq_range))

f_spec_x_axis = f_spec_x_axis[range_indices]
spectrum = lambda x: (np.fft.fftshift(np.abs(np.fft.fft(x[::],n=fftlen)))/len(x))[range_indices]

#Downconversion
t = np.linspace(0,len(modc)/fs,len(modc))

modc_downconverted = modc * np.exp(-1j * 2 * np.pi * 2e5 * t)

modc_i = np.real(modc_downconverted)
modc_q = np.imag(modc_downconverted)

print((modc_i == modc * np.cos(2 * np.pi * 2e5 * t)).all())
print((modc_q == modc * -np.sin(2 * np.pi * 2e5 * t)).all())

modc_i_lp = sig.lfilter(low_pass_filter,1,modc_i)
modc_q_lp = sig.lfilter(low_pass_filter,1,modc_q)

modc_i_rrc = sig.lfilter(rrc,1,modc_i_lp)
modc_q_rrc = sig.lfilter(rrc,1,modc_q_lp)

'''fig, axs = plt.subplots(3,1)
fig.suptitle(f'{mod_type} Modulated Signal (Original)')
axs[0].plot(t, modc_i_lp, label='I')
axs[1].plot(t, modc_q_lp, label='Q')
axs[1].set_title(f'{mod_type} Modulated Signal (Original) I Component')
axs[0].set_xlabel('Time (s)')
axs[0].set_ylabel('Amplitude')
axs[1].set_title(f'{mod_type} Modulated Signal (Original) Q Component')
axs[1].set_xlabel('Time (s)')
axs[2].plot(f_spec_x_axis, spectrum(modc_downconverted))
axs[2].set_title(f'{mod_type} Modulated Signal (Original) Spectrum IQ')
axs[2].set_xlabel('Frequency (Hz)')
axs[2].set_ylabel('Magnitude')
'''

deltaF = 13000

modr_downconverted = modr * np.exp(-1j * 2 * np.pi * (2e5+deltaF) * t)


N_coarse = 2
modr_downconverted_buffer = modr_downconverted**(N_coarse)
modr_downconverted_buffer_spec = spectrum(modr_downconverted_buffer)
max_freq = f_spec_x_axis[np.argmax(modr_downconverted_buffer_spec)]/N_coarse

modr_downconverted = modr_downconverted * np.exp(-1j * 2 * np.pi * t * max_freq)

print(max_freq)

N = len(modr_downconverted)
phase = 0
freq = 0
# These next two params is what to adjust, to make the feedback loop faster or slower (which impacts stability)
alpha = 0.132
beta = 0.00932
out = np.zeros(N, dtype=np.complex64)
freq_log = []
phase_log = []
for i in range(N):
    out[i] = modr_downconverted[i] * np.exp(-1j*phase) # adjust the input sample by the inverse of the estimated phase offset
    error = np.real(out[i]) * np.imag(out[i]) # This is the error formula for 2nd order Costas Loop (e.g. for BPSK)

    # Advance the loop (recalc phase and freq offset)
    freq += (beta * error)
    freq_log.append(freq * fs / (2*np.pi)) # convert from angular velocity to Hz for logging
    phase += freq + (alpha * error)
    phase_log.append(phase)

    # Optional: Adjust phase so its always between 0 and 2pi, recall that phase wraps around every 2pi
    while phase >= 2*np.pi:
        phase -= 2*np.pi
    while phase < 0:
        phase += 2*np.pi

# Plot freq over time to see how long it takes to hit the right offset
out_i_lp = sig.lfilter(low_pass_filter,1,np.real(out))
out_q_lp = sig.lfilter(low_pass_filter,1,np.imag(out))
fig, axs1 = plt.subplots(2,1, constrained_layout=True)
fig.suptitle(f'{mod_type} Modulated Signal (Received) Costas Loop beta = {alpha}')
axs1[0].plot(t, out_i_lp, label='I')
axs1[1].plot(t, out_q_lp, label='Q')
axs1[1].set_title(f'{mod_type} Modulated Signal (Received) Costas Loop I Component')
axs1[0].set_xlabel('Time (s)')
axs1[0].set_ylabel('Amplitude')
axs1[1].set_title(f'{mod_type} Modulated Signal (Received) Costas Loop Q Component mean = {np.mean(np.abs(out_q_lp))}')
axs1[1].set_xlabel('Time (s)')
fig, axs2 = plt.subplots(2,1, constrained_layout=True)
axs2[0].plot(freq_log)
axs2[0].set_title(f'{mod_type} Modulated Signal (Received) Costas Loop Freq')
axs2[0].set_ylabel('Frequency (Hz)')
axs2[1].plot(phase_log)
axs2[1].set_title(f'{mod_type} Modulated Signal (Received) Costas Loop Phase')
        

plt.show()
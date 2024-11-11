import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import pickle
import scipy.signal as sig
import commpy

fs,mod1 = wav.read(r'WaveFiles\test_file__I_Love_Gaming!__200kHz_16kbps_QAM16.wav')
_,mod1_r = wav.read(r'WaveFiles\test_file__I_Love_Gaming!__200kHz_16kbps_QAM16.wav')


symbol_period = 1/(16e3/4)
low_pass_filter = sig.firwin(77, (5/(2*symbol_period))/(fs/2), fs = fs)

RRC_delay = 3*symbol_period
_, rrc = commpy.filters.rrcosfilter(N=int(2*fs*RRC_delay),alpha=0.5,Ts=symbol_period, Fs=fs)

fftlen = 4*len(mod1)
f_spec_x_axis = np.linspace(-fs/2,fs/2,fftlen,endpoint=False)
freq_range = fs/20 * 1.25
range_indices = np.where((f_spec_x_axis >= -freq_range) & (f_spec_x_axis <= freq_range))

f_spec_x_axis = f_spec_x_axis
spectrum = lambda x: (np.fft.fftshift(np.abs(np.fft.fft(x[::],n=fftlen)))/len(x))




t = np.linspace(0,len(mod1)/fs,len(mod1),endpoint=False)
m1_I = mod1 * np.cos(2 * np.pi * 2e5 * t)
m1_Q = mod1 * -np.sin(2 * np.pi * 2e5 * t)

m1_I_lp = sig.lfilter(low_pass_filter, 1, m1_I)
m1_Q_lp = sig.lfilter(low_pass_filter, 1, m1_Q)

m1_complex = m1_I_lp + 1j*m1_Q_lp
m1_Signal = sig.convolve(m1_complex, rrc) / np.sum(rrc**2) * 2

'''fig,axs = plt.subplots(3,1, constrained_layout=True)

axs[0].plot(m1_Signal.real)
axs[0].set_title('I Component Correct')
axs[0].set_xlabel('Time (s)')
axs[0].set_ylabel('Amplitude')
axs[1].plot(m1_Signal.imag)
axs[1].set_title('Q Component Correct')
axs[1].set_xlabel('Time (s)')
axs[2].plot(f_spec_x_axis[range_indices],spectrum(m1_Signal)[range_indices])
axs[2].set_title('Spectrum Correct')
axs[2].set_xlabel('Frequency (Hz)')'''


deltaF = 1e3
mod1_r_I = mod1_r * np.cos(2 * np.pi * (2e5+deltaF) * t)
mod1_r_Q = mod1_r * -np.sin(2 * np.pi * (2e5+deltaF) * t)

mod1_r_I_lp = sig.lfilter(low_pass_filter, 1, mod1_r_I)
mod1_r_Q_lp = sig.lfilter(low_pass_filter, 1, mod1_r_Q)

mod1_r_complex = mod1_r_I_lp + 1j*mod1_r_Q_lp

N = 2
mod1_r_complex_buff = mod1_r_complex**(N)
mod1_r_complex_spec = spectrum(mod1_r_complex_buff)
max_freq = f_spec_x_axis[np.argmax(mod1_r_complex_spec)] / (N)

fig,axs = plt.subplots(1,1, constrained_layout=True)

axs.plot(f_spec_x_axis[range_indices],mod1_r_complex_spec[range_indices])
axs.set_title(f'Spectrum Incorrect | max freq: {max_freq} Hz')
axs.set_xlabel('Frequency (Hz)')


plt.show()
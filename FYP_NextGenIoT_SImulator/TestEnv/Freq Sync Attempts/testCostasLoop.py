import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as sig
import commpy


mod_type = 'QPSK'

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

fftlen = 4 * len(modc)

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

'''
print((modc_i == modc * np.cos(2 * np.pi * 2e5 * t)).all())
print((modc_q == modc * -np.sin(2 * np.pi * 2e5 * t)).all())
'''

modc_i_lp = sig.lfilter(low_pass_filter,1,modc_i)
modc_q_lp = sig.lfilter(low_pass_filter,1,modc_q)

modc_i_rrc = sig.lfilter(rrc,1,modc_i_lp) * 2
modc_q_rrc = sig.lfilter(rrc,1,modc_q_lp) * 2

'''
fig, axs = plt.subplots(3,1)
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

'''4.8khz offset max for LEO'''
deltaF = 4800

modr_downconverted = modr * np.exp(-1j * 2 * np.pi * (2e5+deltaF) * t)

modr_i = np.real(modr_downconverted)
modr_q = np.imag(modr_downconverted)


modr_i_lp = sig.lfilter(low_pass_filter,1,modr_i)
modr_q_lp = sig.lfilter(low_pass_filter,1,modr_q)

out = np.zeros(len(modr),dtype=np.complex128)
error = np.zeros(len(modr),dtype=np.complex128)
phase = np.zeros(len(modr),dtype=np.float64)

Kp = 0.1
Ki = 0.1

approximate = np.sin(2 * np.pi * 2e5 * t) * np.cos(2 * np.pi * 2e5 * t)

def find_error(i):
    return approximate-i

for i in range(len(modr)):
    out[i] = modr_downconverted[i] * np.exp(-1j * 2 * phase[i])
    phase[i] = approximate[i] - out[i].imag*out[i].real

fig, axs = plt.subplots(3,1)
axs[0].plot(t, out.real, label='I')
axs[1].plot(t, out.imag, label='Q')
axs[2].plot(t, phase, label='Phase')

plt.show()
import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav




fs1,mod1 = wav.read(r'WaveFiles\test_file__I_Love_Gaming!__200kHz_16kbps_BPSK.wav')
fs2,mod2 = wav.read(r'WaveFiles\test_file__I_Love_Gaming!__200kHz_16kbps_BPSK.wav')

fftlen = 4 * len (mod1)
spectrum = lambda x: np.fft.fftshift(np.abs(np.fft.fft(x[::],n=fftlen)))/len(x)

f_spec_x_axis = np.linspace(-fs1/2,fs1/2,fftlen,endpoint=False)

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
fig.suptitle('BPSK Modulated Signal')
axs[0].plot(t, m1d_i, label='I')
axs[1].plot(t, m1d_q, label='Q')
axs[0].set_title('BPSK Modulated Signal (Original) I Component')
axs[0].set_xlabel('Time (s)')
axs[0].set_ylabel('Amplitude')
axs[1].set_title('BPSK Modulated Signal (Original) Q Component')
axs[1].set_xlabel('Time (s)')
axs[2].plot(f_spec_x_axis, basem1_spec)
axs[2].set_title('BPSK Modulated Signal (Original) Spectrum')
axs[2].set_xlabel('Frequency (Hz)')
axs[2].set_ylabel('Magnitude')


# initial local oscillator approximate downcoversion
m2d_i = mod2 * np.cos(2 * np.pi * (2e5+1e3) * t)
m2d_q = mod2 * -np.sin(2 * np.pi * (2e5+1e3) * t)

basem2_complex = m2d_i + 1j * m2d_q

#coarse tuning
basem2_complex_buff = basem2_complex**(2) # 2nd power to find the residual frequency offset

basem2_complex_buff_spec = spectrum(basem2_complex_buff)[range_indices]

coarse_freq = f_spec_x_axis[np.argmax(basem2_complex_buff_spec)]/2


# Remove the coarse offset
basem2_complex = basem2_complex * np.exp(-1j * 2 * np.pi * t * (coarse_freq))
print(coarse_freq)

fig, axs2 = plt.subplots(3,1)
fig.suptitle('BPSK Modulated Signal')
axs2[0].plot(t, basem2_complex.real, label='I')
axs2[1].plot(t, basem2_complex.imag, label='Q')
axs2[0].set_title('BPSK Modulated Signal (Modified) I Component')
axs2[0].set_xlabel('Time (s)')
axs2[0].set_ylabel('Amplitude')
axs2[1].set_title('BPSK Modulated Signal (Modified) Q Component')
axs2[1].set_xlabel('Time (s)')
axs2[2].plot(f_spec_x_axis, basem2_complex_buff_spec)
axs2[2].set_title('BPSK Modulated Signal (Modified) Spectrum')
axs2[2].set_xlabel('Frequency (Hz)')
axs2[2].set_ylabel('Magnitude')

plt.show()
from SimulationClassCompact.ModulationClass import Modulator
from SimulationClassCompact.DemodulationClass import Demodulator
from SimulationClassCompact.ChannelClass import *

import matplotlib.pyplot as plt
import numpy as np

def plot_IQ_internal(self, t_Shaped_Pulse, Shaped_Pulse, I_FC, Q_FC, I_processed, Q_processed, Dirac_Comb, RRC_delay):
        fig, ax = plt.subplots(3, 2, constrained_layout=True)
        ax[0,0].plot(t_Shaped_Pulse / self.symbol_period, Shaped_Pulse.real, label='$u(t)$')
        
        # Plot the stems without markers for the real part
        _, stemlines_I_Dirac, baseline_I_Dirac = ax[0,0].stem(
            (RRC_delay + t_Shaped_Pulse) / self.symbol_period, 
            Dirac_Comb.real, 
            linefmt='r-', 
            markerfmt='',
            basefmt='r-'
        )
        baseline_I_Dirac.set_visible(False)
        plt.setp(stemlines_I_Dirac, 'alpha', 0.5)  # Stem line transparency

        # Overlay markers at non-zero positions only
        non_zero_indices_real = np.nonzero(Dirac_Comb.real)[0]
        non_zero_times_real = (RRC_delay + t_Shaped_Pulse[non_zero_indices_real]) / self.symbol_period
        non_zero_values_real = Dirac_Comb.real[non_zero_indices_real]
        ax[0,0].plot(non_zero_times_real, non_zero_values_real, 'ro', alpha=0.75)

        ax[0,0].set_title("Real Part")

        # Imaginary part with stems and non-zero markers
        ax[0,1].plot(t_Shaped_Pulse / self.symbol_period, Shaped_Pulse.imag)

        # Plot the stems without markers for the imaginary part
        _, stemlines_Q_Dirac, baseline_Q_Dirac = ax[0,1].stem(
            (RRC_delay + t_Shaped_Pulse) / self.symbol_period,
            Dirac_Comb.imag,
            linefmt='r-',
            markerfmt='',
            basefmt='r-'
        )
        baseline_Q_Dirac.set_visible(False)
        plt.setp(stemlines_Q_Dirac, 'alpha', 0.5)  # Stem line transparency

        # Overlay markers at non-zero positions only
        non_zero_indices_imag = np.nonzero(Dirac_Comb.imag)[0]
        non_zero_times_imag = (RRC_delay + t_Shaped_Pulse[non_zero_indices_imag]) / self.symbol_period
        non_zero_values_imag = Dirac_Comb.imag[non_zero_indices_imag]
        ax[0,1].plot(non_zero_times_imag, non_zero_values_imag, 'ro', alpha=0.75)

        ax[0,1].set_title("Imaginary Part")

        # Continue with other subplots as usual
        ax[1,0].plot(t_Shaped_Pulse/self.symbol_period, I_FC)
        ax[1,0].plot(t_Shaped_Pulse/self.symbol_period, I_processed)
        ax[1,0].set_title("I Signal")
        ax[1,0].set_ylabel("Amplitude")
        ax[1,0].set_xlabel("Sample Index (T/Ts)")

        ax[1,1].plot(t_Shaped_Pulse/self.symbol_period, Q_FC)
        ax[1,1].plot(t_Shaped_Pulse/self.symbol_period, Q_processed)
        ax[1,1].set_title("Q Signal")
        ax[1,1].set_ylabel("Amplitude")
        ax[1,1].set_xlabel("Sample Index (T/Ts)")

        # Spectrum calculation and plotting remains unchanged
        spectrum = lambda x: np.abs(np.fft.fftshift(np.fft.fft(x[::], n=len(x))) / len(x))
        f_spec_x_axis = np.linspace(-self.sampling_rate / 2, self.sampling_rate / 2, len(Shaped_Pulse), endpoint=False)

        freq_range = self.carrier_freq * 2
        range_indices = np.where((f_spec_x_axis >= -freq_range) & (f_spec_x_axis <= freq_range))

        f_spec_x_axis = f_spec_x_axis[range_indices]
        I_spectrum = spectrum(I_processed)[range_indices]
        Q_spectrum = spectrum(Q_processed)[range_indices]
        I_FC_spectrum = spectrum(I_FC)[range_indices]
        Q_FC_spectrum = spectrum(Q_FC)[range_indices]

        ax[2,0].plot(f_spec_x_axis, I_spectrum)
        ax[2,0].plot(f_spec_x_axis, I_FC_spectrum)
        ax[2,0].set_title("I Spectrum")
        ax[2,0].set_ylabel("Magnitude")
        ax[2,0].set_xlabel("Frequency (Hz)")
        
        ax[2,1].plot(f_spec_x_axis, Q_spectrum)
        ax[2,1].plot(f_spec_x_axis, Q_FC_spectrum)
        ax[2,1].set_title("Q Spectrum")
        ax[2,1].set_ylabel("Magnitude")
        ax[2,1].set_xlabel("Frequency (Hz)")

modulation_modes = ['BPSK', 'QPSK', 'QAM16', 'QAM64', 'QAM256', 'QAM1024', 'QAM4096']
mode = modulation_modes[2]
modulator = Modulator(mode, 16000, 200000)

modulator.IQ_Return = True

'''
with open(rf'FYP_NextGenIoT_Simulator\TestcaseFiles\TinySpeare.txt','r') as file:
    message = file.read()[:15000]
'''
message = "I Love Gaming!"
bitstream = modulator.msgchar2bit(message)


import os, psutil; print(str(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2) + ' MiB')  # in MiB 

t_Shaped_Pulse, modulated_signal, I_FC, Q_FC, I_processed, Q_processed, Dirac_Comb, RRC_delay = modulator.modulate(bitstream)

plot_IQ_internal(modulator, t_Shaped_Pulse, modulated_signal, I_FC, Q_FC, I_processed, Q_processed, Dirac_Comb, RRC_delay)

import os, psutil; print(str(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2) + ' MiB')  # in MiB 

plt.show()




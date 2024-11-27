import commpy.filters
from matplotlib import pyplot as plt
from scipy.io import wavfile as wav
import numpy as np
import scipy.signal as sig
import pickle
import commpy


class Modulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}

    def __init__(self, modulation_mode, bit_rate,carrier_freq) -> None:
       
        #Plot Parameters
        self.plot_choice = None
        self.IQenevlope_plot_choice = None
        self.fig, self.ax = plt.subplots(2, 1, constrained_layout=True)

        #Modulation Parameters
        self.carrier_freq = carrier_freq
        self.modulation_mode = modulation_mode
        self.order = self.modulation_modes[modulation_mode]

        #Bit Rate Parameters
        self.baud_rate = bit_rate/self.order
        self.symbol_period = 1/self.baud_rate

        #Sampler Parameters 
        self.oversampling_factor = 10
        self.sampling_rate = self.oversampling_factor*2*self.carrier_freq # 10x Oversampling Factor for any CF 
        
    def msgchar2bit(self, msg):
        return list(''.join(f'{byte:08b}' for byte in msg.encode('utf-8')))

    def digitalsignal(self, bitstr):
        if len(bitstr) % self.order != 0:
            bitstr.extend(['0']*(self.order - len(bitstr) % self.order))

        bitstr.extend(['0', '0'])
        signal_duration = len(bitstr)*self.symbol_period
        x_axis_digital = np.linspace(0, signal_duration, len(bitstr), endpoint=False)
        digital_signal = np.array([int(bit) for bit in bitstr])
        print(f"Digital Signal: {''.join(bitstr)}")
        return digital_signal, x_axis_digital
    
    def modulate(self, bitstr):
        if self.modulation_mode == 'BPSK':
            return self.bpsk_modulation(bitstr)
        elif self.modulation_mode == 'QPSK':
            return self.qpsk_modulation(bitstr)
        else:
            return self.qam_modulation(bitstr)
        
    def bpsk_modulation(self, bitstr):
        
        I = np.array([2*int(bit)-1 for bit in bitstr[:-2]])
        Q = np.zeros_like(I)

        self.IQenevlope_plot_choice = input("Do you want to plot I and Q? (Y/N): ").upper()

        return self.modulator_calculations(I, Q, bitstr[:-2])

    def qpsk_modulation(self, bitstr):

        bitgroups = [''.join(bitstr[i:i+self.order]) for i in range(0, len(bitstr[:-2]), self.order)]
        I = np.array([2*int(group[0])-1 for group in bitgroups])
        Q = np.array([2*int(group[1])-1 for group in bitgroups])

        self.IQenevlope_plot_choice = input("Do you want to plot I and Q? (Y/N): ").upper()

        return self.modulator_calculations(I, Q, bitgroups)

    def qam_modulation(self, bitstr):

        with open(rf'QAM_LUT_pkl\N{self.modulation_mode}.pkl', 'rb') as f:
            qam_constellations = pickle.load(f)

        bitgroups = [''.join(bitstr[i:i+self.order]) for i in range(0, len(bitstr[:-2]), self.order)]

        I = np.array([qam_constellations[group]['I'] for group in bitgroups])
        Q = np.array([qam_constellations[group]['Q'] for group in bitgroups])

        self.IQenevlope_plot_choice = input("Do you want to plot I and Q? (Y/N): ").upper()

        return self.modulator_calculations(I, Q, bitgroups)

    def modulator_calculations(self, I, Q, bitgroups):
        samples_per_symbol = int(self.symbol_period * self.sampling_rate)
        RRC_delay = 3 * self.symbol_period

        # Simulated SRRC filter and pulse shaping (replace with actual filter for real use)
        _, rrc = commpy.filters.rrcosfilter(N=int(2*self.sampling_rate*RRC_delay),alpha=0.5,Ts=self.symbol_period, Fs=self.sampling_rate)
        shaped_pulse_length = len(bitgroups) * samples_per_symbol + len(rrc) - 1
        Shaped_Pulse = np.zeros(shaped_pulse_length, dtype=complex)
        Dirac_Comb = np.zeros(shaped_pulse_length, dtype=complex)

        for idx, (i_val, q_val) in enumerate(zip(I, Q)):
            start_idx = idx * samples_per_symbol
            Shaped_Pulse[start_idx:start_idx + len(rrc)] += (i_val + 1j * q_val) * rrc
            Dirac_Comb[start_idx] = i_val + 1j * q_val  # Place only at start of each symbol

        t_Shaped_Pulse = np.linspace(0, len(Shaped_Pulse) / self.sampling_rate, len(Shaped_Pulse), endpoint=False)

        ###Upscaling the signal to the carrier frequency###
        I_processed = Shaped_Pulse.real
        Q_processed = Shaped_Pulse.imag
        I_FC = I_processed * np.cos(2 * np.pi * self.carrier_freq * t_Shaped_Pulse)
        Q_FC = Q_processed * -np.sin(2 * np.pi * self.carrier_freq * t_Shaped_Pulse)

        if self.IQenevlope_plot_choice == 'Y':
            self.plot_IQ_internal(t_Shaped_Pulse, Shaped_Pulse, I_FC, Q_FC, I_processed, Q_processed, Dirac_Comb, RRC_delay)

        return t_Shaped_Pulse, I_FC + Q_FC

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
        ax[1,0].plot(t_Shaped_Pulse, I_FC)
        ax[1,0].plot(t_Shaped_Pulse, I_processed)
        ax[1,0].set_title("I Signal")
        ax[1,0].set_ylabel("Amplitude")
        ax[1,0].set_xlabel("Sample Index (T/Ts)")

        ax[1,1].plot(t_Shaped_Pulse, Q_FC)
        ax[1,1].plot(t_Shaped_Pulse, Q_processed)
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

    def plot_digital_signal(self,bitstr):
        digital_signal, x_axis_digital = self.digitalsignal(bitstr)
        self.ax[0].step(x_axis_digital, digital_signal, where="post")
        self.ax[0].vlines(x_axis_digital[::self.order], -0.5, 1.5, color='r', linestyle='--', alpha=0.5)
        self.ax[0].set_ylabel("Digital Signal")

    def plot_modulated_signal(self, t, modulated_signal):
        self.ax[1].plot(t, modulated_signal)
        self.ax[1].set_title(f'Modulated Signal: {self.modulation_mode}')
        self.ax[1].set_ylabel("Amplitude")
        self.ax[1].set_xlabel("Time (s)")

    def plot_full(self,message):
        bitstr = self.msgchar2bit(message)
        self.plot_digital_signal(bitstr)
        t, modulated_signal = self.modulate(bitstr)
        self.plot_modulated_signal(t, modulated_signal)
        #plt.show()
        return t, modulated_signal

    def save(self, filename, modulated_signal):
        
        #norm_modulated_signal = modulated_signal / np.max(np.abs(modulated_signal)) # Old Normalization
        print(np.max(np.abs(modulated_signal))) # Debug print - Max value of the modulated signal
        modulated_signal /= 2
        modulated_signal = np.array(modulated_signal, dtype=np.float32)

        wav.write(filename, self.sampling_rate, modulated_signal)
        print(f"Modulated signal saved as {filename}")

    def plot_and_save(self, message, filename):
        t, modulated_signal = self.plot_full(message)
        self.save(filename+'.wav', modulated_signal)
        return t, modulated_signal

    ###Deprecated Functions###
    '''def modulator_calculations(self, I, Q, bitgroups):
        ###Simulation of the Digital Baseband Signal to Analog Modulation###
        samples_per_symbol = int(self.symbol_period*self.sampling_rate) 

        Dirac_Comb = np.zeros(len(bitgroups)*samples_per_symbol,dtype=complex)
        Dirac_Comb[::samples_per_symbol] = I + 1j*Q
        t_Dirac_Comb = np.linspace(0,len(Dirac_Comb)/self.sampling_rate,len(Dirac_Comb),endpoint=False)

        ###FFT of Dirac_Comb will show ISI due to the Dirac Comb function, thus filter with SRRC to remove ISI###
        RRC_delay = 3*self.symbol_period
        _, rrc = commpy.filters.rrcosfilter(N=int(2*self.sampling_rate*RRC_delay),alpha=0.5,Ts=self.symbol_period, Fs=self.sampling_rate)
        
        Shaped_Pulse = sig.convolve(Dirac_Comb,rrc) #Pulse shaped signal, convolving SRRC over the Dirac Comb function12
        t_Shaped_Pulse = np.linspace(0,len(Shaped_Pulse)/self.sampling_rate,len(Shaped_Pulse),endpoint=False)
        
        ###Upscaling the signal to the carrier frequency###
        I_processed = Shaped_Pulse.real
        Q_processed = Shaped_Pulse.imag
        I_FC = I_processed  *  np.cos(2*np.pi*self.carrier_freq*t_Shaped_Pulse)
        Q_FC = Q_processed  * -np.sin(2*np.pi*self.carrier_freq*t_Shaped_Pulse)

        if self.IQenevlope_plot_choice == 'Y':
            self.plot_IQ_internal(t_Dirac_Comb, Dirac_Comb, t_Shaped_Pulse, Shaped_Pulse, I_FC, Q_FC, I_processed, Q_processed, RRC_delay)

        return t_Shaped_Pulse,  I_FC + Q_FC'''
    

def main():
    message = input("Enter the message: ")

    '''
    with open(r'TestcaseFiles\AsciiTable.txt', 'r', encoding='utf-8') as f:
        message = f.read()
    '''

    while True:
        try:
            carrier_freq = int(input("Enter the carrier frequency: "))
            break
        except KeyboardInterrupt:
            exit()
        except:
            print("Invalid carrier frequency. Please re-enter.")

    while True:
        try:
            bit_rate = int(input("Enter the bit-rate: "))
            break
        except KeyboardInterrupt:
            exit()
        except:
            print("Invalid bit-rate. Please re-enter.")
    while True:
        mod_mode_select = input("Enter the modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
        if mod_mode_select in Modulator.modulation_modes:
            break
        print("Invalid modulation mode. Please reselect.")

    modulator = Modulator(mod_mode_select,bit_rate=bit_rate,carrier_freq=carrier_freq) 

    from ChannelClass import SimpleGWNChannel_dB # Importing the Channel Class for adding noise to the signal only for demonstration purposes

    if input("Do you want to save the modulated signal? (Y/N): ").upper() == 'Y':
        filename = input("Enter the filename to save the modulated signal: ")
        t,signal = modulator.plot_and_save(message, filename)
    else:
        t,signal = modulator.plot_full(message)
        
    plt.show()


if __name__ == "__main__":
    main()

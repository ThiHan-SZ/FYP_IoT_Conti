import numpy as np
import scipy.signal as sig
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import commpy
from ChannelClass import SimpleGWNChannel_dB


class Demodulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
    
    def __init__(self, modulation_mode, bit_rate,carrier_freq) -> None:
       
        #Plot Parameters
        self.plot_choice = None
        self.IQenevlope_plot_choice = None

        #Demodulation Parameters
        self.carrier_freq = carrier_freq
        self.modulation_mode = modulation_mode
        self.order = self.modulation_modes[modulation_mode]

        #Bit Rate Parameters
        self.baud_rate = bit_rate/self.order
        self.symbol_period = 1/self.baud_rate
        self.oversampling_factor = 10
        self.sampling_rate = self.oversampling_factor*2*self.carrier_freq # 10x Oversampling Factor for any CF

        #Demodulation Parameters
        self.Nyquist_Bandwidth = 1/(2*self.symbol_period)
        self.low_pass_filter_cutoff = 5*self.Nyquist_Bandwidth
        self.low_pass_filter_order = 101
        self.low_pass_delay = (self.low_pass_filter_order // 2) / self.sampling_rate
        self.low_pass_filter = self.low_pass_filter()

        self.demodulator_total_delay = None

    def downconverter(self, signal):
        t = np.linspace(0, len(signal)/self.sampling_rate, len(signal), endpoint=False)
        I = signal * np.cos(2 * np.pi * self.carrier_freq * t)
        Q = signal * - np.sin(2 * np.pi * self.carrier_freq * t)
        return I, Q
    
    def low_pass_filter(self):
        low_pass_filter = sig.firwin(self.low_pass_filter_order, self.low_pass_filter_cutoff/(self.sampling_rate/2), fs = self.sampling_rate)
        return low_pass_filter
    
    def demodulate(self, signal):
        I_base, Q_base = self.downconverter(signal)
        I_lp = sig.lfilter(self.low_pass_filter, 1, I_base)
        Q_lp = sig.lfilter(self.low_pass_filter, 1, Q_base)


        RRC_delay = 3*self.symbol_period
        _, rrc = commpy.filters.rrcosfilter(N=int(2*self.sampling_rate*RRC_delay),alpha=0.5,Ts=self.symbol_period, Fs=self.sampling_rate)

        baseband_signal = I_lp + 1j*Q_lp
        RC_signal = sig.convolve(baseband_signal, rrc) / np.sum(rrc**2) * 2

        self.demodulator_total_delay = int((2*RRC_delay + self.low_pass_delay) * self.sampling_rate)

        return RC_signal
    
    def plot(self, demod_signal):
        samples_per_symbol = int(self.symbol_period*self.sampling_rate) 
        fig, ax = plt.subplots(1,2)
        delay = self.demodulator_total_delay
        t_axis = np.linspace(0, len(demod_signal)/self.sampling_rate, len(demod_signal), endpoint=False)
        t_samples = t_axis[delay::samples_per_symbol]
        demod_signal_samples = demod_signal[delay::samples_per_symbol]

        ax[0].plot(t_axis/self.symbol_period, demod_signal.real)
        ax[0].stem(t_samples/self.symbol_period, demod_signal_samples.real, linefmt='r-', markerfmt='ro', basefmt='r-')
        ax[0].set_title("Demodulated Signal (Real)")
        ax[0].set_xlabel("Symbol Periods")
        ax[0].set_ylabel("Amplitude")
        ax[0].grid(True)

        ax[1].plot(t_axis/self.symbol_period, demod_signal.imag)
        ax[1].stem(t_samples/self.symbol_period, demod_signal_samples.imag, linefmt='r-', markerfmt='ro', basefmt='r-')
        ax[1].set_title("Demodulated Signal (Imaginary)")
        ax[1].set_xlabel("Symbol Periods")
        ax[1].set_ylabel("Amplitude")
        ax[1].grid(True)        

    def demod_and_plot(self, signal):
        demod_signal = self.demodulate(signal)
        self.plot(demod_signal)

    def received_constellation(self, demod_signal):
        samples_per_symbol = int(self.symbol_period*self.sampling_rate)
        delay = self.demodulator_total_delay
        t_axis = np.linspace(0, len(demod_signal)/self.sampling_rate, len(demod_signal), endpoint=False)
        t_samples = t_axis[delay::samples_per_symbol]
        demod_signal_samples = demod_signal[delay::samples_per_symbol]

        plt.figure()
        plt.scatter(demod_signal_samples.real, demod_signal_samples.imag)
        plt.title("Received Constellation")
        plt.xlabel("I")
        plt.ylabel("Q")
        plt.grid(True)
        
def main():
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
        if mod_mode_select in Demodulator.modulation_modes:
            break
        print("Invalid modulation mode. Please reselect.")

   

    file = input("Enter the file name/path: ")
    # Read the modulated signal
    fs, modulated = wav.read(file)

    noisymodulatedsignal = SimpleGWNChannel_dB(-5).add_noise(modulated)

    demodulator = Demodulator(mod_mode_select, bit_rate, fs/20)
    demodulated_signal = demodulator.demodulate(noisymodulatedsignal)
    demodulator.received_constellation(demodulated_signal)
    #demodulator.demod_and_plot(modulated)
    plt.show()

if __name__ == "__main__":
    main()
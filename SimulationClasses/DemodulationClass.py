import numpy as np
import scipy.signal as sig
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import commpy
from ChannelClass import SimpleGWNChannel_dB


class Demodulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
    
    def __init__(self, modulation_mode, bit_rate,carrier_freq, plot_IQ, plot_constellation) -> None:
       
        #Plot Parameters
        self.plot_IQ = plot_IQ
        self.plot_constellation = plot_constellation
        self.fig = plt.figure(constrained_layout=True)
        self.ax = self.plot_setup(self.fig)

        #Demodulation Parameters
        self.carrier_freq = carrier_freq
        self.modulation_mode = modulation_mode
        self.order = self.modulation_modes[modulation_mode]

        #Bit Rate Parameters
        self.baud_rate = bit_rate/self.order
        self.symbol_period = 1/self.baud_rate
        self.oversampling_factor = 10
        self.sampling_rate = self.oversampling_factor*2*self.carrier_freq # 10x Oversampling Factor for any CF
        self.samples_per_symbol = int(self.sampling_rate/self.baud_rate)

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

        RC_signal *= 2*((2**(self.order/2))-1)
        return RC_signal[:-(6*self.samples_per_symbol)]
    
    def plot_setup(self, fig):
        axes = {}
        if self.plot_IQ and self.plot_constellation:
            gridspec = fig.add_gridspec(nrows=3, ncols=2)
            axes['Iplot'] = fig.add_subplot(gridspec[0, 0])
            axes['Qplot'] = fig.add_subplot(gridspec[0, 1])
            axes['ConstPlot'] = fig.add_subplot(gridspec[1:, :])
        elif self.plot_IQ:
            gridspec = fig.add_gridspec(nrows=1, ncols=2)
            axes['Iplot'] = fig.add_subplot(gridspec[0, 0])
            axes['Qplot'] = fig.add_subplot(gridspec[0, 1])
        elif self.plot_constellation:
            gridspec = fig.add_gridspec(nrows=1, ncols=1)
            axes['ConstPlot'] = fig.add_subplot(gridspec[0, 0])
        return axes

    def plot(self, demod_signal):
        delay = self.demodulator_total_delay
        t_axis = np.linspace(0, len(demod_signal)/self.sampling_rate, len(demod_signal), endpoint=False)
        t_samples = t_axis[delay::self.samples_per_symbol]
        demod_signal_samples = demod_signal[delay::self.samples_per_symbol]

        self.ax['Iplot'].plot(t_axis/self.symbol_period, demod_signal.real)
        self.ax['Iplot'].stem(t_samples/self.symbol_period, demod_signal_samples.real)
        self.ax['Iplot'].set_title("I-Component")
        self.ax['Iplot'].set_xlabel("Symbol Periods")
        self.ax['Iplot'].set_ylabel("Amplitude")
        self.ax['Iplot'].grid(True)

        self.ax['Qplot'].plot(t_axis/self.symbol_period, demod_signal.imag)
        self.ax['Qplot'].stem(t_samples/self.symbol_period, demod_signal_samples.imag)
        self.ax['Qplot'].set_title("Q-Component")
        self.ax['Qplot'].set_xlabel("Symbol Periods")
        self.ax['Qplot'].set_ylabel("Amplitude")
        self.ax['Qplot'].grid(True)
    
    def received_constellation(self, demod_signal):
        demod_signal_samples = demod_signal[self.demodulator_total_delay::self.samples_per_symbol]
        self.ax['ConstPlot'].scatter(demod_signal_samples.real, demod_signal_samples.imag)
        self.ax['ConstPlot'].set_title("Received Constellation")
        self.ax['ConstPlot'].set_xlabel("I")
        self.ax['ConstPlot'].set_ylabel("Q")
        self.ax['ConstPlot'].grid(True)

    def demod_and_plot(self, signal):
        demod_signal = self.demodulate(signal)
        if self.plot_IQ:
            self.plot(demod_signal)
        if self.plot_constellation:
            self.received_constellation(demod_signal)

    ###### Deprecated Functions ######
    '''def received_constellation(self, demod_signal):
        self.samples_per_symbol = int(self.symbol_period*self.sampling_rate)
        delay = self.demodulator_total_delay
        t_axis = np.linspace(0, len(demod_signal)/self.sampling_rate, len(demod_signal), endpoint=False)
        t_samples = t_axis[delay::self.samples_per_symbol]
        demod_signal_samples = demod_signal[delay::self.samples_per_symbol]

        plt.figure()
        plt.scatter(demod_signal_samples.real, demod_signal_samples.imag)
        plt.title("Received Constellation")
        plt.xlabel("I")
        plt.ylabel("Q")
        plt.grid(True)'''

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
    plot_IQ = input("Plot I and Q components? (Y/N): ").upper() == 'Y'
    plot_constellation = input("Plot Constellation? (Y/N): ").upper() == 'Y'

    noise_lower_bound, noise_upper_bound = (int(i) for i in input("Enter the SNR range (lower_bound, upper_bound): ").split(','))
   

    file = input("Enter the file name/path: ")
    # Read the modulated signal
    fs, modulated = wav.read(file)

    for i in range(noise_lower_bound,noise_upper_bound+1):
        noisymodulatedsignal = SimpleGWNChannel_dB(i).add_noise(modulated)
        demodulator = Demodulator(mod_mode_select, bit_rate, fs/20, plot_IQ, plot_constellation)
        demodulated_signal = demodulator.demodulate(noisymodulatedsignal)
        demodulator.demod_and_plot(noisymodulatedsignal)
        demodulator.fig.suptitle(f"SNR = {i} dB")

    '''noisymodulatedsignal = SimpleGWNChannel_dB(-5).add_noise(modulated)

    demodulator = Demodulator(mod_mode_select, bit_rate, fs/20)
    demodulated_signal = demodulator.demodulate(noisymodulatedsignal)
    #demodulator.received_constellation(demodulated_signal)
    demodulator.plot(demodulated_signal)'''
    plt.show()

if __name__ == "__main__":
    main()
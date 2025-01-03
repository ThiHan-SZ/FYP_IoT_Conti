import numpy as np
import scipy.signal as sig
from scipy import spatial as spysp
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import commpy
import pickle
from ChannelClass import SimpleGWNChannel_dB, SimpleDelayChannel


class Demodulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
    
    def __init__(self, modulation_mode, bit_rate,carrier_freq, plot_IQ, plot_constellation) -> None:
       
        #Plot Parameters
        self.plot_IQ = plot_IQ
        self.plot_constellation = plot_constellation
        self.fig = plt.figure(constrained_layout=True) if self.plot_IQ or self.plot_constellation else None
        self.ax = self.plot_setup(self.fig) if self.plot_IQ or self.plot_constellation else None

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
        self.low_pass_filter_cutoff = 1.5*self.Nyquist_Bandwidth
        self.low_pass_filter_order = 77
        self.low_pass_delay = (self.low_pass_filter_order // 2) / self.sampling_rate
        self.low_pass_filter = self.low_pass_filter()

        self.demodulator_total_delay = None

    def downconverter(self, signal):
        t = np.linspace(0, len(signal)/self.sampling_rate, len(signal), endpoint=False)
        baseband_signal = signal * np.exp(-1j* 2 *np.pi * self.carrier_freq * t)
        I = baseband_signal.real
        Q = baseband_signal.imag
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

        baseband_signal_lp = I_lp + 1j*Q_lp
        RC_signal = sig.convolve(baseband_signal_lp, rrc) / np.sum(rrc**2) * 2 #Energy Normalization and 2x from trig identity

        #Scale the signal to original constellation

        match self.order:
            case 1:
                scaler = 2
            case 2:
                scaler = 1
            case _:
                scaler = (2/3*(2**(self.order)-1))**0.5

        RC_signal *= scaler

        self.demodulator_total_delay = int((2*RRC_delay + self.low_pass_delay) * self.sampling_rate)

        return RC_signal[:-(6*self.samples_per_symbol)]
    
    def demapping(self, demod_signal):
        I = demod_signal[self.demodulator_total_delay::self.samples_per_symbol].real
        Q = demod_signal[self.demodulator_total_delay::self.samples_per_symbol].imag

        bit_array = self.DesicionDemapper(I, Q)

        byte_chunks = [bit_array[i:i+8] for i in range(0, len(bit_array), 8)]

        byte_values = [int(''.join(map(str, chunk)), 2) for chunk in byte_chunks]

        byte_array = bytes(byte_values)

        try:
            text = byte_array.decode('utf-8')
        except:
            text = f"Decode Error Received : {''.join(map(str, bit_array))}"

        return text

    def DesicionDemapper(self, I, Q):
        '''
            I - Demodulated I-Component, in Symbols Array form
            Q - Demodulated Q-Component, in Symbols Array form
            
            Returns the Bitstream of the received signal
        '''
        bitstring = [None]

        if self.order == 1:
            bitstring = np.where(I > 0, 1, 0)
        elif self.order == 2:
            assert len(I) == len(Q), "I and Q must be of the same length"

            I_bits = np.where(I > 0, 1, 0)
            Q_bits = np.where(Q > 0, 1, 0)

            bitstring = np.zeros(len(I)*2, dtype=int)
            bitstring[0::2] = I_bits
            bitstring[1::2] = Q_bits 

        else:
            with open(rf'QAM_LUT_pkl\R{self.modulation_mode}.pkl', 'rb') as f:
                QAM_const = pickle.load(f)
            
            QAM_const_coord = [k for k in QAM_const.keys()]

            QAM_tree = spysp.KDTree(QAM_const_coord)

            coord = [QAM_const_coord[QAM_tree.query(i)[1]] for i in list(zip(I,Q))]

            bitstring = [list(QAM_const[tuple(i)]) for i in coord]

            bitstring = np.array(bitstring).flatten()

        return bitstring
    
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
        print(f"Demodulator delay: {self.demodulator_total_delay}")
        print(f"Signal length: {len(demod_signal)}, Sampling rate: {self.sampling_rate}")

        delay = self.demodulator_total_delay
        t_axis = np.linspace(0, len(demod_signal)/self.sampling_rate, len(demod_signal), endpoint=False)
        t_samples = t_axis[delay::self.samples_per_symbol]
        demod_signal_samples = demod_signal[delay::self.samples_per_symbol]

        if len(t_samples) == 0 or len(demod_signal_samples) == 0:
            print("Warning: No samples available for plotting.")
            return

        self.ax['Iplot'].plot(t_axis/self.symbol_period, demod_signal.real)
        self.ax['Iplot'].stem(t_samples/self.symbol_period, demod_signal_samples.real, linefmt='r', markerfmt='ro')
        self.ax['Iplot'].set_title("I-Component")
        self.ax['Iplot'].set_xlabel("Symbol Periods")
        self.ax['Iplot'].set_ylabel("Amplitude")
        self.ax['Iplot'].grid(True)

        self.ax['Qplot'].plot(t_axis/self.symbol_period, demod_signal.imag)
        self.ax['Qplot'].stem(t_samples/self.symbol_period, demod_signal_samples.imag, linefmt='r', markerfmt='ro')
        self.ax['Qplot'].set_title("Q-Component")
        self.ax['Qplot'].set_xlabel("Symbol Periods")
        self.ax['Qplot'].set_ylabel("Amplitude")
        self.ax['Qplot'].grid(True)


    def demod_and_plot(self, signal):
        demod_signal = self.demodulate(signal)
        if self.plot_IQ:
            self.plot(demod_signal)
        if self.plot_constellation:
            self.received_constellation(demod_signal)

    ###### Synchronizer Functions ######
    def  mu_mu_timing_recovery(self, signal):
        sps = int(self.symbol_period * self.sampling_rate)
        signal = sig.resample_poly(signal, 16, 1)

        mu = 0 # initial estimate of phase of sample
        out = np.zeros(len(signal) + 10, dtype=np.complex64)
        out_rail = np.zeros(len(signal) + 10, dtype=np.complex64) # stores values, each iteration we need the previous 2 values plus current value
        i_in = 0 # input samples index
        i_out = 2 # output index (let first two outputs be 0)
        while i_out < len(signal) and (i_in+16)*16 < len(signal):
            out[i_out] = signal[i_in*16 + int(mu*16)]
            out_rail[i_out] = int(np.real(out[i_out]) > 0) + 1j*int(np.imag(out[i_out]) > 0)
            x = (out_rail[i_out] - out_rail[i_out-2]) * np.conj(out[i_out-1])
            y = (out[i_out] - out[i_out-2]) * np.conj(out_rail[i_out-1])
            mm_val = np.real(y - x)
            mu += sps + 0.3*mm_val
            i_in += int(np.floor(mu)) # round down to nearest int since we are using it as an index
            mu = mu - np.floor(mu) # remove the integer part of mu
            i_out += 1 # increment output index
        out = out[3:i_out] # remove the first two, and anything after i_out (that was never filled out)
        out = sig.resample_poly(out, 1000, 1)[:-2]
        return out
    
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

    file = input("Enter the file name/path: ")
    # Read the modulated signal
    fs, modulated = wav.read(file)
    modulated *= 2

    '''demodulator = Demodulator(mod_mode_select, bit_rate, fs/20, plot_IQ, plot_constellation)
    demodulated_signal = demodulator.demodulate(modulated)
    text = demodulator.demapping(demodulated_signal)
    demodulator.demod_and_plot(modulated)
    demodulator.fig.suptitle("Received Signal")
    print(f'Received Message : {text}')'''

    '''
    noise_lower_bound, noise_upper_bound = 0, 0
    while True:
        try:
            noise_lower_bound, noise_upper_bound = (int(i) for i in input("Enter the SNR range (lower_bound, upper_bound): ").split(','))
            if noise_lower_bound > noise_upper_bound:
                print("Invalid SNR range. Please re-enter.")
            else:
                break
        except KeyboardInterrupt:
            exit()
        except:
            print("Invalid SNR range. Please re-enter.")

    for i in range(noise_lower_bound,noise_upper_bound+1):
        noisymodulatedsignal = SimpleGWNChannel_dB(i).add_noise(modulated)
        demodulator = Demodulator(mod_mode_select, bit_rate, fs/20, plot_IQ, plot_constellation)
        demodulated_signal = demodulator.demodulate(noisymodulatedsignal)
        text = demodulator.demapping(demodulated_signal)
        demodulator.demod_and_plot(noisymodulatedsignal)
        demodulator.fig.suptitle(f"SNR = {i} dB")
        print(f'Received Message : {text}')
    '''

    
    '''SNR = int(input("Enter the SNR in dB: ")) 
    noisymodulatedsignal = SimpleGWNChannel_dB(SNR).add_noise(modulated)
    
    demodulator = Demodulator(mod_mode_select, bit_rate, fs/20, plot_IQ, plot_constellation)
    demodulated_signal = demodulator.demodulate(noisymodulatedsignal)
    text = demodulator.demapping(demodulated_signal)
    demodulator.demod_and_plot(noisymodulatedsignal)
    demodulator.fig.suptitle("Received Signal")
    print(f'Received Message : {text}')
    '''

    DelayFactor = float(input("Enter the delay factor: "))
    delaymodulatedsignal = SimpleDelayChannel(DelayFactor).add_delay(modulated)
    
    demodulator = Demodulator(mod_mode_select, bit_rate, fs/20, plot_IQ, plot_constellation)

    mu_mu_signal = demodulator.mu_mu_timing_recovery(delaymodulatedsignal)

    demodulated_signal = demodulator.demodulate(mu_mu_signal)
    text = demodulator.demapping(demodulated_signal)
    demodulator.demod_and_plot(mu_mu_signal)
    demodulator.fig.suptitle("Received Signal")
    print(f'Received Message : {text}')
    
    
    plt.show()

if __name__ == "__main__":
    main()

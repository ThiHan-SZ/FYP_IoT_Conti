import numpy as np
import scipy.signal as sig
from scipy import spatial as spysp
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import commpy
import pickle


class Demodulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
    
    def __init__(self, modulation_mode, bit_rate, carrier_freq) -> None:
        #Demodulation Parameters
        self.carrier_freq = carrier_freq
        self.modulation_mode = modulation_mode
        self.order = self.modulation_modes[modulation_mode]
        self.demodulator_total_delay = None

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
        """
            Demodulates a signal to its baseband envelope.

            This function performs the following steps:
                1. Downconversion and low-pass filtering to extract in-phase (I) and quadrature (Q) components.
                2. Matched filtering using a root-raised-cosine (RRC) filter for optimal signal recovery.
                3. Energy normalization and scaling based on the modulation order.

            Parameters:
                signal (np.array): The input signal to be demodulated.

            Returns:
                np.array: The baseband envelope of the demodulated signal after processing, 
                truncated to remove delays introduced during filtering.
        """

        ##### Downconversion & Lowpassing #####
        I_base, Q_base = self.downconverter(signal)
        I_lp = sig.lfilter(self.low_pass_filter, 1, I_base)
        Q_lp = sig.lfilter(self.low_pass_filter, 1, Q_base)

        ##### Matched Filtering #####
        RRC_delay = 3*self.symbol_period
        _, rrc = commpy.filters.rrcosfilter(N=int(2*self.sampling_rate*RRC_delay),alpha=0.5,Ts=self.symbol_period, Fs=self.sampling_rate)

        baseband_signal_lp = I_lp + 1j*Q_lp
        RC_signal = sig.convolve(baseband_signal_lp, rrc) / np.sum(rrc**2) * 2 #Energy Normalization and 2x from trig identity

        
        ##### Scaling #####
        if self.order <= 2:
            scaler = 1
        else:
            scaler = (2/3*(2**(self.order)-1))**0.5
        
        RC_signal *= scaler

        self.demodulator_total_delay = int((2*RRC_delay + self.low_pass_delay) * self.sampling_rate)

        return RC_signal[:-(6*self.samples_per_symbol)]
    
    def demapping(self, demod_signal):
        """
            Converts a demodulated signal into text and its corresponding bit array.

            Parameters:
                demod_signal (np.array): The demodulated signal to be processed.

            Returns:
                tuple: 
                    - text (str): Decoded text from the demodulated signal. If decoding fails, 
                    an error message is returned.
                    - bit_array (np.array): The bit array extracted from the demodulated signal.
        """
        bit_array = self.DesicionDemapper(demod_signal)

        byte_chunks = [bit_array[i:i+8] for i in range(0, len(bit_array), 8)]

        byte_values = [int(''.join(map(str, chunk)), 2) for chunk in byte_chunks]

        byte_array = bytes(byte_values)

        try:
            text = byte_array.decode('utf-8')
        except:
            text = f"Decode Error Received : {''.join(map(str, bit_array))}"

        return text, bit_array

    def DesicionDemapper(self, demod_signal):
        """
            Maps the in-phase (I) and quadrature (Q) components of a signal to a bit array.

            Parameters:
                demod_signal (np.array): The input demodulated signal containing I and Q components.

            Returns:
                np.array: Bit array representing the demodulated signal.

            Notes:
                - For binary modulation (order=1), uses the polarity of the I component to determine bits.
                - For QPSK (order=2), uses both I and Q components.
                - For higher-order modulation, a precomputed lookup table (LUT) is used.
        """

        I = demod_signal[self.demodulator_total_delay::self.samples_per_symbol].real
        Q = demod_signal[self.demodulator_total_delay::self.samples_per_symbol].imag
        
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

        bitstring = [int(bit) for bit in bitstring]
        
        return bitstring
'''   
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
    
    def received_constellation(self, demod_signal):
        demod_signal_samples = demod_signal[self.demodulator_total_delay::self.samples_per_symbol]
        self.ax['ConstPlot'].scatter(demod_signal_samples.real, demod_signal_samples.imag)
        self.ax['ConstPlot'].set_title("Received Constellation")
        self.ax['ConstPlot'].set_xlabel("I")
        self.ax['ConstPlot'].set_ylabel("Q")
        self.ax['ConstPlot'].grid(True)
        scaler = ((2**(self.order/2))-1) if self.order > 2 else 1
        x_ticks = np.arange(-scaler, scaler+1, 2)
        y_ticks = np.arange(-scaler, scaler+1, 2)
        self.ax['ConstPlot'].set_xticks(x_ticks)
        self.ax['ConstPlot'].set_yticks(y_ticks)
        

    def demod_and_plot(self, signal):
        demod_signal = self.demodulate(signal)
        if self.plot_IQ:
            self.plot(demod_signal)
        if self.plot_constellation:
            self.received_constellation(demod_signal)
'''
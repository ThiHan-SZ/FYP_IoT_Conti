import numpy as np
import scipy.signal as sig
from scipy import spatial as spysp
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from .RRCFilter import RRCFilter
import pickle


class Demodulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
    def __init__(self, modulation_mode, baud_rate, sampling_rate) -> None: 
        """
        Demodulator Class Initializer

        Parameters:
            modulation_mode (str) : Modulation mode to be used for demodulation. Supported modes are BPSK, QPSK, QAM16, QAM64, QAM256, QAM1024, QAM4096
            baud_rate (float) : Baud rate of the signal to be demodulated
            sampling_rate (float) : Sampling rate of the signal to be demodulated
        """
        #Modulation Parameters
        self.modulation_mode = modulation_mode
        self.order = self.modulation_modes[modulation_mode]
        
        #Bit Rate Parameters
        self.baud_rate = baud_rate
        self.symbol_period = 1/self.baud_rate
        self.oversampling_factor = 10
        self.sampling_rate = sampling_rate
        self.samples_per_symbol = int(self.sampling_rate/self.baud_rate)
        
        #Demodulation Parameters
        self.carrier_freq = sampling_rate/(2*self.oversampling_factor)
        self.demodulator_total_delay = None

        #Filter Parameters
        self.Nyquist_Bandwidth = 1/(2*self.symbol_period)
        self.low_pass_filter_cutoff = 0.9*self.Nyquist_Bandwidth
        self.low_pass_filter_order = 77
        self.low_pass_delay = (self.low_pass_filter_order // 2) / self.sampling_rate
        self.low_pass_filter = self.low_pass_filter()

        #Plotting Parameters
        self.plot_IQ = False
        self.plot_constellation = False
        self.plot_EyeDiagram = False
        self.fig = plt.figure('Demodulator', constrained_layout=True)
        self.ax = None
        
        #RRC Filter Parameters
        self.RRC_alpha = 0.35
    @staticmethod
    def readfile(filename):
        '''
        Reads a .wav file and returns its sample rate and data.
        
        Parameters:
            filename (str): The name of the .wav file to be read.
        
        Returns:
            tuple: A tuple containing the sample rate of the .wav file and its data.
        '''
        rate, data = wav.read(filename)
        # Data * 2 to remove storage halving.
        return rate, data * 2
    
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
                np.array: The baseband envelope of the demodulated signal after processing.
        """

        ##### Downconversion & Lowpassing #####
        I_base, Q_base = self.downconverter(signal)
        I_lp = sig.lfilter(self.low_pass_filter, 1, I_base)
        Q_lp = sig.lfilter(self.low_pass_filter, 1, Q_base)

        ##### Matched Filtering #####
        RRC_delay = 3*self.symbol_period
        _, rrc = RRCFilter(
            N=int(2*self.sampling_rate*RRC_delay),
            alpha=self.RRC_alpha,
            Ts=self.symbol_period, 
            Fs=self.sampling_rate
        )

        baseband_signal_lp = I_lp + 1j*Q_lp
        RC_signal = sig.fftconvolve(baseband_signal_lp, rrc) / np.sum(rrc**2) * 2 #Energy Normalization and 2x from trig identity

        
        ##### Scaling #####
        if self.order <= 2:
            scaler = 1
        else:
            scaler = (2/3*(2**(self.order)-1))**0.5
        
        RC_signal *= scaler

        self.demodulator_total_delay = int((2*RRC_delay + self.low_pass_delay) * self.sampling_rate)

        return RC_signal
        
    
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
        bit_array = self.decision_demapper(demod_signal[:-(6*self.samples_per_symbol)])

        byte_chunks = [bit_array[i:i+8] for i in range(0, len(bit_array), 8)]

        byte_values = [int(''.join(map(str, chunk)), 2) for chunk in byte_chunks]

        byte_array = bytes(byte_values)

        try:
            text = byte_array.decode('utf-8')
        except:
            text = f"Decode Error Received : {''.join(map(str, bit_array))}"

        return text, bit_array

    def decision_demapper(self, demodulated_signal: np.ndarray) -> np.ndarray:
        """Maps the in-phase (I) and quadrature (Q) components of a signal to a bit array.

        Parameters:
            demodulated_signal (np.ndarray): The input demodulated signal containing I and Q components.

        Returns:
            np.ndarray: Bit array representing the demodulated signal.
        """

        i_samples = demodulated_signal[self.demodulator_total_delay::self.samples_per_symbol].real
        q_samples = demodulated_signal[self.demodulator_total_delay::self.samples_per_symbol].imag

        bit_array = np.zeros(len(i_samples) * self.order, dtype=int)

        if self.order == 1:
            bit_array[:] = np.where(i_samples > 0, 1, 0)
        elif self.order == 2:
            i_bits = np.where(i_samples > 0, 1, 0)
            q_bits = np.where(q_samples > 0, 1, 0)

            bit_array[0::2] = i_bits
            bit_array[1::2] = q_bits
        else:
            with open(rf'FYP_NextGenIoT_Simulator/QAM_LUT_pkl/R{self.modulation_mode}.pkl', 'rb') as file:
                qam_const = pickle.load(file)

            qam_tree = spysp.KDTree([k for k in qam_const.keys()])
            coord = qam_tree.query(list(zip(i_samples, q_samples)))[1]

            bit_array[:] = np.array([list(qam_const[tuple(qam_tree.data[i])]) for i in coord]).flatten()

        return bit_array
    
    #### Plotting Functions ####    
    def plot_setup(self, fig):
        """
        Configures and returns a dictionary of plot axes based on the plotting flags set in the object.

        Parameters:
            fig (matplotlib.figure.Figure): The figure object to which the plots will be added.

        Returns:
            Dict: An dictionary containing the axes for the plots. Keys are 'Iplot', 'Qplot', and 'ConstPlot' 
                depending on the plotting configuration. Returns None if no plots are to be generated.

        The function sets up subplots in the provided figure based on the modulation mode and plotting flags:
        - If both Eye Diagram and Constellation plots are enabled:
            - For non-BPSK modulation modes, creates a grid with 3 rows and 2 columns for I, Q, and Constellation plots.
            - For BPSK modulation, creates a grid with a single row for I and Constellation plots.
        - If only Eye Diagram plots are enabled:
            - For non-BPSK modulation modes, creates a grid with 1 row and 2 columns for I and Q plots.
            - For BPSK modulation, creates a grid with a single row for the I plot.
        - If both IQ and Constellation plots are enabled, creates a similar configuration as Eye Diagram and Constellation.
        - If only IQ plots are enabled, creates a grid for I and Q plots.
        - If only Constellation plots are enabled, creates a grid for the Constellation plot.
        - Closes all figures and returns None if no plots are enabled.
        """
        axes = {}
        if self.plot_EyeDiagram and self.plot_constellation: #If EyeDiagram and Constellation are both True
            if self.modulation_mode != 'BPSK':
                gridspec = fig.add_gridspec(nrows=3, ncols=2)
                axes['Iplot'] = fig.add_subplot(gridspec[0, 0])
                axes['Qplot'] = fig.add_subplot(gridspec[0, 1])
                axes['ConstPlot'] = fig.add_subplot(gridspec[1:, :])
            else:
                gridspec = fig.add_gridspec(nrows=2, ncols=1)
                axes['Iplot'] = fig.add_subplot(gridspec[0, 0])
                axes['ConstPlot'] = fig.add_subplot(gridspec[1:, :])
        elif self.plot_EyeDiagram: #If EyeDiagram is True
            if self.modulation_mode != 'BPSK':
                gridspec = fig.add_gridspec(nrows=1, ncols=2)
                axes['Iplot'] = fig.add_subplot(gridspec[0, 0])
                axes['Qplot'] = fig.add_subplot(gridspec[0, 1])
            else:
                gridspec = fig.add_gridspec(nrows=1, ncols=1)
                axes['Iplot'] = fig.add_subplot(gridspec[0, 0])
        elif self.plot_IQ and self.plot_constellation:
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
        else:
            plt.close('all')
            return None
        return axes

    def received_IQ(self, demod_signal):
        delay = self.demodulator_total_delay
        t_axis = np.linspace(0, len(demod_signal)/self.sampling_rate, len(demod_signal), endpoint=False)
        t_samples = t_axis[delay:-(6*self.samples_per_symbol):self.samples_per_symbol]
        demod_signal_samples = demod_signal[delay:-(6*self.samples_per_symbol):self.samples_per_symbol]

        self.ax['Iplot'].plot(t_axis/self.symbol_period, demod_signal.real)
        self.ax['Iplot'].stem(t_samples/self.symbol_period, demod_signal_samples.real, linefmt='r', markerfmt='ro')
        self.ax['Iplot'].set_title("I-Component")
        self.ax['Iplot'].set_xlabel("Symbol Periods (s)")
        self.ax['Iplot'].set_ylabel("Amplitude")
        self.ax['Iplot'].grid(True)

        self.ax['Qplot'].plot(t_axis/self.symbol_period, demod_signal.imag)
        self.ax['Qplot'].stem(t_samples/self.symbol_period, demod_signal_samples.imag, linefmt='r', markerfmt='ro')
        self.ax['Qplot'].set_title("Q-Component")
        self.ax['Qplot'].set_xlabel("Symbol Periods (s)")
        self.ax['Qplot'].set_ylabel("Amplitude")
        self.ax['Qplot'].grid(True)
    
    def received_constellation(self, demod_signal):
        demod_signal = demod_signal[:-(6*self.samples_per_symbol)]
        demod_signal_samples = demod_signal[self.demodulator_total_delay::self.samples_per_symbol]
        self.ax['ConstPlot'].scatter(demod_signal_samples.real, demod_signal_samples.imag,xunits='V', yunits='V')
        self.ax['ConstPlot'].set_title("Received Constellation")
        self.ax['ConstPlot'].set_xlabel("I")
        self.ax['ConstPlot'].set_ylabel("Q")
        self.ax['ConstPlot'].grid(True)
        scaler = ((2**(self.order/2))-1) if self.order > 2 else 1
        x_ticks = np.arange(-scaler, scaler+1, 2)
        y_ticks = np.arange(-scaler, scaler+1, 2)
        self.ax['ConstPlot'].set_xticks(x_ticks)
        self.ax['ConstPlot'].set_yticks(y_ticks)
    
    def eye_diagram(self, demod_signal):
        demod_signal_samples = demod_signal[self.demodulator_total_delay:-6*self.samples_per_symbol:self.samples_per_symbol]
        i_samples = []
        q_samples = []
        BitLen = len(demod_signal_samples)
        for i in range(BitLen - 2):
            i_samples.append(demod_signal[self.demodulator_total_delay + self.samples_per_symbol * i + np.arange(2 * self.samples_per_symbol)].real)
            if self.modulation_mode != 'BPSK':
                q_samples.append(demod_signal[self.demodulator_total_delay + self.samples_per_symbol * i + np.arange(2 * self.samples_per_symbol)].imag)

        i_samples = np.array(i_samples).T
        q_samples = np.array(q_samples).T if self.modulation_mode != 'BPSK' else None
        time_axis = np.linspace(-self.symbol_period, self.symbol_period, 2 * self.samples_per_symbol)
        if self.modulation_mode != 'BPSK':
            self.ax['Iplot'].plot(time_axis, i_samples, color='r',xunits='s', yunits='V')
            self.ax['Qplot'].plot(time_axis, q_samples, color='b',xunits='s', yunits='V')
            self.ax['Iplot'].set_title("I-Component")
            self.ax['Qplot'].set_title("Q-Component")
            self.ax['Iplot'].set_xlabel("Time (s)")
            self.ax['Qplot'].set_xlabel("Time (s)")
            self.ax['Iplot'].set_ylabel("Amplitude")
            self.ax['Qplot'].set_ylabel("Amplitude")
        else:
            self.ax['Iplot'].plot(time_axis, i_samples, color='r',xunits='s', yunits='V')
            self.ax['Iplot'].set_title("I-Component")
            self.ax['Iplot'].set_xlabel("Time (s)")
            self.ax['Iplot'].set_ylabel("Amplitude")
        
    def auto_plot(self, demod_signal):
        """
        Automatically plots the IQ components and/or the received constellation.

        Args:
            demod_signal (np.array): The demodulated signal.
            
        ### To extract figure, use self.fig 
        """
        if self.plot_IQ and not self.plot_EyeDiagram:
            self.received_IQ(demod_signal)
        if self.plot_constellation:
            self.received_constellation(demod_signal)
        if self.plot_EyeDiagram:
            self.eye_diagram(demod_signal)
        
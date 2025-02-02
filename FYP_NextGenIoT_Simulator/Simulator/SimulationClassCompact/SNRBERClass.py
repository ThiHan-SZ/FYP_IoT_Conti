from matplotlib import pyplot as plt
from SimulationClassCompact.ModulationClass import Modulator
from SimulationClassCompact.DemodulationClass import Demodulator
from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB as AWGN

from numpy import array,arange

class SNRBERTest:
    def __init__(self,selected_modes,bit_rate,carrier_freq,snr_up,snr_down,seed):
        """
        Initialize the SNRBERTest object.

        Parameters
        ----------
        selected_modes : list of str
            List of modulation modes to be tested. Must be in {'BPSK', 'QPSK', 'QAM16', 'QAM64', 'QAM256', 'QAM1024', 'QAM4096'}.
        bit_rate : int
            Bit rate of the signal.
        carrier_freq : int
            Carrier frequency of the signal.
        snr_up : int
            Upper limit of the SNR test range (dB).
        snr_down : int
            Lower limit of the SNR test range (dB).
        seed : int
            Seed for the AWGN channel.

        Attributes
        ----------
        selected_modes : list of str
            List of modulation modes to be tested.
        modulators : dict of Modulator
            Dictionary of Modulator objects for each modulation mode.
        demodulators : dict of Demodulator
            Dictionary of Demodulator objects for each modulation mode.
        snr_test_range : numpy array of int
            Array of SNR values to be tested (dB).
        channels : dict of AWGN
            Dictionary of AWGN channel objects for each SNR value.
        modulated_signals : dict of tuple of numpy array
            Dictionary of modulated signals for each modulation mode.
        ber_dict : dict of list of float
            Dictionary of BER values for each modulation mode.
        fig : matplotlib figure
            Figure to plot the BER vs SNR.
        ax : matplotlib axis
            Axis to plot the BER vs SNR.
        """
        self.selected_modes = selected_modes
        self.modulators = {mode: Modulator(mode, bit_rate, carrier_freq) for mode in selected_modes}
        self.demodulators = {mode: Demodulator(mode, bit_rate, self.modulators[mode].sampling_rate) for mode in selected_modes}
        self.snr_test_range = arange(snr_down, snr_up + 1)
        self.channels = {snr: AWGN(snr, seed=seed) for snr in self.snr_test_range}
        
        self.modulated_signals = {mode: (None, None) for mode in selected_modes}
        self.ber_dict = {mode: [] for mode in selected_modes}
        
        self.fig, self.ax = plt.subplots(1, 1)
        
    def __simulateSNRBER(self,message):
        comparison_string = array([int(bit) for bit in Modulator.msgchar2bit_static(message)])
        
        for mode in self.selected_modes:
            modulator = self.modulators[mode]
            demodulator = self.demodulators[mode]
            
            bit_string = modulator.msgchar2bit(message)
            time_axis, modulated_signal = modulator.modulate(bit_string)
            self.modulated_signals[mode] = (time_axis, modulated_signal)
            
            for snr in self.snr_test_range:
                channel = self.channels[snr]
                noisy_signal = channel.add_noise(modulated_signal)
                demodulated_signal = demodulator.demodulate(noisy_signal)
                demodulated_bits = demodulator.demapping(demodulated_signal)[1][:-2]
                error_bits = sum(abs(comparison_string - demodulated_bits))
                self.ber_dict[mode].append(error_bits / len(bit_string))
                
    def plotSNRBER(self,message):
        """
        Plots the BER against SNR for the given message.

        Parameters
        ----------
        message : str
            The message to simulate.

        Returns
        -------
        fig : matplotlib.figure.Figure
            The figure object of the BER vs SNR plot.
        """
        self.__simulateSNRBER(message)
        
        # Scales and tickers
        self.ax.set_yscale('symlog', linthresh=1e-5)
        ticks = [0, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1]
        self.ax.set_yticks(ticks)
        
        # Grid
        self.ax.grid(which="both", linestyle="--", linewidth=0.5)
        
        # Major tickers
        from matplotlib.ticker import MultipleLocator; self.ax.xaxis.set_major_locator(MultipleLocator(1))
        
        colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'black']
        markers = ['o', 's', '^', 'v', '<', '>', 'd']

        for modulation_type, color, marker in zip(self.selected_modes, colors, markers):
            self.ax.plot(self.snr_test_range, self.ber_dict[modulation_type], label=modulation_type, color=color, marker=marker)
        
        self.ax.set_xlabel('SNR (dB)')
        self.ax.set_ylabel('BER')
        self.ax.set_title('BER vs SNR')
        self.ax.legend()
        
        return self.fig
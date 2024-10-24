from matplotlib import pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import math
import pickle
from dataclasses import dataclass , field



@dataclass
class Modulator:
    mod_mode = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
    
    input_msg: str = "Hello World!"
    carrier_freq: int = 10
    mod_mode_select: str = 'BPSK'

    def __post_init__(self):
        self.period = 1 / self.carrier_freq
        self.Sampling_Rate = 44100 #Sampling rate
        self.Sample_Time = self.period / self.Sampling_Rate # Time step between samples
        self.symbol_rate = self.mod_mode[self.mod_mode_select]
        self.show_modulation = False
        self.fileout =  None if input("Do you want to save the plot? (Y/N): ").upper() != 'Y' else input("Enter the file name: ")

    def generate_wave(self, wave_type='cos'):
        """Precomputes cosine or sine wave for carrier frequency."""
        t = np.arange(0, self.period, self.Sample_Time)
        return np.cos(2 * np.pi * self.carrier_freq * t) if wave_type == 'cos' else np.sin(2 * np.pi * self.carrier_freq * t)

    def generate_signals(self):
        graphtime, bitstr = self.user_char_to_bitstream()
        digital_transmission = self.digital_signal(bitstr)

        if self.mod_mode[self.mod_mode_select] != 1:
            self.show_modulation = input("Do you want to see the consituent sub-carriers? (Y/N): ").upper() == 'Y'
        if self.show_modulation:
            modulated, I, Q = self.modulate(bitstr)
        else:
            modulated = self.modulate(bitstr)

        # Pad to match graphtime length
        pad_len_mod = len(graphtime) - len(modulated)
        modulated = np.pad(modulated, (0, pad_len_mod), 'constant',constant_values=(0,0))
        I = np.pad(I, (0, pad_len_mod), 'constant',constant_values=(0,0)) if self.show_modulation else None
        Q = np.pad(Q, (0, pad_len_mod), 'constant',constant_values=(0,0)) if self.show_modulation else None

        pad_len_digi = len(graphtime) - len(digital_transmission)
        digital_transmission = np.pad(digital_transmission, (0, pad_len_digi), 'constant',constant_values=(0,0))
        return graphtime, digital_transmission, modulated, I, Q

    def modulate(self, bitstream):
        """Selects the correct modulation based on mode."""
        if self.mod_mode_select == 'BPSK':
            return self.bpsk_modulation(bitstream)
        elif self.mod_mode_select == 'QPSK':
            return self.qpsk_modulation(bitstream)
        else:
            return self.qam_modulation(bitstream)

    def user_char_to_bitstream(self):
        """Converts input string to a bit stream."""
        bitstring = ''.join(f'{byte:08b}' for byte in self.input_msg.encode('utf-8'))
        bit_period = self.period / self.symbol_rate
        graph_time = np.arange(0, math.ceil(len(bitstring)/10)*10*bit_period + self.Sample_Time, self.Sample_Time)
        return graph_time, bitstring

    def digital_signal(self, bitstream):
        """Generates digital signal from bitstream, adjusted with the symbol rate."""
        symbol_duration = self.period / self.symbol_rate  # Duration of each symbol
        samples_per_symbol = math.floor(symbol_duration / self.Sample_Time)  # Samples per symbol

        # Create the digital signal using np.repeat
        signal = np.concatenate([
            np.repeat(int(bit), samples_per_symbol) for bit in bitstream
        ])
        
        return signal

    def bpsk_modulation(self, bitstream):
        """BPSK modulation."""
        wave_cos = self.generate_wave('cos')
        return np.array([(2 * int(b) - 1) * wave_cos for b in bitstream]).flatten()

    def qpsk_modulation(self, bitstream):
        """QPSK modulation."""
        assert len(bitstream) % 2 == 0, "QPSK requires even number of bits."
        wave_cos, wave_sin = self.generate_wave('cos'), self.generate_wave('sin')
        bit_groups = [bitstream[i:i + 2] for i in range(0, len(bitstream), 2)]
        I = np.array([(2 * int(b[0]) - 1) * wave_cos for b in bit_groups]).flatten()
        Q = np.array([(2 * int(b[1]) - 1) * wave_sin for b in bit_groups]).flatten()
        if self.show_modulation:
            return I + Q, I, Q
        return I + Q

    def qam_modulation(self, bitstream):
        """Handles generic QAM modulation."""
        qam_order = self.mod_mode[self.mod_mode_select]
        assert len(bitstream) % qam_order == 0, f"{self.mod_mode_select} requires symbol size {qam_order}. Got {len(bitstream)} bits."

        with open(rf'QAM_LUT_pkl\{self.mod_mode_select}.pkl', 'rb') as f:
            qam_map = pickle.load(f)

        wave_cos, wave_sin = self.generate_wave('cos'), self.generate_wave('sin')
        bit_groups = [bitstream[i:i + qam_order] for i in range(0, len(bitstream), qam_order)]
        
        I = np.array([qam_map[group]['I'] * wave_cos for group in bit_groups]).flatten()
        Q = np.array([qam_map[group]['Q'] * wave_sin for group in bit_groups]).flatten()
        
        if self.show_modulation:
            return I + Q, I, Q
        
        return I + Q
    
    def modulated_plot(self):
        """Plots digital and modulated signals."""

        # Generate signals
        graphtime, digitaltransmission, modulated, I, Q = self.generate_signals()

        if self.fileout != None:
            amplitude_scaler = 1 if self.mod_mode_select == 'BPSK' or self.mod_mode_select == 'QPSK' else math.sqrt(2) * (2**(self.mod_mode[self.mod_mode_select] / 2) - 1)
            '''
                Scale modulated signal to fit within -1 to 1 range for saving to .wav file 
                QPSK and BPSK are scaled to 1
                QAM signals are scaled to 2^(n/2) - 1 where n is the number of bits per symbol
            '''
            scaled_modulated = modulated / amplitude_scaler

            wav.write(self.fileout + '.wav', self.Sampling_Rate, scaled_modulated[::self.carrier_freq//self.Sampling_Rate])
            

        # Determine the number of subplots based on the show_modulation flag
        num_subplots = 3 if self.show_modulation else 2
        fig, ax = plt.subplots(num_subplots, 1, constrained_layout=True)

        # Plot the digital signal (First subplot, always present)
        ax[0].plot(graphtime, digitaltransmission)
        ax[0].set_title("Digital Signal")
        ax[0].set_ylabel("Amplitude")
        ax[0].vlines(
            graphtime[::int(self.period / self.Sample_Time)], 
            -0.5, 1.5, 
            colors='r', linestyles='dashed', alpha=0.5
        )

        if self.show_modulation:
            # Plot In-Phase and Quadrature components (Second subplot)
            ax[1].set_title("Sub-Carriers")
            ax[1].set_ylabel("Amplitude")
            ax[1].plot(graphtime, I, label="In-Phase", color='g', alpha=0.75)
            ax[1].plot(graphtime, Q, label="Quadrature", color='b', alpha=0.75)
            ax[1].set_xticks([])
            ax[1].vlines(
                graphtime[::int(self.period / self.Sample_Time)], 
                -1 * (max(modulated)) - 0.5, max(modulated) + 0.5, 
                colors='r', linestyles='dashed', alpha=0.5
            )
            ax[1].legend(
                loc='upper right', 
                bbox_to_anchor=(1, -0.05),  # Below the plot, aligned right
                borderaxespad=0.0, 
                ncol=1
            )

            # Plot the modulated signal (Third subplot)
            ax[2].plot(graphtime, modulated)
            ax[2].set_title(f'Modulated Signal: {self.mod_mode_select}')
            ax[2].set_ylabel("Amplitude")
            ax[2].set_xlabel("Time (s)")
            ax[2].vlines(
                graphtime[::int(self.period / self.Sample_Time)], 
                -1 * (max(modulated)) - 0.5, max(modulated) + 0.5, 
                colors='r', linestyles='dashed', alpha=0.5
            )

        else:
            # Plot the modulated signal directly if no modulation subplot
            ax[1].plot(graphtime, modulated)
            ax[1].set_title(f'Modulated Signal: {self.mod_mode_select}')
            ax[1].set_ylabel("Amplitude")
            ax[1].set_xlabel("Time (s)")
            ax[1].vlines(
                graphtime[::int(self.period / self.Sample_Time)], 
                -1 * (max(modulated)) - 0.5, max(modulated) + 0.5, 
                colors='r', linestyles='dashed', alpha=0.5
            )

        # Display the plot
        plt.show()


if __name__ == "__main__":
    input_message = input("Enter the message to be transmitted: ") or "Hello World!"
    carrier_freq = int(input("Enter the carrier frequency: ") or 10)

    with open(rf'55kb.txt', 'rb') as f:
        text = f.read().decode('utf-8')

    input_message = text

    while True:
        mod_mode_select = input("Enter the modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
        if mod_mode_select in Modulator.mod_mode:
            break
        print("Invalid modulation mode. Please reselect.")
    modulator = Modulator(input_message, carrier_freq, mod_mode_select)
    modulator.modulated_plot()
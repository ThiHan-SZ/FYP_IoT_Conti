from matplotlib import pyplot as plt
import numpy as np
import math
import pickle
from dataclasses import dataclass

mod_mode = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
transmit_carrier_freq = 10

@dataclass
class Modulator:
    input: str = "Hello World!"
    carrier_freq: float = transmit_carrier_freq
    mod_mode_select: str = 'BPSK'

    def __post_init__(self):
        self.period = 1 / self.carrier_freq
        self.Sampling_Rate = self.period / 96000 #Sampling rate
        self.symbol_rate = mod_mode[self.mod_mode_select]

    def generate_wave(self, wave_type='cos'):
        """Precomputes cosine or sine wave for carrier frequency."""
        t = np.arange(0, self.period, self.Sampling_Rate)
        return np.cos(2 * np.pi * self.carrier_freq * t) if wave_type == 'cos' else np.sin(2 * np.pi * self.carrier_freq * t)

    def generate_signals(self):
        graphtime, bitstr = self.user_char_to_bitstream()
        digital_transmission = self.digital_signal(bitstr)
        modulated = self.modulate(bitstr)

        # Pad to match graphtime length
        pad_len_mod = len(graphtime) - len(modulated)
        modulated = np.pad(modulated, (0, pad_len_mod), 'constant',constant_values=(0,0))
        pad_len_digi = len(graphtime) - len(digital_transmission)
        digital_transmission = np.pad(digital_transmission, (0, pad_len_digi), 'constant',constant_values=(0,0))

        return graphtime, digital_transmission, modulated

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
        bitstring = ''.join(f'{byte:08b}' for byte in self.input.encode('utf-8'))
        bit_period = self.period / self.symbol_rate
        graph_time = np.arange(0, math.ceil(len(bitstring)/10)*10*bit_period + self.Sampling_Rate, self.Sampling_Rate)
        return graph_time, bitstring

    def digital_signal(self, bitstream):
        """Generates digital signal from bitstream, adjusted with the symbol rate."""
        symbol_duration = self.period / self.symbol_rate  # Duration of each symbol
        samples_per_symbol = math.floor(symbol_duration / self.Sampling_Rate)  # Samples per symbol

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
        in_phase = bitstream[0::2]
        quadrature = bitstream[1::2]
        return np.array([
            (np.sqrt(0.5) * (2 * int(i) - 1) * wave_cos +
             np.sqrt(0.5) * (2 * int(q) - 1) * wave_sin)
            for i, q in zip(in_phase, quadrature)
        ]).flatten()

    def qam_modulation(self, bitstream):
        """Handles generic QAM modulation."""
        qam_order = mod_mode[self.mod_mode_select]
        assert len(bitstream) % qam_order == 0, f"{self.mod_mode_select} requires symbol size {qam_order}."

        with open(rf'QAM_LUT_pkl\{self.mod_mode_select}.pkl', 'rb') as f:
            qam_map = pickle.load(f)

        wave_cos, wave_sin = self.generate_wave('cos'), self.generate_wave('sin')
        bit_groups = [bitstream[i:i + qam_order] for i in range(0, len(bitstream), qam_order)]
        return np.array([
            (qam_map[group]['I'] * wave_cos + qam_map[group]['Q'] * wave_sin)
            for group in bit_groups
        ]).flatten()

    def modulated_plot(self):
        """Plots digital and modulated signals."""
        graphtime, digitaltransmission, modulated = self.generate_signals()

        fig, (ax1, ax2) = plt.subplots(2, 1, constrained_layout=True)
        ax1.plot(graphtime, digitaltransmission)
        ax1.set_title("Digital Signal")
        ax1.set_ylabel("Amplitude")
        ax1.vlines(graphtime[::int(self.period / self.Sampling_Rate)], -0.5, 1.5, colors='r', linestyles='dashed', alpha=0.5)

        ax2.plot(graphtime, modulated)
        ax2.set_title(f'Modulated Signal: {self.mod_mode_select}')
        ax2.set_ylabel("Amplitude")
        ax2.vlines(graphtime[::int(self.period / self.Sampling_Rate)], -1*(max(modulated))-0.5, max(modulated)+0.5, colors='r', linestyles='dashed', alpha=0.5)
        ax2.set_xlabel("Time (s)")
        plt.show()


if __name__ == "__main__":
    input_message = input("Enter the message to be transmitted: ") or "Hello World!"
    carrier_freq = float(input("Enter the carrier frequency: ") or transmit_carrier_freq)

    while True:
        mod_mode_select = input("Enter the modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
        if mod_mode_select in mod_mode:
            break
        print("Invalid modulation mode. Please reselect.")

    modulator = Modulator(input_message, carrier_freq, mod_mode_select)
    modulator.modulated_plot()

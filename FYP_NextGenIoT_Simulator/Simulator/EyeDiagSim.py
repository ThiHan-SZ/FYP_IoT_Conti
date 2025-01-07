import numpy as np
import matplotlib.pyplot as plt

from SimulationClassCompact.ModulationClass import Modulator
from SimulationClassCompact.DemodulationClass import Demodulator
from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB


def main():
    modulation_mode = input("Enter modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
    bit_rate = int(input("Enter bit rate: "))
    carrier_frequency = int(input("Enter carrier frequency: "))

    modulator = Modulator(modulation_mode, bit_rate, carrier_frequency)
    demodulator = Demodulator(modulation_mode, bit_rate, carrier_frequency)

    with open('FYP_NextGenIoT_Simulator/TestcaseFiles/TinySpeare.txt', 'r') as file:
        message = file.read()[:5000]

    bitstream = modulator.msgchar2bit(message)

    modulator.IQ_Return = False

    _, modulated_signal = modulator.modulate(bitstream)

    channel = SimpleGWNChannel_dB(10)
    noisy_modulated = channel.add_noise(modulated_signal)

    demodulated_signal = demodulator.demodulate(noisy_modulated)

    samples_per_symbol = demodulator.samples_per_symbol
    symbol_period = demodulator.symbol_period
    delay = demodulator.demodulator_total_delay
    order = demodulator.order

    def plot_eye_diagram(signal):
        i_samples = []
        q_samples = []
        for i in range(int(len(bitstream) / order) - 2):
            i_samples.append(signal[delay + samples_per_symbol * i + np.arange(2 * samples_per_symbol)].real)
            if modulation_mode != 'BPSK':
                q_samples.append(signal[delay + samples_per_symbol * i + np.arange(2 * samples_per_symbol)].imag)

        i_samples = np.array(i_samples).T
        q_samples = np.array(q_samples).T if modulation_mode != 'BPSK' else None
        time_axis = np.linspace(-symbol_period, symbol_period, 2 * samples_per_symbol)
        if modulation_mode != 'BPSK':
            plt.close('all')  # Close all previous figures
            fig, ax = plt.subplots(2, 1, constrained_layout=True)
            ax[0].plot(time_axis, i_samples, color='r')
            ax[1].plot(time_axis, q_samples, color='b')
        else:
            plt.close('all')  # Close all previous figures
            fig, ax = plt.subplots(1, 1, constrained_layout=True)
            ax.plot(time_axis, i_samples, color='r')
        fig.suptitle("Eye Diagram")
        
    plot_eye_diagram(demodulated_signal)
    plt.show()


if __name__ == '__main__':
    main()

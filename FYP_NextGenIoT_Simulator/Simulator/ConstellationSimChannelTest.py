import numpy as np
import matplotlib.pyplot as plt

from SimulationClassCompact.ModulationClass import Modulator
from SimulationClassCompact.DemodulationClass import Demodulator
from SimulationClassCompact.ChannelClass import *
 
def multiplot_received_constellation(demod_signal, order, samples_per_symbol, delay):
    fig, ax = plt.subplots()
    demod_signal_samples = demod_signal[delay:-6*samples_per_symbol:samples_per_symbol]
    ax.scatter(demod_signal_samples.real, demod_signal_samples.imag)
    ax.set_title("Received Constellation")
    ax.set_xlabel("I")
    ax.set_ylabel("Q")
    ax.grid(True)
    scaler = ((2**(order/2))-1) if order > 2 else 1
    x_ticks = np.arange(-scaler, scaler+1, 2)
    y_ticks = np.arange(-scaler, scaler+1, 2) if order > 2 else np.arange(-1, 2, 1)
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)

def received_constellation(demod_signal, order, samples_per_symbol, delay):
    demod_signal_samples = demod_signal[delay:-6*samples_per_symbol:samples_per_symbol]
    plt.scatter(demod_signal_samples.real, demod_signal_samples.imag)
    plt.title("Received Constellation")
    plt.xlabel("I")
    plt.ylabel("Q")
    plt.grid(True)
    scaler = ((2**(order/2))-1) if order > 2 else 1
    x_ticks = np.arange(-scaler, scaler+1, 2)
    y_ticks = np.arange(-scaler, scaler+1, 2) if order > 2 else np.arange(-1, 2, 1)
    plt.xticks(x_ticks)
    plt.yticks(y_ticks)
    
def main():
    modulation_mode = input("Enter modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
    bit_rate = int(input("Enter bit rate: "))
    carrier_frequency = int(input("Enter carrier frequency: "))

    modulator = Modulator(modulation_mode, bit_rate, carrier_frequency)
    demodulator = Demodulator(modulation_mode, bit_rate, carrier_frequency)

    with open('FYP_NextGenIoT_Simulator/TestcaseFiles/TinySpeare.txt', 'r') as file:
        message = file.read()[:500]

    bitstream = modulator.msgchar2bit(message)

    modulator.IQ_Return = False


    _, modulated_signal = modulator.modulate(bitstream)

    '''delays = np.linspace(-0.5, 0.5, 11, endpoint=True)
    for delay in delays:
        channel2 = SimpleFrequencyDriftChannel(0.03)
        channel3 = SimpleGWNChannel_dB(10)
        noisy_modulated = channel2.add_drift(modulated_signal)
        noisy_modulated = channel3.add_noise(noisy_modulated)

        demodulated_signal = demodulator.demodulate(noisy_modulated)

        samples_per_symbol = demodulator.samples_per_symbol
        symbol_period = demodulator.symbol_period
        delay = demodulator.demodulator_total_delay
        order = demodulator.order

        received_constellation(demodulated_signal, order, samples_per_symbol, delay)
    
    plt.legend(delays, title="Delay (fractions)")'''
    channel = SimpleFlatFadingChannel('rayleigh')
    noisy_modulated = channel.add_fading(modulated_signal)

    demodulated_signal = demodulator.demodulate(noisy_modulated)

    samples_per_symbol = demodulator.samples_per_symbol
    symbol_period = demodulator.symbol_period
    delay = demodulator.demodulator_total_delay
    order = demodulator.order

    received_constellation(demodulated_signal, order, samples_per_symbol, delay)

    plt.show()

if __name__ == '__main__':
    main()
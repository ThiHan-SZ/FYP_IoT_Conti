import numpy as np
import matplotlib.pyplot as plt

from SimulationClassCompact.ModulationClass import Modulator
from SimulationClassCompact.DemodulationClass import Demodulator
from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB

def plot_setup(mod_mode, fig):
    fig.suptitle("Eye Diagram and Constellation")
    axes = {}
    if mod_mode != 'BPSK':
        gridspec = fig.add_gridspec(nrows=3, ncols=2)
        axes['Iplot'] = fig.add_subplot(gridspec[0, 0])
        axes['Qplot'] = fig.add_subplot(gridspec[0, 1])
        axes['ConstPlot'] = fig.add_subplot(gridspec[1:, :])
    else:
        gridspec = fig.add_gridspec(nrows=1, ncols=1)
        axes['Iplot'] = fig.add_subplot(gridspec[0, 0])
        axes['ConstPlot'] = fig.add_subplot(gridspec[1:, :])
    return axes
    
def plot_eye_diagram(signal, bitstream, modulation_mode, order, samples_per_symbol, delay, symbol_period, ax):
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
            ax['Iplot'].plot(time_axis, i_samples, color='r')
            ax['Qplot'].plot(time_axis, q_samples, color='b')
        else:
            ax['Iplot'].plot(time_axis, i_samples, color='r')
    
def received_constellation(demod_signal, order, samples_per_symbol, delay, ax):
    demod_signal_samples = demod_signal[delay:-6*samples_per_symbol:samples_per_symbol]
    ax['ConstPlot'].scatter(demod_signal_samples.real, demod_signal_samples.imag)
    ax['ConstPlot'].set_title("Received Constellation")
    ax['ConstPlot'].set_xlabel("I")
    ax['ConstPlot'].set_ylabel("Q")
    ax['ConstPlot'].grid(True)
    scaler = ((2**(order/2))-1) if order > 2 else 1
    x_ticks = np.arange(-scaler, scaler+1, 2)
    y_ticks = np.arange(-scaler, scaler+1, 2) if order > 2 else np.arange(-1, 2, 1)
    ax['ConstPlot'].set_xticks(x_ticks)
    ax['ConstPlot'].set_yticks(y_ticks)
        
def main():
    modulation_mode = input("Enter modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
    bit_rate = int(input("Enter bit rate: "))
    carrier_frequency = int(input("Enter carrier frequency: "))

    modulator = Modulator(modulation_mode, bit_rate, carrier_frequency)
    demodulator = Demodulator(modulation_mode, bit_rate, modulator.sampling_rate)

    with open('FYP_NextGenIoT_Simulator/TestcaseFiles/UniformMax2ByteUTF8.txt', 'r',encoding="utf8") as file:
        message = file.read()[:5000]

    bitstream = modulator.msgchar2bit(message)

    modulator.IQ_Return = False

    _, modulated_signal = modulator.modulate(bitstream)

    demodulated_signal = demodulator.demodulate(modulated_signal)

    demodulator.plot_EyeDiagram = True
    demodulator.plot_constellation = True

    demodulator.ax = demodulator.plot_setup(demodulator.fig)
    
    demodulator.auto_plot(demodulated_signal)
    
    plt.show()


if __name__ == '__main__':
    main()

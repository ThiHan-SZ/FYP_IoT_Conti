from SimulationClassCompact.ModulationClass import Modulator as Mod
from SimulationClassCompact.DemodulationClass import Demodulator as Demod
from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB
from sk_dsp_comm import digitalcom as dc
import commpy
import matplotlib.pyplot as plt
import numpy as np

mod_mode = input("Enter modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
bit_rate = int(input("Enter bit rate: "))
Carrier_freq = int(input("Enter carrier frequency: "))

modulator = Mod(mod_mode, bit_rate, Carrier_freq)
demodulator = Demod(mod_mode, bit_rate, Carrier_freq)

##### Matched Filtering #####
RRC_delay = 3*modulator.symbol_period
_, rrc = commpy.filters.rrcosfilter(N=int(2*modulator.sampling_rate*RRC_delay),alpha=0.35,Ts=modulator.symbol_period, Fs=modulator.sampling_rate)

message = input("Enter the message: ")

bitstr = modulator.msgchar2bit(message)

modulator.IQ_Return = False

t_Shaped_Pulse, modulated_signal = modulator.modulate(bitstr)

signal = demodulator.demodulate(modulated_signal)

demodulator.plot(signal)

SPS = demodulator.samples_per_symbol
T = demodulator.symbol_period
FS = demodulator.sampling_rate
DELAY = demodulator.demodulator_total_delay


def EyeDiagram(signal):
    samples = []
    for i in range(len(bitstr)-2):
        samples.append(signal[DELAY + SPS*i + np.arange(2*SPS)])
    samples = np.array(samples).T
    plt.figure()
    plt.plot(np.linspace(-T,T,2*SPS), samples.real)
        

EyeDiagram(signal)
#drawFullEyeDiagram(signal)
#plt.tight_layout()

plt.show()
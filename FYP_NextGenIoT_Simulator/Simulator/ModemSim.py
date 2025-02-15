from SimulationClassCompact.ChannelClass import *
from SimulationClassCompact import ModulationClass as Mod, DemodulationClass as Demod
import matplotlib.pyplot as plt

mod_mode = input("Enter modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
bit_rate = int(input("Enter baud rate: "))
Carrier_freq = int(input("Enter carrier frequency: "))

modulator = Mod.Modulator(mod_mode, bit_rate, Carrier_freq)
demodulator = Demod.Demodulator(mod_mode, bit_rate, modulator.sampling_rate)

with open('FYP_NextGenIoT_Simulator/TestcaseFiles/UniformMax2ByteUTF8.txt', 'r',encoding="utf8") as file:
    message = file.read()[:500]

bitstream = modulator.msgchar2bit(message)

modulator.IQ_Return = True

t_axis, Shaped_Pulse, I_FC, Q_FC, I_SP, Q_SP, Dirac_Comb, RRC_delay = modulator.modulate(bitstream)
#IQplot_fig = modulator.IQ_plot(t_axis, Shaped_Pulse, I_FC, Q_FC, I_SP, Q_SP, Dirac_Comb, RRC_delay)

demodulator.plot_IQ = True

demodulator.plot_constellation = True

offset = SimpleFrequencyOffsetChannel(0.01)
mixed = I_FC + Q_FC

#offsetsignal = offset.add_offset(mixed)

plt.show()
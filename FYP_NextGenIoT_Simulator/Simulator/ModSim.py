from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB
from SimulationClassCompact import ModulationClass as Mod, DemodulationClass as Demod
import matplotlib.pyplot as plt

mod_mode = input("Enter modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ")
bit_rate = int(input("Enter bit rate: "))
Carrier_freq = int(input("Enter carrier frequency: "))

modulator = Mod.Modulator(mod_mode, bit_rate, Carrier_freq)

message = input("Enter message: ")

bitstr = modulator.msgchar2bit(message)

modulator.IQ_Return = False

t_Shaped_Pulse, modulated_signal = modulator.modulate(bitstr)

demodulator = Demod.Demodulator(mod_mode, bit_rate, Carrier_freq)

demod_sig = demodulator.demodulate(modulated_signal)

text, _ = demodulator.demapping(demod_sig)

print("Received Message: ", text)

demodulator.demod_and_plot(modulated_signal)

demodulator.fig.suptitle("Received Signal")
plt.show()

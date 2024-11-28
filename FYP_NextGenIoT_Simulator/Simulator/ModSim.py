from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB
from SimulationClassCompact import ModulationClass as Mod, DemodulationClass as Demod
import matplotlib.pyplot as plt

mod_mode = input("Enter modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
bit_rate = int(input("Enter bit rate: "))
Carrier_freq = int(input("Enter carrier frequency: "))

modulator = Mod.Modulator(mod_mode, bit_rate, Carrier_freq)



with open('FYP_NextGenIoT_Simulator/TestcaseFiles/TinySpeare.txt', 'r') as file:
    message = file.read()[:5000]


# message = input("Enter the message: ")

bitstr = modulator.msgchar2bit(message)

int_bitstr = [int(i) for i in bitstr[:-2]]

modulator.IQ_Return = False

t_Shaped_Pulse, modulated_signal = modulator.modulate(bitstr)

demodulator = Demod.Demodulator(mod_mode, bit_rate, Carrier_freq)

noisy_demodulator = Demod.Demodulator(mod_mode, bit_rate, Carrier_freq)

noisy_channel = SimpleGWNChannel_dB(38)

noisy_modulated_signal = noisy_channel.add_noise(modulated_signal)

demod_sig = demodulator.demodulate(modulated_signal)

noisy_demod_sig = noisy_demodulator.demodulate(noisy_modulated_signal)

text, bits = demodulator.demapping(demod_sig)

noisy_text, noisy_bits = noisy_demodulator.demapping(noisy_demod_sig)

BER = 1 - ((int_bitstr == bits[:len(int_bitstr)]).mean())
print(f'BER of {mod_mode} Modulation: {BER*100}%')

BER = 1 - ((int_bitstr == noisy_bits[:len(int_bitstr)]).mean())
print(f'BER of {mod_mode} Modulation with Noise: {BER*100}%')

demodulator.demod_and_plot(modulated_signal)

noisy_demodulator.demod_and_plot(noisy_modulated_signal)

demodulator.fig.suptitle("Received Signal")

noisy_demodulator.fig.suptitle("Received Signal with Noise")
plt.show()

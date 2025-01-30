from SimulationClassCompact.ChannelClass import *
from SimulationClassCompact import ModulationClass as Mod, DemodulationClass as Demod
import matplotlib.pyplot as plt

mod_mode = input("Enter modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
bit_rate = int(input("Enter bit rate: "))
Carrier_freq = int(input("Enter carrier frequency: "))

modulator = Mod.Modulator(mod_mode, bit_rate, Carrier_freq)
demodulator = Demod.Demodulator(mod_mode, bit_rate, modulator.sampling_rate)

modulator.RRC_alpha = 0.35
demodulator.RRC_alpha = 0.35

with open('FYP_NextGenIoT_Simulator/TestcaseFiles/UniformMax2ByteUTF8.txt', 'r',encoding="utf8") as file:
    message = file.read()[:1000]

bitstream = modulator.msgchar2bit(message)

modulator.IQ_Return = False

_, modulated_signal = modulator.modulate(bitstream)

modulator.save_signal = True

modulator.save(f"user_file__UniformMax2ByteUTF8__200kHz_16kbps_N{mod_mode}.wav", modulated_signal)
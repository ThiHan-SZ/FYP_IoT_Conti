from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io
import sys

sys.path.insert(1, r"FYP_NextGenIoT_Simulator\Simulator")
from SimulationClassCompact.ModulationClass import Modulator
from SimulationClassCompact.DemodulationClass import Demodulator

out = io.BytesIO()

with Image.open(rf'FYP_NextGenIoT_Simulator/SNR_BER_Fixed_again_again.png') as img:
    img.save(out, format="png")

image_in_bytes = out.getvalue()

encoded_b2 = "".join([format(n, '08b') for n in image_in_bytes])

modulation_mode = input("Enter modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
bit_rate = int(input("Enter bit rate: "))
carrier_frequency = int(input("Enter carrier frequency: "))

modulator = Modulator(modulation_mode, bit_rate, carrier_frequency)
demodulator = Demodulator(modulation_mode, bit_rate, carrier_frequency)

bitstr = list(encoded_b2)
print(len(bitstr)/8)

if len(bitstr) % modulator.order != 0:
    bitstr.extend(['0']*(modulator.order - len(bitstr) % modulator.order))
    
bitstr.extend(['0', '0'])

bitstream = bitstr

_, modulated_signal = modulator.modulate(bitstream)

demodulated_signal = demodulator.demodulate(modulated_signal)

_, bitarray = demodulator.demapping(demodulated_signal)

byte_array = bytes(bitarray)

with open(rf"FYP_NextGenIoT_Simulator\SNR_BER_decoded.png", 'wb') as f:
    f.write(byte_array)
from SimulationClassCompact.ModulationClass import Modulator as Mod
from SimulationClassCompact.DemodulationClass import Demodulator as Demod
from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

# Define modulation types and parameters
MODULATION_TYPES = ['BPSK', 'QPSK', 'QAM16', 'QAM64', 'QAM256', 'QAM1024', 'QAM4096']
BIT_RATE = 1800
CARRIER_FREQ = 18e3

# Initialize modulators and demodulators
modulators = {mod: Mod(mod, BIT_RATE, CARRIER_FREQ) for mod in MODULATION_TYPES}
demodulators = {mod: Demod(mod, BIT_RATE, CARRIER_FREQ) for mod in MODULATION_TYPES}

# Initialize dictionaries for modulated signals and BER
modulated_signals = {mod: (None, None) for mod in MODULATION_TYPES}
ber_dict = {mod: [] for mod in MODULATION_TYPES}

fig, ax = plt.subplots(1, 1)

# Input message and SNR
with open(r'FYP_NextGenIoT_Simulator\TestcaseFiles\TinySpeare.txt', 'r') as file:
    message = file.read()[:20000]

snr_up = int(input("Enter the SNR upper limit in dB: "))
snr_down = int(input("Enter the SNR lower limit in dB: "))
sample = 1
snr_test_range = np.linspace(snr_down, snr_up, sample*(snr_up-snr_down) + 1, endpoint=True)

# Convert message to bit string
bit_string = Mod.msgchar2bit_static(message)
int_bit_string = np.array([int(bit) for bit in bit_string[:-2]])

# Process each modulation type
for modulation_type in MODULATION_TYPES:
    modulator = modulators[modulation_type]
    demodulator = demodulators[modulation_type]
    
    bit_string = modulator.msgchar2bit(message)
    time_axis, modulated_signal = modulator.modulate(bit_string)
    modulated_signals[modulation_type] = (time_axis, modulated_signal)
    
    for snr in snr_test_range:
        channel = SimpleGWNChannel_dB(snr)
        noisy_signal = channel.add_noise(modulated_signal)
        demod_signal = demodulator.demodulate(noisy_signal)
        rx_message, demod_bit_string = demodulator.demapping(demod_signal)
        
        ber = 1 - ((int_bit_string == demod_bit_string[:len(int_bit_string)]).mean())
        ber_dict[modulation_type].append(ber)

# Plot results
ax.set_yscale('log')
ax.set_ylim(1e-6, 1e0)
ax.grid(which="both", linestyle='--', linewidth=0.5)
ax.xaxis.set_major_locator(MultipleLocator(1))

colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'black']
markers = ['o', 's', '^', 'v', '<', '>', 'd']

for modulation_type, color, marker in zip(MODULATION_TYPES, colors, markers):
    ax.plot(snr_test_range, ber_dict[modulation_type], label=modulation_type, color=color, marker=marker, markevery=sample)

ax.set_xlabel('SNR (dB)')
ax.set_ylabel('BER')
ax.set_title('BER vs SNR')
ax.legend()
plt.show()


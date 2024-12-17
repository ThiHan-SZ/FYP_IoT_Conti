from SimulationClassCompact.ModulationClass import Modulator as Mod
from SimulationClassCompact.DemodulationClass import Demodulator as Demod
from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

# Define modulation types and parameters
MODULATION_TYPES = ['BPSK', 'QPSK', 'QAM16', 'QAM64', 'QAM256', 'QAM1024', 'QAM4096']
BIT_RATE = 40000
CARRIER_FREQ = 200000

# Initialize modulators and demodulators
modulators = {mod: Mod(mod, BIT_RATE, CARRIER_FREQ) for mod in MODULATION_TYPES}
demodulators = {mod: Demod(mod, BIT_RATE, CARRIER_FREQ) for mod in MODULATION_TYPES}

# Initialize dictionaries for modulated signals and BER
modulated_signals = {mod: (None, None) for mod in MODULATION_TYPES}
ber_dict = {mod: [] for mod in MODULATION_TYPES}

fig, ax = plt.subplots(1, 1)

# Input message and SNR
with open(r'FYP_NextGenIoT_Simulator\TestcaseFiles\TinySpeare.txt', 'r') as file:
    message = file.read()[:15000]
snr_up,snr_down = 0,0

while snr_up <= snr_down:
    try:
        snr_up = int(input("Enter the SNR upper limit in dB: "))
        snr_down = int(input("Enter the SNR lower limit in dB: "))
        assert snr_up > snr_down, "SNR upper limit must be greater than SNR lower limit"
    except KeyboardInterrupt:
        exit()
    except:
        print("Invalid SNR. Please re-enter.")

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
        print(f"Status : {modulation_type} | SNR : {snr}")
        channel = SimpleGWNChannel_dB(snr)
        noisy_signal = channel.add_noise(modulated_signal)
        demod_signal = demodulator.demodulate(noisy_signal)
        rx_message, demod_bit_string = demodulator.demapping(demod_signal)
        
        ber = 1 - ((int_bit_string == demod_bit_string[:len(int_bit_string)]).mean())
        ber_dict[modulation_type].append(ber)

# Set y-axis to symlog scale
ax.set_yscale('symlog', linthresh=1e-5)
# Custom ticks to include 0 and log-scale values
ticks = [0, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1]
ax.set_yticks(ticks)

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


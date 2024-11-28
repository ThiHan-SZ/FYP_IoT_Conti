from SimulationClassCompact.ModulationClass import Modulator as SimMod
from SimulationClassCompact.DemodulationClass import Demodulator as SimDemod
from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

# Define modulation types and parameters
modulation_types = ['BPSK', 'QPSK', 'QAM16', 'QAM64', 'QAM256', 'QAM1024', 'QAM4096']
bit_rate = 1800
carrier_freq = 18e3

# Initialize modulators and demodulators
modulators = {mod: SimMod(mod, bit_rate, carrier_freq) for mod in modulation_types}
demodulators = {mod: SimDemod(mod, bit_rate, carrier_freq) for mod in modulation_types}

# Initialize dictionaries for modulated signals and BER
modulated_signals = {mod: (None, None) for mod in modulation_types}
BER_dict = {mod: [] for mod in modulation_types}

# Input message and SNR
with open(r'FYP_NextGenIoT_Simulator\TestcaseFiles\TinySpeare.txt', 'r') as file:
    msg = file.read()[:10]
SNR_up = int(input("Enter the SNR upper limit in dB: "))
SNR_down = int(input("Enter the SNR lower limit in dB: "))
Sample = 1
SNR_test_range = np.linspace(SNR_down, SNR_up, Sample*(SNR_up-SNR_down) + 1, endpoint=True)

# Convert message to bit string
bitstr = SimMod.msgchar2bit_static(msg)
int_bitstr = np.array([int(bit) for bit in bitstr])

slicer_l = 0
slicer_r = len(modulation_types)

# Process each modulation type
for mode in modulation_types[slicer_l:slicer_r]:
    modulator = modulators[mode]
    demodulator = demodulators[mode]
    
    bitstr = modulator.msgchar2bit(msg)
    t_axis, modulated_sig = modulator.modulate(bitstr) if not modulator.deep_return else modulator.modulate(bitstr)[:2]
    modulated_signals[mode] = (t_axis, modulated_sig)
    
    for snr in SNR_test_range:
        channel = SimpleGWNChannel_dB(snr)
        noisy_signal = channel.add_noise(modulated_sig)
        demod_signal = demodulator.demodulate(noisy_signal)
        RXmessage, demod_bitstr = demodulator.demapping(demod_signal)
        
        BER = 1 - ((int_bitstr == demod_bitstr[:len(int_bitstr)]).mean())
        BER_dict[mode].append(BER)

# Plot results
fig, ax = plt.subplots(1, 1)
ax.set_yscale('log')
ax.set_ylim(1e-10, 1e0)
ax.grid(which="both", linestyle='--', linewidth=0.5)
ax.xaxis.set_major_locator(MultipleLocator(1))

colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'black']
markers = ['o', 's', '^', 'v', '<', '>', 'd']

for mode, color, marker in zip(modulation_types[slicer_l:slicer_r], colors[slicer_l:slicer_r], markers[slicer_l:slicer_r]):
    ax.plot(SNR_test_range, BER_dict[mode], label=mode, color=color, marker=marker, markevery=Sample)

ax.set_xlabel('SNR (dB)')
ax.set_ylabel('BER')
ax.set_title('BER vs SNR')
ax.legend()
plt.show()

'''demod_signal = demodulator.demodulate(modualted_sig)
RXmessage, demod_bitstr = demodulator.demapping(demod_signal)

BER = (int_bitstr == demod_bitstr[:len(int_bitstr)]).mean() * 100
print(f'Message from {mode} Demodulation: {RXmessage}')
print(f'BER of {modulator.modulation_mode} Modulation: {BER}%')'''

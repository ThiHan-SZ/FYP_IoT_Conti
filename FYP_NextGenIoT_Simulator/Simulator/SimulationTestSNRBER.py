import concurrent.futures
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from SimulationClassCompact.ModulationClass import Modulator as Mod
from SimulationClassCompact.DemodulationClass import Demodulator as Demod
from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB
from tqdm import tqdm

# Define the modulation types and parameters
MODULATION_TYPES = ['BPSK', 'QPSK', 'QAM16', 'QAM64', 'QAM256', 'QAM1024', 'QAM4096']
BIT_RATE = 40000
CARRIER_FREQ = 200000

# Initialize modulators and demodulators
modulators = {mod: Mod(mod, BIT_RATE, CARRIER_FREQ) for mod in MODULATION_TYPES}
demodulators = {mod: Demod(mod, BIT_RATE, CARRIER_FREQ) for mod in MODULATION_TYPES}

# Define the worker function that will be executed by each thread
def worker(modulation_type, snr_value):
    # Get the modulator and demodulator objects
    modulator = modulators[modulation_type]
    demodulator = demodulators[modulation_type]

    # Convert message to bit string
    with open(r'FYP_NextGenIoT_Simulator\TestcaseFiles\TinySpeare.txt', 'r') as file:
        message = file.read()[:15000]
    bit_string = modulator.msgchar2bit(message)

    # Modulate the bit string
    time_axis, modulated_signal = modulator.modulate(bit_string)

    # Add noise to the modulated signal
    channel = SimpleGWNChannel_dB(snr_value, seed=1)
    noisy_signal = channel.add_noise(modulated_signal)

    # Demodulate the noisy signal
    demodulated_signal = demodulator.demodulate(noisy_signal)

    # Demap the demodulated signal
    demodulated_bits = demodulator.demapping(demodulated_signal)[1]

    # Calculate the BER
    int_bit_string = np.array([int(bit) for bit in bit_string[:-2]])
    error_bits = np.sum(np.abs(int_bit_string - demodulated_bits))
    ber = error_bits / len(bit_string)

    return (modulation_type, snr_value, ber)

# Define the SNR values
snr_up, snr_down = 0, 0
while snr_up <= snr_down:
    try:
        snr_up = int(input("Enter the SNR upper limit in dB: "))
        snr_down = int(input("Enter the SNR lower limit in dB: "))
        assert snr_up > snr_down, "SNR upper limit must be greater than SNR lower limit"
    except ValueError:
        print("Invalid input. Please try again.")
snr_values = np.linspace(snr_down, snr_up, (snr_up-snr_down) + 1, endpoint=True)
results = []
# Create a ThreadPoolExecutor with a smaller number of workers
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    # Submit the tasks to the executor
    futures = []
    for modulation_type in MODULATION_TYPES:
        for snr_value in snr_values:
            futures.append(executor.submit(worker, modulation_type, snr_value))

    # Use tqdm to display a progress bar
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Calculating BER"):
        result = future.result()
        results.append(result)

# Plot the results
fig, ax = plt.subplots(1, 1)

# Set y-axis to symlog scale
ax.set_yscale('symlog', linthresh=1e-5)
# Custom ticks to include 0 and log-scale values
ticks = [0, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1]
ax.set_yticks(ticks)

ax.grid(which="both", linestyle='--', linewidth=0.5)
ax.xaxis.set_major_locator(MultipleLocator(1))

colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'black']
markers = ['o', 's', '^', 'v', '<', '>', 'd']

for i, modulation_type in enumerate(MODULATION_TYPES):
    bers = [result[2] for result in results if result[0] == modulation_type]
    ax.plot(snr_values, bers, label=modulation_type, color=colors[i], marker=markers[i], markevery=1)

ax.set_xlabel('SNR (dB)')
ax.set_ylabel('BER')
ax.set_title('BER vs SNR')
ax.legend()
plt.show()
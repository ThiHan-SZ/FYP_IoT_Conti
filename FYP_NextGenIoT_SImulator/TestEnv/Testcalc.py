import numpy as np
import timeit
import commpy
import scipy.signal as sig
from memory_profiler import profile
import matplotlib.pyplot as plt

# Mock data for testing
I = np.random.choice([-1, 1], size=100)  # Simulated I values
Q = np.random.choice([-1, 1], size=100)  # Simulated Q values
bitgroups = ['01'] * 100  # Mock bitgroups data

class ModulatorTest:
    def __init__(self, carrier_freq, baud_rate, sampling_rate):
        self.symbol_period = 1 / baud_rate
        self.sampling_rate = sampling_rate
        self.carrier_freq = carrier_freq
    
    @profile  # Original method
    def modulator_calculations_original(self, I, Q, bitgroups):
        samples_per_symbol = int(self.symbol_period * self.sampling_rate)

        Dirac_Comb = np.zeros(len(bitgroups) * samples_per_symbol, dtype=complex)
        Dirac_Comb[::samples_per_symbol] = I + 1j * Q

        RRC_delay = 3*self.symbol_period
        _, rrc = commpy.filters.rrcosfilter(N=int(2*self.sampling_rate*RRC_delay),alpha=0.5,Ts=self.symbol_period, Fs=self.sampling_rate)
        
        Shaped_Pulse = sig.convolve(Dirac_Comb,rrc) #Pulse shaped signal, convolving SRRC over the Dirac Comb function
        t_Shaped_Pulse = np.linspace(0,len(Shaped_Pulse)/self.sampling_rate,len(Shaped_Pulse),endpoint=False)
        
        ###Upscaling the signal to the carrier frequency###
        I_processed = Shaped_Pulse.real
        Q_processed = Shaped_Pulse.imag
        I_FC = I_processed  *  np.cos(2*np.pi*self.carrier_freq*t_Shaped_Pulse)
        Q_FC = Q_processed  * -np.sin(2*np.pi*self.carrier_freq*t_Shaped_Pulse)

        return t_Shaped_Pulse, I_FC + Q_FC

    @profile  # Optimized method
    def modulator_calculations_optimized(self, I, Q, bitgroups):
        samples_per_symbol = int(self.symbol_period * self.sampling_rate)
        RRC_delay = 3 * self.symbol_period

        # Simulated SRRC filter and pulse shaping (replace with actual filter for real use)
        _, rrc = commpy.filters.rrcosfilter(N=int(2*self.sampling_rate*RRC_delay),alpha=0.5,Ts=self.symbol_period, Fs=self.sampling_rate)
        shaped_pulse_length = len(bitgroups) * samples_per_symbol + len(rrc) - 1
        Shaped_Pulse = np.zeros(shaped_pulse_length, dtype=complex)

        for idx, (i_val, q_val) in enumerate(zip(I, Q)):
            start_idx = idx * samples_per_symbol
            Shaped_Pulse[start_idx:start_idx + len(rrc)] += (i_val + 1j * q_val) * rrc

        t_Shaped_Pulse = np.linspace(0, len(Shaped_Pulse) / self.sampling_rate, len(Shaped_Pulse), endpoint=False)

        ###Upscaling the signal to the carrier frequency###
        I_processed = Shaped_Pulse.real
        Q_processed = Shaped_Pulse.imag
        I_FC = I_processed * np.cos(2 * np.pi * self.carrier_freq * t_Shaped_Pulse)
        Q_FC = Q_processed * -np.sin(2 * np.pi * self.carrier_freq * t_Shaped_Pulse)

        return t_Shaped_Pulse, I_FC + Q_FC

# Set parameters for testing
carrier_freq = 1e6  # Carrier frequency in Hz
baud_rate = 1e3     # Symbol rate in symbols per second
sampling_rate = 10 * 2 * carrier_freq  # 10x Oversampling

# Create an instance of the ModulatorTest
modulator_test = ModulatorTest(carrier_freq, baud_rate, sampling_rate)

# Timing tests
original_time = timeit.timeit(lambda: modulator_test.modulator_calculations_original(I, Q, bitgroups), number=1)
optimized_time = timeit.timeit(lambda: modulator_test.modulator_calculations_optimized(I, Q, bitgroups), number=1)

print(f"Original execution time: {original_time:.4f} seconds")
print(f"Optimized execution time: {optimized_time:.4f} seconds")

fig, ax = plt.subplots(1,2)
ax[0].plot(*modulator_test.modulator_calculations_original(I, Q, bitgroups))
ax[0].set_title("Original")
ax[1].plot(*modulator_test.modulator_calculations_optimized(I, Q, bitgroups))
ax[1].set_title("Optimized")
plt.show()

print(f"Is Equal Check: {np.allclose(*modulator_test.modulator_calculations_original(I, Q, bitgroups), *modulator_test.modulator_calculations_optimized(I, Q, bitgroups))}")
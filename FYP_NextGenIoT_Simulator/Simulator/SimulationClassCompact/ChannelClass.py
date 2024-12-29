from numpy import sum, abs, sqrt, exp, pi, arange,sinc,hamming
from scipy.signal import convolve
from numpy.random import normal, seed as nprseed

class SimpleGWNChannel_dB:
    def __init__(self, SNR, seed=1):
        """
        Initializes the SimpleGWNChannel_dB class with a specified SNR and an optional random seed.

        Parameters:
        - SNR (float): The Signal-to-Noise Ratio in decibels.
        - seed (int, optional): The seed for the random number generator to ensure reproducibility. 
        Defaults to 1. If None, no seeding is applied.
        """
        self.SNR = SNR
        self.seed = seed
        if seed is not None:
            nprseed(seed)

    def add_noise(self, signal):
        signal_power = sum(abs(signal)**2) / len(signal)
        snr_linear = 10**(self.SNR/10)
        
        noise_power = signal_power / snr_linear
        noise_std_dev = sqrt(noise_power)

        noise = normal(0, noise_std_dev, len(signal))
        return signal + noise
    
class SimpleDelayChannel:
    def __init__(self, delay):
        """
        Initializes the SimpleDelayChannel class with a specified delay.

        Parameters:
        - delay (float): The fractional delay in samples that will be applied to the signal.
        """
        self.delay = delay

    def add_delay(self, signal):
        # Create and apply fractional delay filter fractional delay, in signal
        N = 21 # number of taps
        n = arange(-N//2, N//2) # ...-3,-2,-1,0,1,2,3...
        h = sinc(n - self.delay) # calc filter taps
        h *= hamming(N) # window the filter to make sure it decays to 0 on both sides
        h /= sum(h) # normalize to get unity gain, we don't want to change the amplitude/power
        signal = convolve(signal, h) # apply filter
        return signal
    
class SimpleFlatFadingChannel:
    def __init__(self, type, seed=1):
        """
        Initializes the SimpleFlatFadingChannel class with a specified type and an optional random seed.

        Parameters:
        - type (str): The type of fading, either 'rayleigh' or 'rician'.
        - seed (int, optional): The seed for the random number generator to ensure reproducibility. 
        Defaults to 1. If None, no seeding is applied.
        """
        if type != "rayleigh" and type != "rician":
            raise ValueError("Invalid type, must be 'rayleigh' or 'rician'")
        elif type == 'rician':
            rician_k = int(input("Enter the Rician K factor: "))
        self.type = type
        
        self.seed = seed
        if seed is not None:
            nprseed(seed)
        
    def add_fading(self, signal):
        
        if self.type == "rayleigh":
            # Diffuse component (Rayleigh fading)
            h = (normal(0, 1, size=signal.shape) + 1j * normal(0, 1, size=signal.shape)) / sqrt(10)
                
        elif self.type == "rician":
            # Line-of-sight (LOS) component
            los_component = sqrt(self.rician_k / (self.rician_k + 1))
            
            # Diffuse component (Rayleigh fading)
            diffuse_component = (normal(0, 1, size=signal.shape) + 1j * normal(0, 1, size=signal.shape)) / sqrt(10)
            
            # Rician fading: LOS + diffuse components
            h = los_component + sqrt(1 / (self.rician_k + 1)) * diffuse_component
            
        return signal * h

class SimpleFrequencyDriftChannel:
    def __init__(self, frequency_drift_rate):
        """
        Initializes the SimpleFrequencyDriftChannel class with a specified frequency drift rate.

        Parameters:
        - frequency_drift_rate (float): The frequency drift rate in rad/sample.
        """

        self.frequency_drift_rate = frequency_drift_rate
        
    def add_drift(self, signal):
        # Apply frequency drift to the signal
        signal = signal * exp(1j * 2 * pi * self.frequency_drift_rate * arange(len(signal)) / len(signal))
        return signal

class SimpleFrequencyOffsetChannel:
    def __init__(self, frequency_offset):
        """
        Initializes the SimpleFrequencyOffsetChannel class with a specified frequency offset.

        Parameters:
        - frequency_offset (float): The frequency offset in Hz to be applied to the signal.
        """
        self.frequency_offset = frequency_offset
        
    def add_offset(self, signal):
        # Apply frequency offset to the signal
        signal = signal * exp(1j * 2 * pi * self.frequency_offset)
        return signal
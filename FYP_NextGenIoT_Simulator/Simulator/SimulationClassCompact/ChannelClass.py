from numpy import sum, abs, sqrt
from numpy.random import normal, seed as nprseed

class SimpleGWNChannel_dB:

    def __init__(self, SNR, seed=1):
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
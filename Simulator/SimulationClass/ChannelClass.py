from numpy import sum, abs, sqrt
from numpy.random import normal

class SimpleGWNChannel_dB:

    def __init__(self, SNR):
        self.SNR = SNR

    def add_noise(self, signal):
        
        signal_power = sum(abs(signal)**2) / len(signal)
        snr_linear = 10**(self.SNR/10)
        
        noise_power = signal_power / snr_linear
        noise_std_dev = sqrt(noise_power)

        noise = normal(0, noise_std_dev, len(signal))
        return signal + noise
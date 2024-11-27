from numpy import sum, abs, sqrt, arange, sinc, hamming, convolve
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
    
class SimpleDelayChannel:

    def __init__(self, delay):
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
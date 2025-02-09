from numpy import sum, abs, sqrt, exp, pi, arange,sinc,hamming
from scipy.signal import fftconvolve
from numpy.random import normal, seed as nprseed
import numpy as np
import matplotlib.pyplot as plt

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
        """
        Adds Gaussian noise to the input signal based on the specified Signal-to-Noise Ratio (SNR).

        Args:
            signal (np.array): The input signal to which noise is to be added.

        Returns:
            np.array: The noisy signal after adding Gaussian noise.

        The noise is generated using the SNR provided during the class initialization.
        The noise power is calculated based on the signal power and the SNR.
        """
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
        assert delay > 0 and delay < 1
        self.delay = delay

    def add_delay(self, signal):
        """
        Applies a fractional delay to the signal using a filter with
        'hamming' window and 'sinc' taps.

        Parameters:
        - signal (numpy.array): The signal to be delayed.

        Returns:
        - numpy.array: The delayed signal.
        """
        # Create and apply fractional delay filter fractional delay, in signal
        N = 21 # number of taps
        n = arange(-N//2, N//2) # ...-3,-2,-1,0,1,2,3...
        h = sinc(n - self.delay) # calc filter taps
        h *= hamming(N) # window the filter to make sure it decays to 0 on both sides
        h /= sum(h) # normalize to get unity gain, we don't want to change the amplitude/power
        signal = fftconvolve(signal, h) # apply filter
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
        self.rician_k = None
        self.type = type
        self.seed = seed
        if seed is not None:
            nprseed(seed)
        
    def add_fading(self, signal):      
        """
        Applies fading to the input signal based on the specified channel type.

        Parameters:
        - signal (np.array): The input signal to which the fading effect will be applied.

        Returns:
        - np.array: The signal with applied fading effect.

        The function supports two types of fading:
        1. Rayleigh Fading: A diffuse multipath component is applied, modeled as a complex Gaussian process without a line of sight component.
        2. Rician Fading: A combination of a line-of-sight component and a diffuse multipath component is applied, controlled by the Rician K-factor.
        """
        if self.type == "rayleigh":
            # Diffuse component (Rayleigh fading)
            real = normal(0, 1, size=signal.shape)
            imag = normal(0, 1, size=signal.shape)
            h = sqrt(real**2 + imag**2) / sqrt(2)
                
        elif self.type == "rician":
            assert self.rician_k is not None
            linear_k = 10**(self.rician_k/10)
            # Line-of-sight (LOS) component
            los_component = sqrt(linear_k / (linear_k + 1))
            
            # Diffuse component (Rayleigh fading)
            diffuse_component = (normal(0, 1, size=signal.shape) + 1j * normal(0, 1, size=signal.shape)) / sqrt(2)
            
            # Rician fading: LOS + diffuse components
            h = los_component + sqrt(1 / (linear_k + 1)) * diffuse_component
            
        return signal * h

class SimpleFrequencyDriftChannel:
    def __init__(self, frequency_drift_rate):
        """
        Initializes the SimpleFrequencyDriftChannel class with a specified frequency drift rate.

        Parameters:
        - frequency_drift_rate (float): The frequency drift rate in rad/sample.
        """

        self.frequency_drift_rate = frequency_drift_rate
        self.accumulated_drift = 0
        
    def add_drift(self, signal,sampling_rate):
        """
        Applies a frequency drift to the input signal.

        Parameters:
        - signal (np.array): The input signal to which the frequency drift will be applied.

        Returns:
        - np.array: The signal with applied frequency drift.
        """
        signal = signal.astype(complex)
        signal *= np.exp(-1j * 2 * np.pi * (0.5 * self.frequency_drift_rate * arange(0, len(signal), dtype=float) / sampling_rate  ** 2))  
                
        return signal

class SimpleFrequencyOffsetChannel:
    def __init__(self, frequency_offset):
        """
        Initializes the SimpleFrequencyOffsetChannel class with a specified frequency offset.

        Parameters:
        - frequency_offset (float): The frequency offset in Hz to be applied to the signal.
        """
        self.frequency_offset = frequency_offset
        
    def add_offset(self, signal, sampling_rate):
        """
        Applies a frequency offset to the input signal.

        Parameters:
        - signal (np.array): The input signal to which the frequency offset will be applied.

        Returns:
        - np.array: The signal with applied frequency offset.
        """
        time = arange(0, len(signal), dtype=float) / sampling_rate
        # Apply frequency offset to the signal
        signal = signal * exp(-1j * 2 * pi * self.frequency_offset * time)
        print(f"Applied Frequency Offset: {self.frequency_offset} Hz")

        
        return signal
    
def ApplyChannels(selected_channels, channel_params, signal, sampling_rate):
    """
    Applies a sequence of channels to the input signal based on the selected channels and parameters.

    Parameters:
    - selected_channels (list of str): List of channels to be applied to the signal.
    - channel_params (dict): Dictionary of channel parameters. The keys are the channel names and the values are the corresponding parameters.
    - signal (np.array): The input signal to which the channels will be applied.
    - sampling_rate (int): Sampling rate of the signal.

    Returns:
    - np.array: The signal with the applied channels.

    Supported channels are:
    - AWGN
    - Fading (Rayleigh or Rician)
        - Rician requires K input
    - Freq Drift
    - Freq Offset
    - Delay

    If a channel is not supported, a ValueError is raised.
    """
    if selected_channels:
        for channel, value in channel_params.items():
            match channel:
                case "AWGN":
                    AWGNChannel = SimpleGWNChannel_dB(SNR=value)
                    signal = AWGNChannel.add_noise(signal)
                    continue
                case "Fading":
                    FlatFadingChannel = SimpleFlatFadingChannel(type=str(value).lower())
                    if value == "Rician":
                        assert "K value" in channel_params
                        FlatFadingChannel.rician_k = float(channel_params["K value"])
                    signal = FlatFadingChannel.add_fading(signal)
                    continue
                case "Freq Drift":
                    FreqDriftChannel = SimpleFrequencyDriftChannel(frequency_drift_rate=value)
                    signal = FreqDriftChannel.add_drift(signal,sampling_rate)
                    continue
                case "Freq Offset":
                    FreqOffsetChannel = SimpleFrequencyOffsetChannel(frequency_offset=value)
                    signal = FreqOffsetChannel.add_offset(signal, sampling_rate)
                    continue
                case "Delay":
                    DelayChannel = SimpleDelayChannel(delay=value)
                    signal = DelayChannel.add_delay(signal)
                    continue
                case "K value":
                    # Case will only exist if Rician is selected but K is handled above
                    continue
                case _:
                    raise ValueError(f"Invalid channel: {channel}")
    
        return signal
    
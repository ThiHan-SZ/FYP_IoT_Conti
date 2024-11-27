import numpy as np
import scipy.signal as sig
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import commpy
import math

class Demodulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
    
    def __init__(self, modulation_mode, bit_rate,carrier_freq) -> None:
       

        #Demodulation Parameters
        self.carrier_freq = carrier_freq
        self.modulation_mode = modulation_mode
        self.order = self.modulation_modes[modulation_mode]

        #Bit Rate Parameters
        self.baud_rate = bit_rate/self.order
        self.symbol_period = 1/self.baud_rate
        self.oversampling_factor = 10
        self.sampling_rate = self.oversampling_factor*2*self.carrier_freq # 10x Oversampling Factor for any CF
        self.samples_per_symbol = int(self.sampling_rate/self.baud_rate)

        #Demodulation Parameters
        self.Nyquist_Bandwidth = 1/(2*self.symbol_period)
        self.low_pass_filter_cutoff = 5*self.Nyquist_Bandwidth
        self.low_pass_filter_order = 101
        self.low_pass_delay = (self.low_pass_filter_order // 2) / self.sampling_rate
        self.low_pass_filter = self.low_pass_filter()

        self.demodulator_total_delay = None
    
    def PhaseLockedLoop(self, signal):
        # PLL Parameters
        Kp = 0.01  # Proportional gain
        Ki = 0.001  # Integral gain
        N = len(signal)
        
        # State variables
        freq = 0
        phase = 0
        integrator = 0
        
        # Output arrays
        phase_out = np.zeros(N)
        
        for i in range(1, N):
            # Phase detector
            error = np.angle(signal[i] * np.exp(-1j * phase))
            
            # Loop filter (PI controller)
            integrator += Ki * error
            freq = Kp * error + integrator
            
            # Update phase
            phase += freq
            phase_out[i] = phase
        
        return phase_out
    
    def downconverter(self, signal):
        t = np.linspace(0, len(signal)/self.sampling_rate, len(signal), endpoint=False)
        phase = self.PhaseLockedLoop(signal)
        I = signal * np.cos(2*np.pi*t + phase)
        Q = signal * - np.sin(2*np.pi*t + phase)
        return I, Q

    def low_pass_filter(self):
        low_pass_filter = sig.firwin(self.low_pass_filter_order, self.low_pass_filter_cutoff/(self.sampling_rate/2), fs = self.sampling_rate)
        return low_pass_filter
    
    def demodulate(self, signal):
        I_base, Q_base = self.downconverter(signal)
        I_lp = sig.lfilter(self.low_pass_filter, 1, I_base)
        Q_lp = sig.lfilter(self.low_pass_filter, 1, Q_base)


        RRC_delay = 3*self.symbol_period
        _, rrc = commpy.filters.rrcosfilter(N=int(2*self.sampling_rate*RRC_delay),alpha=0.5,Ts=self.symbol_period, Fs=self.sampling_rate)

        baseband_signal = I_lp + 1j*Q_lp
        RC_signal = sig.convolve(baseband_signal, rrc) / np.sum(rrc**2) * 2

        self.demodulator_total_delay = int((2*RRC_delay + self.low_pass_delay) * self.sampling_rate)

        RC_signal *= 2*((2**(self.order/2))-1)
        return RC_signal[:-(6*self.samples_per_symbol)]
    


def main():
    while True:
        try:
            bit_rate = int(input("Enter the bit-rate: "))
            break
        except KeyboardInterrupt:
            exit()
        except:
            print("Invalid bit-rate. Please re-enter.")
    while True:
        mod_mode_select = input("Enter the modulation mode (BPSK, QPSK, QAM 16/64/256/1024/4096): ").upper()
        if mod_mode_select in Demodulator.modulation_modes:
            break
        print("Invalid modulation mode. Please reselect.")
   
    file = input("Enter the file name/path: ")
    # Read the modulated signal
    fs, modulated = wav.read(file)

    demodulator = Demodulator(mod_mode_select, bit_rate, 221000)


    I,Q = demodulator.downconverter(modulated)


    I2,Q2 = downconverter2(modulated,fs/20)

    fig,ax = plt.subplots(2,2, constrained_layout=True)
    ax[0,0].plot(I)
    ax[0,0].set_title("I")
    ax[0,1].plot(Q)
    ax[0,1].set_title("Q")

    ax[1,0].plot(I2)
    ax[1,0].set_title("I2")
    ax[1,1].plot(Q2)
    ax[1,1].set_title("Q2")
    plt.show()

def downconverter2(signal,carrier_freq): #Correct
    #Bit Rate Parameters
   
    oversampling_factor = 10
    sampling_rate = oversampling_factor*2*carrier_freq # 10x Oversampling Factor for any CF

    t = np.linspace(0, len(signal)/sampling_rate, len(signal), endpoint=False)
    I = signal * np.cos(2 * np.pi * carrier_freq * t)
    Q = signal * - np.sin(2 * np.pi * carrier_freq * t)
    return I, Q

if __name__ == "__main__":
    main()
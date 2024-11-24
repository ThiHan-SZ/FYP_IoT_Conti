import commpy.filters
from matplotlib import pyplot as plt
from scipy.io import wavfile as wav
import numpy as np
import scipy.signal as sig
import pickle
import commpy
from matplotlib.figure import Figure

class SimpleModulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}

    def __init__(self, modulation_mode, bit_rate,carrier_freq) -> None:
       
        #Plot Parameters
        self.plot_choice = None
        self.IQenevlope_plot_choice = None

        #Modulation Parameters
        self.carrier_freq = carrier_freq
        self.modulation_mode = modulation_mode
        self.order = self.modulation_modes[modulation_mode]

        #Bit Rate Parameters
        self.baud_rate = bit_rate/self.order
        self.symbol_period = 1/self.baud_rate

        #Sampler Parameters 
        self.oversampling_factor = 10
        self.sampling_rate = self.oversampling_factor*2*self.carrier_freq # 10x Oversampling Factor for any CF 
        
    def msgchar2bit(self, msg):
        return list(''.join(f'{byte:08b}' for byte in msg.encode('utf-8')))

    def digitalsignal(self, bitstr):
        if len(bitstr) % self.order != 0:
            bitstr.extend(['0']*(self.order - len(bitstr) % self.order))

        bitstr.extend(['0', '0'])
        signal_duration = len(bitstr)*self.symbol_period
        x_axis_digital = np.linspace(0, signal_duration, len(bitstr), endpoint=False)
        digital_signal = np.array([int(bit) for bit in bitstr])
        print(f"Digital Signal: {''.join(bitstr)}")
        return digital_signal, x_axis_digital
    
    def modulate(self, bitstr):
        print("Calling Modulate")
        if self.modulation_mode == 'BPSK':
            return self.bpsk_modulation(bitstr)
        elif self.modulation_mode == 'QPSK':
            return self.qpsk_modulation(bitstr)
        else:
            return self.qam_modulation(bitstr)
        
    def bpsk_modulation(self, bitstr):
        print("BPSK Modulation running")
        I = np.array([2*int(bit)-1 for bit in bitstr[:-2]])
        Q = np.zeros_like(I)

        return self.modulator_calculations(I, Q, bitstr[:-2])

    def modulator_calculations(self, I, Q, bitgroups):
        samples_per_symbol = int(self.symbol_period * self.sampling_rate)
        RRC_delay = 3 * self.symbol_period

        # Simulated SRRC filter and pulse shaping (replace with actual filter for real use)
        _, rrc = commpy.filters.rrcosfilter(N=int(2*self.sampling_rate*RRC_delay),alpha=0.5,Ts=self.symbol_period, Fs=self.sampling_rate)
        shaped_pulse_length = len(bitgroups) * samples_per_symbol + len(rrc) - 1
        Shaped_Pulse = np.zeros(shaped_pulse_length, dtype=complex)
        Dirac_Comb = np.zeros(shaped_pulse_length, dtype=complex)

        for idx, (i_val, q_val) in enumerate(zip(I, Q)):
            start_idx = idx * samples_per_symbol
            Shaped_Pulse[start_idx:start_idx + len(rrc)] += (i_val + 1j * q_val) * rrc
            Dirac_Comb[start_idx] = i_val + 1j * q_val  # Place only at start of each symbol

        t_Shaped_Pulse = np.linspace(0, len(Shaped_Pulse) / self.sampling_rate, len(Shaped_Pulse), endpoint=False)

        ###Upscaling the signal to the carrier frequency###
        I_processed = Shaped_Pulse.real
        Q_processed = Shaped_Pulse.imag
        I_FC = I_processed * np.cos(2 * np.pi * self.carrier_freq * t_Shaped_Pulse)
        Q_FC = Q_processed * -np.sin(2 * np.pi * self.carrier_freq * t_Shaped_Pulse)
        
        return t_Shaped_Pulse, I_FC + Q_FC

    def digital_modulated_plot(self, bitstr, t_m_s, modulated_signal):
        '''
            Generate the MATPLOTLIB fig for the digital signal and the modulated signal

            Parameters:
            bitstr: str - The bitstring to be modulated
            t_m_s: np.array - Time array for the modulated signal
            modulated_signal: np.array - The modulated signal
        '''
        digimod_fig = Figure()
        ax1 = digimod_fig.add_subplot(211)  # Top subplot for digital signal
        ax2 = digimod_fig.add_subplot(212)  # Bottom subplot for modulated signal

        # Digital Signal
        digital_signal, x_axis_digital = self.digitalsignal(bitstr)

        ax1.step(x_axis_digital, digital_signal, where="post")
        ax1.vlines(x_axis_digital[::self.order], -0.5, 1.5, color='r', linestyle='--', alpha=0.5)
        ax1.set_ylabel("Digital Signal")
        ax1.set_title("Digital Signal")

        # Modulated Signal
        ax2.plot(t_m_s, modulated_signal)
        ax2.set_title(f"Modulated Signal: {self.modulation_mode}")
        ax2.set_ylabel("Amplitude")
        ax2.set_xlabel("Time (s)")

        return digimod_fig

    def save(self, filename, modulated_signal):
        
        #norm_modulated_signal = modulated_signal / np.max(np.abs(modulated_signal)) # Old Normalization
        print(np.max(np.abs(modulated_signal))) # Debug print - Max value of the modulated signal
        modulated_signal /= 2
        modulated_signal = np.array(modulated_signal, dtype=np.float32)

        wav.write(filename, self.sampling_rate, modulated_signal)
        print(f"Modulated signal saved as {filename}")
    
if __name__ == "__main__":
    pass

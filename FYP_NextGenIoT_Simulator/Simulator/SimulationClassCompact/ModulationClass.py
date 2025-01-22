import commpy.filters
from scipy.io import wavfile as wav
import numpy as np
import scipy.signal as sig
import pickle
import commpy


class Modulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
    
    def __init__(self, modulation_mode, bit_rate,carrier_freq) -> None:
        '''
            Initialize the Modulator class

            Parameters:
                modulation_mode (str): Modulation mode to be used. Can be 'BPSK', 'QPSK', 'QAM16', 'QAM64', 'QAM256', 'QAM1024', 'QAM4096'.
                bit_rate (int): Bit rate of the signal.
                carrier_freq (int): Carrier frequency of the signal.
        '''
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

        #IQ Return and Save Parameters
        self.IQ_Return = False
        self.save_signal = False

    @staticmethod
    def msgchar2bit_static(msg):
        '''
            Convert bits to characters

            Parameters:
                msg (str): Bit string to be converted to characters
        '''
        return list(''.join(f'{byte:08b}' for byte in msg.encode('utf-8')))
    
    def msgchar2bit(self, msg):
        '''
            Convert characters to bits

            Parameters:
                msg (str): Message to be converted to bits
        '''
        bitstr = list(''.join(f'{byte:08b}' for byte in msg.encode('utf-8')))

        if len(bitstr) % self.order != 0:
            bitstr.extend(['0']*(self.order - len(bitstr) % self.order))

        bitstr.extend(['0', '0'])

        return bitstr

    def digitalsignal(self, bitstr):
        '''
            Convert bits to digital signal

            Parameters:
                bitstr (str): Bit string to be converted to digital signal            
        '''
        signal_duration = len(bitstr)*self.symbol_period
        x_axis_digital = np.linspace(0, signal_duration, len(bitstr), endpoint=False)
        digital_signal = np.array([int(bit) for bit in bitstr])
        return digital_signal, x_axis_digital

    def modulate(self, bitstr):
        '''
            Modulate the digital signal

            Parameters:
                bitstr (str): Bit string to be modulated

            Returns:
                tuple: A tuple containing:
                    t_Shaped_Pulse (np.array): Time axis of the shaped pulse.
                    mixed (np.array): Mixed modulated signal with pulse shaping and carrier frequency upconversion.
                
            If `IQ_Return` is True, the function also returns:
                - I_FC (np.array): In-phase Upconverted component of the transmission signal.
                - Q_FC (np.array): Quadrature Upconverted component of the transmission signal.
                - I_processed (np.array): In-phase component of the pulse shaped signal.
                - Q_processed (np.array): Quadrature component of the pulse shaped signal.
                - Dirac_Comb (np.array): Dirac Comb impulse train.
                - RRC_delay (float): Delay due to the Root Raised Cosine Filter.
        '''
        if self.modulation_mode == 'BPSK':
            return self.__bpsk_modulation(bitstr)
        elif self.modulation_mode == 'QPSK':
            return self.__qpsk_modulation(bitstr)
        else:
            return self.__qam_modulation(bitstr)
        
    def __bpsk_modulation(self, bitstr):
        '''
            Modulate the digital signal using BPSK

            Parameters:
                bitstr (str): Bit string to be modulated
        '''
        
        I = np.array([2*int(bit)-1 for bit in bitstr[:-2]])
        Q = np.zeros_like(I)

        return self.__modulator_calculations(I, Q, bitstr[:-2])

    def __qpsk_modulation(self, bitstr):
        '''
            Modulate the digital signal using QPSK

            Parameters:
                bitstr (str): Bit string to be modulated
        '''

        bitgroups = [''.join(bitstr[i:i+self.order]) for i in range(0, len(bitstr[:-2]), self.order)]
        I = np.array([2*int(group[0])-1 for group in bitgroups])
        Q = np.array([2*int(group[1])-1 for group in bitgroups])

        return self.__modulator_calculations(I, Q, bitgroups)

    def __qam_modulation(self, bitstr):
        '''
            Modulate the digital signal using QAM - N

            Parameters:
                bitstr (str): Bit string to be modulated
        '''

        with open(rf'FYP_NextGenIoT_Simulator\QAM_LUT_pkl\N{self.modulation_mode}.pkl', 'rb') as f:
            qam_constellations = pickle.load(f)

        bitgroups = [''.join(bitstr[i:i+self.order]) for i in range(0, len(bitstr[:-2]), self.order)]

        I = np.array([qam_constellations[group]['I'] for group in bitgroups])
        Q = np.array([qam_constellations[group]['Q'] for group in bitgroups])

        return self.__modulator_calculations(I, Q, bitgroups)
    
    def __modulator_calculations(self, I, Q, bitgroups):
        """
            Performs the modulation calculations for the given I and Q components and bit groups.

            Args:
                I (np.array): In-phase component of the signal.
                Q (np.array): Quadrature component of the signal.
                bitgroups (list): List of bit groups of size `order`.

            Returns:
                tuple: A tuple containing:
                    t_Shaped_Pulse (np.array): Time axis of the shaped pulse.
                    mixed (np.array): Mixed modulated signal with pulse shaping and carrier frequency upconversion.
                
            If `IQ_Return` is True, the function also returns:
                - I_FC (np.array): In-phase Upconverted component of the transmission signal.
                - Q_FC (np.array): Quadrature Upconverted component of the transmission signal.
                - I_processed (np.array): In-phase component of the pulse shaped signal.
                - Q_processed (np.array): Quadrature component of the pulse shaped signal.
                - Dirac_Comb (np.array): Dirac Comb impulse train.
                - RRC_delay (float): Delay due to the Root Raised Cosine Filter.
        """

        samples_per_symbol = int(self.symbol_period * self.sampling_rate)
        RRC_delay = 3 * self.symbol_period

        # Simulated SRRC filter and pulse shaping (replace with actual filter for real use)
        _, rrc = commpy.filters.rrcosfilter(N=int(2*self.sampling_rate*RRC_delay),alpha=0.35,Ts=self.symbol_period, Fs=self.sampling_rate)
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

        if self.IQ_Return == True:
            return t_Shaped_Pulse, Shaped_Pulse, I_FC, Q_FC, I_processed, Q_processed, Dirac_Comb, RRC_delay
        
        return t_Shaped_Pulse, I_FC + Q_FC

    def save(self, filename, modulated_signal):
        '''
            Save the modulated signal to a WAV file

            Parameters:
                filename (str): Name of the file to be saved
                modulated_signal (np.array): Modulated signal to be saved
        '''
        assert self.save_signal == True, "Set save_signal to True to save the modulated signal before calling function."
        modulated_signal /= 2
        modulated_signal = np.array(modulated_signal, dtype=np.float32)

        wav.write(filename, self.sampling_rate, modulated_signal)
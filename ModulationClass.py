import commpy.filters
from matplotlib import pyplot as plt
import numpy as np
import pickle
import commpy

class Modulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}

    def __init__(self, modulation_mode, bit_rate,carrier_freq) -> None:
        self.sampling_rate = 2*2*carrier_freq # 2x Oversampling Factor for any CF
        self.carrier_freq = carrier_freq
        self.modulation_mode = modulation_mode
        self.order = self.modulation_modes[modulation_mode]
        self.plot_choice = None
        self.IQenevlope_plot_choice = None
        self.fig, self.ax = self.setup_plot()
        self.baud_rate = bit_rate/self.order
        self.symbol_period = 1/self.baud_rate

    def setup_plot(self):
        self.plot_choice = input("Do you want to plot I and Q? (Y/N): ").upper() if self.modulation_mode[:2] == 'QAM' or self.modulation_mode == "QPSK"  else 'N'
        num_plots = 3 if self.plot_choice == 'Y' else 2
        return plt.subplots(num_plots, 1, constrained_layout=True)
        
    def msgchar2bit(self, msg):
        return list(''.join(f'{byte:08b}' for byte in msg.encode('utf-8')))

    def digitalsignal(self, bitstr):
        bitstr.extend(['0', '0'])
        signal_duration = len(bitstr) / self.order / self.carrier_freq
        x_axis_digitalsig, _ = np.linspace(0, signal_duration, len(bitstr), retstep=True, endpoint=False)
        return bitstr, x_axis_digitalsig
    
    def modulate(self, bitstr):
        if self.modulation_mode == 'BPSK':
            return self.bpsk_modulation(bitstr)
        elif self.modulation_mode == 'QPSK':
            return self.qpsk_modulation(bitstr)
        else:
            return self.qam_modulation(bitstr)
        
    def bpsk_modulation(self, bitstr):
        pass

    def qpsk_modulation(self, bitstr):
        pass

    def qam_modulation(self, bitstr):
        assert len(bitstr) % self.order == 0, f"{self.modulation_mode} requires symbol size {self.order}. Got {len(bitstr)} bits."

        with open(rf'QAM_LUT_pkl\{self.modulation_mode}.pkl', 'rb') as f:
            qam_constellations = pickle.load(f)

        bitgroups = [''.join(bitstr[i:i+self.order]) for i in range(0, len(bitstr), self.order)]

        I = np.array([qam_constellations[group]['I'] for group in bitgroups])
        Q = np.array([qam_constellations[group]['Q'] for group in bitgroups])

        self.IQenevlope_plot_choice = input("Do you want to plot I and Q? (Y/N): ").upper()

        return self.qam_calculations(I, Q, bitgroups)

    def qam_calculations(self, I, Q, bitgroups):
        '''Simulation of the Digital Baseband Signal to Analog Modulation''' 
        samples_per_symbol = int(24*self.symbol_period*self.carrier_freq) 

        Dirac_Comb = np.zeros(len(bitgroups)*samples_per_symbol,dtype=complex)
        Dirac_Comb[::samples_per_symbol] = I + 1j*Q
        t_Dirac_Comb = np.linspace(0,len(Dirac_Comb)/self.sampling_rate,len(Dirac_Comb),endpoint=False)

        '''FFT of Dirac_Comb will show ISI due to the Dirac Comb function, thus filter with SRRC to remove ISI'''
        RRC_delay = 3*self.symbol_period
        _, rrc = commpy.filters.rrcosfilter(N=int(2*self.sampling_rate*RRC_delay),alpha=0.5,Ts=self.symbol_period, Fs=self.sampling_rate)
        
        Shaped_Pulse = np.convolve(Dirac_Comb,rrc) #Pulse shaped signal, convolving SRRC over the Dirac Comb function
        t_Shaped_Pulse = np.linspace(0,len(Shaped_Pulse)/self.sampling_rate,len(Shaped_Pulse),endpoint=False)
        
        '''Upscaling the signal to the carrier frequency'''
        I_processed = Shaped_Pulse.real
        Q_processed = Shaped_Pulse.imag
        I_FC = I_processed  *  np.cos(2*np.pi*self.carrier_freq*t_Shaped_Pulse)
        Q_FC = Q_processed  * -np.sin(2*np.pi*self.carrier_freq*t_Shaped_Pulse)

        if self.IQenevlope_plot_choice == 'Y':
            self.plot_IQ_internal(t_Dirac_Comb, Dirac_Comb, t_Shaped_Pulse, Shaped_Pulse, I_FC, Q_FC, I_processed, Q_processed, RRC_delay)

        return t_Shaped_Pulse,  I_FC + Q_FC

    def plot_IQ_internal(self, t_Dirac_Comb, Dirac_Comb, t_Shaped_Pulse, Shaped_Pulse, I_FC, Q_FC, I_processed, Q_processed, RRC_delay):
        fig, ax = plt.subplots(4, 2, constrained_layout=True)
        ax[0,0].plot((t_Dirac_Comb+RRC_delay)/self.symbol_period, Dirac_Comb.real, label='$x(t)$') # artificial extra delay for the baseband samples
        ax[0,0].plot(t_Shaped_Pulse/self.symbol_period, Shaped_Pulse.real, label='$u(t)$')
        ax[0,0].set_title("Real Part")
        ax[0,1].plot((t_Dirac_Comb+RRC_delay)/self.symbol_period, Dirac_Comb.imag)
        ax[0,1].plot(t_Shaped_Pulse/self.symbol_period, Shaped_Pulse.imag)
        ax[0,1].set_title("Imaginary Part")
        
        ax[1,0].plot(t_Shaped_Pulse,I_FC)
        ax[1,0].plot(t_Shaped_Pulse,I_processed)
        ax[1,0].set_title("I Signal")
        ax[1,0].set_ylabel("Amplitude")
        ax[1,0].set_xlabel("Time (s)")
        ax[1,1].plot(t_Shaped_Pulse,Q_FC)
        ax[1,1].plot(t_Shaped_Pulse,Q_processed)
        ax[1,1].set_title("Q Signal")
        ax[1,1].set_ylabel("Amplitude")
        ax[1,1].set_xlabel("Time (s)")

    def plot_digital_signal(self,bitstr):
        digital_signal, x_axis_digital = self.digitalsignal(bitstr)
        self.ax[0].step(x_axis_digital, digital_signal, where="post")
        self.ax[0].vlines(x_axis_digital[::self.order], -0.5, 1.5, color='r', linestyle='--', alpha=0.5)
        #self.ax[0].set_xticks(x_axis_digital)
        self.ax[0].set_ylabel("Digital Signal")



def main():
    message = input("Enter the message: ")
    while True:
        try:
            carrier_freq = int(input("Enter the carrier frequency: "))
            break
        except KeyboardInterrupt:
            exit()
        except:
            print("Invalid carrier frequency. Please re-enter.")

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
        if mod_mode_select in Modulator.modulation_modes:
            break
        print("Invalid modulation mode. Please reselect.")

    modulator = Modulator(mod_mode_select,bit_rate=bit_rate,carrier_freq=carrier_freq)
    bitstring = modulator.msgchar2bit(message)
    modulator.modulate(bitstring)

    print(bitstring)

    modulator.plot_digital_signal(bitstring)
    plt.show()


if __name__ == "__main__":
    main()

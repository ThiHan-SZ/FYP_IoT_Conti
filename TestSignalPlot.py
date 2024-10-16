from matplotlib import pyplot as plt
import numpy as np
import math
import scipy as sp

# For the purposes of this we will use a singal power of unity


mod_mode = {'BPSK':1, 'QPSK':2, '16QAM':4, '64QAM':6}

transmit_carrier_freq = 10
class Modulator:
    def __init__(self, input = "Hello World!", carrier_freq = transmit_carrier_freq, mod_mode_select = 'BPSK'):
        self.input = input
        self.carrier_freq = carrier_freq
        self.period = 1/carrier_freq
        self.mod_mode_select = mod_mode_select
        self.digitalSig = np.array([])
        self.graphres = (1/self.carrier_freq)/1000
        self.check = False

    def GenerateSignals(self):
        symbolrate = mod_mode[self.mod_mode_select]
        graphtime, bitstr = self.UserChar2BitStream(self.input, self.mod_mode_select)
        digitaltransmission = self.DigitalSignal(bitstr)

        match self.mod_mode_select:
            case 'BPSK':
                modulated = self.BPSKModulation(bitstr, self.carrier_freq)
            case 'QPSK':
                modulated = self.QPSKModulation(bitstr, self.carrier_freq)
            case '16QAM':
                modulated = self.QAM16Modulation(bitstr, self.carrier_freq)
            case '64QAM':
                modulated = self.QAM64Modulation(bitstr, self.carrier_freq)

        modulated = np.pad(modulated, (0, len(graphtime) - len(modulated)), 'constant', constant_values=(0,0))
        digitaltransmission = np.pad(digitaltransmission, (0, len(graphtime) - len(digitaltransmission)), 'constant', constant_values=(0,0))

        return graphtime, digitaltransmission, modulated
    
    def ModulatedPlot(self):
        graphtime, digitaltransmission, modulated = self.GenerateSignals()
        
        fig, (ax1,ax2) = plt.subplots(2, 1)
        ax1.plot(graphtime, digitaltransmission)
        ax1.set_title("Digital Signal")
        ax1.set_ylabel("Amplitude")

        ax1.vlines(x= graphtime[::int(self.period/self.graphres)], ymin = -0.5, ymax = 1.5, colors = 'r', linestyles = 'dashed',alpha=0.5)
        ax2.plot(graphtime, modulated)
        ax2.set_title("Modulated Signal")
        ax2.set_ylabel("Amplitude")
        ax2.vlines(x= graphtime[::int(self.period/self.graphres)], ymin = -1.5, ymax = 1.5, colors = 'r', linestyles = 'dashed',alpha=0.5)
        ax2.set_xlabel("Time (s)")
        plt.show()


    def UserChar2BitStream(self, input = "Hello World!", mod_mode_select = 'BPSK'):
        symbolrate = mod_mode[mod_mode_select] #Select the symbol rate based on the modulation mode
        
        strbytes = input.encode('utf-8') #Convert the input string to binary
        strbit = ''.join(f'{byte:08b}' for byte in strbytes) #Convert the binary string to a bit string

        symbol_period = self.period/symbolrate #Calculate the time period of the carrier wave, translates to the time per symbol
        graph_time = np.arange(0, math.ceil(len(strbit)/10)*10*symbol_period + self.graphres, self.graphres) #Create the time axis for the graph
        
        return graph_time, strbit

    def DigitalSignal(self, bitstream):
        symbolrate = mod_mode[self.mod_mode_select] #Select the symbol rate based on the modulation mode
        symbol_period = self.period/symbolrate 
        wavegenarr = np.arange(0, symbol_period, self.graphres)
        digitaltransmission = np.array([])
        for i in range(len(bitstream)):
            if bitstream[i] == '0':
                bit_sig = np.zeros(len(wavegenarr))
            else:
                bit_sig = np.ones(len(wavegenarr))
            digitaltransmission = np.append(digitaltransmission, bit_sig)
        return digitaltransmission
    
    def BPSKModulation(self, bitstream, carrier_freq = transmit_carrier_freq):
        assert len(bitstream)>0, "BPSK requires bits"  
        wavegenarr = np.arange(0, self.period, self.graphres) #Create the time axis for the carrier wave
        modulatedtransmission = np.array([])
        for i in range(len(bitstream)):
            mod_bit_sig = (2*int(bitstream[i])-1)*np.cos(2 * np.pi * carrier_freq * wavegenarr) #Modulate the bitstream
            modulatedtransmission = np.append(modulatedtransmission, mod_bit_sig)
        return modulatedtransmission
    
    def QPSKModulation(self, bitstream, carrier_freq = transmit_carrier_freq):
        assert len(bitstream) % 2 == 0, "QPSK requires an even number of bits"
        wavegenarr = np.arange(0, self.period, self.graphres)
        modulatedtransmission = np.array([])
        Primary = bitstream[0::2]
        Quadrature = bitstream[1::2]
        for i in range(0, len(Primary)):
            mod_bit_sig = (np.sqrt(1/2))*(int(Primary[i])*2-1) * np.cos(2 * np.pi * carrier_freq * wavegenarr) + (np.sqrt(1/2))*(int(Quadrature[i])*2-1) * np.sin(2 * np.pi * carrier_freq * wavegenarr) #Modulate the bitstream in quadrature form
            modulatedtransmission = np.append(modulatedtransmission, mod_bit_sig)
        return modulatedtransmission
    
    def QAM16Modulation(self, bitstream, carrier_freq = transmit_carrier_freq):
        assert len(bitstream) % 4 == 0, "16QAM requires an even number of bits with group size 4"
        wavegenarr = np.arange(0, self.period, self.graphres)
        modulatedtransmission = np.array([])
        bit1 = bitstream[0::4]
        bit2 = bitstream[1::4]
        bit3 = bitstream[2::4]
        bit4 = bitstream[3::4]


    

if __name__ == "__main__":
    inputmessage = input("Enter the message to be transmitted: ")
    carrier_freq = float(input("Enter the carrier frequency: "))
    try:
        mod_mode_select = input("Enter the modulation mode (BPSK, QPSK, 8PSK, 16QAM, 64QAM): ").upper()
        mod_test = mod_mode[mod_mode_select]
    except:
        print("Invalid modulation mode. Defaulting to BPSK.")
        mod_mode_select = 'BPSK'

    Modulator = Modulator(inputmessage, carrier_freq, mod_mode_select)
    Modulator.ModulatedPlot()




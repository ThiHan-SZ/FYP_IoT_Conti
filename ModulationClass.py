from matplotlib import pyplot as plt
import numpy as np
import math
import scipy as sp
import pickle

# For the purposes of this we will use a singal power of unity


mod_mode = {'BPSK':1, 'QPSK':2, '16QAM':4, '64QAM':6, '256QAM':8 , '1024QAM':10, '4096QAM':12}

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
            case '256QAM':
                modulated = self.QAM256Modulation(bitstr, self.carrier_freq)
            case '1024QAM':
                modulated = self.QAM1024Modulation(bitstr, self.carrier_freq)
            case '4096QAM':
                modulated = self.QAM4096Modulation(bitstr, self.carrier_freq)

        modulated = np.pad(modulated, (0, len(graphtime) - len(modulated)), 'constant', constant_values=(0,0))
        digitaltransmission = np.pad(digitaltransmission, (0, len(graphtime) - len(digitaltransmission)), 'constant', constant_values=(0,0))

        return graphtime, digitaltransmission, modulated
    
    def ModulatedPlot(self):
        graphtime, digitaltransmission, modulated = self.GenerateSignals()
        
        fig, (ax1,ax2) = plt.subplots(2, 1, constrained_layout=True)
        ax1.plot(graphtime, digitaltransmission)
        ax1.set_title("Digital Signal")
        ax1.set_ylabel("Amplitude")

        ax1.vlines(x= graphtime[::int(self.period/self.graphres)], ymin = -0.5, ymax = 1.5, colors = 'r', linestyles = 'dashed',alpha=0.5)
        ax2.plot(graphtime, modulated)
        ax2.set_title(f'Modulated Signal : {self.mod_mode_select}')
        ax2.set_ylabel("Amplitude")
        ax2.vlines(x= graphtime[::int(self.period/self.graphres)], ymin = -max(modulated)-1, ymax = max(modulated)+1, colors = 'r', linestyles = 'dashed',alpha=0.5)
        ax2.set_xlabel("Time (s)")
        plt.show()


    def UserChar2BitStream(self, input = "Hello World!", mod_mode_select = 'BPSK'):
        symbolrate = mod_mode[mod_mode_select] #Select the symbol rate based on the modulation mode
        
        strbytes = input.encode('utf-8') #Convert the input string to binary
        strbit = ''.join(f'{byte:08b}' for byte in strbytes) #Convert the binary string to a bit string

        bit_period = self.period/symbolrate #Calculate the time period of the carrier wave, translates to the time per symbol
        graph_time = np.arange(0, math.ceil(len(strbit)/10)*10*bit_period + self.graphres, self.graphres) #Create the time axis for the graph
        
        return graph_time, strbit

    def DigitalSignal(self, bitstream):
        symbolrate = mod_mode[self.mod_mode_select] #Select the symbol rate based on the modulation mode
        bit_period = self.period/symbolrate 
        wavegenarr = np.arange(0, bit_period, self.graphres)
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
        InPhase = bitstream[0::2]
        Quadrature = bitstream[1::2]
        for i in range(0, len(InPhase)):
            mod_bit_sig = (np.sqrt(1/2))*(int(InPhase[i])*2-1) * np.cos(2 * np.pi * carrier_freq * wavegenarr) + (np.sqrt(1/2))*(int(Quadrature[i])*2-1) * np.sin(2 * np.pi * carrier_freq * wavegenarr) #Modulate the bitstream in quadrature form
            modulatedtransmission = np.append(modulatedtransmission, mod_bit_sig)
        return modulatedtransmission
    
    def QAM16Modulation(self, bitstream, carrier_freq = transmit_carrier_freq):
        assert len(bitstream) % 4 == 0, "16QAM requires an even number of bits with group size 4"
        with open('QAM16.pkl', 'rb') as f:
            QAM16 = pickle.load(f)
        wavegenarr = np.arange(0, self.period, self.graphres)
        modulatedtransmission = np.array([])
        bitgroup = [bitstream[i:i+4] for i in range(0, len(bitstream), 4)]
        for group in bitgroup:
            mod_bit_sig = (QAM16[group]['I']) * np.cos(2 * np.pi * carrier_freq * wavegenarr) + (QAM16[group]['Q']) * np.sin(2 * np.pi * carrier_freq * wavegenarr)
            modulatedtransmission = np.append(modulatedtransmission, mod_bit_sig)
        return modulatedtransmission   

    def QAM64Modulation(self, bitstream, carrier_freq = transmit_carrier_freq):
        assert len(bitstream) % 6 == 0, "64QAM requires an even number of bits with group size 6| Got length: " + str(len(bitstream))
        with open('QAM64.pkl', 'rb') as f:
            QAM64 = pickle.load(f)
        wavegenarr = np.arange(0, self.period, self.graphres)
        modulatedtransmission = np.array([])
        bitgroup = [bitstream[i:i+6] for i in range(0, len(bitstream), 6)]
        for group in bitgroup:
            mod_bit_sig = (QAM64[group]['I']) * np.cos(2 * np.pi * carrier_freq * wavegenarr) + (QAM64[group]['Q']) * np.sin(2 * np.pi * carrier_freq * wavegenarr)
            modulatedtransmission = np.append(modulatedtransmission, mod_bit_sig)
        return modulatedtransmission

    def QAM256Modulation(self, bitstream, carrier_freq = transmit_carrier_freq):
        assert len(bitstream) % 8 == 0, "256QAM requires an even number of bits with group size 8| Got length: " + str(len(bitstream))
        with open('QAM256.pkl', 'rb') as f:
            QAM256 = pickle.load(f)
        wavegenarr = np.arange(0, self.period, self.graphres)
        modulatedtransmission = np.array([])
        bitgroup = [bitstream[i:i+8] for i in range(0, len(bitstream), 8)]
        for group in bitgroup:
            mod_bit_sig = (QAM256[group]['I']) * np.cos(2 * np.pi * carrier_freq * wavegenarr) + (QAM256[group]['Q']) * np.sin(2 * np.pi * carrier_freq * wavegenarr)
            modulatedtransmission = np.append(modulatedtransmission, mod_bit_sig)
        return modulatedtransmission 
    
    def QAM1024Modulation(self, bitstream, carrier_freq = transmit_carrier_freq):
        assert len(bitstream) % 10 == 0, "1024QAM requires an even number of bits with group size 10| Got length: " + str(len(bitstream))
        with open('QAM1024.pkl', 'rb') as f:
            QAM1024 = pickle.load(f)
        wavegenarr = np.arange(0, self.period, self.graphres)
        modulatedtransmission = np.array([])
        bitgroup = [bitstream[i:i+10] for i in range(0, len(bitstream), 10)]
        for group in bitgroup:
            mod_bit_sig = (QAM1024[group]['I']) * np.cos(2 * np.pi * carrier_freq * wavegenarr) + (QAM1024[group]['Q']) * np.sin(2 * np.pi * carrier_freq * wavegenarr)
            modulatedtransmission = np.append(modulatedtransmission, mod_bit_sig)
        return modulatedtransmission
    
    def QAM4096Modulation(self, bitstream, carrier_freq = transmit_carrier_freq):
        assert len(bitstream) % 12 == 0, "4096QAM requires an even number of bits with group size 12| Got length: " + str(len(bitstream))
        with open('QAM4096.pkl', 'rb') as f:
            QAM4096 = pickle.load(f)
        wavegenarr = np.arange(0, self.period, self.graphres)
        modulatedtransmission = np.array([])
        bitgroup = [bitstream[i:i+12] for i in range(0, len(bitstream), 12)]
        for group in bitgroup:
            mod_bit_sig = (QAM4096[group]['I']) * np.cos(2 * np.pi * carrier_freq * wavegenarr) + (QAM4096[group]['Q']) * np.sin(2 * np.pi * carrier_freq * wavegenarr)
            modulatedtransmission = np.append(modulatedtransmission, mod_bit_sig)
        return modulatedtransmission

if __name__ == "__main__":
    inputmessage = input("Enter the message to be transmitted: ")
    if inputmessage == "":
        inputmessage = "Hello World!"
    carrier_freq = float(input("Enter the carrier frequency: "))
    mod_mode_flag = False
    while not mod_mode_flag:
        try:
            mod_mode_select = input("Enter the modulation mode (BPSK, QPSK, 8PSK, 16/64/256/1024/4096 QAM): ").upper()
            mod_test = mod_mode[mod_mode_select]
            mod_mode_flag = True
        except:
            print("Invalid modulation mode. Please reselect mode.")

    Modulator = Modulator(inputmessage, carrier_freq, mod_mode_select)
    Modulator.ModulatedPlot()




from SimulationClass.ModulationClass import Modulator as SimMod
from SimulationClass.DemodulationClass import Demodulator as SimDemod
from SimulationClass.ChannelClass import SimpleGWNChannel_dB
import matplotlib.pyplot as plt
import numpy as np

# Test All Modulation Types (BPSK, QPSK, QAM16, QAM64, QAM256, QAM1024, QAM4096)
# Message will be standardised 
# Carrier Frequency will be 18kHz
# Bit Rate will be 1800bps

modulatorBPSK = SimMod('BPSK', 1800, 18e3)
modulatorQPSK = SimMod('QPSK', 1800, 18e3)
modulatorQAM16 = SimMod('QAM16', 1800, 18e3)
modulatorQAM64 = SimMod('QAM64', 1800, 18e3)
modulatorQAM256 = SimMod('QAM256', 1800, 18e3)
modulatorQAM1024 = SimMod('QAM1024', 1800, 18e3)
modulatorQAM4096 = SimMod('QAM4096', 1800, 18e3)

demodulatorBPSK = SimDemod('BPSK', 1800, 18e3)
demodulatorQPSK = SimDemod('QPSK', 1800, 18e3)
demodulatorQAM16 = SimDemod('QAM16', 1800, 18e3)
demodulatorQAM64 = SimDemod('QAM64', 1800, 18e3)
demodulatorQAM256 = SimDemod('QAM256', 1800, 18e3)
demodulatorQAM1024 = SimDemod('QAM1024', 1800, 18e3)
demodulatorQAM4096 = SimDemod('QAM4096', 1800, 18e3)

Dict_ofModems = {
    'BPSK': (modulatorBPSK, demodulatorBPSK),
    'QPSK': (modulatorQPSK, demodulatorQPSK),
    'QAM16': (modulatorQAM16, demodulatorQAM16),
    'QAM64': (modulatorQAM64, demodulatorQAM64),
    'QAM256': (modulatorQAM256, demodulatorQAM256),
    'QAM1024': (modulatorQAM1024, demodulatorQAM1024),
    'QAM4096': (modulatorQAM4096, demodulatorQAM4096)
}

Dict_ofModulatedSignals = {
    'BPSK': (None,None),
    'QPSK': (None,None),
    'QAM16': (None,None),
    'QAM64': (None,None),
    'QAM256': (None,None),
    'QAM1024': (None,None),
    'QAM4096': (None,None)
}

Dict_ofBER = {
    'BPSK': [],
    'QPSK': [],
    'QAM16': [],
    'QAM64': [],
    'QAM256': [],
    'QAM1024': [],
    'QAM4096': []
}

# Test BPSK Modulation
msg = input("Enter the bit string to be modulated: ")

SNR = int(input("Enter the SNR limit in dB: "))

SNR_test_range = np.linspace(0,SNR,np.abs(SNR*16))

bitstr = SimMod.msgchar2bit(msg)
int_bitstr = np.array([int(bit) for bit in bitstr])

for mode,(modulator,demodulator) in Dict_ofModems.items():
    digital_signal, x_axis_digital = modulator.digitalsignal(bitstr)
    
    if modulator.deep_return != True:
        t_axis, modualted_sig = modulator.modulate(bitstr)
    else:
        t_axis, modualted_sig, I_FC, Q_FC, I_SP, Q_SP, Dirac_Comb, RRC_Delay = modulator.modulate(bitstr)
    
    Dict_ofModulatedSignals[modulator.modulation_mode] = (t_axis, modualted_sig)
    
    for i in SNR_test_range:
        channel = SimpleGWNChannel_dB(i)
        noisy_signal = channel.add_noise(modualted_sig)
        demod_signal = demodulator.demodulate(noisy_signal)
        RXmessage, demod_bitstr = demodulator.demapping(demod_signal)
        
        BER = ((int_bitstr == demod_bitstr[:len(int_bitstr)]).mean() * 100)
        Dict_ofBER[modulator.modulation_mode].append(BER)

plt.plot(SNR_test_range, Dict_ofBER['BPSK'], label='BPSK')
plt.plot(SNR_test_range, Dict_ofBER['QPSK'], label='QPSK')
plt.plot(SNR_test_range, Dict_ofBER['QAM16'], label='QAM16')
plt.plot(SNR_test_range, Dict_ofBER['QAM64'], label='QAM64')
plt.plot(SNR_test_range, Dict_ofBER['QAM256'], label='QAM256')
plt.plot(SNR_test_range, Dict_ofBER['QAM1024'], label='QAM1024')
plt.plot(SNR_test_range, Dict_ofBER['QAM4096'], label='QAM4096')
plt.xlabel('SNR (dB)')
plt.ylabel('BER (%)')
plt.title('BER vs SNR')
plt.legend()
plt.show()




'''demod_signal = demodulator.demodulate(modualted_sig)
RXmessage, demod_bitstr = demodulator.demapping(demod_signal)

BER = (int_bitstr == demod_bitstr[:len(int_bitstr)]).mean() * 100
print(f'Message from {mode} Demodulation: {RXmessage}')
print(f'BER of {modulator.modulation_mode} Modulation: {BER}%')'''

from matplotlib import pyplot as plt
import numpy as np
import math
import pickle


class Modulator:
    modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}

    def __init__(self,message) -> None:
        self.message = message
        self.bitstring = np.array(list(self.msgchar2bit(message)))

    def msgchar2bit(self, msg):
        bitstring = ''.join(f'{byte:08b}' for byte in msg.encode('utf-8'))
        return bitstring
    
    def digitalsignal(self, bitstr):
        bitstr.append(bitstr[-1])
        x_axis_digitalsig = np.linspace(0,1,len(bitstr))
        return bitstr, x_axis_digitalsig
    
    


message = input("Enter Msg : ")





bitstring = list(msgchar2bit(message))

strlen = len(bitstring)
bps = 8
transmission_duration = strlen/bps
print(bitstring)


fig, ax = plt.subplots(2,1,constrained_layout=True)
ax[0].step(np.linspace(0,transmission_duration, strlen+1),digitalsignal(bitstring),where="post")
ax[0].set_xticks(np.linspace(0,transmission_duration, strlen+1))
plt.show()

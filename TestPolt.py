import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter

carrier_freq = 10
period = 1/carrier_freq
graphres = 0.001

graphtime = np.arange(0, period*8, graphres)
wavegenarr = np.arange(0, period, graphres)
modulatedtransmission = np.array([])
bitstream = '0010110101100101'
bitstream1 = bitstream[0::2]
bitstream2 = bitstream[1::2]
for i in range(0, len(bitstream1)):
    if bitstream2[i] == '0':
        mod_bit_sig = -np.sin(2 * np.pi * carrier_freq * wavegenarr)
    else:
        mod_bit_sig = np.sin(2 * np.pi * carrier_freq * wavegenarr)
    if bitstream1[i] == '0':
        mod_bit_sig += -np.cos(2 * np.pi * carrier_freq * wavegenarr)
    else:
        mod_bit_sig += np.cos(2 * np.pi * carrier_freq * wavegenarr)
    modulatedtransmission = np.append(modulatedtransmission, mod_bit_sig)
    

'''for i in range(0, len(bitstream), 2):
    if bitstream[i] == '0':
        if bitstream[i+1] == '0':
            mod_bit_sig = np.sin(2 * np.pi * carrier_freq * wavegenarr + np.pi/4)
        else:
            mod_bit_sig = np.sin(2 * np.pi * carrier_freq * wavegenarr + 7*np.pi/4)
    else:
        if bitstream[i+1] == '0':
            mod_bit_sig = np.sin(2 * np.pi * carrier_freq * wavegenarr + 3*np.pi/4)
        else:
            mod_bit_sig = np.sin(2 * np.pi * carrier_freq * wavegenarr + 5*np.pi/4)'''

plt.plot(graphtime, modulatedtransmission)

plt.grid(True)

plt.show()
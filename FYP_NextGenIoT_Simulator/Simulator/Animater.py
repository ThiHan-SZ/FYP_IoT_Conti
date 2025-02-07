import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import scipy.signal as sig
from SimulationClassCompact.RRCFilter import RRCFilter
from SimulationClassCompact.ChannelClass import *
from SimulationClassCompact.ModulationClass import Modulator
from SimulationClassCompact.DemodulationClass import Demodulator

modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
mod_type = 'QPSK'
sys.path.insert(1, r"FYP_NextGenIoT_Simulator\Simulator")

import pickle
import scipy.spatial as spysp
import scipy.io.wavfile as wav
import commpy

'''with open(f'FYP_NextGenIoT_Simulator/QAM_LUT_pkl/R{mod_type}.pkl', 'rb') as file:
    qam_const = pickle.load(file)
qam_tree = spysp.KDTree([k for k in qam_const.keys()])

keys = qam_const.keys()'''

sampling_rate , signal = wav.read(rf'FYP_NextGenIoT_Simulator\WaveFiles\user_file\user_file__5010Char2BUTF8__200kHz_16kbps_{mod_type}.wav')

signal *= 2

order = modulation_modes[mod_type]

demodulator = Demodulator(mod_type,16000,sampling_rate)

signalDemod1 = demodulator.demodulate(signal)[:-(6*demodulator.samples_per_symbol)]

delayChannel = SimpleDelayChannel(0.1)
delayChanelDemod1 = demodulator.demodulate(delayChannel.add_delay(signal))[:-(6*demodulator.samples_per_symbol)]

guide_Symbols = signalDemod1[demodulator.demodulator_total_delay::demodulator.samples_per_symbol]
bbSymbols = delayChanelDemod1[demodulator.demodulator_total_delay::demodulator.samples_per_symbol]

fig, ax = plt.subplots()
scatter = ax.scatter(bbSymbols[0].real, bbSymbols[0].imag, label='First Symbols', c='b',s=45)
scatter_current = ax.scatter(bbSymbols[0].real, bbSymbols[0].imag, label='First Current Symbol', c='r',s=15)

scatter_guide = ax.scatter(guide_Symbols[0].real, guide_Symbols[0].imag, label='Guide Symbols', c='purple',s=45)
scatter_guide_current = ax.scatter(guide_Symbols[0].real, guide_Symbols[0].imag, label='Guide Current Symbol', c='y',s=15)

scaler = ((2**(order/2))-1) if order > 2 else 1
x_ticks = np.arange(-scaler, scaler+1, 2)
y_ticks = np.arange(-scaler, scaler+1, 2)

ax.set(xlim=[x_ticks.min()-2, x_ticks.max()+2], ylim=[y_ticks.min()-2, y_ticks.max()+2], xlabel='I', ylabel='Q')
ax.grid(True)
scaler = ((2**(order/2))-1) if order > 2 else 1
x_ticks = np.arange(-scaler, scaler+1, 2)
y_ticks = np.arange(-scaler, scaler+1, 2)
ax.set_xticks(x_ticks)
ax.set_yticks(y_ticks)

# Function to update the scatter plot
def update(frame):
    # Update the scatter plot data
    bb_symbols = bbSymbols[:frame]
    guide_Symbolsframe = guide_Symbols[:frame]

    bb_current = bbSymbols[frame-1]
    guide_Symbols_current = guide_Symbols[frame-1]

    bb_symbols = np.column_stack((bb_symbols.real, bb_symbols.imag))
    bb_current = np.column_stack((bb_current.real, bb_current.imag))

    guide_Symbolsframe = np.column_stack((guide_Symbolsframe.real, guide_Symbolsframe.imag))
    guide_Symbols_current  = np.column_stack((guide_Symbols_current.real, guide_Symbols_current.imag))
    
    scatter.set_offsets(bb_symbols)
    scatter_current.set_offsets(bb_current)

    scatter_guide.set_offsets(guide_Symbolsframe)
    scatter_guide_current.set_offsets(guide_Symbols_current)
    
    fig.suptitle(f"Symbols {frame-5} to {frame}")
    fig.legend(['Decoded Symbols','Current Decoded Symbol', 'Guide Symbols', 'Current Guide Symbol'])
    # Return the artists to be updated
    return scatter, scatter_guide
# Create the animation
frames = len(bbSymbols[:2500])
ani = animation.FuncAnimation(fig, update, frames=frames, interval=1000)
# Show the animation
plt.show()
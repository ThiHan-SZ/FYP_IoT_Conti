import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import scipy.signal as sig 
from matplotlib.widgets import Button


'''# Define parameters
Ts = 1/2000
time = 0.3
t = np.arange(0, time, Ts)  # time vector

f0 = 200
phoff = np.pi/2  # carrier freq. and phase
fc = 200  # assumed freq. at receiver

# Generate received signal
rp = np.cos(2*np.pi*fc*t + phoff)

# Define filter parameters
fl = 100
ff = np.array([0, 0.01, 0.02, 1])
fa = np.array([1, 1, 0, 0])

# Design LPF using firpm equivalent (scipy.signal.firwin)
h = sig.firwin2(fl+1, ff,fa)

# Define algorithm parameters
mu = 0.01  # algorithm stepsize

# Initialize vectors
theta = np.zeros(len(t))
theta[0] = 0  # initialize vector for estimates
z = np.zeros(fl+1)  # initialize buffer for LPF

# Initialize VCO output vector
VCO = np.zeros(len(t))

# Main loop
for k in range(len(t)-1):
    VCO[k] = np.sin(2*np.pi*f0*t[k] + theta[k])
    z = np.roll(z, -1)  # shift buffer
    z[-1] = rp[k]*VCO[k]
    update = np.flipud(h).dot(z)  # new output of LPF
    theta[k+1] = theta[k] - mu*update  # algorithm update
    
fig,axs = plt.subplots(3,1)
axs[0].plot(t, np.cos(2*np.pi*fc*t))
axs[0].plot(t, VCO)
axs[0].legend(['Carrier','VCO'])
axs[1].plot(t, VCO)
axs[2].plot(t, theta)
plt.show()'''

modulation_modes = {'BPSK': 1, 'QPSK': 2, 'QAM16': 4, 'QAM64': 6, 'QAM256': 8, 'QAM1024': 10, 'QAM4096': 12}
mod_type = 'QAM64'

sys.path.insert(1, r"FYP_NextGenIoT_Simulator\Simulator")
import pickle
import scipy.spatial as spysp
import scipy.io.wavfile as wav
import commpy
with open(f'FYP_NextGenIoT_Simulator/QAM_LUT_pkl/R{mod_type}.pkl', 'rb') as file:
    qam_const = pickle.load(file)

qam_tree = spysp.KDTree([k for k in qam_const.keys()])
keys = qam_const.keys()
sampling_rate ,modc = wav.read(rf'FYP_NextGenIoT_Simulator\WaveFiles\test_file__AsciiTabletxt__200kHz_16kbps_N{mod_type}.wav')
_  ,modr = wav.read(rf'FYP_NextGenIoT_Simulator\WaveFiles\test_file__AsciiTabletxt__200kHz_16kbps_N{mod_type}.wav')

modr*=2
modc*=2

order = modulation_modes[mod_type]
CARRIER = 2e5
baud_rate = 16000/order
symbol_period = 1/baud_rate
samples_per_symbol = int(sampling_rate/baud_rate)

Nyquist_Bandwidth = 1/(2*symbol_period)
low_pass_filter_cutoff = 1.5*Nyquist_Bandwidth
low_pass_filter_order = 77
low_pass_delay = (low_pass_filter_order // 2) / sampling_rate
low_pass_filter = sig.firwin(low_pass_filter_order, low_pass_filter_cutoff/(sampling_rate/2), fs = sampling_rate)

RRC_delay = 3*symbol_period
_, rrc = commpy.filters.rrcosfilter(N=int(2*sampling_rate*RRC_delay),alpha=0.5,Ts=symbol_period, Fs=sampling_rate)

demodulator_total_delay = int((2*RRC_delay + low_pass_delay) * sampling_rate)

if order <= 2:
    scaler = 1
else:
    scaler = (2/3*(2**(order)-1))**0.5

def downconverter(signal):
    t = np.linspace(0, len(signal)/sampling_rate, len(signal), endpoint=False)
    baseband_signal = signal * np.exp(-1j* (2 * np.pi * (CARRIER) * t))
    I = baseband_signal.real
    Q = baseband_signal.imag
    return I, Q, t

guide_I_base, guide_Q_base, t = downconverter(modc)
guide_I_lp = sig.lfilter(low_pass_filter, 1, guide_I_base)
guide_Q_lp = sig.lfilter(low_pass_filter, 1, guide_Q_base)

guide_baseband_signal_lp = guide_I_lp + 1j*guide_Q_lp
guide_RC_signal = sig.convolve(guide_baseband_signal_lp, rrc) / np.sum(rrc**2) * 2

guide_RC_signal *= scaler

guide_Signal = guide_RC_signal[:-(6*samples_per_symbol)]

guide_Symbols = guide_Signal[demodulator_total_delay::samples_per_symbol]

foff = 1e2
poff = np.pi*0.2
modr_baseband = modr * np.exp(-1j* (2 * np.pi * (CARRIER) * t))
I_base, Q_base = modr_baseband.real, modr_baseband.imag 


I_lp = sig.lfilter(low_pass_filter, 1, I_base)
Q_lp = sig.lfilter(low_pass_filter, 1, Q_base)

baseband_signal_lp = I_lp + 1j*Q_lp
RC_signal = sig.convolve(baseband_signal_lp, rrc) / np.sum(rrc**2) * 2 #Energy Normalization and 2x from trig identity

#Scale the signal to original constellation

RC_signal *= scaler

Signal = RC_signal[:-(6*samples_per_symbol)]

pbSymbols = Signal[demodulator_total_delay::samples_per_symbol]

bbSymbols = np.zeros(len(pbSymbols), dtype=complex)
theta = np.zeros(len(pbSymbols))

N=1000
firstNSymbol = guide_Symbols[:N]
expectedCoord = [list(keys)[i] for i in qam_tree.query(list(zip(firstNSymbol.real, firstNSymbol.imag)))[1]] # qam_tree.query(list(zip(firstNSymbol.real, firstNSymbol.imag)))[1]


'''subsetN = 1000
deltaAng = np.zeros(subsetN)
bbSymbols = np.zeros(subsetN, dtype=complex)
phi=0
mu = 0.1

k=1
for s in pbSymbols[:subsetN]:
    bbSymbols[k-1] = s * np.exp(-1j * phi)
    
    coord = expectedCoord[k-1]
    
    decisionSymbol = coord[0] + 1j*coord[1]
            
    decisionError = decisionSymbol - bbSymbols[k-1]

    differenceAng = (np.atan2(np.imag(np.conj(decisionSymbol) * bbSymbols[k-1]), np.real(np.conj(decisionSymbol) * bbSymbols[k-1])))

    deltaAng[k-1] = (differenceAng)
    phi += differenceAng * mu
    
    print(phi/np.pi)
    
    k+=1

fig,axs = plt.subplots(1,1, figsize=(10,10))
scaler = ((2**(order/2))-1) if order > 2 else 1
x_ticks = np.arange(-scaler, scaler+1, 2)
y_ticks = np.arange(-scaler, scaler+1, 2)
axs.set(xlim=[x_ticks.min()-2, x_ticks.max()+2], ylim=[y_ticks.min()-2, y_ticks.max()+2], xlabel='I', ylabel='Q')
axs.grid(True)
axs.set_xticks(x_ticks)
axs.set_yticks(y_ticks)

#axs.scatter(pbSymbols[:subsetN].real, pbSymbols[:subsetN].imag)
axs.scatter(guide_Symbols[:subsetN].real, guide_Symbols[:subsetN].imag)
expectedI,expectedQ = zip(*expectedCoord[:subsetN])
axs.scatter(expectedI,expectedQ)
axs.scatter(bbSymbols.real, bbSymbols.imag, color='red')
axs.legend(['Guide Symbols', 'Expected Symbols','Adjusted Symbols'])'''


k=1
mu=0.05
phaseNow = 0
phaseEst = 0

for s in pbSymbols:
    bbSymbols[k-1] = s * np.exp(-1j * phaseNow)

    if k <= N:        
        coord = expectedCoord[k-1]
        decisionSymbol = coord[0] + 1j*coord[1]
        
        decisionError = decisionSymbol - bbSymbols[k-1]
        
        differenceAng = (np.atan2(np.imag(np.conj(decisionSymbol) * bbSymbols[k-1]), np.real(np.conj(decisionSymbol) * bbSymbols[k-1])))
        theta[k-1] = differenceAng
        
        phaseNow += differenceAng * mu
    
    k += 1

fig3,ax3 = plt.subplots(3,1, figsize=(10,10))

scaler = ((2**(order/2))-1) if order > 2 else 1
x_ticks = np.arange(-scaler, scaler+1, 2)
y_ticks = np.arange(-scaler, scaler+1, 2)
ax3[0].grid(True)
ax3[0].set_xticks(x_ticks)
ax3[0].set_yticks(y_ticks)
ax3[1].grid(True)
ax3[1].set_xticks(x_ticks)
ax3[1].set_yticks(y_ticks)
ax3[2].grid(True)
ax3[2].set_xticks(x_ticks)
ax3[2].set_yticks(y_ticks)

ax3[0].scatter(guide_Symbols.real, guide_Symbols.imag)
ax3[1].scatter(pbSymbols.real, pbSymbols.imag)
ax3[2].scatter(bbSymbols.real, bbSymbols.imag)

fig2,ax2 = plt.subplots()
ax2.plot(theta)    

# Initialize the figure and axes
fig, ax = plt.subplots()
scatter = ax.scatter(bbSymbols[0].real, bbSymbols[0].imag, label='BB Symbols', c='b')
scatter_guide = ax.scatter(guide_Symbols[0].real, guide_Symbols[0].imag, label='Guide Symbols', c='r')
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
    bb_symbols = np.column_stack((bb_symbols.real, bb_symbols.imag))
    guide_Symbolsframe = np.column_stack((guide_Symbolsframe.real, guide_Symbolsframe.imag))
    
    scatter.set_offsets(bb_symbols)
    scatter_guide.set_offsets(guide_Symbolsframe)
    
    fig.suptitle(f"Frame {frame}")
    # Return the artists to be updated
    return scatter, scatter_guide

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=len(bbSymbols), interval=16)

# Show the animation
plt.show()
'''
bbSymbols = np.array()
for s in modr_RC[demodulator_total_delay::samples_per_symbol]:
    # Demodulate the passband symbol and store in array
    bbSymbols[k-1] = s * np.exp(-1j * phaseNow)
    
    # Find the nearest QAM constellation point to symbol s
    decisionSymbol = 
    
    # Calculate the phase error
    decisionError = decisionSymbol - s
    
    # Calculate the new phase estimate
    theta[k-1] = phaseEst
    phaseEst += mu * (np.imag(np.conj(decisionError) * s) /
                      (np.abs(decisionSymbol) * np.abs(s)))
    
    # Calculate the next demodulation phase value
    phaseNow += phaseInc + phaseEst
    
    k += 1'''
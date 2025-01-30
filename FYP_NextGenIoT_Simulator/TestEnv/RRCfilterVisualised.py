import matplotlib.pyplot as plt
import numpy as np
import commpy

Ts = 8/16000
Fs = 4e6
RRC_alpha = 0.35

samples_per_symbol = int(Ts * Fs)
RRC_delay = 3 * Ts

def RRCFilter(N, alpha, Ts, Fs):
    """
    Generates a root raised cosine (RRC) filter (FIR) impulse response. Adapted from commpy due to small bug, filter does not extend to full range of samples.

    Parameters
    ----------
    N : int
        Length of the filter in samples.

    alpha : float
        Roll off factor (Valid values are [0, 1]).

    Ts : float
        Symbol period in seconds.

    Fs : float
        Sampling Rate in Hz.

    Returns
    ---------

    time_idx : 1-D ndarray of floats
        Array containing the time indices, in seconds, for
        the impulse response.

    h_rrc : 1-D ndarray of floats
        Impulse response of the root raised cosine filter.
    """
    T_delta = 1/float(Fs)
    time_idx = ((np.arange(N+1)-N/2))*T_delta
    sample_num = np.arange(N+1)
    h_rrc = np.zeros(N+1, dtype=float)

    for x in sample_num:
        t = (x-N/2)*T_delta
        if t == 0.0:
            h_rrc[x] = 1.0 - alpha + (4*alpha/np.pi)
        elif alpha != 0 and t == Ts/(4*alpha):
            h_rrc[x] = (alpha/np.sqrt(2))*(((1+2/np.pi)* \
                    (np.sin(np.pi/(4*alpha)))) + ((1-2/np.pi)*(np.cos(np.pi/(4*alpha)))))
        elif alpha != 0 and t == -Ts/(4*alpha):
            h_rrc[x] = (alpha/np.sqrt(2))*(((1+2/np.pi)* \
                    (np.sin(np.pi/(4*alpha)))) + ((1-2/np.pi)*(np.cos(np.pi/(4*alpha)))))
        else:
            h_rrc[x] = (np.sin(np.pi*t*(1-alpha)/Ts) +  \
                    4*alpha*(t/Ts)*np.cos(np.pi*t*(1+alpha)/Ts))/ \
                    (np.pi*t*(1-(4*alpha*t/Ts)*(4*alpha*t/Ts))/Ts)

    return time_idx, h_rrc



t, rrc1 = RRCFilter(N = int(2*Fs*RRC_delay), alpha = 0, Ts = Ts, Fs = Fs)
plt.plot(t, rrc1)
plt.plot(t,rrc1**2)

plt.plot(t,[0]*len(t), 'k--')
plt.axvline(x = 0, color = 'b', label = '0 Line')
#ax2.plot(t,[0]*len(t), 'k--')
#ax2.axvline(x = 0, color = 'b', label = '0 Line')
for i in np.arange(-3,4)*Ts:
    plt.axvline(i, -0.1, 0.9,linestyle = 'dashed')
    #ax2.axvline(i, -0.1, 0.9,linestyle = 'dashed')
plt.legend()
plt.show()
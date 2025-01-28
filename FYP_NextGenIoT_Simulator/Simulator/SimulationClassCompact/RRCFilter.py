from numpy import pi,sin,cos,sqrt,arange,zeros

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
    time_idx = ((arange(N+1)-N/2))*T_delta
    sample_num = arange(N+1)
    h_rrc = zeros(N+1, dtype=float)

    for x in sample_num:
        t = (x-N/2)*T_delta
        if t == 0.0:
            h_rrc[x] = 1.0 - alpha + (4*alpha/pi)
        elif alpha != 0 and t == Ts/(4*alpha):
            h_rrc[x] = (alpha/sqrt(2))*(((1+2/pi)* \
                    (sin(pi/(4*alpha)))) + ((1-2/pi)*(cos(pi/(4*alpha)))))
        elif alpha != 0 and t == -Ts/(4*alpha):
            h_rrc[x] = (alpha/sqrt(2))*(((1+2/pi)* \
                    (sin(pi/(4*alpha)))) + ((1-2/pi)*(cos(pi/(4*alpha)))))
        else:
            h_rrc[x] = (sin(pi*t*(1-alpha)/Ts) +  \
                    4*alpha*(t/Ts)*cos(pi*t*(1+alpha)/Ts))/ \
                    (pi*t*(1-(4*alpha*t/Ts)*(4*alpha*t/Ts))/Ts)

    return time_idx, h_rrc
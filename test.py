import numpy as np
import matplotlib.pyplot as plt

# Parameters
N = 1000  # Number of symbols
sps = 8   # Samples per symbol
fc = 2e3  # Carrier frequency
fs = 16e3 # Sampling rate
t = np.arange(0, N*sps)/fs

# Bit generation
bits = np.random.randint(0, 2, N*2)
symbols = bits.reshape(-1, 2)

# QPSK Mapping
mapping = {
    (0,0): (1, 1),
    (0,1): (-1, 1),
    (1,1): (-1, -1),
    (1,0): (1, -1)
}
I, Q = zip(*[mapping[tuple(b)] for b in symbols])
I = np.repeat(I, sps)
Q = np.repeat(Q, sps)

# IQ modulation
carrier_I = np.cos(2*np.pi*fc*t)
carrier_Q = np.sin(2*np.pi*fc*t)
tx_signal = I * carrier_I - Q * carrier_Q

# IQ demodulation (coherent)
rx_I = tx_signal * carrier_I * 2
rx_Q = -tx_signal * carrier_Q * 2

# Low-pass filter (simple moving average here)
def lpf(signal, span=16):
    return np.convolve(signal, np.ones(span)/span, mode='same')

I_baseband = lpf(rx_I)
Q_baseband = lpf(rx_Q)

# Downsample (symbol decisions)
I_sym = I_baseband[sps//2::sps]
Q_sym = Q_baseband[sps//2::sps]

plt.figure()
plt.scatter(I_sym, Q_sym)
plt.title("QPSK Constellation After Demodulation")
plt.grid(True)
plt.axis('equal')
plt.show()

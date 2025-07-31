import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import upfirdn, correlate

# RRC filter design
def rrc_filter(beta, sps, span):
    N = span * sps
    t = np.arange(-N/2, N/2 + 1) / sps
    eps = 1e-8
    h = np.zeros_like(t)
    for i in range(len(t)):
        if abs(t[i]) < eps:
            h[i] = 1.0 - beta + 4 * beta / np.pi
        elif abs(abs(t[i]) - 1/(4*beta)) < eps:
            h[i] = (beta / np.sqrt(2)) * (
                (1 + 2/np.pi) * np.sin(np.pi/(4*beta)) +
                (1 - 2/np.pi) * np.cos(np.pi/(4*beta))
            )
        else:
            h[i] = (np.sin(np.pi * t[i] * (1 - beta)) +
                    4 * beta * t[i] * np.cos(np.pi * t[i] * (1 + beta))) / \
                   (np.pi * t[i] * (1 - (4 * beta * t[i])**2))
    return h

# Parameters
sps = 3
beta = 0.35
span = 6
fc = 0.1  # Normalized carrier frequency (relative to Fs)
num_data = 500
rolloff = beta

# QPSK Mapping
def bits_to_symbols(bits):
    mapping = {
        (0,0): 1+1j,
        (0,1): -1+1j,
        (1,1): -1-1j,
        (1,0): 1-1j
    }
    bit_pairs = bits.reshape(-1, 2)
    return np.array([mapping[tuple(b)] for b in bit_pairs])

# Generate preamble and data
preamble_bits = np.tile([0, 0, 0, 1, 1, 1, 1, 0], 4)
preamble = bits_to_symbols(preamble_bits)
data_bits = np.random.randint(0, 2, num_data * 2)
data = bits_to_symbols(data_bits)
symbols = np.concatenate([preamble, data])

# RRC filter
rrc = rrc_filter(beta, sps, span)

# Transmit signal
tx = upfirdn(rrc, symbols, up=sps)

# Time vector
t = np.arange(len(tx))

# Carrier modulation
carrier = np.exp(1j * 2 * np.pi * fc * t)
modulated = tx * carrier

# Add sine tone interference (optional)
sine = 0.5 * np.exp(1j * 2 * np.pi * 0.02 * t)
tx_signal = modulated + sine

# Receiver: Mix down (demodulate)
rx = tx_signal * np.exp(-1j * 2 * np.pi * fc * t)

# Matched RRC filter
rx_filtered = upfirdn(rrc, rx, up=1, down=1)

# Symbol synchronization via preamble cross-correlation
rx_energy = rx_filtered / np.max(np.abs(rx_filtered))
preamble_upsampled = upfirdn(rrc, preamble, up=sps)
correlation = correlate(rx_energy, preamble_upsampled, mode='valid')
start_idx = np.argmax(np.abs(correlation))
aligned = rx_filtered[start_idx:]

# Downsample after alignment
samples = aligned[sps*span//2::sps]

# Phase correction using preamble
rx_preamble = samples[:len(preamble)]
angle_offset = np.angle(np.sum(rx_preamble * np.conj(preamble)))
samples_corrected = samples * np.exp(-1j * angle_offset)

# Data after preamble
rx_data = samples_corrected[len(preamble)-1:]

# Constellation Plot
plt.figure()
plt.scatter(np.real(rx_data), np.imag(rx_data), color='blue', alpha=0.6)
plt.title("QPSK Constellation After Time & Phase Correction")
plt.grid(True)
plt.axis('equal')
plt.show()

# Eye Diagram (I-channel)
def plot_eye(signal, sps, num_traces=100):
    trace_len = 2 * sps
    for i in range(num_traces):
        start = i * trace_len
        if start + trace_len < len(signal):
            plt.plot(np.real(signal[start:start+trace_len]), color='blue', alpha=0.3)
    plt.title("Eye Diagram (I-component)")
    plt.xlabel("Sample")
    plt.grid(True)
    plt.show()

plot_eye(np.real(aligned), sps)

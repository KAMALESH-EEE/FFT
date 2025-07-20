import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate, upfirdn
from scipy.signal.windows import hann

# Parameters
sps = 4                     # Samples per symbol
num_data_symbols = 100      # QPSK symbols after preamble
snr_db = 20                 # Signal-to-noise ratio
fractional_delay = 2.3      # Delay in samples
rolloff = 0.35
span = 6                    # RRC filter span in symbols

# Helper: QPSK Modulator
def bits_to_qpsk(bits):
    symbols = (2*bits[0::2] - 1) + 1j * (2*bits[1::2] - 1)
    symbols /= np.sqrt(2)
    return symbols

# Helper: RRC filter
def rrc_filter(beta, span, sps):
    N = span * sps
    t = np.arange(-N/2, N/2 + 1) / sps
    with np.errstate(divide='ignore', invalid='ignore'):
        rrc = (np.sinc(t) *
               np.cos(np.pi * beta * t) /
               (1 - (2 * beta * t)**2))
    rrc[t == 0] = 1.0 - beta + (4 * beta / np.pi)
    rrc[np.abs(2 * beta * t) == 1] = (beta / np.sqrt(2)) * \
        ((1 + 2 / np.pi) * np.sin(np.pi / (4 * beta)) +
         (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
    return rrc / np.sqrt(np.sum(rrc**2))

# 1. Create known preamble
preamble_bits = np.random.randint(0, 2, 40)
preamble_symbols = bits_to_qpsk(preamble_bits)

# 2. Generate random QPSK data
data_bits = np.random.randint(0, 2, num_data_symbols * 2)
data_symbols = bits_to_qpsk(data_bits)

# 3. Combine preamble + data
tx_symbols = np.concatenate([preamble_symbols, data_symbols])

# 4. Pulse shaping (RRC filter)
rrc = rrc_filter(rolloff, span, sps)
tx_samples = upfirdn(h=rrc, x=tx_symbols, up=sps)

# 5. Add fractional delay using linear interpolation
n = np.arange(len(tx_samples))
delayed_n = n - fractional_delay
rx_samples = np.interp(delayed_n, n, tx_samples.real) + 1j * np.interp(delayed_n, n, tx_samples.imag)

# 6. Add AWGN
rx_samples += (np.random.randn(*rx_samples.shape) + 1j * np.random.randn(*rx_samples.shape)) * \
              10 ** (-snr_db / 20)

# 7. Matched filter
rx_matched = np.convolve(rx_samples, rrc[::-1], mode='same')

# 8. Downsample reference preamble to sample domain
ref_preamble_samples = upfirdn(h=rrc, x=preamble_symbols, up=sps)

# 9. Correlate to find timing offset
corr = correlate(rx_matched, ref_preamble_samples)
peak_index = np.argmax(np.abs(corr))
sync_index = peak_index - len(ref_preamble_samples) + 1

print(f"Estimated symbol start at sample index: {sync_index:.2f}")

# 10. Plot correlation
plt.figure(figsize=(10, 4))
plt.stem(np.abs(corr))
plt.title("Preamble Correlation for Time Sync")
plt.xlabel("Sample Index")
plt.ylabel("Correlation Magnitude")
plt.grid(True)
plt.axvline(x=peak_index, color='r', linestyle='--', label="Sync Peak")
plt.legend()
plt.tight_layout()
plt.show()

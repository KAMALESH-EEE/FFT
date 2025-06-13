import numpy as np
import struct

# Parameters
fs = 100e6            # Sample rate: 100 MSPS
f_tone = 10e6         # Tone frequency: 10 MHz
duration = 1e-3       # Duration: 1 ms
num_samples = int(fs * duration)

# Time vector
t = np.arange(num_samples) / fs

# Generate complex sinusoid
IQ = 0.8 * np.exp(1j * 2 * np.pi * f_tone * t)  # Amplitude 0.8

# Scale to int16 range
I = np.int16(np.real(IQ) * 32767)
Q = np.int16(np.imag(IQ) * 32767)

# Pack I and Q into 32-bit words (I in upper 16 bits, Q in lower)
data_32bit = [((int(i) << 16) | (int(q) & 0xFFFF)) & 0xFFFFFFFF for i, q in zip(I, Q)]

# Write to binary file
with open("synthetic_adc_data.bin", "wb") as f:
    for word in data_32bit:
        f.write(struct.pack("<I", word))  # Little-endian uint32

print(f"✅ File 'synthetic_adc_data.bin' created with {num_samples} samples.")

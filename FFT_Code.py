import numpy as np
import matplotlib.pyplot as plt
import math
import scipy

print(scipy.__version__)
print(plt.__package__)

i=[t for t in range(100000)]
q=[math.sin(t) for t in range(100000)]

# Simulated example
# Replace with your actual ADC IQ data
I = np.array(q)  # In-phase samples
Q = np.array(q)  # Quadrature samples


IQ = I 

# Perform FFT
N = len(IQ)
fft_data = np.fft.fft(IQ, n=N)
fft_shifted = np.fft.fftshift(fft_data)  # Shift zero freq to center
magnitude = 20 * np.log10(np.abs(fft_data))  # dB scale

# Frequency axis
fs = 1e6  # Sampling rate (example: 1 MSps). Change as per your ADC.
freq = (np.fft.fftfreq(N, d=1/fs))

print(np.fft.fftfreq(N, d=1/fs))

# Plot
plt.figure(figsize=(10, 5))
plt.plot(freq / 1e6, magnitude)  # Convert Hz to MHz
plt.title("Frequency Spectrum (FFT of IQ Data)")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Magnitude (dB)")
plt.grid(True)
plt.tight_layout()
plt.show()
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load your actual I/Q data from CSV
df = pd.read_csv('your_iq_data.csv')  # Replace with your filename

# Extract I and Q columns
I = df['I'].values
Q = df['Q'].values

# Form complex signal
IQ = I + 1j * Q

# Sampling rate (Hz) — you MUST set this to your ADC's sampling rate
Fs = 1e6  # Example: 1 MHz

# Perform FFT
N = len(IQ)
IQ_fft = np.fft.fftshift(np.fft.fft(IQ, n=N))  # Shift zero freq to center
f = np.fft.fftshift(np.fft.fftfreq(N, d=1/Fs))  # Frequency axis

np.fft.fftshift()
# Magnitude in dB
magnitude_dB = 20 * np.log10(np.abs(IQ_fft) + 1e-12)  # add small value to avoid log(0)

# Plot
plt.figure(figsize=(10, 5))
plt.plot(f / 1e6, magnitude_dB)  # Frequency in MHz
plt.title('FFT Spectrum of I/Q Signal')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Magnitude (dB)')
plt.grid(True)
plt.tight_layout()
plt.show()

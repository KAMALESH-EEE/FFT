import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt
from math import sin, pi, sqrt
from scipy.signal import butter, lfilter
'''
# Sampling and time setup
Fs = 100e6                   # Sampling rate = 100 MHz
T = 1 / Fs                  # Sampling period
N = int(5e6)                    # Number of samples
f_sig = 10e4                # Signal frequency = 10 MHz

t = np.arange(N) * T        # Time array
print(len(t))
k = 2 * pi


def lowpass_filter(signal, cutoff, fs, order=6):
    b, a = butter(order, cutoff / (fs / 2), btype='low')
    return lfilter(b, a, signal)



# Generate a sine wave of 1 Vpeak
C = np.sin(k * f_sig * t)
B = np.sin(k * 1e3 * t)
D = np.sin(k * f_sig * t)

A = lowpass_filter((D*C), 5e4, Fs, order=4)
#A = D*C


# Plot time-domain signal
plt.plot(t, A)  # Plot only first 100 samples for clarity
plt.title("Time Domain Signal")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (V)")
plt.show(block=False)
plt.pause(6)
plt.close()

# Perform FFT
V = np.fft.fft(A)
V = V / N   # Normalize the FFT
F = np.fft.fftfreq(N, T)

# Calculate magnitude in dBV
mag = np.abs(V)
mag[mag == 0] = 1e-12  # Avoid log(0)

R = 50
Vrms = mag / sqrt(2)
P = (Vrms ** 2) / R
Pdbm = 10 * np.log10(P / 1e-3)

# Plot FFT result
plt.plot(F, Pdbm)  # Plot only positive frequencies
plt.title("FFT Magnitude in dBV")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dBV)")
plt.grid(True)
plt.show()

'''


s = 10000
T = 1E-3



t = np.array([i for i in range(s)]) * T

#y = np.array([1 if i< 0.1 else -1  for i in t])

x1 = [1 for i in range (10)] 
x2 = [0 for i in range (10)]
y = []

for i in range(500):
    y+=x1
    y+=x2

#y= np.sinc(2*np.pi*1*t)

plt.plot(t[:100],y[:100])
plt.show()

Y = np.fft.fft(y) / len(y)
fre = np.fft.fftfreq(len(y),T)


plt.plot(fre,np.abs(Y))
plt.show()
 


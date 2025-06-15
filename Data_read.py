# importing Libraries
import os

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt 
import struct
from RK import *


# Changing Directory
os.chdir("D:\DP_testing")

#opening ADC Bin File
with open("ADC_IQ_rx10.bin",'rb') as f:
    raw = f.read()


# reading ADC 32 bit data as tuple
Ns = len(raw)//4
Data = struct.unpack(f"<{Ns}I",raw)

Fs = Ns / 5

#Converting into array
IQ = np.array(Data)

t = 1099.978189 - 1099.97768885
print(1/t)


# Spliting IQ data and signed
Q = (IQ & 0xffff).astype(np.int16)
I = (IQ >> 16).astype(np.int16)

# Making it complex
IQ = I + 1j*Q

#Time domain calc

T = np.array([(i/Fs)*1000 for i in range(len(I))])

plt.plot(T,I)
plt.plot(T,Q)
plt.show()


from scipy.fft import fft, fftfreq

fft_result = fft(IQ)
freqs = fftfreq(Ns, 1/Fs)

plt.plot(freqs / 1e6, 20 * np.log10(np.abs(fft_result)))
plt.title("Spectrum (dB)")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Magnitude (dB)")
plt.grid()
plt.show()



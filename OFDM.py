import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# OFDM ORTHOGONALITY DEMONSTRATION
# ============================================================

# Parameters
N = 8                  # Number of subcarriers
Tu = 1.0               # Useful OFDM symbol duration
Delta_f = 1 / Tu       # Subcarrier spacing

# Sampling
Fs = 1000              # Samples/sec
t = np.arange(0, Tu, 1 / Fs)

# ------------------------------------------------------------
# 1. Generate two OFDM subcarriers
# ------------------------------------------------------------

k1 = 1
k2 = 2

f1 = k1 * Delta_f
f2 = k2 * Delta_f

# Complex subcarriers
s1 = np.exp(1j * 2 * np.pi * f1 * t)
s2 = np.exp(1j * 2 * np.pi * f2 * t)

# Real parts for plotting
s1_real = np.real(s1)
s2_real = np.real(s2)

# ------------------------------------------------------------
# 2. TIME DOMAIN
# ------------------------------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(t, s1_real, label=f"Subcarrier {k1} ({f1:.1f} Hz)")
plt.plot(t, s2_real, label=f"Subcarrier {k2} ({f2:.1f} Hz)")

plt.title("OFDM Subcarriers - Time Domain")
plt.xlabel("Time")
plt.ylabel("Amplitude")
plt.grid(True)
plt.legend()
plt.show()

# ------------------------------------------------------------
# 3. Check orthogonality using correlation/integral
# ------------------------------------------------------------

# Inner product:
# integral s1(t) * conjugate(s2(t)) dt

orthogonal_value = np.sum(s1 * np.conj(s2)) / Fs

self_1 = np.sum(s1 * np.conj(s1)) / Fs
self_2 = np.sum(s2 * np.conj(s2)) / Fs

print("TIME DOMAIN")
print("----------------------------")

print(f"Energy of subcarrier 1 : {self_1:.6f}")
print(f"Energy of subcarrier 2 : {self_2:.6f}")

print(f"Cross correlation      : {orthogonal_value:.6e}")

print("\nIdeally:")
print("Cross correlation = 0")
print("Therefore, the two subcarriers are orthogonal.")

# ------------------------------------------------------------
# 4. FREQUENCY DOMAIN
# ------------------------------------------------------------

# FFT
FFT_SIZE = 8192

S1 = np.fft.fftshift(np.fft.fft(s1, FFT_SIZE))
S2 = np.fft.fftshift(np.fft.fft(s2, FFT_SIZE))

freq = np.fft.fftshift(
    np.fft.fftfreq(FFT_SIZE, 1 / Fs)
)

# Normalize
S1_mag = np.abs(S1) / len(s1)
S2_mag = np.abs(S2) / len(s2)

# Plot frequency response
plt.figure(figsize=(10, 5))

plt.plot(freq, S1_mag, label=f"Subcarrier {k1}")
plt.plot(freq, S2_mag, label=f"Subcarrier {k2}")

plt.xlim(-5, 8)

plt.title("OFDM Subcarriers - Frequency Domain")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.legend()
plt.show()

# ------------------------------------------------------------
# 5. Demonstrate the nulls
# ------------------------------------------------------------

print("\nFREQUENCY DOMAIN")
print("----------------------------")

# Find FFT bins closest to f1 and f2
idx_f1 = np.argmin(np.abs(freq - f1))
idx_f2 = np.argmin(np.abs(freq - f2))

print(f"Subcarrier 1 frequency = {f1} Hz")
print(f"Subcarrier 2 frequency = {f2} Hz")

print("\nAt f1:")
print(f"Subcarrier 1 magnitude = {S1_mag[idx_f1]:.4f}")
print(f"Subcarrier 2 magnitude = {S2_mag[idx_f1]:.4f}")

print("\nAt f2:")
print(f"Subcarrier 1 magnitude = {S1_mag[idx_f2]:.4f}")
print(f"Subcarrier 2 magnitude = {S2_mag[idx_f2]:.4f}")
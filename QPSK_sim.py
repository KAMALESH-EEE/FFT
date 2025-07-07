import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import upfirdn,lfilter,firwin

sps = 3
Rs = 6.144E6 # Sampling rate
Rd = 4.096E6  # Data rate
Rb = Rd/2 # In QPSK Symbol rate = Data rate / 2
T = int(input('Enter time mSec: '))
T /= 1000
N = int(T*Rb*sps) #No_of_Samples
Nb = int(T*Rd) #No_of_bits
n = [i for i in range(N)]
t = np.array(n)/Rs

print(Rb)


RF = 0.35
BW = Rb * (1.35)
print(BW)


st = '1010011101010101'
GrayMap = {'00':(1,-1),'01':(1,1),'10':(-1,1),'11':(-1,-1)}
s = ['0' for i in range(Nb-len(st))]
s = ''.join(s)
st +=s
st = '000000'+st
_I = []
_Q = []

i = 0
while (i<len(st)):
  _i,_q = GrayMap[st[i:i+2]]
  _I.append(_i)
  _Q.append(_q)
  i+=2
plt.stem(_I[3:13],label = 'I data')
#plt.stem(_Q[3:13],label = 'Q data')
plt.legend()
plt.show()




#upsampling
I = [0 for i in range(N)]
Q = [0 for i in range(N)]
i=0
s = 1
for j in range(0,len(I),3):
  I[j+s] = _I[i]
  Q[j+s] = _Q[i]
  i+=1
del(i)
I = np.array(I)
Q = np.array(Q)
plt.stem(n[0:60],I[0:60],label = 'I data')
#plt.stem(n[9:39],Q[9:39],label = 'Q data')
plt.legend()
plt.show()


def rrc_filter(alpha, span, sps):
    N = span * sps
    t = np.linspace(-span/2, span/2, N, endpoint=False)
    t = np.where(t == 0, 1e-8, t)  # avoid divide-by-zero
    numerator = np.sin(np.pi * t * (1 - alpha)) + 4 * alpha * t * np.cos(np.pi * t * (1 + alpha))
    denominator = np.pi * t * (1 - (4 * alpha * t) ** 2)
    h = numerator / denominator
    h /= np.sqrt(np.sum(h**2))  # Normalize energy
    return h

h = rrc_filter(0.35,6,3)

plt.plot(h)
plt.show()






up_I = np.convolve(I, h, mode='same')
up_Q = np.convolve(Q, h, mode='same')

plt.stem(n[0:60],up_I[0:60],label = 'I data')
#plt.stem(n[9:39],up_Q[9:39],label = 'Q data')
plt.legend()
plt.show()


Interpolation  = 30
Sampling_rate = Rs * Interpolation
print(Sampling_rate)

# === FIR Low-pass Filter Design (Anti-Imaging) ===
cutoff = Rs / 2  # 3.072 MHz cutoff
num_taps = 121
lpf = firwin(num_taps, cutoff / (Sampling_rate / 2), window='hamming')
ip_I = upfirdn([1],up_I,up = Interpolation)
ip_Q = upfirdn([1],up_Q,up = Interpolation)

plt.plot(n[0:1800],ip_I[0:1800],label = 'I data')
#plt.stem(n[9:39],ip_Q[9:39],label = 'Q data')
plt.legend()
plt.show()

# === Apply Filter ===
DAC_I = lfilter(lpf, 1.0, ip_I)
DAC_Q = lfilter(lpf, 1.0, ip_Q)

plt.plot(n[0:1800],DAC_I[0:1800],label = 'I data')
#plt.stem(n[9:39],DAC_I[9:39],label = 'Q data')
plt.legend()
plt.show()

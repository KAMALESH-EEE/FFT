import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import upfirdn,lfilter,firwin



sps = 3
Rs = 6.144E6 # Sampling rate
Rd = 4.096E6  # Data rate
Rb = Rd/2 # In QPSK Symbol rate = Data rate / 2
T = int(input('Enter time mSec: ')) * 0.8
T /= 1000


N = int(T*Rb*sps) #No_of_Samples
Nb = int(T*Rd) #No_of_bits
n = [i for i in range(N)]
t = np.array(n)/Rs

print('Symbol Rate: ',Rb)




RF = 0.35
BW = Rb * (1.35)
Vi = 20
print('Occupaid Band width: ',BW*0.9)




st = '100101011101010101'
GrayMap = {'00':(1,-1),'01':(1,1),'10':(-1,1),'11':(-1,-1)}
s = ['0' for i in range(Nb-len(st))]
s = ''.join(s)
st +=s
st = '00'+st
_I = []
_Q = []

i = 0
while (i<len(st)):
  _i,_q = GrayMap[st[i:i+2]]
  _I.append(_i)
  _Q.append(_q)
  i+=2

Tend = Vi
plt.cla()
plt.stem(_I[:Tend],label = 'I Data')
#plt.stem(_Q[:Tend],label = 'Q data')
plt.legend()
plt.title('RAW DATA')
plt.show(block = False)

input()



#upsampling
I = [0 for i in range(len(_I)*3)]
Q = [0 for i in range(len(_Q)*3)]
Tend = Vi * 3
i=0
s = 1


for j in range(0,len(I),3):
  I[j+s] = _I[i]
  Q[j+s] = _Q[i]
  i+=1
del(i)
I = np.array(I)
Q = np.array(Q)
plt.cla()
plt.stem(n[:Tend],I[:Tend],label = 'I data')
#plt.stem(n[:Tend],Q[:Tend],label = 'Q data')
plt.legend()
plt.title('UPSAMPLED')
plt.show(block = False)

input()





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

plt.cla()
plt.plot(h)
plt.title('Impulse Response of RRC Filter')
plt.grid()
plt.show(block = False)

input()






up_I = np.convolve(I, h, mode='same')
up_Q = np.convolve(Q, h, mode='same')

plt.cla()
plt.plot(n[:Tend],up_I[:Tend],label = 'I data')
plt.plot(n[:Tend],up_Q[:Tend],label = 'Q data')
plt.legend()

plt.title('Pulse Shape after RRC Filter')
plt.grid()
plt.show(block = False)

input()



Interpolation  = 30
Sampling_rate = Rs * Interpolation
print('Sampling Rate: ',Sampling_rate)

# === FIR Low-pass Filter Design (Anti-Imaging) ===
cutoff = Rs / 2  # 3.072 MHz cutoff
num_taps = 121
lpf = firwin(num_taps, cutoff / (Sampling_rate / 2), window='hamming')




ip_I = upfirdn([1],up_I,up = Interpolation)
ip_Q = upfirdn([1],up_Q,up = Interpolation)

Tend = Vi * 3 *Interpolation

'''plt.plot(ip_I[:Tend],label = 'I data')
plt.plot(ip_Q[:Tend],label = 'Q data')
plt.legend()
plt.title('Interpolation Output')
plt.grid()
plt.show()'''

# === Apply Filter ===
DAC_I = lfilter(lpf, 1.0, ip_I)
DAC_Q = lfilter(lpf, 1.0, ip_Q)

plt.cla()
plt.plot(n[:Tend], DAC_I[:Tend],label = 'I data')
plt.plot(n[:Tend], DAC_Q[:Tend],label = 'Q data')
plt.legend()
plt.title('Interpolation and Low-Pass Filter')
plt.grid()
plt.show(block = False)

input()



# Modulation

DAC_Rd = 5E9
vi =Vi * 3 * Interpolation
Interpolation = DAC_Rd / Sampling_rate
print('DAC interpolation: ',Interpolation)
Tend = int(vi * Interpolation)


lpf = firwin(num_taps, (Sampling_rate / 2) / (DAC_Rd / 2), window='hamming')


DAC_upI = upfirdn([1],DAC_I,up = Interpolation)
DAC_upQ = upfirdn([1],DAC_Q,up = Interpolation)


DAC_upI = lfilter(lpf, 1.0, DAC_upI)
DAC_upQ = lfilter(lpf, 1.0, DAC_upQ)

tfc = np.arange(len(DAC_upI)) / DAC_Rd

Fc = 3E6

Sig_I = DAC_upI * np.cos(2 * np.pi * Fc * tfc)
Sig_Q = DAC_upQ * np.sin(2 * np.pi * Fc * tfc)

plt.cla()
plt.plot(Sig_I[:Tend],label = 'I data')
plt.plot(Sig_Q[:Tend],label = 'Q data')
plt.legend()
plt.title('Interpolation in DAC')
plt.grid()

plt.show(block = False)

input()


DAC_GAIN = 0
Sig_I = Sig_I * (2**DAC_GAIN)
Sig_Q = Sig_Q * (2**DAC_GAIN)


DAC_OUT = Sig_I - Sig_Q

plt.cla()
plt.plot(tfc[:Tend],DAC_OUT[:Tend],label = 'DAC data')
plt.legend()
plt.title('Final DAC Output')
plt.grid()
plt.show(block = False)

input()

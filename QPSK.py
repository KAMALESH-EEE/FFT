#importing libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import *
from time import sleep

print('Libraries imported')


#=================Software=========================
#User Data

User_Data = 'SDRTEAM'

#Adding Header & Fooder

Src = 'PRJ'
Des = 'SYS'

FULL_Data = Src + User_Data + Des

print(FULL_Data)


No_of_bits = len(FULL_Data) * 8

print('No of Bits: ',No_of_bits)

input() # hold the terminal

#=================FPGA=========================


# timing calculation:

Data_Rate = 4.096e6

Time_Slot = 0.8e-3

Data_per_mS = Data_Rate * Time_Slot

Symbol_Rate = Data_Rate / 2

Sample_Rate = 6.144e6

N = np.arange(0,(Sample_Rate * Time_Slot))

Fnco = 30e6 # NCO frequency (Carrier Frequency)

No_of_Samples = len(N)

k = 2*np.pi

t = N /  Sample_Rate # Time array


# Local Oscilator wave generation

sin_LO = np.sin(k * Fnco * t) # sine wave
cos_LO = np.cos(k * Fnco * t)

ST = 0
ED = 100

PF = False

while PF and ED < No_of_Samples:
    plt.plot(t[ST:ED],sin_LO[ST:ED],)
    #plt.plot(t[ST:ED],cos_LO[ST:ED])
    plt.grid()
    plt.show(block = False)
    
    plt.pause (0.1)
    plt.cla()

    ST = ST + 50
    ED = ED + 50
    
plt.close()


#Printing Calculated Values:
print('Data Rate: ',Data_Rate,'bits/S')
print('Data per mS (slot Number Data)',Data_per_mS)

print('Sybol Rate: ', Symbol_Rate,' Simbols/S')
print('No of Samples: ', No_of_Samples)



print('Data from ADSP',FULL_Data)

#converting to Bit-Stream

BIT_STREAM = ''

for i in FULL_Data:
    st = str(bin(ord(i)))[2::]
    print (i,'->',st)
    BIT_STREAM += st
    
print('BIT STREAM',BIT_STREAM)

# Encoding (LDPC)

Code_Rate = 3/4

D_L = len(BIT_STREAM)



















# Modulation:

print (Sample_Rate / Symbol_Rate)














def LDPC_ENCODE(data,CodeRate):
    DL = len (data)
    CL = DL // CodeRate
    print(CL)
    DF = CL - DL
    DF = int (DL // DF )
    print(DF)
    st = ''
    for i in range(0,DL,DF):
        st += data[i:i+DF]
        st += '0'
    print(st)
    LDPC_DECODE(st,CodeRate)
    
def LDPC_DECODE(data,CodeRate):
    CL = len (data)
    DL = (CL * CodeRate) // 1
    print(CL)
    DF = CL - DL
    DF = int (DL // DF )
    print(DF)
    st = ''
    for i in range(CL-1,-1,-1*DF):
        try:
            st = st[:i]+st[i+1:]
        except :
            st = st[:i]
    print(st)
    
  
LDPC_ENCODE('1111111',3/4)

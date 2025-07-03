#importing libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import *
from time import sleep

print('Libraries imported')

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
ED =8000



while PF and ED < No_of_Samples+802:
    plt.plot(t[ST:ED],sin_LO[ST:ED])
    plt.plot(t[ST:ED],cos_LO[ST:ED])
    plt.grid()
    plt.show()
    #sleep(5)
    ST = ST+8000
    ED = ED+8000
    break


#Printing Calculated Values:
print('Data Rate: ',Data_Rate,'bits/S')
print('Data per mS (slot Number Data)',Data_per_mS)

print('Sybol Rate: ', Symbol_Rate,' Simbols/S')
print('No of Samples: ', No_of_Samples)




input() # hold the terminal


#User Data

Data = 'HELLOSDR'

No_of_bits = len(Data) * 8

print('No of Bits: ',No_of_bits)

# Modulation:

print (Sample_Rate / Symbol_Rate)








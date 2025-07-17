import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import upfirdn,lfilter,firwin



#Software

Block_Size = 108
No_of_Blocks_Slot = 2
Slot_Size = Block_Size * No_of_Blocks_Slot
Packet_Size = Slot_Size * 4

User_Data_Packet_Size = Packet_Size - 32

No_of_Slots = 180

Data_Size = No_of_Slots * User_Data_Packet_Size

print('No Bits per second: ',Data_Size * 8)

def Encypt(Data,Key):
    En_Data = ''
    for i in Data:
        En_Data += (chr(ord(i)+Key))
    return En_Data
    
def Decypt(Data,Key):
    De_Data = ''
    for i in Data:
        De_Data += (chr(ord(i)-Key))
    return De_Data
    
    
def Find_CheckSum(Data):
    cs = 0
    for i in Data:
        cs+=ord(i)
    return cs
    
    
USER_DATA = 'RADIO-RELAY_PRHP_HCRR_NG-SDR_MANPACK_SFF-SDR_UCR'


SRC = '10.5.15.25'
DES = '10.5.15.20'


ETH_DATA = SRC+'::'+USER_DATA+'::'+DES

print('Ethernet Data',ETH_DATA)


CS = Find_CheckSum(ETH_DATA)



SLOT_DATA =ETH_DATA + f'::{CS}'

print(SLOT_DATA)

KEY = 5
    

#FPGA Modules

FIFO = [SLOT_DATA]


def Generate_BitStream (DATA):
    DATA = Encypt(DATA,KEY)
    print(DATA)
    
    BS = ''
    Data_Size = len(DATA)
    if Data_Size != 216:
        print('Data size mismatch')
        if Data_Size > 216:
            DATA = DATA[:216]
            print('Excess data truncated')
            
        elif Data_Size < 216:
            for i in range(Data_Size, 216):
                DATA += '_'
            print('Random Bits added')
            
    for i in DATA:
        B=str(bin(ord(i))[2:])
        if len(B) < 8:
            for i in range(8 - len(B)):
                B = '0'+B
        BS+=B
    return BS
    
def Data_BitStream (BS):
    j=0
    DATA = ''

    for i in range(8,len(BS)+1,8):
        Char = BS[j:i]
        DATA+= chr(int(Char,2))
        j=i
    return DATA
    
    
def Scrambler (Data,Poly = 'V'):
    Poly = str(bin(ord(Poly)))[2::]
    Poly = ('0' + Poly) if len(Poly) < 8 else Poly
    Poly = '01001101'
    P = ''
    OUT = ''
    for i in range (int(len(Data)/8)):
        P+=Poly
    for i in range (len(Data)):
        OUT += '0' if P[i] == Data[i] else '1'
    return OUT
    
    
    
    
    
    
    
def Interleaver (Data,n,m):
    size = n*m
    if len(Data) > size:
        Data = Data[:size]
        
    elif len(Data) < size:
        
        for i in range(size - len(Data)):
            Data += '0'
    A = ''
    M =[[] for i in range(n)]
    
    for i in range (n):
        for j in range (i*m,(i*m)+m):
            M[i].append(Data[j])
        #print(M[i])
      
    for i in range(m):
        for j in range(n):
            A+=M[j][i]
        
    return A
            
            
def GrayMap(Data):

    GrayMap = {'00':(1,1),'01':(1,-1),'10':(-1,-1),'11':(-1,1)}

   
    _I = []
    _Q = []

    i = 0
    while (i<len(Data)):
      _i,_q = GrayMap[Data[i:i+2]]
      _I.append(_i)
      _Q.append(_q)
      i+=2
    return [_I,_Q]






def rrc_filter(alpha, span, sps):
    N = span * sps
    t = np.linspace(-span/2, span/2, N, endpoint=False)
    t = np.where(t == 0, 1e-8, t)  # avoid divide-by-zero
    numerator = np.sin(np.pi * t * (1 - alpha)) + 4 * alpha * t * np.cos(np.pi * t * (1 + alpha))
    denominator = np.pi * t * (1 - (4 * alpha * t) ** 2)
    h = numerator / denominator
    h /= np.sqrt(np.sum(h**2))  # Normalize energy
    return h
    



#FPGA Calculations

sps = 3 # Samples per Symbol
Rs = 6.144E6 # Sampling rate
Rd = 4.096E6  # Data rate
Rb = Rd/2 # In QPSK Symbol rate = Data rate / 2


RF = 0.35
BW = Rb * (1.35)

print('Occupaid Band width: ',BW* 8.4)


Vi = 20

h = rrc_filter(0,6,3)


# === FIR Low-pass Filter Design (Anti-Imaging) ===
cutoff = Rs / 2.5  # 3.072 MHz cutoff
num_taps = 121
lpf = firwin(num_taps, cutoff / ((Rs*30) / 2), window='hamming')

plt.cla()
plt.plot(h)
plt.title('Impulse Response of RRC Filter')
plt.grid()
plt.show(block = False)

input()


def Modulate (Data):
    
    BS = Generate_BitStream (Data)
    Scr_BS = Scrambler(BS)
    
    
    #print(Scr_BS)
    
    
    print('No of S/W bits in Slot: ', len(Scr_BS))
    
    Int_BS = Interleaver (Scr_BS, 3 , 768) # Assume LDPC included in Interleaver 
    
    Nb = len(Int_BS)
    print('No of actual bits in Slot: ', Nb)
    
    T = Nb / Rd
    
    
    N = int(Nb * sps / 2)  #No_of_Samples
    
    n = [i for i in range(N)]
    t = np.array(n)/Rs

    print('Symbol Rate: ',Rb)
    
    #print(Int_BS)

    IQ = GrayMap(Int_BS)
    _I,_Q = IQ[0] , IQ[1]
    

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


    ip_I = upfirdn([1],up_I,up = Interpolation)
    ip_Q = upfirdn([1],up_Q,up = Interpolation)

    Tend = Vi * 3 *Interpolation

    print(len(up_I),len(ip_I))

    '''plt.plot(ip_I[:Tend],label = 'I data')
    plt.plot(ip_Q[:Tend],label = 'Q data')
    plt.legend()
    plt.title('Interpolation Output')
    plt.grid()
    plt.show()'''

    # === Apply Filter ===
    global lpf

    DAC_I = lfilter(lpf, 1.0, ip_I)
    DAC_Q = lfilter(lpf, 1.0, ip_Q)

    plt.cla()
    
    plt.plot(n[:Tend], DAC_I[:Tend],label = 'I data')
    #plt.plot(n[:Tend], DAC_Q[:Tend],label = 'Q data')
    plt.legend()
    plt.title('Interpolation and Low-Pass Filter')
    plt.grid()
    plt.show(block = False)

    input()
    plt.savefig('DAC_IN')


    # Modulation

    DAC_Rd = 6.2E9
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

    Fc = int(input('Enter Frequency(kHz): '))*1000

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
    print(Tend)
    input()

    return DAC_OUT


def Demodulate (ADC_IN):

    tfc = np.arange(len(ADC_IN)) / 6.2E9

    Fc = int(input('Enter Frequency(kHz): '))*1000

    Sig_I = ADC_IN * np.cos(2 * np.pi * Fc * tfc)
    Sig_Q = ADC_IN * np.sin(2 * np.pi * Fc * tfc)
    
    plt.cla()
    plt.plot(tfc[:60546],Sig_I[:60546],label = 'ADC data')
    plt.legend()
    plt.title('ADC IQ sepration')
    plt.grid()
    plt.show(block = False)

    input()
    



    ADC_dn_I = upfirdn([1],Sig_I,down = 33.63715277777778)
    ADC_dn_Q = upfirdn([1],Sig_Q, down = 33.63715277777778)


    ADC_dn_I = lfilter(lpf, 1.0, ADC_dn_I)
    ADC_dn_Q = lfilter(lpf, 1.0, ADC_dn_Q)


    plt.cla()
    plt.plot(tfc[:1800],ADC_dn_I[:1800],label = 'ADC data')
    plt.legend()
    plt.title('Final ADC Output')
    plt.grid()
    plt.show(block = False)
    input()
    plt.savefig('ADC_OUT')

ADC_IN =[]


for i in FIFO:
    TX = Modulate(i)
    print(TX[:10])
    Noise = np.random.randint(0,10,size= (len(TX)))
    Noise = Noise * (TX.max() / 100)
    TX = TX + Noise
    plt.cla()
    plt.plot(TX[:60546],label = 'TX')
    plt.legend()
    plt.title('TX + Noise')
    plt.grid()
    plt.show(block = False)
    print(TX[:10])
    input()


    Demodulate(TX)
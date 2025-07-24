import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import upfirdn,lfilter,firwin

from random import choice

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

KEY = 0
    

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

    Graymap = {'00':(1,1),'01':(1,-1),'10':(-1,-1),'11':(-1,1)}

   
    _I = []
    _Q = []

    i = 0
    while (i<len(Data)):
      _i,_q = Graymap[Data[i:i+2]]
      _I.append(_i)
      _Q.append(_q)
      i+=2
    return [_I,_Q]

def Grayde_Map(Sample):
    Data = ''
    Graymap = {(1,1):'00',(1,-1):'01', (-1,-1):'10',(-1,1):'11'}
    for k in Sample:
        iq = (-1 if k.real < 0 else 1) , (-1 if k.imag < 0 else 1)
        Data+=Graymap[iq]

    return Data


def rrc_filter(alpha, span, sps):
    N = span * sps
    t = np.linspace(-span/2, span/2, N, endpoint=False)
    t = np.where(t == 0, 1e-8, t)  # avoid divide-by-zero
    numerator = np.sin(np.pi * t * (1 - alpha)) + 4 * alpha * t * np.cos(np.pi * t * (1 + alpha))
    denominator = np.pi * t * (1 - (4 * alpha * t) ** 2)
    h = numerator / denominator
    h /= np.sqrt(np.sum(h**2))  # Normalize energy
    return h
    

Test_S = None

#FPGA Calculations

sps = 3 # Samples per Symbol
Rs = 6.144E6 # Sampling rate
Rd = 4.096E6  # Data rate
Rb = Rd/2 # In QPSK Symbol rate = Data rate / 2


RF = 0.35
BW = Rb * (1.35)

print('Occupaid Band width: ',BW* 8.4)


Vi = 20

ConSine = [1 if i%2 == 0 else -1 for i in range(10)]


h = rrc_filter(0,6,3)

X1 = np.array([1, -1, 1, -1, -1, -1, -1, -1, 1, -1, 1, -1, -1, -1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, -1, 1, 1, -1, -1, -1, -1, 1, -1, -1, -1, 1, 1, -1, 1, -1, 1, -1, 1, 1, 1, -1, 1, -1, 1, 1, -1, 1, 1, -1, 1, -1, 1])
preamble = X1*1.5


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

stt = 0

def Modulate (Data):

    global Test_S
    
    BS = Generate_BitStream (Data)
    Scr_BS = Scrambler(BS)    
    
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
    print(len(Int_BS))
    
    IQ = GrayMap(Int_BS)
    _I,_Q = IQ[0] , IQ[1]
    

    plt.cla()
    plt.stem(_I,label = 'I Data')
    #plt.stem(_Q,label = 'Q data')
    plt.legend()
    plt.title('RAW DATA')
    plt.show(block = False)

    input()

    _I = list(preamble)+_I
    _Q = list(preamble)+_Q

    #upsampling
    I = [0 for i in range(len(_I)*3)]
    Q = [0 for i in range(len(_Q)*3)]
    PreD =  [0 for i in range(len(preamble)*3)]
    i=0
    s = 1

    for j in range(0,len(I),3):
      I[j+s] = _I[i]
      Q[j+s] = _Q[i]
      i+=1
    i=0
 
    for j in range(0,len(PreD),3):
        PreD[j+s] = preamble[i]
        i+=1
    del(i)

    I = np.array(I)
    Q = np.array(Q)


    plt.cla()
    plt.stem(I,label = 'I data')
    #plt.stem(n[Q,label = 'Q data')
    plt.legend()
    plt.title('UPSAMPLED')
    plt.show(block = False)

    input()



    up_I = np.convolve(I, h, mode='same')
    up_Q = np.convolve(Q, h, mode='same')

    PreD = list(np.convolve(np.array(PreD), h, mode='same'))
    Peek = max(PreD)

    StPeek = PreD.index(Peek)
    print(Peek ,'@', StPeek)
    print(len(PreD) - StPeek)

    plt.cla()
    plt.plot(up_I,label = 'I data')
    plt.plot(up_Q,label = 'Q data')
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
    
    plt.plot(DAC_I,label = 'I data')
    #plt.plot(DAC_Q,label = 'Q data')
    plt.legend()
    plt.title('Interpolation and Low-Pass Filter')
    plt.grid()
    plt.show(block = False)

    input()
    plt.savefig('DAC_IN')


    # Modulation

    DAC_Rd = 6.2E9
 
    Interpolation = 33
    print('DAC interpolation: ',Interpolation)

    lpf = firwin(num_taps, (Sampling_rate / 2) / (DAC_Rd / 2), window='hamming')


    DAC_upI = upfirdn([1],DAC_I,up = Interpolation)
    DAC_upQ = upfirdn([1],DAC_Q,up = Interpolation)


    DAC_upI = lfilter(lpf, 1.0, DAC_upI)
    DAC_upQ = lfilter(lpf, 1.0, DAC_upQ)

   

    tfc = np.arange(len(DAC_upI)) / DAC_Rd

    Fc = 100e6

    #Fc = int(input('Enter Frequency(MHz): '))*1e6

    Sig_I = DAC_upI * np.cos(2 * np.pi * Fc * tfc)
    Sig_Q = DAC_upQ * np.sin(2 * np.pi * Fc * tfc)

    

    plt.cla()
    plt.plot(Sig_I,label = 'I data')
    plt.plot(Sig_Q,label = 'Q data')
    plt.legend()
    plt.title('Interpolation in DAC')
    plt.grid()

    plt.show(block = False)

    input()

    DAC_GAIN = 0
    Sig_I = Sig_I * (2**DAC_GAIN)
    Sig_Q = Sig_Q * (2**DAC_GAIN)

    DAC_OUT = Sig_I - Sig_Q
    Test_S = DAC_OUT
    plt.cla()
    plt.plot(DAC_OUT,label = 'DAC data')
    plt.legend()
    plt.title('Final DAC Output')
    plt.grid()
    plt.show(block = False)

    input()

    return DAC_OUT


def Demodulate (ADC_IN):

    global Test_S

    tfc = np.arange(len(ADC_IN)) / 6.2E9

    
    RX_Gain = 7
    ADC_IN = ADC_IN * (2**RX_Gain)

    Fc = 100000000

   
    #Fc = int(input('Enter Frequency(MHz): '))*1e6

    ADC_IN = Test_S
    

    Sig_I = ADC_IN * np.cos(2 * np.pi * Fc * tfc)
    Sig_Q = ADC_IN * np.sin(2 * np.pi * Fc * tfc)


    
    plt.cla()
    plt.plot(Sig_I,label = 'ADC data')
    plt.legend()
    plt.title('ADC IQ sepration')
    plt.grid()
    plt.show(block = False)

    input()
    
    lpf = firwin(num_taps, (184.32e6 / 2) / (6.2e9 / 2), window='hamming')

 

    ADC_dn_I = upfirdn([1],Sig_I,down = 33)
    ADC_dn_Q = upfirdn([1],Sig_Q, down = 33)


    ADC_dn_I = lfilter(lpf, 1.0, ADC_dn_I)
    ADC_dn_Q = lfilter(lpf, 1.0, ADC_dn_Q)


    print(max(ADC_dn_I))

    plt.cla()
    plt.plot(ADC_dn_I,label = 'ADC data')
    plt.legend()
    plt.title('Final ADC Output')
    plt.grid()
    plt.show(block = False)
    input()
    plt.savefig('ADC_OUT')


    dc_I = upfirdn([1],ADC_dn_I,down = 30)
    dc_Q = upfirdn([1],ADC_dn_Q, down = 30)

    plt.cla()
    plt.plot(dc_I,label = 'I')
    plt.legend()
    plt.title('Decipolation')
    plt.grid()
    plt.show(block = False)
    input()






    rrc_I = np.convolve(dc_I,h, mode='same')
    rrc_Q = np.convolve(dc_Q,h, mode='same')

    rrc_I = dc_I
    rrc_Q = dc_Q

    plt.cla()
    plt.plot(rrc_I,label = 'I')
    plt.legend()
    plt.title('RX RRC Out')
    plt.grid()
    plt.show(block = False)
    input()




    dn_I = []
    dn_Q = []

    for i in range(0,len(rrc_I),3):
        dn_I.append( np.sum(rrc_I[i+1:i+2]))
        dn_Q.append( np.sum(rrc_Q[i+1:i+2]))

    dn_I = dn_I[len(preamble):]
    dn_Q = dn_Q[len(preamble):]
    
    

    dn_DATA = (np.array(dn_I)) + (1j * np.array(dn_Q))

    # plt.close()
    # plt.figure(figsize=(6, 6))
    # plt.scatter(dn_DATA.real[:20], dn_DATA.imag[:20], s=2, color='blue', alpha=0.6)
    # plt.axhline(0, color='black', lw=0.5)
    # plt.axvline(0, color='black', lw=0.5)
    # plt.grid(True, linestyle='--', alpha=0.5)
    # plt.title('Constellation Diagram')
    # plt.xlabel("In-phase (I)")
    # plt.ylabel("Quadrature (Q)")
    # plt.axis('equal')
    # plt.xlim([-1.5, 1.5])
    # plt.ylim([-1.5, 1.5])
    # plt.show()

    
    dn_DATA = list(dn_DATA)

    DATA = Grayde_Map(dn_DATA)


    print(len(DATA))

    Int_BS = Interleaver (DATA, 768,3)

    Scr_BS = Scrambler(Int_BS)
    BS = Data_BitStream (Scr_BS)
    print(BS)

ADC_IN =[]


for i in FIFO:
    TX = Modulate(i)

    Noise = np.random.randint(0,10,size= (len(TX)))
    Noise = Noise * (TX.max() / 100)
    TX = TX + Noise
    plt.cla()
    plt.plot(TX,label = 'TX')
    plt.legend()
    plt.title('TX + Noise')
    plt.grid()
    plt.show(block = False)
    input()


    Demodulate(TX)
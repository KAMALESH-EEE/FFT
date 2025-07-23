import numpy as np


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

Data = '0011011011'
mapped = GrayMap(Data) 
IQ = np.array(mapped[0])+1j*np.array(mapped[1])
demap = Grayde_Map(IQ)
print(Data == demap)
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import get_window, correlate

preamble = [1,1,-1,1,1,-1,1,1,-1,1,-1,-1,1,1,-1,1,1]
Con_sine = [-1,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1]

def Add_Preamble(Data):
    Data = Con_sine+preamble+list(Data)
    return  Data


def Remove_Preamble(Sample):
    Samples = []
    for k in Sample:
        Samples.append(-1 if k < 0 else 1)

    corr = correlate(np.array(Samples), np.array(preamble), mode='valid')
    peek = np.argmax(corr)
    Data = Samples[peek+len(preamble)::]
    return Data

DATA = [1,-1,1,-1,1,1,1,1]
print(DATA)
pre = Add_Preamble(DATA)
rem = Remove_Preamble(pre)

print(pre)
print(rem)

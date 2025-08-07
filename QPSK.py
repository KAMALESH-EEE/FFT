from math import log10
ND = -152
BW = 3e6
Gain = 30
NF = 4
NFloor = NF + Gain + (10*log10(BW)) + ND
print(NFloor)
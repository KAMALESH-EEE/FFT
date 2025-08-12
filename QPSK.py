from math import log10
ND = -147
D_BW = 6.144e6
ADC_NFloor = 10*log10(D_BW) + ND
print('ADC Noise Floor:',ADC_NFloor,'dBFs')

k = -174
A_BW = 3e6
NF = 5
Gain = 30
RF_NFloor = Gain + NF + 10*log10(A_BW) + k

print('RF Noise Floor:',RF_NFloor,'dBm')

ADC_input_impedance = 200
System_impedance = 50



SYS_NFloor = RF_NFloor if RF_NFloor > ADC_NFloor else ADC_NFloor
SIG_pwr = float(input('Input Signal Power in dBm: '))

SNR = (SIG_pwr+Gain) - SYS_NFloor

print('SNR: ',SNR)
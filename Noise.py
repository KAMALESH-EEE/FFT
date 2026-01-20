from math import log10

NoiseFloor      =       -174        #dBm/Hz

ADC_raw_sr      =       184.32E6    #Sample/Second (Msam/S)

ADC_pro_sr      =       6.144E6     #Sample/Second (Msam/S)

dBFs_Offset     =       5.2         #dB

Noise_Figure    =       2.5

No_of_Samples   =       2E3         # 2k samples

#----------------------------  FFT Calculation -----------------------------------------

FFT_noisefloor  =       -80        #dBFs

ADC_RBW         =       ADC_raw_sr / No_of_Samples      #Hz

NSD_at_ADC      =       (FFT_noisefloor + dBFs_Offset) - (10 * log10(ADC_RBW))   # dBFs/Hz  Power per Bin - bandpower (RBW)

RX_Gain         =       40          #dB

Expected_ADC_NF = NoiseFloor + (10 * log10(ADC_RBW)) + RX_Gain + Noise_Figure #dBm

print(Expected_ADC_NF - dBFs_Offset, 'dBFs')


#----------------------------  DSP Calculation -----------------------------------------

Fliter_BW       =       2.5E6

Avg_NoiseFloor  =       NSD_at_ADC + (10 * log10(Fliter_BW))

print(Avg_NoiseFloor, 'dBm')

RSSI            =       -44

print('SNR: ', RSSI - Avg_NoiseFloor)

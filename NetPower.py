from math import log10

PWR_dB=[]
BW_MHz=[]
netPWR=[]

def dB2W (p):
    return 10**((p-30)/10)

def W2dB (p):
    return 10*log10(p*1000)

RBW = 100e3

while True:
    db = float(input('Enter power(dBm):' ))

    BW = float(input('Enter Bandwidth(MHz): '))

    PWR_dB.append(db)
    BW_MHz.append(BW)
    netP = db + (10 * log10(BW*(1e6 / RBW)))
    netPWR.append(netP)
    print('Total power: ',netP,' dBm')
    st = input('Enter "exit" to calculate Net power ')
    if st == 'exit':
        break

PWR = 0

for i in netPWR:
    PWR += dB2W(i)

print('Net Power: ',round(W2dB(PWR),3),'dBm')
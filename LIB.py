import sys
from math import log10, sqrt

# sys.path.append("/home/kamalesh/python-dsp-libs/numpy")
# sys.path.append("/home/kamalesh/python-dsp-libs/scipy")
# sys.path.append("/home/kamalesh/python-dsp-libs/matplotlib")


def Signed(value,size):
    Max = 2**size
    return value if value < Max else value - 2*Max 

def Unsigned (value,size):
    Max = 2**size
    return value if value >= 0 else 2*Max + value


def dBm2Watt(db_value):
    return (10**((db_value-30)/10))

def Watt2dBm(Watt_value):
    return (10*log10(Watt_value)+30)

def Volt2dBm(Volt):
    return Watt2dBm(((Volt/sqrt(2))**2)/1)

import struct


def Bit_Stream(d,size = 108):
    data = d.encode()
    pack = struct.pack(f'{size}s',data)
    return pack

def Str_Stream(b,size = 108):
    data = list(struct.unpack(f'{size}s',b))[0]
    return data.decode()

def Scrambler(Data,poly=int('01010101',2)):
    Arr = bytearray(Data)
    Scr = bytes([i^poly for i in Arr])
    return Scr

def To_Bits(Data):
    if type(Data) == bytes:
        Data = bytearray(Data)
    bits = [(byte >> (7-i))&1 for byte in Data for i in range(8)]
    return bits

def From_Bits(Bits):
    Bits = Bits[::]
    if len(Bits) % 8 != 0:
        for i in range(len(Bits)%8):
            Bits.append(0)
    Arr = bytearray([])
    for b in range(0,len(Bits),8):
        Byte = sum([bit << (7-i) for bit,i in zip(Bits[b:b+8],range(8))])
        Arr.append(Byte)
    return bytes(Arr)


print(Str_Stream(Scrambler(From_Bits(To_Bits(Scrambler(Bit_Stream('Kamalesh')))))))



class BYTES:
    def __init__ (self,raw_bytes):
        self.raw_bytes = raw_bytes
        self.Bytes = []
        self.ArrSize = 0

    def split(self,size=1):
        self.ArrSize = len(self.raw_bytes) // size
        
        for i in range (0,self.ArrSize,size):
            a = 0
            for j in range (0,size):
                a = (a<<8) + self.raw_bytes[i+j]
            self.Bytes.append(a)

    def mask (self,en,st):
        if (st > en):
            st,en   =  en,st
        temp = int.from_bytes(self.raw_bytes)
        mskbit = (2 ** ((en-st)+1)) -1
        return ((temp >> st) & mskbit)

a = b'\x01\x0a\x1a\xaa\xaf\xff\xab\xac\x01\x0a\x1a\xaa\xaf\xff\xab\xac\x01\x0a\x1a\xaa\xaf\xff\xab\xac\x01\x0a\x1a\xaa\xaf\xff\xab\xac'

obj = BYTES(a)

obj.split(2)

print(hex(obj.mask(255 , (255-15))))




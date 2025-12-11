import hashlib
class FH:

    def __init__ (self,RX = True, path = 'dummy.bin'):
        
        self.path = path
        if RX:
            self.FileName = path
            self.CheckSum = 0
            self.RawData = bytearray([])
        elif not RX:
            with open(path,'rb') as FILE:
                file = FILE.read()
                self.FileName = FILE.name
            self.CheckSum = self.md5_checksum()
            self.RawData = bytearray(file)
        
    def md5_checksum(self):
        md5 = hashlib.md5()
        with open(self.path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                md5.update(block)
        return md5.hexdigest()
    
    def RX_write(self):
        with open(self.path,'wb') as FILE:
                FILE.write(bytes(self.RawData))

        if self.CheckSum == self.md5_checksum():
            return True
        return False

    
if __name__ == '__main__' :
    
    TX = FH(False,'DAC_IN.png')
    RX = FH(True,'Out.png')
    RX.RawData = TX.RawData[:]
    RX.CheckSum = TX.CheckSum
    print(RX.RX_write())
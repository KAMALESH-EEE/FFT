import hashlib
import time
import socket
import struct
# class FH:

#     def __init__ (self,RX = True, path = 'dummy.bin'):
        
#         self.path = path
#         if RX:
#             self.FileName = path
#             self.CheckSum = 0
#             self.RawData = bytearray([])
#         elif not RX:
#             with open(path,'rb') as FILE:
#                 file = FILE.read()
#                 self.FileName = FILE.name
#             self.CheckSum = self.md5_checksum()
#             self.RawData = bytearray(file)
        
#     def md5_checksum(self):
#         md5 = hashlib.md5()
#         with open(self.path, "rb") as f:
#             for block in iter(lambda: f.read(4096), b""):
#                 md5.update(block)
#         return md5.hexdigest()
    
#     def RX_write(self):
#         with open(self.path,'wb') as FILE:
#                 FILE.write(bytes(self.RawData))

#         if self.CheckSum == self.md5_checksum():
#             return True
#         return False

class ETH_HANDLE:

    def __init__(self,ip,port,PR = 100, PS = 800,tx_port=6001):
        self.SOCK   =   socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.SOCK.bind((ip,port))
        self.SOCK.settimeout(10)

        self.DEST_IP     =   "127.0.0.1"
        self.DEST_PORT   =    tx_port

        self.PacketRate  =    PR
        self.PacketSize  =    PS

        self.File        =    None

        self.MAX_SIZE   =   2**32 -1

        self.CMD        =  {'New_Transfer':b'\x01','Data_PKT':b'\x02','ACK':b'\x03','Loss_PKT':b'\x04','TX_completed':b'\x05','RX_completed':b'\x06'}

    def TX_Config(self):
        Name        =   'PySpice.zip'#input('Enter File Name: ')
        self.File   = FILE_HANDLE (Name,0,self.PacketSize)
        self.File.packetize()
        if len (self.File.data) > self.MAX_SIZE:
            print('Buffer Over Flow')
            return

        self.Transmite()

    def Transmite (self):
        
        data_ = self.CMD['New_Transfer']+ struct.pack('I',self.File.size) + f'{self.File.Name}'.encode()
        self.SOCK.sendto(data_,(self.DEST_IP,self.DEST_PORT)) 
        self.File.TxPKT = self.File.TxPKT[10:]
        while True:
            while True:
                try:
                    data,addr   =   self.SOCK.recvfrom(1024)
                    print(data)
                    if data[0] == self.CMD['ACK'][0]:
                        break
                except TimeoutError:
                    self.SOCK.sendto(data_,(self.DEST_IP,self.DEST_PORT))
                    print('Retried',data_)
                    
            try:
                while len(self.File.TxPKT) != 0:
                    print('Data Transfer will start soon')
                    print(f'Total Packets {self.File.size}')
                
                    time.sleep(0.1)
                    
                    self.FileTransfer()
                    print('File Transmission completed')

                    pkt = self.CMD['TX_completed']
                    self.SOCK.sendto(pkt,(self.DEST_IP,self.DEST_PORT))
                    while True:
                        try:
                            data,addr   =   self.SOCK.recvfrom(2048)
                            
                        except TimeoutError:
                            self.SOCK.sendto(pkt,(self.DEST_IP,self.DEST_PORT))
                            continue
                    
                        if data[0] == self.CMD['RX_completed'][0]:
                            print('File Received other end')
                            return

                        elif data[0] == self.CMD['Loss_PKT'][0]:
                           
                            lst = list(struct.unpack(f'{int((len(data)-1) // 4)}I',data[1:]))
                            print('Lossed PKT_IDs',lst)
                            self.File.TxPKT = lst
                            break
                break

            except Exception as e:
                print(e)

    def FileTransfer (self):
        self.SOCK.sendto(b'Dummy',(self.DEST_IP,self.DEST_PORT))
        for i in self.File.TxPKT:
            data = self.File.data[i]
            pkt = self.CMD['Data_PKT']+struct.pack('I',i) + data
            self.SOCK.sendto(pkt,(self.DEST_IP,self.DEST_PORT))
            print(f'PKT_ID {i}/{self.File.size} Transmitted | time = {time.time()}')
            time.sleep(1/self.PacketRate)
       
            
    def RX_Config (self):
        while True:
            self.SOCK.settimeout(None)
            print('Server is Running...')

            try:
                data, addr =  self.SOCK.recvfrom(2048*2048)
                print("Received:", data[0] == self.CMD['New_Transfer'][0])

            except TimeoutError:
                print("Receive timed out, retry")
                continue
            self.SOCK.settimeout(5)
            try:
                #ACK = data.decode()
                if data[0] == self.CMD['New_Transfer'][0]:

                    na,si = data[5:].decode(),struct.unpack('I',data[1:5])[0]
                    self.File = FILE_HANDLE (na,size=si)

                    print(f'Ready to receive {na} File ')

                    self.Receive()

            except Exception as e:
                print(e)
            time.sleep(0.1)

    def Receive(self):
        self.SOCK.sendto(self.CMD["ACK"],(self.DEST_IP,self.DEST_PORT))
        self.File.time = time.time()
        while True:
            while True:
                while True:
                    try:
                        data,addr   =   self.SOCK.recvfrom(2048)
                        break
                    except TimeoutError:
                        self.SOCK.sendto(self.CMD["ACK"],(self.DEST_IP,self.DEST_PORT))

                self.FileReceive()
                break

            lst = b''
            for i,data in self.File.data.items():
                if data == None:
                    lst += struct.pack('I',i)

            if len(lst) == 0:
                self.File.time = time.time() - self.File.time
                self.SOCK.sendto(self.CMD["RX_completed"],(self.DEST_IP,self.DEST_PORT))
                self.File.depacketize()
                print('File Saved')
                print('Total Time Taken ',self.File.time,'S')
                break

            else:
                lst = self.CMD["Loss_PKT"]+lst
                self.SOCK.sendto(lst,(self.DEST_IP,self.DEST_PORT))
                while True:
                    try:
                        print(self.SOCK.recvfrom(2048))
                        self.FileReceive()
                        break
                    except TimeoutError:
                        self.SOCK.sendto(lst,(self.DEST_IP,self.DEST_PORT))


    def FileReceive (self):

        self.SOCK.settimeout(None)

        while True:
            pkt,addr   =   self.SOCK.recvfrom(2048)
            if (self.DEST_IP,self.DEST_PORT) != addr:
                print(addr, 'Not acceptable IP')
                continue

            if pkt[0] == self.CMD['Data_PKT'][0]:
                i=  struct.unpack('I',pkt[1:5])[0]
                data = pkt[5:]
                print(f'PKT_ID {i}/{self.File.size} Recived | time = {time.time()}')
                self.File.data.update({i:data})
            
            elif pkt[0] == self.CMD['TX_completed'][0]:
                break

            else:
                print('CMD:',pkt[0], 'Not valid for file Transfer!')
        self.SOCK.settimeout(5)
        


class FILE_HANDLE:
    def __init__(self, Name, size = 0, p_size=1024):
        self.Name   =   Name
        self.size   =   size
        self.p_size =   p_size

        self.data  = {}
        self.TxPKT = []
        self.time  = 0

        for i in range(size):
            self.data.update({i+1:None})
            

        

    def packetize(self):
        with open (self.Name,"rb") as f:
            i=1
            while True:
                data = f.read(self.p_size)
                if not data:
                    break
                self.data.update({i:data})
                self.TxPKT.append(i)
                i+=1

        self.size = len(self.data)

    def depacketize (self):
        with open ("_New_"+self.Name,"wb") as f:

            for i,data in self.data.items():
                f.write(data)

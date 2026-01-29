
import time
import socket
import struct


class ETH_HANDLE:

    def __init__(self,ip,port,PR = 100, PS = 800):
        self.SOCK   =   socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.SOCK.bind((ip,port))

        self.DEST_IP     =   "127.0.0.1"
        self.DEST_PORT   =    6000

        self.PacketRate  =    PR
        self.PacketSize  =    PS

        self.File        =    None

    def TX_Config(self):
        Name        =   input('Enter File Name: ')
        self.File   = FILE_HANDLE (Name,0,self.PacketSize)
        self.File.packetize()
        self.Transmite()

    def Transmite (self):
        
        data = f'GET::{self.File.Name}::{self.File.size}::\n'
        self.SOCK.sendto(data.encode(),(self.DEST_IP,self.DEST_PORT)) 

        while True:
            data,addr   =   self.SOCK.recvfrom(1024)
            try:
                ACK = data.decode()
                if 'READY' in ACK:
                    print('Data Transfer start soon')
                    print(f'Total Packets {self.File.size}')
                
                    time.sleep(1)

                    for i,data in self.File.data.items():
                        if i == 10:
                            continue
                        pkt = data + struct.pack('H',i)
                        self.SOCK.sendto(pkt,(self.DEST_IP,self.DEST_PORT))
                        print(f'PKT_ID {i} Transmitted | time = {time.time()}')
                        time.sleep(1/self.PacketRate)
                    pkt = b'Done' + struct.pack('H',0)
                    
                    self.SOCK.sendto(pkt,(self.DEST_IP,self.DEST_PORT))
                    print('Initial File packets completed')
                    while True:
                        

                        data,addr   =   self.SOCK.recvfrom(2048)
                        try:
                            if 'COMP'.encode() in data:
                                break

                            elif 'LOSS'.encode() in data:
                                
                                lst = struct.unpack('H',data[4:])
                                print('Lossed PKT_IDs',lst)
                                for i in lst:
                                    data = self.File.data[i]
                                    pkt = data + struct.pack('H',i)
                                    self.SOCK.sendto(pkt,(self.DEST_IP,self.DEST_PORT))
                                    print('Retry File packets completed')
                                    time.sleep(1/self.PacketRate)
                                pkt = b'Done' + struct.pack('H',0)
                                
                                self.SOCK.sendto(pkt,(self.DEST_IP,self.DEST_PORT))


                        except Exception as e:
                            print(e)
            except Exception as e:
                print(e)
                
            
    def RX_Config (self):
        while True:
            print('Server is Running...')

            data,addr   =   self.SOCK.recvfrom(2048)
            try:
                ACK = data.decode()
                if 'GET' in ACK:
                    inf   = ACK.split('::')
                    na,si = inf[1],int(inf[2])
                    self.File = FILE_HANDLE (na,size=si)
                    
                    self.SOCK.sendto("READY\n".encode(),(self.DEST_IP,self.DEST_PORT)) 


                    print(f'Ready to receive {na} File ')

                    self.Receive()              

            except Exception as e:
                print(e)
            time.sleep(1)

    def Receive(self):

        while True:
            while True:
                if True:
                    pkt,addr   =   self.SOCK.recvfrom(2048)
                    if (self.DEST_IP,self.DEST_PORT) != addr:
                        print(addr, 'Not acceptable IP')
                        continue

                    data,i = pkt[:-2],int(struct.unpack('H',pkt[-2:])[0])
                    
                    if i == 0:
                        break
                    print(f'PKT_ID {i} Recived | time = {time.time()}')
                    self.File.data.update({i:data})

                

            lst = b''
            for i,data in self.File.data.items():
                if data == None:
                    lst += struct.pack('H',i)

            if len(lst) == 0:

                self.SOCK.sendto("COMP\n".encode(),(self.DEST_IP,self.DEST_PORT))
                self.File.depacketize()
                print('File Saved')
                break

            else:
                lst = 'LOSS'.encode()+lst
                self.SOCK.sendto(lst,(self.DEST_IP,self.DEST_PORT))



class FILE_HANDLE:
    def __init__(self, Name, size = 0, p_size=1024):
        self.Name   =   Name
        self.size   =   size
        self.p_size =   p_size

        self.data  = {}

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
                i+=1

        self.size = len(self.data)

    def depacketize (self):
        with open ("_New_"+self.Name,"wb") as f:

            for i,data in self.data.items():
                f.write(data)



RX = ETH_HANDLE("0.0.0.0",6001,10,10)
RX.RX_Config()
import socket
from ETH_FileHandler import FH
import time

HOST = "127.0.0.1"
PORT = 5000

class SERVER:
        
    def __init__ (self,IP,Port, HF = False):

        self.IP,self.Port = IP,Port

        self.FIFO = []
        self.HandlerFlag = HF
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(( self.IP,self.Port))
        self.server.listen(1)

        #print(f"Server listening on { self.IP}:{self.Port}")

        self.conn, self.addr = self.server.accept()
        #print("Connected by", self.addr)

    def RECV (self,Size = 1024):
        
        try:
            if True:
                data = self.conn.recv(Size)
                if not data:
                    return
                #print("Received:", data.decode())
                self.FIFO.append(data)
                if self.HandlerFlag :
                    self.Handle()

            self.conn.close()
            self.server.close()
        except:
            self.conn.close()
            self.server.close()

    def Handle (self):
        while len(self.FIFO) > 0:
            Rec = self.FIFO.pop(0)
            print("Received: ",Rec)
            self.conn.sendall(f"{len(Rec)} Bytes Reacived!".encode())

    def FileTransfer(self):
        while True:
            
            self.RECV(1024)
            print(self.FIFO)
            while len(self.FIFO) > 0:
                Rec = self.FIFO.pop(0).decode()
                #print(Rec)
                if 'RUN' in Rec:
                    Data = Rec.split('::')
                    print(Data)
                    #RX = FH(True,'New_'+Data[1])
                    RX = FH(True,'Out.txt')
                    RX.CheckSum = Data[2]
                    self.RECV(1024*1024)
                    RX.RawData = bytearray(self.FIFO.pop(0))
                    self.conn.sendall('True'.encode())
                    #print(RX.RawData)
                    print('File Write Status',RX.RX_write())
                    
                break

while True:
    
    srv = SERVER(HOST,PORT,False)
    
    srv.FileTransfer()
    
    #print("Server Closed..!")
    del(srv)
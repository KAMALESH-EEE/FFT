import socket
from ETH_FileHandler import FH
import time

HOST = "127.0.0.1"
HOST = input('IP:')
PORT = 5000
PORT = int(input('PORT:'))
class SERVER:
        
    def __init__ (self,IP,Port, HF = False):

        self.IP,self.Port = IP,Port

        self.FIFO = []
        self.HandlerFlag = HF
        self.AliveFlag = False
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(( self.IP,self.Port))
        self.server.listen(1)

        print(f"Server listening on { self.IP}:{self.Port}")

        self.conn, self.addr = self.server.accept()
        print("Connected by", self.addr)
        self.AliveFlag = True

    def RECV (self,Size = 1024):
        
        #try:
        if True:
            if True:
                data = self.conn.recv(Size)
                if not data:
                    print("Client Closed")
                    self.conn.close()
                    self.server.close()
                    self.AliveFlag = False
                    return False
                #print("Received:", data.decode())
                self.FIFO.append(data)
                if self.HandlerFlag :
                    self.Handle()
        #except Exception as e:
        if False:
            print("Error: ",e)
            self.conn.close()
            self.server.close()
            self.AliveFlag = False
        return True

    def Handle (self):
        while len(self.FIFO) > 0:
            Rec = self.FIFO.pop(0)
            print("Received: ",Rec)
            self.conn.sendall(f"{len(Rec)} Bytes Reacived!".encode())

    def FileTransfer(self):
        if self.RECV():
            if len(self.FIFO) > 0:
                Rec = self.FIFO.pop(0).decode()
                print("REC",Rec)
                if 'RUN' in Rec:
                    Data = Rec.split('::')
                    print(Data)
                    #RX = FH(True,'New_'+Data[1])
                    RX = FH(True,'Out.png')
                    RX.CheckSum = Data[2]
                    if self.RECV(1024*1024):
                        RX.RawData = bytearray(self.FIFO.pop(0))

                        self.conn.sendall(str(RX.RX_write()).encode())
                    #print(RX.RawData)
                else:
                    print("Data Received but not a File handling data")
            else:
                print('No Data Received!')
        else:
            return
                    

while True:
    
    srv = SERVER(HOST,PORT,False)
    while srv.AliveFlag:
        srv.FileTransfer()
    
    #print("Server Closed..!")
    
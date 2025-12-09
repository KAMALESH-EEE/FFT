import socket

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

        print(f"Server listening on { self.IP}:{self.Port}")

        self.conn, self.addr = self.server.accept()
        print("Connected by", self.addr)

    def RECV (self):
        while True:
            data = self.conn.recv(1024)
            if not data:
                break
            #print("Received:", data.decode())
            self.FIFO.append(data)
            if self.HandlerFlag :
                self.Handle()

        self.conn.close()
        self.server.close()

    def Handle (self):
        while len(self.FIFO) > 0:
            print("Received: ",self.FIFO.pop(0).decode())

srv = SERVER(HOST,PORT,True)
srv.RECV()

input()
import socket
import time
from ETH_FileHandler import FH

SERVER_IP = "127.0.0.1"
#SERVER_IP = input()
PORT = 5000
#PORT = int(input('PORT:'))

TX = FH(False,'DAC_IN.png')

print(TX.FileName)
Data = 'RUN::'+TX.FileName+'::'+TX.CheckSum+'::'
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

while True:
    client.sendall(Data.encode())
    time.sleep(1)
    client.sendall(TX.RawData)

    rec = client.recv(1024)
    print(rec.decode())
    

import socket
import time
from ETH_FileHandler import FH

SERVER_IP = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

TX = FH(False,'Dummy.txt')
print(TX.FileName)
Data = 'RUN::'+TX.FileName+'::'+TX.CheckSum+'::'
i = 0
while i < 500:
    print(f'Writting: {i+1}')
    client.sendall(Data.encode())
    client.sendall(TX.RawData)
    print(TX.RawData)
    rec = client.recv(1024)
    if not rec :
        break
    if 'True' in rec.decode():
        i+=1
    

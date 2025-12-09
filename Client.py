import socket
import time

SERVER_IP = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

while True:
    msg = 2
    client.sendall(str(hex(msg)).encode())
    print("Sent:", msg)

    ack = client.recv(1024)
    print("Received:", ack.decode())

    time.sleep(1)
    

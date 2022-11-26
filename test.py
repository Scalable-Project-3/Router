import socket
import sys
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 35222))
for line in sys.stdin:
    msg = line
    print(msg)
    sock.sendto(msg.encode(), ("127.0.0.1", 34333))
    msg, addr = sock.recvfrom(1024)
    print(msg, addr)


import socket
import sys
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for line in sys.stdin:
    sock.sendto(line.encode(), ("127.0.0.1", 34333))


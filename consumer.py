import socket
import threading
from multiprocessing import Process, Queue, JoinableQueue
import time
import random

ROUTER_PORT = 33333
CONSUMER_PORT = 35333
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class Consumer:
    def __init__(self,host):
        self.host = host

    def Listen_device(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, CONSUMER_PORT))
        while True:
            msg, addr = sock.recvfrom(1024)
            addr_str = addr[0] + ':' + str(addr[1])
            print(msg)

    def send_interest():
        interest_name = ['cow/temperature', 'cow/speed', 'cow/pressure']
        requester_name = ['farmer/area/1/cow', 'farmer/area/2/cow', 'farmer/area/3/cow']
        for Interest_Name in interest_name:
            for Requester_Name in requester_name:
                message = f'interest,{Interest_Name},{Requester_Name}'.encode('utf-8')
                sock.sendto(message, ("127.0.0.1", 34333))

    def main(self):
        listen_thread = threading.Thread(target=consumer.Listen_device())
        listen_thread.start()
        send_interest()

if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    consumer = Consumer(host)
    consumer.main()

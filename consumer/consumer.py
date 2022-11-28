import socket
import time
import random
import sys
import threading
import asyncio
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.application import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import PromptSession
import pandas as pd
import csv

ROUTER_PORT = 33333
CONSUMER_PORT = 33533
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
class Consumer:
    def __init__(self, host):
        self.host = host

    def listen_device(self):
        try:
            sock.bind((self.host, CONSUMER_PORT))
            while True:
                msg, addr = sock.recvfrom(1024)
                print(msg)

        finally:
            sock.close()
            print('socket close')

    def test(self, interest_name):
        sock.sendto(interest_name.encode(), ("127.0.0.1", 34333))

    async def send_interest(self):
        isLoop=True;
        kb=KeyBindings()
        @kb.add('c-c')
        async def _(event):
            nonlocal isLoop
            isLoop=False
            event.app.exit()

        session = PromptSession()
        while isLoop:
            try:
                interest_name = await session.prompt_async('>>', key_bindings=kb)
                with open('./configure.csv', 'r') as f:
                    reader = csv.reader(f)
                    console=interest_name.split(',')[1].split('/')[0]+'/'+interest_name.split(',')[1].split('/')[1]+'/'+interest_name.split(',')[1].split('/')[2]
                    for row in reader:
                        if (row[0]== console):
                            msg = bytes(interest_name, 'utf-8')
                            print(str(row[1]))
                            sock.sendto(msg, (str(row[1]), 34333))
                print('send interest_name: %s' % interest_name)
                t = threading.Thread(target = self.test, args = (interest_name,))
                t.setDaemon(True)
                t.start()
            except KeyboardInterrupt:
                return

    async def main(self):
        head_row = pd.read_csv('./configure.csv', nrows=0)
        head_row_list = list(head_row)
        csv_result = pd.read_csv('./configure.csv', usecols=head_row_list)
        with patch_stdout():
            try:
                await self.send_interest()
            finally:
                pass

    def run(self):
        try:
            from asyncio import run
        except ImportError:
            asyncio.run_until_complete(self.main())
        else:
            asyncio.run(self.main())


if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    consumer = Consumer(host)
    listen_thread = threading.Thread(target=consumer.listen_device)
    listen_thread.setDaemon(True)
    listen_thread.start()
    consumer.run()


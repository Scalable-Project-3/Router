#!./pj3-env/bin/python

import socket
import threading
import sys, getopt

ROUTER_PORT = 33333
DEVICE_PORT = 34333


class Router:

    def __init__(self, host, port, device_port, router_name):
        self.host = host
        self.port = port
        self.device_port = device_port
        self.router_name = router_name
        self.router_name_end_idx = len(self.router_name)

        # name: ip:port
        self.name_ip_map = {}
        # interest_name: {requester_name}
        self.pit = {}
        # resource_name: [next_hop_name]
        self.fib = {}
        # name: val
        self.content_store = {}
        # socket for sending msg
        self.sender_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sender_sock.bind((self.host, self.device_port))
        # with open('config/config.txt', 'rb') as f:
        #     lines = f.readlines()
        #     for line in lines:
        #         info = line.strip().split(',')
        #         if info[1] == self.router_name:
        #             continue
        #
        #         other_router_addr = info[0]
        #         other_router_name = info[1]
        #         self.name_ip_map[other_router_name] = other_router_addr
        #         self.fib[other_router_name] = other_router_name

    def updateNameIpMap(self, name, ipaddr):
        if not name in self.name_ip_map:
            self.name_ip_map[name] = ipaddr

    def updatePIT(self, interest_name, requester_name, addr, operation='update'):
        if operation == 'update':
            # interest_name: Bob/Temperature; requester_name: control center
            if interest_name in self.pit:
                self.pit[interest_name].add(requester_name)
            else:
                # create a new set for this interest
                requester_list = {requester_name}
                self.pit[interest_name] = requester_list
            # if the sender of this interest packet is an unknown host
            # update the name ip map
            self.updateNameIpMap(requester_name, addr)
        elif operation == 'delete':
            if interest_name in self.pit:
                self.pit.pop(interest_name)

    def updateFIB(self, sender_name, resource_name, addr):
        if resource_name in self.fib:
            next_hop_list = self.fib[resource_name]
            if len(next_hop_list) > 3:
                next_hop_list.pop()
                self.fib[resource_name].insert(0, sender_name)
        else:
            next_hop_list = [sender_name]
            self.fib[resource_name] = next_hop_list
        # if the sender of this resource packet is an unknown host
        # update the name ip map
        self.updateNameIpMap(sender_name, addr)

    def isInCS(self, name):
        if name in self.content_store:
            return True
        return False

    def updateCS(self, name, content):
        self.content_store[name] = content

    # interest name: Bob/temperature
    # interest format: "interest,interest_name,requester_name"
    def forwardInterest(self, interest_name):
        if interest_name in self.fib:
            next_hops = self.fib[interest_name]
            for next_hop in next_hops:
                new_msg = "interest," + interest_name + "," + self.router_name
                self.sendData(interest_name, new_msg, next_hop)
        else:
            # prefix matching
            name_arr = interest_name.split('/')
            final_match = ''
            tmp = ''
            for name in name_arr:
                tmp = tmp + name
                if tmp not in self.fib:
                    break
                final_match = tmp
                tmp = tmp + '/'

            new_msg = 'interest,' + self.router_name + '/' + interest_name + ',' + self.router_name
            self.sendData('', new_msg, final_match)

        print("No forward info in FIB")

    def sendData(self, name, new_msg, dest_name=None):
        # new_resource_msg = "resource," + self.router_name + "," + resource_name + "," + resource_content
        if dest_name is None:
            if name in self.pit:
                requester_names = self.pit[name]
                for requester in requester_names:
                    if requester in self.name_ip_map:
                        ip_port = self.name_ip_map[requester].split(":")
                        print(ip_port)
                        print(new_msg)
                        self.sender_sock.sendto(new_msg.encode(), (ip_port[0], int(ip_port[1])))
            else:
                print("Unknown requester, Store in CS...")
        else:
            if dest_name in self.name_ip_map:
                ip_port = self.name_ip_map[dest_name].split(':')
                print(ip_port)
                print(new_msg)
                self.sender_sock.sendto(new_msg.encode(), (ip_port[0], int(ip_port[1])))

    def getAreaPrefix(self, full_interest):
        name_arr = full_interest.split('/')
        area_prefix = ''
        for i in range(3):
            area_prefix = area_prefix + name_arr[i] + '/'

        return area_prefix[:-1]

    # def forward2Router(self, msg, addr):
    #     interest_name, requester_name = msg[1][self.router_name_end_idx + 1:], msg[2]
    #     # msg[1]: diver/area/{num}/Bob/Temperature
    #     # msg[2]: control center || diver/area/{num}
    #     forwarded_router = self.getAreaPrefix(msg[1])
    #     self.updatePIT(interest_name, requester_name, addr)
    #     self.forwardInterest()

    # message format:
    # discover message: "discover,sender_name" stored in name_ip_map
    # interest message: "interest,interest_name,requester_name" stored in pit
    # resource message: "resource,sender_name,resource_name,val"
    #                   update fib and store content in content store
    def handleMsg(self, msg, addr):
        if msg:
            msg = msg.decode('utf-8')
            print('Received message: ', msg)
            msg = msg.split(',')
            if len(msg) >= 2 and msg[0] == 'discover':
                device_name = msg[1].lower()
                self.updateNameIpMap(device_name, addr)
                self.updateFIB(device_name, device_name, addr)
            elif len(msg) >= 3 and msg[0] == 'interest':
                # if self.getAreaPrefix(msg[1]) != self.router_name:
                #     self.forward2Router(msg, addr)
                # else:
                interest_name, requester_name = msg[1][self.router_name_end_idx + 1:].lower(), msg[2].lower()
                # interest_name: Bob/Temperature
                # requester_name: control center
                if not self.isInCS(interest_name):
                    # if not hit CS, check and update PIT
                    self.updatePIT(interest_name, requester_name, addr)
                    self.forwardInterest(interest_name)
                else:
                    # first update name ip map in case it doesn't exist
                    self.updateNameIpMap(requester_name, addr)
                    # if hit, directly return data
                    new_msg = "resource," + self.router_name + "," + msg[1] + "," + self.content_store[interest_name]
                    self.sendData(interest_name, new_msg, requester_name)
            elif len(msg) >= 4 and msg[0] == 'resource':
                # resource,Bob,Bob/Temperature,37
                sender_name, resource_name, content = msg[1].lower(), msg[2].lower(), msg[3]
                self.updateFIB(sender_name, resource_name, addr)
                # resource,diver/area/1,diver/area/1/Bob/Temperature,37
                new_msg = "resource," + self.router_name + "," + self.router_name + '/' + resource_name + "," + content
                self.sendData(resource_name, new_msg)
                self.updatePIT(resource_name, '', '', 'delete')
                self.updateCS(resource_name, content)
            else:
                print('cannot recognize this message')
        else:
            print('empty msg received')

    def listenToDevices(self):
        while True:
            msg, addr = self.sender_sock.recvfrom(1024)
            addr_str = addr[0] + ':' + str(addr[1])
            self.handleMsg(msg, addr_str)


def main(argv):
    host = ''
    port = ''
    device_port = ''
    router_name = ''

    try:
        opts, args = getopt.getopt(argv, "ho:p:d:n:", ["host=", "port=", "device_port=", "name="])
    except getopt.GetoptError:
        print('router.py -o <host> -p <port> -d <device port> -n <router name>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("router.py -o <host> -p <port> -d <device port> -n <router name>")
            sys.exit()
        elif opt in ("-o", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-d", "--device"):
            device_port = arg
        elif opt in ("-n", "--name"):
            router_name = arg
    if host == '' or port == '' or router_name == '':
        print("use command line:", "router.py -o <host> -p <port> -d <device port> -n <router name>")
        sys.exit()

    print('host: ', host)
    print('port: ', port)
    print('device port: ', device_port)
    print('router name: ', router_name)

    router = Router(host, int(port), int(device_port), router_name)
    listen_thread = threading.Thread(target=router.listenToDevices())
    listen_thread.start()


if __name__ == '__main__':
    main(sys.argv[1:])

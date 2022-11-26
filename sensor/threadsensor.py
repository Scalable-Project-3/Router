import socket
import logging
import threading
import time
import socket
import random


def sensorData(clientMsg, i):
    clientMsg = clientMsg.lower()
    clientMsg = clientMsg.replace(" ", "")
    clientMsg_arr = clientMsg.split(',')
    clientMsg = clientMsg_arr[1].split('/')
    sensorValue = ""
    if "temperature" in clientMsg:
        sensorValue += "Temperature," + str(random.randint(35, 40))
    if "pressure" in clientMsg:
        sensorValue += "Pressure/" + str(random.randint(76, 84)) + "/"
    if "speed" in clientMsg:
        sensorValue += "Speed/" + str(random.randint(0, 5)) + "/"
    if "surroundingtemperature" in clientMsg:
        sensorValue += "Surrounding Temperature/" + str(random.randint(5, 10)) + "/"
    if "bloodoxygenlevel" in clientMsg:
        sensorValue += "Blood oxygen level/" + str(random.randint(80, 100)) + "/"
    if "heartbeat" in clientMsg:
        sensorValue += "Heart Beat/" + str(random.randint(75, 80)) + "/"
    if "hydration" in clientMsg:
        sensorValue += "Hydration/" + str(random.randint(69, 73)) + "/"
    if "bloodsugar" in clientMsg:
        sensorValue += "Blood Sugar/" + str(random.randint(89, 93)) + "/"

    return sensorValue


def discovery(UDPsensor, i):
    bytesToSend = str.encode("discover," + i)
    routerAddressPort = ("127.0.0.1", 34333)
    UDPsensor.sendto(bytesToSend, routerAddressPort)


def pi_sensor(i):
    hostname = socket.gethostname()
    localIP = socket.gethostbyname(hostname)
    localPort = i[0]
    bufferSize = 1024
    UDPsensor = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPsensor.bind((localIP, localPort))
    print("UDP snsor up and listening in port " + str(i[0]))
    discovery(UDPsensor, i[1])
    while (True):
        bytesAddressPair = UDPsensor.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        clientMsg = message.decode("utf-8")
        # msgFromServer = i[1] + "\n" + sensorData(clientMsg, i[1])
        # resource format: "resource,sender_name,resource_name,val"
        msgFromServer = "resource," + i[1] + "," + i[1] + '/' + sensorData(clientMsg, i[1])
        print(msgFromServer)
        bytesToSend = str.encode(msgFromServer)
        UDPsensor.sendto(bytesToSend, address)
        print(clientMsg,address)

for i in [[33000, 'Bob'], [34000, 'Alice'], [35000, 'Eve'], [36000, 'John'], [37000, 'Ben']]:
    logging.info("Main    : create and start thread %d.", i)
    x = threading.Thread(target=pi_sensor, args=(i,))
    x.start()
    time.sleep(2)

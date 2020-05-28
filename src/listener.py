#!/usr/bin/python
# -*- coding: utf-8 -*-

from bluetooth import *
from subprocess import call
from threading import Thread
from sound import hps, record
import tuner, time

# Unique identifier for the GuitarAutoTuner service, used by the client to connect
UUID = '88027442-d30d-4ea1-b1be-23e85c96901a'


def getServerSocket():
    'Activates discoverability, opens a bluetooth server socket and publishes the server'
    call(['sudo', 'hciconfig', 'hci0', 'piscan'])

    servSocket = BluetoothSocket(RFCOMM)
    servSocket.bind(('', PORT_ANY))
    servSocket.listen(1)

    advertise_service(servSocket, 'GuitarAutoTuner Service',
                      service_id = UUID,
                      service_classes = [UUID, SERIAL_PORT_CLASS],
                      profiles = [SERIAL_PORT_PROFILE])
    return servSocket


def getClientSocket(serverSocket):
    'Returns the client socket when a connection is established'
    clientSocket, clientAddress = serverSocket.accept()
    print "Connected to the client", clientAddress
    return clientSocket


def defaultTuner():
    'Launchs repeatedly the default tuner (without need of application)'
    while True:
        tuner.main()
        if tuner.STOP: break
        time.sleep(2)


def receiveCommand(clientSocket):
    'Waits to receive a command on the client socket, decodes it and returns it'
    data = str(clientSocket.recv(1024)).split(":")
    print data
    return data[0], data[1:]


def executeCommand(command, args, clientSocket):
    'Interprets the command sent by the client and executes it'

    if command == "TUNE":
        try:
            time.sleep(1)
            tuner.main(float(args[0]))
        except:
            clientSocket.send("ERROR")
            return
        clientSocket.send("OK")

    elif command == "GETPITCH":
        try:
            pitch = getPitch()
            print pitch
        except:
            clientSocket.send("ERROR")
            return
        clientSocket.send(str(pitch) if pitch is not None else "ERROR")

    else:
        print "Bad command sent by application: " + command


def getPitch():
    'Tries 30 times to get a good value of pitch'

    for i in range(30):
        data = record.rec(int(record.RATE*0.2))
        record.closeStream()

        pitch = hps.obtainPitch(data, fftScale = 6, fftFraction = 2)
        if pitch is not None: return pitch

    return None


def main():
    ''' Main funtion of listener
    Creates thread for default tuner and waits for bluetooth connections.
    When the client is connected, we stop the default tuner and we proceed
    to receive and execute commands from it.
    Once the connection is closed, we go back to the beginning and start again.
    '''
    while True:
        default = Thread(target=defaultTuner)
        default.setDaemon(True)
        default.start()
        print "Default tuner called"

        servSocket = getServerSocket()
        clientSocket = getClientSocket(servSocket)
        tuner.stopTuner()
        default.join()

        try:
            while True:
                command, args = receiveCommand(clientSocket)
                executeCommand(command, args, clientSocket)
        except:
            print "Connection closed"
            servSocket.close()


if __name__ == '__main__': main()

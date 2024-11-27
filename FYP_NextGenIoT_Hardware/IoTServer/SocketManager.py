from threading import Lock

import timeUtil
import SequanSocket



class SocketManager:
    __currentSocket = None
    __retry_times = 50
    __delay_chip = 100
    __RSSI = 0
    socket_lock = Lock()

    def __init__(self, port, bps, timex, retryTimes=50, delay_chip=100):
        self.__currentSocket = SequanSocket.SequanSocket(port, bps, timex)
        self.__retry_times = retryTimes
        self.__delay_chip = delay_chip
        timeUtil.milliSleep(200)
        if not self.__currentSocket.isEnable():
            if self.__currentSocket.enableModule():
                print("waiting for SETUP functions")
                while not self.__currentSocket.isEnable():
                    print("try to attach to the network")
            else:
                print("enable module function failed...")
        print("Module Functions Initialization complete, now you can connect to Network")

    def setTCPSocket(self, ip, port):
        while not self.__currentSocket.makeTCPconnection(ip, port):
            timeUtil.milliSleep(1000)
            print("Try to make TCP connection...")
            print("rssi:", self.getRssi())
        return self.__getSocket()

    def setUDPSocket(self, ip, port):
        while not self.__currentSocket.makeUDPconnection(ip, port):
            timeUtil.milliSleep(1000)
            print("Try to make UDP connection...")
        return self.__getSocket()

    def RecvWithNoTimeout(self):
        if self.__getSocket().isBufferEmpty():
            return ""
        else:
            return self.__getSocket().getBuffer().decode()


    def RecvWithTimeout(self):
        i = self.__retry_times
        while i > 0 and self.__getSocket().isBufferEmpty():
            timeUtil.milliSleep(self.__delay_chip)
        if not self.__getSocket().isBufferEmpty():
            return self.__getSocket().getBuffer().decode()
        else:
            return ""

    def RecvWithInfinityLoop(self):
        while self.__getSocket().isBufferEmpty():
            timeUtil.milliSleep(100)
        with self.socket_lock:
            pass
        #print("recv after lock")
        content = self.__getSocket().getBuffer()
        #print(content)
        #print(type(content) == type('1'))
        if type(content) == type('1'):
            return ""
        else:
            return content.decode()

    def sendPacketWrapper(self, packet):
        if self.__currentSocket.isConnectedToServer():
            self.__currentSocket.sendPacket(packet)

    def endConnection(self):
        self.__currentSocket.exitTransmission()
        self.__currentSocket.closeSocket()

    def getRssi(self):
        self.__RSSI = self.__getSocket().getRSSI()
        return self.__RSSI

    def getRssi_inTrans(self):
        with self.socket_lock:
            self.__RSSI = self.__getSocket().getRSSIAndResumeSocket()
        return self.__RSSI

    def __getSocket(self):
        return self.__currentSocket

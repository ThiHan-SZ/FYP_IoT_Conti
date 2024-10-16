import logging
import time

import timeUtil

import serial


class SequanSocket:
    __CMD_dict = {
        "AT_TEST": "AT",
        "SET_SOCKET": "AT+SQNSD=1",
        "ENABLE_MODULE": "AT+CFUN=1",
        "SHUTDOWN_SOCKET": "AT+SQNSH=1",
        "CHECK_MODULE": "AT+CEREG?"
    }
    __buffer = ""
    __serialPort = None
    __connection = None

    def __init__(self, port, speed, timeoutx):
        self.__serialPort = serial.Serial(port, speed, timeout=timeoutx / 1000, write_timeout=0)
        self.__serialPort.flushInput()
        self.cleanBuffer()
        timeUtil.milliSleep(1000)
        IS_EXIT = False
        if not self.checkATfunction() and not IS_EXIT:
            print("Try to init the module...")
            self.exitTransmission()
            self.cleanBuffer()
            IS_EXIT = self.IsEXIT()
        while not self.checkATfunction() and not IS_EXIT:
            print("The module has no response...How about restart this module?")
            self.exitTransmission()
            self.cleanBuffer()
            IS_EXIT = self.IsEXIT()
        self.cleanBuffer()
        self.closeSocket()

    def __sendCmdAndCheck(self, command, expect_result1, expect_result2=None):
        return self.__sendRawAndCheck(command + '\r' + '\n', expect_result1, expect_result2)

    def __sendRawAndCheck(self, command, expect_result, other_expect_result=None):
        IS_SUCCESS = False
        if self.__serialPort is not None:
            logging.debug(command)
            self.__serialPort.write(command.encode())
            timeUtil.milliSleep(500)
            result_lines = self.__serialPort.readlines()
            #print(command, result_lines)
            for line in result_lines:
                #print(command)
                #print(line)
                #logging.debug(line)
                if expect_result in line.decode():
                    #print(line.decode())
                    IS_SUCCESS = True
                if other_expect_result is not None and other_expect_result in line.decode():
                    IS_SUCCESS = True
        return IS_SUCCESS

    def checkATfunction(self):
        return self.__sendCmdAndCheck(self.__CMD_dict["AT_TEST"], "OK")

    def IsEXIT(self):
        return self.__sendCmdAndCheck("+++", "ERROR")

    def enableModule(self):
        return self.__sendCmdAndCheck(self.__CMD_dict["ENABLE_MODULE"], "OK")

    def isEnable(self):
        return self.__sendCmdAndCheck(self.__CMD_dict["CHECK_MODULE"], "+CEREG: 2,5", "+CEREG: 2,1")

    def makeTCPconnection(self, ip, port):
        if self.__makeConnection(self.__CMD_dict["SET_SOCKET"] + ",0,", ip, port):
            self.__connection = "TCP"
        return self.__connection == "TCP"

    def makeUDPconnection(self, ip, port):
        if self.__makeConnection(self.__CMD_dict["SET_SOCKET"] + ",1,", ip, port):
            self.__connection = "UDP"
        return self.__connection == "UDP"

    def isConnectedToServer(self):
        logging.debug(self.__connection)
        return self.__connection is not None

    def __makeConnection(self, CMD, ip, port):
        CMD_tail = f"{port},\"{ip}\",0,0,0"
        CMD += CMD_tail
        return self.__sendCmdAndCheck(CMD, "CONNECT")

    def sendPacket(self, packet):
        if self.__serialPort is not None:
            self.__serialPort.write(packet.encode("UTF-8"))
        else:
            print("No Serial Port...")

    def exitTransmission(self):
        time.sleep(1)
        self.__sendRawAndCheck("+++", "OK")
        time.sleep(1)
        return self.IsEXIT()

    def closeSocket(self):
        self.__connection = None
        return self.__sendCmdAndCheck(self.__CMD_dict["SHUTDOWN_SOCKET"], "OK")

    def isBufferEmpty(self):
        logging.debug(self.__serialPort.in_waiting)
        return self.__serialPort.inWaiting() == 0

    def cleanBuffer(self):
        return self.__serialPort.reset_output_buffer()

    def getBuffer(self):
        if not self.isBufferEmpty():
            self.__buffer = self.__serialPort.read(self.__serialPort.inWaiting())
            self.cleanBuffer()
            return self.__buffer
        else:
            return ""

    def resumeSocket(self):
        return self.__sendCmdAndCheck("AT+SQNSO=1", "CONNECT")

    def getRSSI(self):
        result = 0
        if self.__serialPort is not None:
            command = "AT+CSQ\r\n"
            self.__serialPort.write(command.encode())
            timeUtil.milliSleep(200)
            result_lines = self.__serialPort.readlines()
            # print("line:",result_lines)
            for line in result_lines:
                #print(line)
                if "+CSQ:" in line.decode():
                    logging.debug(line)
                    line_decode = line.decode()
                    result = -113 + 2 * (int(line_decode.split(':')[1].split(',')[0]))
        return str(result)

    def getRSSIAndResumeSocket(self):
        IS_EXIT = False
        while not self.checkATfunction() and not IS_EXIT:
            #print("Try to EXIT the transmission mode...")
            self.exitTransmission()
            self.cleanBuffer()
            IS_EXIT = self.IsEXIT()
        self.cleanBuffer()
        result = self.getRSSI()
        self.resumeSocket()
        self.cleanBuffer()
        return result


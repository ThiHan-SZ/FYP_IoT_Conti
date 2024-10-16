import socket
import timeUtil
import buildUtil

obj = socket.socket()
obj.connect(('127.0.0.1', 6000))

counter = 0
RSSI = -60

counter = 0
delay = 1000

while counter < 5:
    counter += 1
    packet = buildUtil.build_packet(counter,RSSI)
    obj.sendall(bytes(packet, encoding='utf-8'))
    print(packet)
    timeUtil.milliSleep(delay)

obj.close()
import SocketManager
import buildUtil
import timeUtil
from serial.tools import list_ports
port_list = list(list_ports.comports())

print("begin init!")
port = "COM8"

'''
num = len(port_list)
if num <=0:
    port_list = list(list_ports.comports())
    print("找不到任何串口设备")
    exit()
else:
    port = port_list[num-1][0]
'''


bps = 115200
timex = 5
retry_times = 5
delay_chip = 20
ip = "3.1.103.12"
port_num = "6000"

CYCLE_DELAY = 1  #SEC
GET_RSSI_AFTER_CYCLE_NUM = 1

socketManager = SocketManager.SocketManager(port,bps,timex,2,1)
RSSI = socketManager.getRssi()
print("RSSI:", RSSI)
socketManager.setUDPSocket(ip, port_num)  # Change this line
print("setup UDP cmplt!")  # Change this line

counter = 0
delay = 1000
RSSI = -60

while True:
    if counter % GET_RSSI_AFTER_CYCLE_NUM == 0:
        RSSI = socketManager.getRssi_inTrans()
        print("RSSI:", RSSI)
    content = socketManager.RecvWithNoTimeout()
    if len(content) != 0:
        print("content:",content)
    if"NO CARRIER" in content:
        print("remote side link failed... try to reconnected")
        socketManager.endConnection()
        socketManager.setUDPSocket(ip, port_num)  # Change this line
    counter += 1
    packet = buildUtil.build_packet(counter, RSSI)
    print(packet)
    socketManager.sendPacketWrapper(packet)
    timeUtil.milliSleep(delay)

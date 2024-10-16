import SocketManager
import buildUtil
import timeUtil
from serial.tools import list_ports
port_list = list(list_ports.comports())

print("begin init!")
port = "/dev/ttyUSB0"

num = len(port_list)
if num <=0:
    port_list = list(list_ports.comports())
    print("找不到任何串口设备")
    exit()
else:
    port = port_list[num-1][0]

bps = 115200
timex = 5
retry_times = 5
delay_chip = 20
ip = "18.183.153.1"
port_num = "6000"

CYCLE_DELAY = 1  #SEC
GET_RSSI_AFTER_CYCLE_NUM = 1

socketManager = SocketManager.SocketManager(port,bps,timex,2,1)
RSSI = socketManager.getRssi()
print("RSSI:", RSSI)
socketManager.setTCPSocket(ip, port_num)
print("setup TCP cmplt!")

counter = 0
delay = 60000
RSSI = -60

while True:
    content = socketManager.RecvWithNoTimeout()
    if len(content) != 0:
        print("content:",content)
    if"NO CARRIER" in content:
        print("remote side link failed... try to reconnected")
        socketManager.endConnection()
        socketManager.setTCPSocket(ip, port_num)


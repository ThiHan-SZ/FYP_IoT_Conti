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

socketManager = SocketManager.SocketManager(port,bps,timex,2,100)
RSSI = socketManager.getRssi()
print("RSSI:", RSSI)
socketManager.setTCPSocket(ip, port_num)
print("setup TCP cmplt!")

counter = 0
delay = 30000
RSSI = -60
heartbeat_timestamp = timeUtil.getTimeStampInMs()

while True:
    content = socketManager.RecvWithNoTimeout()
    # detect the heartbeat.
    if len(content) != 0:
        print("received content:",content)
        heartbeat_timestamp = timeUtil.getTimeStampInMs()
        if"NO CARRIER" in content:
            print("remote side link failed... try to reconnected")
            socketManager.endConnection()
            socketManager.setTCPSocket(ip, port_num)
            heartbeat_timestamp = timeUtil.getTimeStampInMs()
        else:
            print("Received heartbeat at" + timeUtil.getDateString() )

    # build a new packet
    counter += 1
    if counter % GET_RSSI_AFTER_CYCLE_NUM == 0:
        RSSI = socketManager.getRssi_inTrans()
        print("RSSI:", RSSI)

    packet = buildUtil.build_packet(counter, RSSI)
    print(packet)
    socketManager.sendPacketWrapper(packet)

    # timeout process
    if timeUtil.isTimeOut(heartbeat_timestamp,300000):
        print("remote side No response... try to reconnected")
        socketManager.endConnection()
        socketManager.setTCPSocket(ip, port_num)
        heartbeat_timestamp = timeUtil.getTimeStampInMs()

    # delay
    timeUtil.milliSleep(delay)



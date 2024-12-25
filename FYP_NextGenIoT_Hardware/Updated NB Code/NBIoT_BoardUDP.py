
import SocketManager
import buildUtil
import timeUtil
from serial.tools import list_ports

# import csv
port_list = list(list_ports.comports())

print("begin init!")
port = "COM8"
# port = "/dev/ttyUSB0"

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

CYCLE_DELAY = 1  # SEC
GET_RSSI_AFTER_CYCLE_NUM = 1

socketManager = SocketManager.SocketManager(port, bps, timex, 2, 1)  # (2,100)
RSSI = socketManager.getRssi()
print("RSSI:", RSSI)
MONI = socketManager.getMoni()
print("MONI:", MONI)
socketManager.setUDPSocket(ip, port_num)
print("setup UDP cmplt!")

counter = 0
delay = 100
RSSI = -60
# heartbeat_timestamp = timeUtil.getTimeStampInMs()
# file_name = "result/" + timeUtil.getDateString4title() + ".csv"

'''
with open(file_name, 'w') as f:
    csv_write = csv.writer(f)
    csv_head = ["sequence number", "RSSI", "send time", "content"]
    csv_write.writerow(csv_head)
'''

while True:
    '''    
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
    '''

    # build a new packet
    counter += 1
    if counter % GET_RSSI_AFTER_CYCLE_NUM == 0:
        RSSI = socketManager.getRssi_inTrans()
        print("RSSI:", RSSI)
        MONI = socketManager.getMoni_inTrans()
        print("MONI:", MONI)
        content = socketManager.RecvWithNoTimeout()
    if len(content) != 0:
        print("content:", content)
    if "NO CARRIER" in content:
        print("remote side link failed... try to reconnected")
        socketManager.endConnection()
        socketManager.setUDPSocket(ip, port_num)

    # packet = buildUtil.build_packet(counter, RSSI)
    packet = buildUtil.build_packet_with_custom_data(counter, RSSI, MONI)
    print(packet)
    socketManager.sendPacketWrapper(packet)
    timeUtil.milliSleep(delay)

    '''
    with open(file_name, 'a+') as f:
        csv_write = csv.writer(f)
        data_row = [counter,RSSI,timeUtil.getTimeOnlyString(),packet]
        csv_write.writerow(data_row)
    socketManager.sendPacketWrapper(packet)
    '''

    '''
    # timeout process
    if timeUtil.isTimeOut(heartbeat_timestamp,300000):
        print("remote side No response... try to reconnected")
        socketManager.endConnection()
        socketManager.setTCPSocket(ip, port_num)
        heartbeat_timestamp = timeUtil.getTimeStampInMs()
    '''

    # delay
    timeUtil.milliSleep(delay)



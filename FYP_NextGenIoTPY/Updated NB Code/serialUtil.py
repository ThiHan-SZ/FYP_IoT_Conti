from serial.tools import list_ports

port_list = list(list_ports.comports())

num = len(port_list)

if num <=0:
    print("找不到任何串口设备")
else:
    print(port_list[num-1][0])
    for i in range(num):
        port = list(port_list[i])
        print(port)
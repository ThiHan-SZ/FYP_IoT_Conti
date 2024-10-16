#!/usr/bin/python
#encoding:utf-8

'''
server
'''
import socket, sys, select
import threading
import csv

import buildUtil
import timeUtil

BUF_SIZE = 4096
PORT = 6000
TIMELIMIT = 30000 #ms

inputs = []
outputs = []

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print("Error creating socket: %s" %e)
    sys.exit()

try:
    server.bind(("0.0.0.0", PORT))
except socket.error:
    print ("Bind failed!")
    sys.exit()
print ("Socket bind complete")

server.listen(10)
print ("Socket now listening")


def link_handler(link, client):
    """
    该函数为线程需要执行的函数，负责具体的服务器和客户端之间的通信工作
    :param link: 当前线程处理的连接
    :param client: 客户端ip和端口信息，一个二元元组
    :return: None
    """
    global inputs
    SIG_CONN_FAIL = False

    print("服务器开始接收来自[%s:%s]的请求...." % (client[0], client[1]))
    heartBeatTime = timeUtil.getTimeStampInMs()
    inputs.append(link)

    file_name = timeUtil.getDateString4title()+".csv"
    client_recv_buffer = ""

    with open(file_name,'w') as f:
        csv_write = csv.writer(f)
        csv_head = ["sequence number", "RSSI", "send time", "received time", "received date"]
        csv_write.writerow(csv_head)

    while not SIG_CONN_FAIL:     # 利用一个死循环，保持和客户端的通信状态
        r_list, w_list, e_list = select.select(inputs, outputs, inputs, 1)
        for connection in r_list:    # 当socket有数据时，将数据读取进缓存中
            if connection == link:
                try:
                    client_data = connection.recv(1024).decode()
                    client_recv_buffer += client_data
                    # print("来自[%s:%s]的客户端向你发来信息：%s" % (client[0], client[1], client_data))
                    heartBeatTime = timeUtil.getTimeStampInMs()
                except Exception as e:
                    print(e)
                    print ("One Client (IP: %s) Connected over!" % client[0])
                    inputs.remove(link)
                    SIG_CONN_FAIL = True
                    break
                else:
                    if client_data == "":
                        print("other side (IP: %s) TCP Connection terminated!" % client[0])
                        inputs.remove(link)
                        SIG_CONN_FAIL = True

        while len(client_recv_buffer) != 0:
            start_index, end_index = buildUtil.getStartAndEndIndex(client_recv_buffer)
            # print(client_recv_buffer)
            # print(start_index, end_index)
            pkt, client_recv_buffer = buildUtil.cutThePacketFromBuffer(client_recv_buffer,start_index,end_index)
            # print("pkt:"+pkt)
            #print("client_buffer:"+client_recv_buffer)
            if len(pkt) != 0:
                if buildUtil.isPacketValid(pkt):
                    seq_num, rssi, sendtime = buildUtil.read_packet(pkt)
                    # print(pkt)
                    with open(file_name, 'a+') as f:
                        csv_write = csv.writer(f)
                        data_row = [seq_num,rssi,sendtime,timeUtil.getTimeStampInMs(),timeUtil.getDateString()]
                        print("decode cmplt: SEQ="+seq_num+" ,sendtime="+sendtime)
                        csv_write.writerow(data_row)




        if timeUtil.isTimeOut(heartBeatTime, TIMELIMIT):
            print("TIMEOUT, BREAK THE CONNECTION....")
            inputs.remove(link)
            SIG_CONN_FAIL = True

    link.close()

print('启动socket服务，等待客户端连接...')

while True:
    conn, address = server.accept()
    print ("Connected with %s: %s " % (address[0], str(address[1])))
    t = threading.Thread(target=link_handler, args=(conn, address))
    t.start()

server.close()

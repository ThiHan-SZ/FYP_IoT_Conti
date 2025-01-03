'''
packet的格式如下
$len#00000000#RSSI#TIMESTAMP?
1+5+1+8+1+4+1+13+1
'''

import timeUtil

ALIGNMENT_LEN = 5
ALIGNMENT_SER = 8
ALIGNMENT_RSSI = 4

START_SYM = '$'
END_SYM = '?'


def getPaddingIntString(num, align=8):
    if isinstance(num,int):
        integerStr = str(num)
        return integerStr.zfill(align)
    else:
        #print("else")
        return num.zfill(align)

def getStartAndEndIndex(str):
    start_index = str.find("$")
    end_index = str.find("?")
    return start_index, end_index

def cutThePacketFromBuffer(str,start_index,end_index):
    '''
    :param str: 接受buffer内的内容
    :param start_index: packet的开始索引
    :param end_index: packet的结束索引
    :return: packet字符串，剩余字符串
    '''
    if len(str) == 0:
        #buffer内部没有内容
        return "", ""
    elif start_index == -1 and end_index == -1 and len(str) != 0:
        #buffer内部有内容，但是没有packet开始符号和终止符号，这样就把buffer直接清空
        return "", ""
    elif start_index == -1 and end_index != -1:
        #buffer内部有内容，没有开始符号，但是有终止符号，那么直接认为是掉包
        return "", ""
    elif start_index != -1 and end_index == -1:
        #buffer内不为空，有了开始符号，但是没有终止符号
        return "", str
    elif end_index != -1 and start_index != -1 and start_index>end_index:
        #buffer不为空，且结束符号在前,开始符号在后
        return "", str[start_index:]
    else:
        if len(str) == end_index+1:
            return str[start_index:end_index+1], ""
        else:
            return str[start_index:end_index+1], str[end_index+1:]

def isPacketValid(pkt):
    '''
    根据送入的packet报文中的长度，判断packet是否为合法packet（MD5对于arduino来说可能过于 heavy了）
    :param pkt:
    :return:
    '''
    if len(pkt) < 35:
        return False
    else:
        return int(pkt[1:ALIGNMENT_LEN+1]) == len(pkt)

def build_packet(serialNum, RSSI):
    pkt = ""
    content = ""+'#'+getPaddingIntString(serialNum,ALIGNMENT_SER) + \
        '#'+getPaddingIntString(RSSI,ALIGNMENT_RSSI) + \
        '#'+ timeUtil.getTimeStampInMs() + \
        '?'
    len4pkt = len(content)+6
    pkt = pkt + '$' + getPaddingIntString(len4pkt,ALIGNMENT_LEN) + content
    return pkt

def read_packet(pkt):
    index = str(pkt).find('#')+1
    ser_num = int(pkt[index:index+ALIGNMENT_SER])
    index = index + ALIGNMENT_SER + 1
    rssi = int(pkt[index:index+ALIGNMENT_RSSI])
    index = index + ALIGNMENT_RSSI + 1
    timestamp = pkt[index:index+13]
    return ser_num, rssi, timestamp
    pass



'''
# buffer = "$00035#00000000#-050#1676194404193?$"
# buffer = "AT?$00035#00000000#-050#1676194404193"
buffer = "AT?+++"
start_index, end_index = getStartAndEndIndex(buffer)
print(start_index,end_index)
print(cutThePacketFromBuffer(buffer,start_index,end_index))
print(isPacketValid("$00035#00000000#-050#1676194404193?"))
print(read_packet("$00035#00000005#-050#1676194404193?"))
'''


# -*- coding: utf-8 -*-
import serial
import time
#打开串口
PS_Getimage =		[ 0XEF,0X01,0XFF,0XFF,0XFF,0XFF,0X01,0X00,0X03,0X01,0X00,0X05 ]#录入图像
PS_GenChar1 =		[ 0xEF,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0x00,0x04,0x02,0x01,0x00,0x08 ]#在特征区1生成特征
PS_GenChar2=		[ 0xEF,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0x00,0x04,0x02,0x02,0x00,0x09 ]#在特征区2生成特征
PS_Match =		    [ 0xEF,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0x00,0x03,0x03,0x00,0x07 ]#对比匹配与否
PS_Search_stored1 = [ 0xEF,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0x00,0x08,0x04,0x01,0x00,0x01,0x00,0x20,0x00,0x2F ]#以特征区1的指纹特征进行全局搜索
PS_Search_stored2 = [ 0xEF,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0x00,0x08,0x04,0x02,0x00,0x01,0x00,0x20,0x00,0x30 ]#以特征区2的指纹特征进行全局搜索
PS_RegModel=		[ 0xEF,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0x00,0x03,0x05,0x00,0x09 ]#合并1、2区特征并存于1、2区
PS_StoreChar_1tox = [ 0xEF,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0x00,0x06,0x06,0x01,0x00,0x03,0x00,0x11 ] #在指纹库指定ID处添加指纹
PS_Empty =		    [ 0xEF,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0x00,0x03,0x0d,0x00,0x11 ] #清空指纹库
PS_DeletChar =		[ 0xEF,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0x00,0x07,0x0c,0x00,0x01,0x00,0x01,0x00,0x16 ]#清空指纹库
global rec_data
rec_data = [3,3,3,3,3,3,3,3,3,3,3]

serialPort="/dev/ttyAMA0" #串口6
baudRate=57600 #波特率


def Send_A_Cmd(serInstance, atCmdStr):
    # print("Command: %s" % atCmdStr)
    serInstance.write(atCmdStr)

def receive_data( ser ):
    global rec_data
    while not ( ser.inWaiting() > 0 ):
        pass
    rec_data = []
    time.sleep(1)
    if ser.inWaiting() > 0:
        for num in range(0, ser.inWaiting()):
             rec_data.insert( num, ser.read(1) )
    ##===========调试用===========
    # if rec_data != [3,3,3,3,3,3,3,3,3,3]:
    #     if rec_data != []:
    #         print( rec_data )  # 可以接收中文

def check_and_set( ID ):
    check = 0
    PS_StoreChar_1tox[11] = ( ID // 256 ) % 256
    PS_StoreChar_1tox[12] = ID % 256
    check = PS_StoreChar_1tox[6] + (PS_StoreChar_1tox[7] * 256) + PS_StoreChar_1tox[8] + PS_StoreChar_1tox[9] + \
            PS_StoreChar_1tox[10] + (PS_StoreChar_1tox[11] * 256) + PS_StoreChar_1tox[12]
    PS_StoreChar_1tox[13] = ( check // 256 ) % 256
    PS_StoreChar_1tox[14] = check % 256

def ADD_FINGERPRINT( ser,ID ):
    while rec_data[9] != b'\x00':#改成do while
        Send_A_Cmd( ser,PS_Getimage )
        receive_data( ser )
    rec_data[9] = 3
    while rec_data[9] != b'\x00':
        Send_A_Cmd( ser,PS_GenChar1 )
        receive_data( ser )
    rec_data[9] = 3
    while rec_data[9] != b'\x00':
        Send_A_Cmd( ser, PS_Getimage )
        receive_data( ser )
    rec_data[9] = 3
    while rec_data[9] != b'\x00':
        Send_A_Cmd( ser,PS_GenChar2 )
        receive_data( ser )
    rec_data[9] = 3
    Send_A_Cmd( ser, PS_Match )
    receive_data( ser )
    if rec_data[9] != b'\x00':
        return 0
    rec_data[9] = 3
    while rec_data[9] != b'\x00':
        Send_A_Cmd( ser, PS_RegModel )
        receive_data( ser )
    rec_data[9] = 3
    check_and_set( int(ID) );
    Send_A_Cmd( ser, PS_StoreChar_1tox )
    receive_data( ser )
    if rec_data[9] == b'\x00':
        rec_data[9] = 3
        return 1
    return 0

def CHECK_FINGERPRINT( ser ):
    #print( "请刷指纹！" )
    rec_data[9] = 3
    while rec_data[9] != b'\x00':
        Send_A_Cmd( ser, PS_Getimage )
        receive_data( ser )
    rec_data[9] = 3
    while rec_data[9] != b'\x00':
        Send_A_Cmd( ser, PS_GenChar1 )
        receive_data( ser )
    rec_data[9] = 3
    Send_A_Cmd( ser, PS_Search_stored1 )
    receive_data( ser )
    if rec_data[9] == b'\x00':
       # print("身份验证成功！ID= %d" %int.from_bytes(rec_data[10] * 256 + rec_data[11], byteorder='big', signed=False))
        return 1,str(int.from_bytes(rec_data[10] * 256 + rec_data[11], byteorder='big', signed=False))
    elif rec_data[9] == b'\x09':
        #print("身份验证错误！指纹库中没有匹配的身份！")
        return 0,' '
    elif rec_data[9] == b'\x01':
        #print("数据收包错误！")
        return 2,'2'

def CLEAR_LIBRARY( ser ):
    rec_data[9] = 3
    while rec_data[9] != b'\x00':
        Send_A_Cmd(ser, PS_Empty)
        receive_data( ser )
        return 1
    #print("指纹库已清空!")
    return 0

def check_and_set_delete( ID, delete_num ):
    global det_check
    PS_DeletChar[10] = (ID // 256) % 256
    PS_DeletChar[11] = ID % 256
    PS_DeletChar[12] = (delete_num // 256) % 256
    PS_DeletChar[13] = delete_num % 256
    det_check = PS_DeletChar[6] + (PS_DeletChar[7] * 256) + PS_DeletChar[8] + PS_DeletChar[9] + (PS_DeletChar[10] * 256) + \
            PS_DeletChar[11] + (PS_DeletChar[12] * 256) + PS_DeletChar[13]
    PS_DeletChar[14] = (det_check // 256) % 256
    PS_DeletChar[15] = det_check % 256

def DELETE_FINGERPRINTS( ser,ID,delete_num ):
    check_and_set_delete(int(ID), int(delete_num))
    rec_data[9] = 3
    Send_A_Cmd(ser, PS_DeletChar)
    receive_data(ser)
    if rec_data[9] == b'\x00':
        return 1
#       print("成功删除 ID= %d 起的 %d 个指纹" %(eval(ID), eval(delete_num)))
    elif rec_data[9] == b'\x01':
        return 2
        #print("数据收包错误!")
    elif rec_data[9] == b'\x10':
       # print("删除模板失败！")
        return 3

def DELETE_ONE_FINGER( ser ,ID):
    PS_DeletChar[10] = (int(ID) // 256) % 256
    PS_DeletChar[11] = int(ID) % 256
    PS_DeletChar[12] = (0x00 // 256) % 256
    PS_DeletChar[13] = 0x01 % 256
    det_check = PS_DeletChar[6] + (PS_DeletChar[7] * 256) + PS_DeletChar[8] + PS_DeletChar[9] + (PS_DeletChar[10] * 256) + \
            PS_DeletChar[11] + (PS_DeletChar[12] * 256) + PS_DeletChar[13]
    PS_DeletChar[14] = (det_check // 256) % 256
    PS_DeletChar[15] = det_check % 256
    rec_data[9] = 3
    Send_A_Cmd(ser, PS_DeletChar)
    receive_data(ser)
    if rec_data[9] == b'\x00':
        return 1
        #print("成功删除 ID= %d的指纹" %(eval(ID)))
    elif rec_data[9] == b'\x01':
        return 2
        #print("数据收包错误!")
    elif rec_data[9] == b'\x10':
        return 3
        #print("删除模板失败！")
    return 0


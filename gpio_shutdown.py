# coding=utf-8
#import OPiZero_GPIO
import time
import os,sys
import signal
import socket
import fcntl
import struct
import datetime
import subprocess
import OPi.GPIO as GPIO
from oled.device import ssd1306, sh1106,const
from oled.render import canvas
from PIL import ImageFont, ImageDraw
#以下为主程序
PinBUTT=11
PinInfor=13
GPIO.setboard(GPIO.ZEROPLUS)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PinBUTT, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
GPIO.setup(PinInfor, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip="ip_error"
    s.close()
    return ip

try:
    nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')#现在
    #读取CPU温度
    file=open("/sys/class/thermal/thermal_zone0/temp")
    temp=float(file.read())/1000
    print(str(temp))
    temp=("%.1f" %temp)
    file.close()
    #读取CPU使用率
    cmd= "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell = True )
    print (CPU)
    #读取内存使用情况
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell = True )
    print ('%s'%MemUsage)
    #读取MMC使用情况
    cmd = "df -h | awk '/mmcblk0p1/{printf \"MMC : %4.1f/%dGB %s\",$3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell = True )
    print ('%s'%Disk)
    #读取U盘使用情况
    cmd = "df -h | awk '/sda/{printf \"UPAN : %4.1f/%dGB %s\",$3,$2,$5}'"
    DiskA = subprocess.check_output(cmd, shell = True )
    print ('%s'%DiskA)  
    #通过OLED屏幕显示信息
    device = ssd1306(port=0, address=0x3C)  # rev.1 users set port=0
    with canvas(device) as draw:
        font=ImageFont.load_default()
        draw.text((0, 0),str(temp)+" C", font=font, fill=255)
        draw.text((0, 10),"IP:"+get_host_ip(), font=font, fill=255)
        draw.text((0, 20),CPU, font=font, fill=255)
        draw.text((0, 30),MemUsage, font=font, fill=255)
        draw.text((0, 40),Disk, font=font, fill=255)
        draw.text((0, 50),DiskA, font=font, fill=255)
    #显示10s
    time.sleep(10)
    device.command(const.DISPLAYOFF)
    while(1):
        if GPIO.input(PinInfor):
            #去抖动
            time.sleep(0.05)
            if GPIO.input(PinInfor):
                time.sleep(0.3)
                if GPIO.input(PinInfor)==0:
                #短按PinInfor按钮，显示系统信息
                    print ('%s'%str(get_host_ip()))
                    nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')#现在
                    cmd= "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
                    CPU = subprocess.check_output(cmd, shell = True )
                    print (CPU)
                    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
                    MemUsage = subprocess.check_output(cmd, shell = True )
                    print ('%s'%MemUsage)
                    cmd = "df -h | awk '/mmcblk0p1/{printf \"MMC : %4.1f/%dGB %s\",$3,$2,$5}'"
                    Disk = subprocess.check_output(cmd, shell = True )
                    print ('%s'%Disk)
                    cmd = "df -h | awk '/sda/{printf \"UPAN : %4.1f/%dGB %s\",$3,$2,$5}'"
                    DiskA = subprocess.check_output(cmd, shell = True )
                    print ('%s'%DiskA)  
                    file=open("/sys/class/thermal/thermal_zone0/temp")
                    temp=float(file.read())/1000
                    temp=("%.1f" %temp)
                    file.close()
                    with canvas(device) as draw:
                        font=ImageFont.load_default()
                        draw.text((0, 0),str(temp)+" C", font=font, fill=255)
                        draw.text((0, 10),"IP:"+get_host_ip(), font=font, fill=255)
                        draw.text((0, 20),CPU, font=font, fill=255)
                        draw.text((0, 30),MemUsage, font=font, fill=255)
                        draw.text((0, 40),Disk, font=font, fill=255)
                        draw.text((0, 50),DiskA, font=font, fill=255)
                    device.command(const.DISPLAYON)
                    time.sleep(10)
                    device.command(const.DISPLAYOFF)#关闭OLED屏幕
                else:
                    time.sleep(0.5)
                    #长安PinInfor按钮，执行备份文件到FTP
                    if GPIO.input(PinInfor):
                            with canvas(device) as draw:
                                font=ImageFont.load_default()
                                draw.text((0, 10),"FTP sync now!", font=font, fill=255)
                            device.command(const.DISPLAYON)
                            Succ="LFTP syn finished"
                            cmd= "bash /home/pi/python3/ftp_syn_once.sh"
                            CPU = subprocess.check_output(cmd, shell = True )
                            result = Succ in CPU
                            #print (str(result))
                            if result==1:
                                FTPmsg="FTP syn successed"
                            else:
                                FTPmsg="FTP syn error"
                            with canvas(device) as draw:
                                font=ImageFont.load_default()
                                draw.text((0, 30),FTPmsg, font=font, fill=255)
                            device.command(const.DISPLAYON)
                            time.sleep(10)
                            device.command(const.DISPLAYOFF)
        if GPIO.input(PinBUTT):
            time.sleep(0.2)#去抖动
            if GPIO.input(PinBUTT): 
                print ("Shut down the Orangepi")
                for i in range(5):
                    with canvas(device) as draw:
                        font=ImageFont.load_default()
                        draw.text((0, 0),'shutdown in', font=font, fill=255)
                        draw.text((0, 10),str(5-i)+"s", font=font, fill=255)
                    device.command(const.DISPLAYON)
                    time.sleep(1)
                device.command(const.DISPLAYOFF)#关闭OLED屏幕
                #关机
                os.system("shutdown -h now")
                sys.exit()
        time.sleep(0.3)              # wait 0.2 seconds
finally:
    print("Finally")
    GPIO.cleanup()

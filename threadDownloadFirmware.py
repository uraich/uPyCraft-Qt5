#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import threading
from esptool import ESPLoader
import urllib
from urllib import request
import socket
import shutil
import codecs

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#from Esp import ESPTool

class threadUserFirmware(QThread):
    sig_firmwareAnyErase = pyqtSignal(int)
    sig_firmwareAnyUpdate = pyqtSignal(int)
    sig_firmwareAnyDown = pyqtSignal(int)
    sig_goMicrobitUpdate = pyqtSignal()
    sig_percentChange = pyqtSignal(int)
    
    def __init__(self, board, savepath, com, iserase, size, addr, parent):
        # super(threadUserFirmware,self).__init__(parent)
        super().__init__()

        self.board=board
        self.savepath=savepath
        self.com=com
        self.iserase=iserase
        self.size=size
        self.erasePer=0
        self.erasestart=False
        self.erasetimer=None
        self.burnaddr=0
        if addr=="0x0":
            self.burnaddr=0
        else:
            self.burnaddr=0x1000

        print("burnaddr=====0x%x"%self.burnaddr)

    def run(self):
        print("You are using esptool version %s"%esptool.__version__)
        esptool=ESPLoader.detect_chip()
        print("Chip ID: %s"%progFW.CHIP_NAME)
        print(esptool.get_chip_description())
        print(esptool.get_chip_features())
        
        # get MAC address and print it
        mac=esptool.read_mac()
        print("The %s has the MAC address"%progFW.CHIP_NAME,end=' ')
        for i in range(0,6):
            if i != 5:
                print("%x"%mac[i],end=':')
            else:
                print("%x"%mac[i])

        flashID=progFW.flash_id()
        print("Flash id:0x%x"%flashID)
        
        print("user firmware esptool created and thread started")

        # self.connect(esptool,SIGNAL("percentchange"),self.updateFirmwarePer)
        # self.connect(esptool,SIGNAL("eraseStart"),self.eraseStart)
        self.sig_percentChange.connect(self.updateFirmwarePer)
        #esptool.sig_eraseStart.connect(self.eraseStart)
        
        if self.iserase=="yes":
            print("erase flag is set")
        else:
            print("erase flag is NOT set")

        print("iserase: %s"%self.iserase)
        if self.iserase=="yes":
            self.erasetimer=threading.Timer(0.1,self.eraseTimer)
            self.erasetimer.start()
            try:
                print("Starting to burn board %s "%self.board)
                print("Burn task momentarily disabled")
                #Esp.Burn(esptool,str(self.board),self.savepath,self.com,True)
                time.sleep(1)
                self.erasePer=100
                # self.emit(SIGNAL("sig_firmwareAnyErase"),self.erasePer)
                self.sig_firmwareAnyErase.emit(self.erasePer)
                self.erasetimer.cancel()
            except:
                time.sleep(1)
                self.erasePer=-1
                # self.emit(SIGNAL("sig_firmwareAnyErase"),self.erasePer)
                self.sig_firmwareAnyErase.emit(self.erasePer)
                self.erasetimer.cancel()
                self.erasestart=False
                self.exit()
                return

        if self.iserase=="yes":
            # self.emit(SIGNAL("sig_firmwareAnyErase"),100)
            self.sig_firmwareAnyErase.emit(100)
        try:
            if self.board=="esp32" or self.board=="esp8266" or self.board=="TPYBoardV202":
                print("Took away burn")
                #Esp.Burn(esptool,str(self.board),self.savepath,self.com,False,self.burnaddr)
            else:#microbit
                print("In threaddownloadfirmware:savepath=%s"%self.savepath)
                # self.emit(SIGNAL("sig_firmwareAnyUpdate"),-2)
                self.sig_firmwareAnyUpdate.emit(-2)
                time.sleep(0.5)
                # self.emit(SIGNAL("sig_goMicrobitUpdate"))
                self.sig_goMicrobitUpdate.emit()
        except:
            # self.emit(SIGNAL("sig_firmwareAnyUpdate"),-1)
            self.sig_firmwareAnyUpdate.emit(-1)
            self.exit()
            return
        if self.board=="esp8266":
            Esp.downOkReset()

        self.exit()

    def cbdownFirmware(self,blocknum,blocksize,totalsize):
        print(blocknum)
        print(blocksize)
        print(totalsize)

        per=100.0*blocknum*blocksize/self.size
        if per>=100:
            per=100
            # self.emit(SIGNAL("sig_firmwareAnyDown"),per)
            self.sig_firmwareAnyDown.emit(per)
            return

        # self.emit(SIGNAL("sig_firmwareAnyDown"),per)
        self.sig_firmwareAnyDown.emit(per)

    def updateFirmwarePer(self,per):
        print("updateFirmwarePer:%d"%per)
        # self.emit(SIGNAL("sig_firmwareAnyUpdate"),per)
        self.sig_firmwareAnyUpdate.emit(per)

    def eraseStart(self):
        print("set eraseStart to true")
        self.erasestart=True

    def eraseTimer(self):
        if self.erasestart==True:
            self.erasePer+=0.5

        if self.erasePer>=99:
            self.erasePer=99
            # self.emit(SIGNAL("sig_firmwareAnyErase"),self.erasePer)
            self.sig_firmwareAnyErase.emit(self.erasePer)
            self.erasestart=False
            return
        # self.emit(SIGNAL("sig_firmwareAnyErase"),self.erasePer)
        self.sig_firmwareAnyErase.emit(self.erasePer)

        self.erasetimer=threading.Timer(0.1,self.eraseTimer)
        self.erasetimer.start()

class threadDownloadFirmware(QThread):
    def __init__(self, url, board, savepath, com, iserase, size, addr, parent):
        # super(threadDownloadFirmware,self).__init__(parent)
        super().__init__()
        
        self.url=url
        self.board=board
        self.savepath=savepath
        self.com=com
        self.iserase=iserase
        self.size=size
        self.erasePer=0
        self.reDownloadNum=0
        self.downloadOk=False
        self.erasestart=False

        self.erasetimer=None

        self.burnaddr=0
        if addr=="0x0":
            self.burnaddr=0
        else:
            self.burnaddr=0x1000

        print("burnaddr2=====%d"%self.burnaddr)


    def run(self):
        self.reDownload()
        if self.downloadOk==True:

            esptool=Esp.ESPTool()
            print("esptool created")
            # self.connect(esptool,SIGNAL("percentchange"),self.updateFirmwarePer)
            # self.connect(esptool,SIGNAL("eraseStart"),self.eraseStart)
            #esptool.sig_percentChange.connect(self.updateFirmwarePer)
            #esptool.sig_eraseStart.connect(self.eraseStart)

            if self.iserase=="yes":
                self.erasetimer=threading.Timer(0.1,self.eraseTimer)
                self.erasetimer.start()
                try:
                    print("Tying to burn board %s"%self.board)
                    Esp.Burn(esptool,str(self.board),self.savepath,self.com,True)
                    time.sleep(1)
                    self.erasePer=100
                    # self.emit(SIGNAL("sig_firmwareAnyErase"),self.erasePer)
                    self.sig_firmwareAnyErase.emit(self.erasePer)
                    self.erasetimer.cancel()
                except:
                    time.sleep(1)
                    self.erasePer=-1
                    # self.emit(SIGNAL("sig_firmwareAnyErase"),self.erasePer)
                    self.sig_firmwareAnyErase.emit(self.erasePer)
                    self.erasetimer.cancel()
                    self.erasestart=False
                    self.exit()
                    return

            if self.iserase=="yes":
                # self.emit(SIGNAL("sig_firmwareAnyErase"),100)
                self.sig_firmwareAnyErase.emit(100)
            try:
                if self.board=="esp32" or self.board=="esp8266" or self.board=="TPYBoardV202":
                    Esp.Burn(esptool,str(self.board),self.savepath,self.com,False,self.burnaddr)
                else:#microbit
                    print("In threaddownloadfirmware:savepath=%s"%self.savepath)
                    # self.emit(SIGNAL("sig_firmwareAnyUpdate"),-2)
                    self.sig_firmwareAnyUpdate.emit(-2)
                    time.sleep(0.5)
                    # self.emit(SIGNAL("sig_goMicrobitUpdate"))
                    self.sig_goMicrobitUpdate.emit()
            except:
                # self.emit(SIGNAL("sig_firmwareAnyUpdate"),-1)
                self.sig_firmwareAnyUpdate.emit(-1)
                self.exit()
                return
            if self.board=="esp8266" or self.board=="TPYBoardV202":
                Esp.downOkReset()

        self.exit()

    def reDownload(self):
        if self.reDownloadNum==3:
            self.downloadOk=False
            # self.emit(SIGNAL("sig_firmwareAnyDown"),-1)
            self.sig_firmwareAnyDown.emit(-1)
            return
        try:
            socket.setdefaulttimeout(5)
            request.urlretrieve(self.url,self.savepath,self.cbdownFirmware)
            self.downloadOk=True
            return
        except:
            print("urllib err :%s"%self.url)
            self.reDownloadNum+=1
            self.reDownload()



    def cbdownFirmware(self,blocknum,blocksize,totalsize):
        print(blocknum)
        print(blocksize)
        print(totalsize)

        per=100.0*blocknum*blocksize/self.size
        if per>=100:
            per=100
            # self.emit(SIGNAL("sig_firmwareAnyDown"),per)
            self.sig_firmwareAnyDown.emit(per)
            return

        # self.emit(SIGNAL("sig_firmwareAnyDown"),per)
        self.sig_firmwareAnyDown.emit(per)

    def updateFirmwarePer(self,per):
        print("updateFirmwarePer:%d"%per)
        # self.emit(SIGNAL("sig_firmwareAnyUpdate"),per)
        self.sig_firmwareAnyUpdate.emit(per)

    def eraseStart(self):
        self.erasestart=True

    def eraseTimer(self):
        if self.erasestart==True:
            self.erasePer+=0.5

        if self.erasePer>=99:
            self.erasePer=99
            # self.emit(SIGNAL("sig_firmwareAnyErase"),self.erasePer)
            self.sig_firmwareAnyErase.emit(self.erasePer)
            self.erasestart=False
            return
        # self.emit(SIGNAL("sig_firmwareAnyErase"),self.erasePer)
        self.sig_firmwareAnyErase.emit(self.erasePer)

        self.erasetimer=threading.Timer(0.1,self.eraseTimer)
        self.erasetimer.start()

#!/usr/bin/env python3
#
# The class has methods to erase the Esp32 or Esp8266  flash and to flash it
# with a new micro Python version
# copyright U. Raich for the University of Cape Coast, Ghana
# written for the AFNOG-2019 workshop, Kampala, Uganda
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301 USA.

from PyQt5.QtGui  import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import esptool
import subprocess,shlex
import time
import threading

class EspTool(QObject):
    sig_eraseStart=pyqtSignal()
    sig_percentChange=pyqtSignal(int)
    CHUNK_SIZE=20
    def __init__(self,parent=None):
        super().__init__()
        self.esp=esptool.ESPLoader().detect_chip()
        print("You are using esptool version %s"%esptool.__version__)
        self.chip=self.esp.CHIP_NAME.lower()
        print("ESPTool created, chip is %s"%self.chip)
        if self.esp.CHIP_NAME.lower() == "esp8266":
            print("Chip ID: 0x%x"%self.esp.chip_id())
        elif self.esp.CHIP_NAME.lower() == "esp32":
            mac=self.esp.read_mac()
            print("%x"%mac[3],end='')
            print("%x"%mac[4],end='')
            print("%x"%mac[5])
   
        # get at the flash chip id
        proc=subprocess.Popen(['esptool', 'flash_id'],stdout=subprocess.PIPE)

        for line in proc.stdout:
            lineString = line.strip().decode("utf-8")
            if 'Chip' in lineString:
                print(lineString)
            if 'Manu' in lineString:
                print("Flash Chip %s"%lineString)
            if 'MAC' in lineString:
                print(lineString)
            if 'flash size' in lineString:
                print(lineString)
        
    def getConnectedChip(self):
        return self.chip
    
    def updatePer(self,per):
        #self.emit(SIGNAL("percentchange"),per)
        pass
    def burnTimer(self):
        for i in range(100):
            time.sleep(0.1)
            self.sig_percentChange.emit(i)
        self.sig_percentChange.emit(100)

    def each_chunk(self,stream, separator):
        buffer = ''
        while True:  # until EOF
            chunk = stream.read(self.CHUNK_SIZE)  # I propose 4096 or so
            if not chunk:  # EOF?
                yield buffer
                break
            buffer += chunk.decode("utf-8")
            while True:  # until no separator is found
                try:
                    part, buffer = buffer.split(separator, 1)
                except ValueError:
                    break
                else:
                    yield part
                    
    def Burn(self,board,filename,com_port,eraseFlag,burnaddr=0):
        print("Burn called")
        print("board: %s" % board)
        print("port: %s" % com_port)
        print("board: %s" % filename)

        if eraseFlag:
            print("Erasing")
            print("chip to be erased: %s chip to which we are connected: %s" %(board,self.chip))
            print("Sending erase start signal")
            self.sig_eraseStart.emit()
            proc=subprocess.Popen(['esptool', 'erase_flash'],stdout=subprocess.PIPE)
            # wait for erase to finish
            proc.wait()
            #for line in proc.stdout:
                #lineString = line.strip().decode("utf-8")
                #print(lineString)
            #time.sleep(0.5)
            print("Sending erase done signal")
            self.sig_percentChange.emit(100)
        else:
            print("Burning micro Python for board %s at address 0x%x"%(board,burnaddr))
            cmdLine='esptool write_flash --flash_size=detect --flash_mode dio ' + hex(burnaddr) + ' ' + filename
            print('Calling the programming sub process')
            print('Command line: %s'%cmdLine)
            args=shlex.split(cmdLine)
            proc=subprocess.Popen(args,stdout=subprocess.PIPE)
            #proc=subprocess.Popen('/opt/ucc/afnog/afnog-2019/tests/uPyCraft/writePercentage/writePercentage',stdout=subprocess.PIPE)
            for chunk in self.each_chunk(proc.stdout,'\r'):
                percentage=0
                print(chunk)
                idx=chunk.find('(')
                try:
                    percentage=int(chunk[idx+1:idx+3])
                except:
                    pass
                #print('Progress: %02d'%percentage)
                self.sig_percentChange.emit(percentage)
            proc.wait()    
            self.sig_percentChange.emit(100)
if __name__ == "__main__":

    def eraseStart():
        print("Erase start");
    def perChange(per):
        print("Percent change: %d"%per)

    esp = EspTool()
    board="esp32"
    savepath='/home/uli/.uPyCraft/download/mpy-fw-esp8266-20170721.bin'
    com="/dev/ttyUSB0"
    print("chip connected: %s"%esp.getConnectedChip())
    #print(str(esp.requestedString))
    esp.sig_eraseStart.connect(eraseStart)
    esp.sig_percentChange.connect(perChange)
    print("Erasing...")
    esp.Burn(board,savepath,com,True,0x0)
    print("Burning...")
    esp.Burn(board,savepath,com,False,0x0)
    print("Burn done")

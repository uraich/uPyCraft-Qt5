# Mount the SD card
# Peter hinch 30th Jan 2016
# adapted to the WeMos D1 mini by Uli Raich
import sys, os, sdcard, machine

if sys.platform == 'esp8266':
    print('SD-card test on ESP8266')
    SPI_CS = 15
    spi = machine.SPI(1)

elif sys.platform == 'esp32':
    print('SD-card test on ESP32')
    sck = machine.Pin(18)
    miso= machine.Pin(19)
    mosi= machine.Pin(23)
    SPI_CS = 5
    spi = machine.SPI(2, baudrate=32000000, sck=sck, mosi=mosi, miso=miso)

sdcardAvail=True
spi.init()  # Ensure right baudrate   
try:
    sd = sdcard.SDCard(spi, machine.Pin(SPI_CS)) # ESP8266 version
except:
    sdcardAvail = False
    
if sdcardAvail:
    print("sdcard created")
else:
    print("No sdcard found")
    sys.exit()

vfs = os.VfsFat(sd)

try:
    os.mount(vfs, '/sd')
except:
    print('problem mounting the sd card')

print('Filesystem check')
print(os.listdir('/sd'))


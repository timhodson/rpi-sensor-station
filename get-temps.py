# straight from an example by http://www.seanlandsman.com/2013/02/the-raspberry-pi-and-wireless-rf-xrf.html?m=1

import serial
from time import sleep, gmtime, strftime

DEVICE = '/dev/ttyAMA0'
BAUD = 9600

print (strftime("%a, %d %b %Y %H:%M:%S: Starting\n", gmtime()))

ser = serial.Serial(DEVICE, BAUD)
while True:
    print("%s: Checking..." % strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
    n = ser.inWaiting()
    if n != 0:
        msg = ser.read(n)
        print("%s: %s" % (strftime("%a, %d %b %Y %H:%M:%S", gmtime()), msg))
    sleep(1 * 60)
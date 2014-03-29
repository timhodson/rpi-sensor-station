__author__ = 'timhodson'
# based on an example by http://www.seanlandsman.com/2013/02/the-raspberry-pi-and-wireless-rf-xrf.html?m=1
import serial
from time import sleep, gmtime, strftime
import csv
import sys
from LLAP import LLAP

DEVICE = '/dev/ttyAMA0'
BAUD = 9600

if len(sys.argv) < 2:
    print "Exit: No filename given"
    exit()

outfile = sys.argv[1]
ofh = open(outfile, 'w')
csv_writer = csv.writer(ofh, dialect='excel')

llap = LLAP()

print (strftime("%a, %d %b %Y %H:%M:%S: Starting\n", gmtime()))

ser = serial.Serial(DEVICE, BAUD)
while True:
    print("%s: Checking..." % strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
    n = ser.inWaiting()
    if n != 0:
        msg = ser.read(n)
        print("%s: %s" % (strftime("%a, %d %b %Y %H:%M:%S", gmtime()), msg))
        for response in llap.get_responses(msg):
            response.prepend(strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
            csv_writer.writerow(response)
    sleep(1 * 60)



# code flow
# event based
    # for each event
    # log raw msg
    # split message into components
    # store messages by device and by event.
    #
# batt event

# battlow event
    # some sort of alert via twitter/sms/email?
# temp reading event
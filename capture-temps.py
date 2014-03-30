__author__ = 'timhodson'
# based on an example by http://www.seanlandsman.com/2013/02/the-raspberry-pi-and-wireless-rf-xrf.html?m=1
import serial
from time import sleep, gmtime, strftime, time
import csv
import sys
import os
from LLAP import LLAP
from firebase import firebase

# serial configuration
DEVICE = '/dev/ttyAMA0'
BAUD = 9600

# output file generation
if len(sys.argv) < 2:
    print "Exit: No filename given"
    exit()

outfile = sys.argv[1]
ofh = open(outfile, 'w')
csv_writer = csv.writer(ofh, dialect='excel')

# firebase configuration
if any([os.getenv('FIREBASE_TOKEN') is None, os.getenv('FIREBASE_EMAIL') is None]):
    print "\nBoth FIREBASE_TOKEN and FIREBASE_EMAIL must be set in your OS environment"
    exit(1)

# connect to Firebase
authentication = firebase.FirebaseAuthentication(os.getenv('FIREBASE_TOKEN'), os.getenv('FIREBASE_EMAIL'))
fb = firebase.FirebaseApplication('https://rpi-sensor-network.firebaseio.com/', authentication)


def csv_writer_callback(response):
    response['time'] = time()
    print response.values()
    csv_writer.writerow(response.values())
    ofh.flush()


def firebase_writer_callback(data):
    # write some data to firebase for temperature readings.
    fb.put('/' + data['deviceId'], data['time'], data)

# set up our llap callbacks
llap = LLAP()
llap.register_observer('ALL', csv_writer_callback)
llap.register_observer('TMPA', firebase_writer_callback)


print (strftime("%a, %d %b %Y %H:%M:%S: Starting\n", gmtime()))

ser = serial.Serial(DEVICE, BAUD)
while True:
    print("%s: Checking..." % strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
    n = ser.inWaiting()
    if n != 0:
        msg = ser.read(n)
        print("%s: %s" % (strftime("%a, %d %b %Y %H:%M:%S", gmtime()), msg))

        # this is all we need to call now that we have registered our callbacks!
        llap.get_responses(msg)

    sleep(1 * 60)


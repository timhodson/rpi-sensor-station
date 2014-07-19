__author__ = 'timhodson'
# based on an example by http://www.seanlandsman.com/2013/02/the-raspberry-pi-and-wireless-rf-xrf.html?m=1
import serial
from time import sleep, gmtime, strftime
import csv
import sys
import os
from LLAP import LLAP
from firebase import firebase
from pprint import pformat
import requests

# serial configuration
DEVICE = '/dev/ttyAMA0'
BAUD = 9600

# check some vars that we need before we get going
# output file generation
if len(sys.argv) < 2:
    print "Exit: No filename given"
    exit()

# firebase configuration
if any([os.getenv('FIREBASE_TOKEN') is None, os.getenv('FIREBASE_EMAIL') is None]):
    print "\nBoth FIREBASE_TOKEN and FIREBASE_EMAIL must be set in your OS environment"
    exit(1)

outfile = sys.argv[1]
ofh = open(outfile, 'w')
csv_writer = csv.writer(ofh, dialect='excel')


def log_msg(msg):
    print "%s: %s" % (strftime("%a, %d %b %Y %H:%M:%S", gmtime()), msg)


def fb_connect():
    """
     Connect to Firebase
    """
    log_msg("Connecting to firebase")
    authentication = firebase.FirebaseAuthentication(os.getenv('FIREBASE_TOKEN'), os.getenv('FIREBASE_EMAIL'))
    fb = firebase.FirebaseApplication('https://rpi-sensor-network.firebaseio.com/', authentication)
    return fb


def csv_writer_callback(response):
    log_msg(response.values())
    csv_writer.writerow(response.values())
    ofh.flush()


def fb_retry(fb, url, identifier, data, seconds):
    sleep(seconds)
    try:
        fb.put(url, identifier, data)
        log_msg("Written to firebase")
    except (requests.Timeout, requests.ConnectionError, requests.RequestException, requests.HTTPError) as e:
        log_msg("fb_retry: Got an Exception: will retry in %d seconds. \n%s" % (int(seconds) + 60, e))
        fb_retry(fb, url, identifier, data, seconds + 60)


def firebase_data_writer_callback(data):
    # write some data to firebase for temperature readings.\
    fb = fb_connect()  # only connect when we actually want to write to fb
    data['.priority'] = int(data['time'])
    data['readingId'] = str(data['time']).replace('.', data['deviceId'])  # replace period with deviceID
    url = '/' + data['deviceId']
    identifier = data['readingId']
    try:
        fb.put(url, identifier, data)
        log_msg("Written to firebase")
    except (requests.Timeout, requests.ConnectionError, requests.RequestException, requests.HTTPError) as e:
        log_msg("Writing Data to Firebase: Got a Timeout: will retry in 60 seconds.\n%s" % e)
        fb_retry(fb, url, identifier, data, 60)


def firebase_error_writer_callback(data):
    """
    Expecting to see ERROR messages
    """
    fb = fb_connect()
    data['.priority'] = int(data['time'])
    data['readingId'] = str(data['time']).replace('.', data['responseType'])
    url = '/errors'
    identifier = data['readingId']
    try:
        fb.put(url, identifier, data)
        log_msg("Written to firebase")
    except (requests.Timeout, requests.ConnectionError, requests.RequestException, requests.HTTPError) as e:
        log_msg("Writing Errors to Firebase: Got a Timeout: will retry in 60 seconds.\n%s" % e)
        fb_retry(fb, url, identifier, data, 60)


def firebase_status_writer_callback(data):
    """
     Expecting to see BATT and BATTLOW messages
    """
    fb = fb_connect()
    data['.priority'] = int(data['time'])
    data['readingId'] = str(data['time']).replace('.', data['deviceId'])
    url = '/' + data['deviceId'] + '/status'
    identifier = data['readingId']
    try:
        fb.put(url, identifier, data)
        log_msg("Written to firebase")
    except (requests.Timeout, requests.ConnectionError, requests.RequestException, requests.HTTPError) as e:
        log_msg("Writing Status to Firebase: Got a Timeout: will retry in 60 seconds.\n%s" % e)
        fb_retry(fb, url, identifier, data, 60)


# set up our llap callbacks
llap = LLAP()
llap.register_observer('ALL', csv_writer_callback)
llap.register_observer('TMPA', firebase_data_writer_callback)
llap.register_observer('BATTLOW', firebase_status_writer_callback)
llap.register_observer('BATT', firebase_status_writer_callback)
llap.register_observer('ERROR', firebase_error_writer_callback)


log_msg("Starting")

ser = serial.Serial(DEVICE, BAUD)
while True:
    log_msg("Checking...")
    n = ser.inWaiting()
    if n != 0:
        msg = ser.read(n)
        log_msg(msg)

        # this is all we need to call now that we have registered our callbacks!
        llap.get_responses(msg)

    sleep(1 * 60)


__author__ = 'timhodson'

from LLAP import LLAP
from pprint import pformat

llap = LLAP()

print "TEST: build some requests"
print llap.build_request("AA", "TEMP")
print llap.build_request("AA", "HELLO")

print "TEST: trying some invalid requests"
try:
    print llap.build_request("AAB", "HELLO")
except Exception:
    print "failed as expected with deviceid AAB"

try:
    print llap.build_request("AB", "HELLOHELLO")
except Exception:
    print "failed as expected with request HELLOHELLO"


def print_data(event, data):
    print "EVENT %s TRIGGERED and passed DATA: %s" % (event, pformat(data))

print "TEST: Register an observer"
llap.register_observer('TMPA', print_data)

print "TEST: different types of response with values and hyphen padding"

print llap.get_responses("aABBATT2.67-")
print llap.get_responses("aABAWAKE----")
print llap.get_responses("aABSLEEPING-")

print "TEST: process multiple responses in one message"
print pformat(llap.get_responses("aABTMPA20.23aABAWAKE----aABBATT2.76-aABSLEEPING-"))

print "TEST: call get_responses without capturing return value - just relying on event to trigger something "
llap.get_responses("aABTMPA23.13")
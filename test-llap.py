__author__ = 'timhodson'

from LLAP import LLAP
from pprint import pformat

llap = LLAP()

print llap.build_request("AA", "TEMP")
print llap.build_request("AA", "HELLO")
try:
    print llap.build_request("AAB", "HELLO")
except Exception:
    print "failed as expected with deviceid AAB"
try:
    print llap.build_request("AB", "HELLOHELLO")
except Exception:
    print "failed as expected with request HELLOHELLO"

print llap.get_responses("aABTMPA23.13")
print llap.get_responses("aABBATT2.67-")
print llap.get_responses("aABAWAKE----")
print llap.get_responses("aABSLEEPING-")

print pformat(llap.get_responses("aABTMPA20.23aABAWAKE----aABBATT2.76-aABSLEEPING-"))

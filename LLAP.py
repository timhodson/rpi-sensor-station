__author__ = 'timhodson'


# a python module to support llap
# currently mainly the llap Thermister device Persona
class LLAP:

    RESPONSES = {
        'AWAKE': 'Device is awake',
        'TMPA': 'temperature reading',
        'BATTLOW': 'battery low',
        'BATT': 'battery reading',
        'SLEEPING': 'Device is going to sleep',
        'STARTED': 'Device has started',
        'ERROR': 'There is an error'
    }

    REQUESTS = {
        'APVER': 'LLAP version number',
        'BATT': 'Battery level in volts',
        'TEMP': 'request the temperature',
        # not bothered with the other 'tweeks' that we could do.
    }

    def __init__(self):
        pass

    def split_msg(self, msg):
        # split the message up into bits
        # there may be more than one llap response in a message
        print "split_msg:input: ", msg
        self.validate_msg(msg)
        bits = {
            'raw': msg,
            'a': msg[0],
            'deviceId': msg[1:3]
        }
        for key in self.RESPONSES.keys():
            if key in msg:
                bits['responseType'] = msg[3:3+len(key)]
                bits['responseValue'] = msg[3+len(key):].rstrip("-")
        return bits

    def get_responses(self, msg):
        responses = []
        if len(msg) % 12 != 0:
            raise Exception("message not divisible by 12")
        msg_count = len(msg)/12
        s = 0
        for i in range(1, msg_count+1):
            print i, " : ", msg_count
            e = i*12
            print msg[s:e]
            responses.append(self.split_msg(msg[s:e]))
            s += 12  # increment start ready for next loop
        return responses

    def build_request(self, devid, type):
        if len(devid) > 2 or len(type) > 9:
            raise Exception("invalid parameters to build_request")
        request = '{0}{1}{2:-<9}'.format('a', devid, type)
        self.validate_msg(request)
        return request

    def validate_msg(self, msg):
        if len(msg) > 12:
            raise Exception("completed request is too long")

#ends
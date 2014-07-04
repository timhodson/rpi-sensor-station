__author__ = 'timhodson'

from time import time

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

    observers = []

    def __init__(self):
        # might want to do something clever with detecting serial ports and what not?
        pass

    def split_response(self, response):
        """Split the response up into bits

        Keyword arguments:
        response -- the string to split into bits.

        Returns:
        bits -- the bits of the response
        """
        self.validate_msg(response)
        bits = {
            'raw': response,
            'deviceId': response[1:3],
            'time': time()
        }
        for key in self.RESPONSES.keys():
            if key in response:
                bits['responseType'] = response[3:3 + len(key)]
                bits['responseValue'] = response[3 + len(key):].rstrip("-")
        self.notify_observers(bits['responseType'], bits)
        return bits

    def get_responses(self, msg):
        """Get the parsed responses out of an arbitrary message string.
        You are assumed to have got the LLAP message yourself
        by whatever means from the serial port

        Keyword arguments:
        msg -- a String which may contain LLAP responses from a device.

        Returns:
        responses -- a list of dictionaries for each response found in the message.
        You don't have to do anything with this if you have already registered a listener for the messages.
        """
        responses = []
        if len(msg) % 12 != 0:
            self.notify_observers(
                'ERROR',
                {
                    'responseType': 'ERROR',
                    'responseValue': 'Serial message not divisible by twelve',
                    'msg': msg,
                    'time': time()
                }
            )
        if len(msg) >= 12:
            # attempt to process as much as we can...
            # find the first lower case a in the string and trim msg to that.
            msg = msg[msg.index('a'):]
            msg_count = len(msg) / 12
            s = 0
            for i in range(1, msg_count + 1):
                e = i * 12
                responses.append(self.split_response(msg[s:e]))
                s += 12  # increment start ready for next loop
        return responses

    def build_request(self, devid, type):
        self.validate_request(devid, type)
        request = '{0}{1}{2:-<9}'.format('a', devid, type)
        self.validate_msg(request)
        return request

    @staticmethod
    def validate_msg(msg):
        if len(msg) > 12:
            # todo - raise some more specific Exceptions
            raise LlapException("completed request is too long")

    @staticmethod
    def validate_request(d, t):
        if len(d) > 2 or len(t) > 9:
            raise LlapException("invalid parameters to build_request")

    def register_observer(self, event, observer):
        """Register an observer to deal with each response found.
        Each callback is self contained and cannot be chained with other callbacks.
        For example: you cannot register a callback to add a timestamp
        to every message and then expect other callbacks to also see that timestamp.

        Keyword arguments:
        event -- the type of message to react to
        observer -- a reference to the callback to execute
        """
        self.observers.append({event: observer})

    def unregister_observer(self, event, observer):
        newList = []
        flag = False
        for observerDict in self.observers:
            if observerDict.keys()[0] == event:
                if observerDict[event] == observer:
                    flag = True
            if flag is not True:
                newList.append(observerDict)
        self.observers = newList

    def notify_observers(self, event, data):
        for observer in self.observers:
            if observer.keys()[0] == event or observer.keys()[0] == 'ALL':
                observer.values()[0](data)


class LlapException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

#ends

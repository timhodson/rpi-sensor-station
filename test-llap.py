__author__ = 'timhodson'

from LLAP import LLAP, LlapException
from pprint import pformat
import unittest


class TestLLAPFunctionality(unittest.TestCase):
    def setUp(self):
        self.llap = LLAP()

    def test_build_request(self):
        self.assertEqual(self.llap.build_request('AA', 'TEMP'), 'aAATEMP-----')
        self.assertEqual(self.llap.build_request('AA', 'HELLO'), 'aAAHELLO----')
        self.assertRaises(LlapException, self.llap.build_request, 'AAB', 'HELLO')
        self.assertRaises(LlapException, self.llap.build_request, 'AB', 'HELLOHELLO')

    def test_register_observer(self):
        self.assertEqual(len(self.llap.observers), 0)

        # note that we test with a fictitious event name
        # These tests run in parallel and don't seem to be run with their own llap object so events get fired!
        self.llap.register_observer('TMP', self.print_data)
        self.assertEqual(len(self.llap.observers), 1)
        self.assertDictEqual(self.llap.observers[0], {'TMP': self.print_data})

        self.llap.unregister_observer('TMP', self.print_data)
        self.assertEqual(len(self.llap.observers), 0)

    def test_get_responses(self):
        data = self.llap.get_responses("aABBATT2.67-")
        self.assertDictEqual(self.update_time(data[0]),
                             {'responseType': 'BATT', 'raw': 'aABBATT2.67-', 'responseValue': '2.67', 'deviceId': 'AB',
                              'time': 0})

        data = self.llap.get_responses("aABBATTLOW--")
        self.assertDictEqual(self.update_time(data[0]),
                             {'responseType': 'BATT', 'raw': 'aABBATTLOW--', 'responseValue': 'LOW', 'deviceId': 'AB',
                              'time': 0})

        data = self.llap.get_responses("aABAWAKE----")
        self.assertDictEqual(self.update_time(data[0]),
                             {'responseType': 'AWAKE', 'raw': 'aABAWAKE----', 'responseValue': '', 'deviceId': 'AB',
                              'time': 0})

        data = self.llap.get_responses("aABSLEEPING-")
        self.assertDictEqual(self.update_time(data[0]),
                             {'responseType': 'SLEEPING', 'raw': 'aABSLEEPING-', 'responseValue': '', 'deviceId': 'AB',
                              'time': 0})

    def test_multiple_responses(self):
        data = self.llap.get_responses("aABTMPA20.24aABAWAKE----aABBATT2.76-aABSLEEPING-")
        data = [self.update_time(x) for x in data]
        expected = [{'deviceId': 'AB',
                     'raw': 'aABTMPA20.24',
                     'responseType': 'TMPA',
                     'responseValue': '20.24',
                     'time': 0},
                    {'deviceId': 'AB',
                     'raw': 'aABAWAKE----',
                     'responseType': 'AWAKE',
                     'responseValue': '',
                     'time': 0},
                    {'deviceId': 'AB',
                     'raw': 'aABBATT2.76-',
                     'responseType': 'BATT',
                     'responseValue': '2.76',
                     'time': 0},
                    {'deviceId': 'AB',
                     'raw': 'aABSLEEPING-',
                     'responseType': 'SLEEPING',
                     'responseValue': '',
                     'time': 0}]
        self.assertEqual(data, expected)

    def test_messages_of_incorrect_length(self):
        """
        The messages should still get completed even if one of the messages was not read completely from serial input.
        (all llap messages should start with a lower case 'a' and run for 12 chars.
        """
        data = self.llap.get_responses("--aZZTMPA20.23aABAWAKE----aABBATT2.76-aABSLEEPING-aZZ-----")
        data = [self.update_time(x) for x in data]
        expected = [{'deviceId': 'ZZ',
                     'raw': 'aZZTMPA20.23',
                     'responseType': 'TMPA',
                     'responseValue': '20.23',
                     'time': 0},
                    {'deviceId': 'AB',
                     'raw': 'aABAWAKE----',
                     'responseType': 'AWAKE',
                     'responseValue': '',
                     'time': 0},
                    {'deviceId': 'AB',
                     'raw': 'aABBATT2.76-',
                     'responseType': 'BATT',
                     'responseValue': '2.76',
                     'time': 0},
                    {'deviceId': 'AB',
                     'raw': 'aABSLEEPING-',
                     'responseType': 'SLEEPING',
                     'responseValue': '',
                     'time': 0}]
        self.assertEqual(data, expected)

    def update_time(self, d):
        if d.get('time'):
            d['time'] = 0
        return d

    def print_data(self, data):
        print "EVENT %s TRIGGERED and passed DATA: %s" % (data['responseType'], pformat(data))

def suite1():
    suite = unittest.TestSuite()
    suite.addTest(TestLLAPFunctionality("test_build_request"))
    suite.addTest(TestLLAPFunctionality("test_register_observer"))
    suite.addTest(TestLLAPFunctionality("test_get_responses"))
    suite.addTest(TestLLAPFunctionality("test_multiple_responses"))
    suite.addTest(TestLLAPFunctionality("test_messages_of_incorrect_length"))
    return suite


unittest.TextTestRunner(verbosity=2).run(suite1())

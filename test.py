import unittest
import config
from sigfoxapiv2 import Sigfox
from pprint import pprint
from datetime import datetime, timedelta
from math import trunc

sigfox = Sigfox(config.USERNAME, config.PASSWORD)


class TestSigfoxDeviceEndpoints(unittest.TestCase):
    def test_get_device_types(self):
        status, _ = sigfox.get_device_types()
        self.assertEqual(status, 200, "HTTP status should be 200")

    def test_get_device(self):
        status, _ = sigfox.get_device(config.TEST_ID)
        self.assertEqual(status, 200, "HTTP status should be 200")

    def test_get_devices(self):
        status, _ = sigfox.get_devices(config.TEST_DEVICE_TYPE_ID)
        self.assertEqual(status, 200, "HTTP status should be 200")

    def test_get_device_messages(self):
        status, _ = sigfox.get_device_messages(config.TEST_ID)
        self.assertEqual(status, 200, "HTTP status should be 200")

        status, _ = sigfox.get_device_messages(config.TEST_ID, config.TEST_TIMESTAMP)
        self.assertEqual(status, 200, "HTTP status should be 200")

    def test_get_device_callbacks(self):
        status, _ = sigfox.get_device_type_callbacks(config.TEST_DEVICE_TYPE_ID)
        self.assertEqual(status, 200, "HTTP status should be 200")

    ##def test_create_device_callbacks(self):
    ##    status, _ = sigfox.create_device(config.TEST_DEVICE_TYPE_ID)
    ##    self.assertEqual(status, 200, "HTTP status should be 200")


##
##def test_update_device_callbacks(self):
##    status, _ = sigfox.update_device(config.TEST_DEVICE_TYPE_ID)
##    self.assertEqual(status, 200, "HTTP status should be 200")


class TestSigfoxContractEndpoints(unittest.TestCase):
    def test_get_contract_information(self):
        status, _ = sigfox.get_contract_information()
        self.assertEqual(status, 200, "HTTP status should be 200")


class TestSigfoxDeviceTypeCallback(unittest.TestCase):
    def test_device_type_list(self):
        status, _ = sigfox.get_device_type_list()
        self.assertEqual(status, 200, "HTTP status should be 200")


if __name__ == "__main__":
    unittest.main()

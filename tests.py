import os
import webassistant
import unittest

import json

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        webassistant.app.testing = True
        self.app = webassistant.app.test_client()

    def tearDown(self):
        pass

    def test_temp(self):
        r = self.app.get('/webhooks/temp/fakeroom')
        assert "Unknown sensor" in r.data.decode('utf-8')

if __name__ == '__main__':
    unittest.main()

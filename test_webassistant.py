from unittest import TestCase
from webassistant import parse_sensor, get_temp

class SimpleTests(TestCase):

    def test_parser(self):
        line = "temp: 25.2 ts: 1524479608"

        res = parse_sensor(line)

        assert res['temp'] == '25,2'
        assert res['age'] > 1

    def test_real_sensor(self):
        room = "salon"
        temp, age, comment = get_temp(room)

        assert ',' in temp
        assert age > 1
        assert comment == "dans le salon."

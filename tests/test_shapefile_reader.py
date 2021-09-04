import asyncio
import unittest
from datetime import datetime

from pystibmivb import ShapefileService
from tests import MockAPIClient


class TestShapefileReader(unittest.TestCase):
    def setUp(self):
        self.LOOP = asyncio.get_event_loop()

    def test_filtered_out(self):
        async def check_color(sf_reader, line_id, expected_text_color):
            l = await sf_reader.get_line_info(line_id)
            self.assertEqual(l.get_line_text_color(), expected_text_color)

        async def go(LOOP):
            APIClient = MockAPIClient()

            sf_reader = ShapefileService(APIClient)
            sf_reader._force_update = True

            frinfo = await sf_reader.get_stop_infos("Scherdemael")
            print(frinfo)
            nlinfo = await sf_reader.get_stop_infos("Scherdemaal")

            self.assertEqual(frinfo.get_line_info(46).get_line_color(), nlinfo.get_line_info(46).get_line_color())
            self.assertEqual(frinfo.get_line_info(46).get_line_type(), nlinfo.get_line_info(46).get_line_type())
            self.assertEqual(frinfo.get_line_info(46).get_line_nr(), nlinfo.get_line_info(46).get_line_nr())

            l46 = await sf_reader.get_line_info(46)
            self.assertEqual(l46.get_line_color(), "#DE3B21")
            self.assertEqual(l46.get_line_text_color(), "#000000")
            self.assertEqual(l46.get_line_type(), "B")
            self.assertEqual(l46.get_line_nr(), 46)

            await check_color(sf_reader, 3, "#000000")
            await check_color(sf_reader, 5, "#FFFFFF")
            await check_color(sf_reader, 6, "#FFFFFF")

        self.LOOP.run_until_complete(go(self.LOOP))

    def test_location(self):
        # https://xkcd.com/2170/
        async def go(LOOP):
            APIClient = MockAPIClient()

            sf_reader = ShapefileService(APIClient)
            sf_reader._force_update = True

            info = await sf_reader.get_stop_infos("Scherdemael")

            self.assertAlmostEqual(info.get_location()["lat"], 50.8311, delta=0.0001)
            self.assertAlmostEqual(info.get_location()["lon"], 4.2896, delta=0.0001)

        self.LOOP.run_until_complete(go(self.LOOP))

    def test_locations(self):
        # https://xkcd.com/2170/
        async def go(LOOP):
            APIClient = MockAPIClient()

            sf_reader = ShapefileService(APIClient)
            sf_reader._force_update = True

            info = await sf_reader.get_stop_infos("Scherdemael")

            print(info.get_locations())
            self.assertAlmostEqual(50.8312, info.get_locations()['3755']["lat"], delta=0.0001)
            self.assertAlmostEqual(4.2900, info.get_locations()['3755']["lon"], delta=0.0001)

            self.assertAlmostEqual(50.8309, info.get_locations()['3713']["lat"], delta=0.0001)
            self.assertAlmostEqual(4.2892, info.get_locations()['3713']["lon"], delta=0.0001)

        self.LOOP.run_until_complete(go(self.LOOP))

    def test_gtfs_next_passage(self):
        # https://xkcd.com/2170/
        async def go(LOOP):
            APIClient = MockAPIClient()

            sf_reader = ShapefileService(APIClient)
            sf_reader._force_update = True

            now = datetime.now()
            info = await sf_reader.get_next_stop_passage('3755', None, now)
            self.assertLess(now, info)
            info = await sf_reader.get_next_stop_passage('3755', None, datetime(2020, 1, 28, hour=2, minute=32, second=2))
            self.assertEqual(datetime(2020, 1, 28, hour=5, minute=7, second=27), info)
            info = await sf_reader.get_next_stop_passage('3755', None, datetime(2020, 1, 28, hour=5, minute=10, second=2))
            self.assertEqual(datetime(2020, 1, 28, hour=5, minute=12, second=44), info)
            info = await sf_reader.get_next_stop_passage('3755', None, datetime(2020, 1, 28, hour=23, minute=58, second=2))
            self.assertEqual(datetime(2020, 1, 28, hour=23, minute=58, second=51), info)
            info = await sf_reader.get_next_stop_passage('3755', None, datetime(2020, 1, 29, hour=0, minute=59, second=52))
            self.assertEqual(datetime(2020, 1, 29, hour=5, minute=7, second=27), info)

        self.LOOP.run_until_complete(go(self.LOOP))


if __name__ == '__main__':
    unittest.main()

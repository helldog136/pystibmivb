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

            frinfo = await sf_reader.get_stop_infos("Scherdemael")
            nlinfo = await sf_reader.get_stop_infos("Scherdemaal")

            self.assertEqual(frinfo.get_line_info(46).get_line_color(), nlinfo.get_line_info(46).get_line_color())
            self.assertEqual(frinfo.get_line_info(46).get_line_type(), nlinfo.get_line_info(46).get_line_type())
            self.assertEqual(frinfo.get_line_info(46).get_line_nr(), nlinfo.get_line_info(46).get_line_nr())

            l46 = await sf_reader.get_line_info(46)
            self.assertEqual(l46.get_line_color(), "#DE3B21")
            self.assertEqual(l46.get_line_text_color(), "#FFFFFF")
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

            info = await sf_reader.get_stop_infos("Scherdemael")

            self.assertAlmostEqual(info.get_location()["lat"], 50.8311, delta=0.0001)
            self.assertAlmostEqual(info.get_location()["lon"], 4.2896, delta=0.0001)

        self.LOOP.run_until_complete(go(self.LOOP))

    def test_locations(self):
        # https://xkcd.com/2170/
        async def go(LOOP):
            APIClient = MockAPIClient()

            sf_reader = ShapefileService(APIClient)

            info = await sf_reader.get_stop_infos("Scherdemael")

            print(info.get_locations())
            self.assertAlmostEqual(info.get_locations()['3755']["lat"], 50.8312, delta=0.0001)
            self.assertAlmostEqual(info.get_locations()['3755']["lon"], 4.2900, delta=0.0001)

            self.assertAlmostEqual(info.get_locations()['3713']["lat"], 50.8309, delta=0.0001)
            self.assertAlmostEqual(info.get_locations()['3713']["lon"], 4.2892, delta=0.0001)

        self.LOOP.run_until_complete(go(self.LOOP))

    def test_gtfs_next_passage(self):
        # https://xkcd.com/2170/
        async def go(LOOP):
            APIClient = MockAPIClient()

            sf_reader = ShapefileService(APIClient)

            now = datetime.now()
            info = await sf_reader.get_next_stop_passage('3755', now)
            self.assertLess(now, info)
            info = await sf_reader.get_next_stop_passage('3755', datetime(2020, 1, 28, hour=2, minute=32, second=2))
            self.assertEqual(info, datetime(2020, 1, 28, hour=5, minute=7, second=27))
            info = await sf_reader.get_next_stop_passage('3755', datetime(2020, 1, 28, hour=5, minute=10, second=2))
            self.assertEqual(info, datetime(2020, 1, 28, hour=5, minute=18, second=27))
            info = await sf_reader.get_next_stop_passage('3755', datetime(2020, 1, 28, hour=23, minute=58, second=2))
            self.assertEqual(info, datetime(2020, 1, 28, hour=23, minute=59, second=51))
            info = await sf_reader.get_next_stop_passage('3755', datetime(2020, 1, 28, hour=23, minute=59, second=52))
            self.assertEqual(info, datetime(2020, 1, 29, hour=5, minute=7, second=27))

        self.LOOP.run_until_complete(go(self.LOOP))


if __name__ == '__main__':
    unittest.main()

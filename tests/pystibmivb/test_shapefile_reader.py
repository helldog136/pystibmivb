import asyncio
import unittest

from pystibmivb import ShapefileService
from tests.pystibmivb import MockAPIClient


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


if __name__ == '__main__':
    unittest.main()

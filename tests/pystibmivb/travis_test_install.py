"""Example usage of pystibmivb."""
import asyncio
import unittest

from pystibmivb import STIBService
from tests.pystibmivb import MockAPIClient


class TestPassages(unittest.TestCase):
    def setUp(self):
        self.LOOP = asyncio.get_event_loop()

    def tearDown(self):
        self.LOOP.close()

    def test_filtered_out(self):
        async def go(LOOP):
            stop_name = "scherdemael"
            lines_filter = [(46, "Glibert")]

            APIClient = MockAPIClient()

            service = STIBService(APIClient)
            print(await service.get_passages(stop_name, lines_filter))

        self.LOOP.run_until_complete(go(self.LOOP))


if __name__ == '__main__':
    unittest.main()




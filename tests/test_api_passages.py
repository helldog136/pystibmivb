"""Example usage of pystibmivb."""
import asyncio
import datetime
import json
import unittest

import aiohttp

from pystibmivb import STIBService, Passage, LineInfo, InvalidLineFilterException, NoScheduleFromAPIException, \
    InvalidStopNameException, STIBStop
from tests import MockAPIClient


class TestPassages(unittest.TestCase):
    def setUp(self):
        self.LOOP = asyncio.get_event_loop()

    def test_filtered_in_terminus(self):
        async def go(LOOP):
            stop_name = "scherdemael"
            lines_filter = [(46, "Glibert")]

            APIClient = MockAPIClient()

            service = STIBService(APIClient)

            stop = STIBStop(service, stop_name, lines_filter)

            passages = await stop.get_passages()

            now = datetime.datetime.now()
            delta1 = datetime.timedelta(minutes=3, seconds=25)
            delta2 = datetime.timedelta(minutes=13, seconds=22)

            # Check message
            self.assertEqual(passages[0]["message"], "foofr")
            self.assertEqual(passages[1]["message"], "")

        self.LOOP.run_until_complete(go(self.LOOP))

    def test_invalid_stop_name(self):
        async def go(LOOP):
            stop_name = "foobar"

            APIClient = MockAPIClient()

            service = STIBService(APIClient)
            res = "No exception raised"
            try:
                passages = await service.get_passages(stop_name)
            except InvalidStopNameException as e:
                res = "InvalidStopNameException raised!"

            self.assertEqual(res, "InvalidStopNameException raised!")

        self.LOOP.run_until_complete(go(self.LOOP))

    def test_filtered_in_direction(self):
        async def go(LOOP):
            stop_name = "Scherdemael"
            lines_filter = [(46, 1)]

            APIClient = MockAPIClient()

            service = STIBService(APIClient)
            passages = await service.get_passages(stop_name, lines_filter)

            now = datetime.datetime.now()
            delta1 = datetime.timedelta(minutes=3, seconds=25)
            delta2 = datetime.timedelta(minutes=13, seconds=22)

            # Check message
            self.assertEqual(passages[0]["message"], "foofr")
            self.assertEqual(passages[1]["message"], "")

        self.LOOP.run_until_complete(go(self.LOOP))

    def test_filtered_in_invalid_filter(self):
        async def go(LOOP):
            stop_name = "Scherdemael"
            lines_filter = [(104, 1)]

            APIClient = MockAPIClient()

            service = STIBService(APIClient)

            hasRaised = False
            try:
                await service.get_passages(stop_name, lines_filter)
            except InvalidLineFilterException:
                hasRaised = True

            self.assertTrue(hasRaised)

        self.LOOP.run_until_complete(go(self.LOOP))

    def test_serializable(self):
        async def go(LOOP):
            stop_name = "scherdemael"
            lines_filter = [(46, "Glibert")]
            custom_session = aiohttp.ClientSession()

            APIClient = MockAPIClient()

            service = STIBService(APIClient)
            passages = await service.get_passages(stop_name, lines_filter)

            print(json.dumps(passages))

            await custom_session.close()

        self.LOOP.run_until_complete(go(self.LOOP))

    def test_atomic_passage_serialization(self):
        now = datetime.datetime.now()
        delta1 = datetime.timedelta(minutes=3, seconds=25)
        p = Passage(stop_id=42, lineId=21, destination="FooDest",
                    expectedArrivalTime=(now + delta1).strftime("%Y-%m-%dT%H:%M:%S"),
                    lineInfos=LineInfo(line_nr=21, line_type="B", line_color="#FFFFFF", line_text_color="#000000"),
                    message="FooMsg", now=now)

        js = json.loads(json.dumps(p))
        self.assertEqual(js["stop_id"], 42)
        self.assertEqual(js["line_id"], 21)
        self.assertEqual(js["destination"], "FooDest")
        self.assertEqual(js["expected_arrival_time"], (now + delta1).strftime("%Y-%m-%dT%H:%M:%S"))
        self.assertEqual(js["line_color"], "#FFFFFF")
        self.assertEqual(js["line_text_color"], "#000000")
        self.assertEqual(js["line_type"], "B")
        self.assertEqual(js["message"], "FooMsg")
        self.assertEqual(js["arriving_in"]["min"], 3)
        self.assertEqual(js["arriving_in"]["sec"], 24)

    def test_empty_response_crawls_for_data(self):
        async def go(LOOP):
            stop_name = "De Brouckère"
            lines_filter = [(5, 1)]

            APIClient = MockAPIClient()

            service = STIBService(APIClient)
            exception = "Unraised"
            try:
                passages = await service.get_passages(stop_name, lines_filter,
                                                      now=datetime.datetime(2020, 1, 28, hour=23, minute=59, second=52))
            except NoScheduleFromAPIException as e:
                exception = "Raised"
                passages = e.get_next_passages()
            self.assertEqual(exception, "Raised")
            self.assertGreaterEqual(len(passages), 1)
            self.assertEqual('2020-01-29T00:07:01', passages[0]['expected_arrival_time'])

        self.LOOP.run_until_complete(go(self.LOOP))


if __name__ == '__main__':
    unittest.main()

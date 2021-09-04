import unittest
from pystibmivb import STIBAPIClient, STIBService, STIBStop
import aiohttp
import asyncio

CLIENT_ID = 'Wirff1HT1tTH7mLX1dMQAbOEHDoa'  # testing api key, not production one ;)
CLIENT_SECRET = 'tYKqSKbmjw3hKsoNtaaKKtXXP0sa'  # testing api key, not production one ;)


class TestIntegrationWithTrueStibApi(unittest.TestCase):
    def setUp(self):
        self.LOOP = asyncio.get_event_loop()

    def test_filtered_in_terminus(self):
        async def go(LOOP):
            try:
                stop_name = "Saint-Denis"
                custom_session = aiohttp.ClientSession()

                APIClient = STIBAPIClient(LOOP, custom_session, CLIENT_ID, CLIENT_SECRET)

                service = STIBService(APIClient)

                stop = STIBStop(service, stop_name)

                print(await stop.get_passages())
                await custom_session.close()
            except Exception as e:
                self.fail("Integration test Failed! An exception occurred"+str(e))

        self.LOOP.run_until_complete(go(self.LOOP))


if __name__ == '__main__':
    unittest.main()

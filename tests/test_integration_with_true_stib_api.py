import unittest
from pystibmivb import STIBAPIClient, STIBService
import aiohttp
import asyncio

CLIENT_ID = 'Wirff1HT1tTH7mLX1dMQAbOEHDoa'  # testing api key, not production one ;)
CLIENT_SECRET = 'tYKqSKbmjw3hKsoNtaaKKtXXP0sa'  # testing api key, not production one ;)


class TestIntegrationWithTrueStibApi(unittest.TestCase):
    def setUp(self):
        self.LOOP = asyncio.get_event_loop()

    def test_filtered_in_terminus(self):
        async def go(LOOP):
            result = "Integration test Succeded!"
            try:
                stop_name = "Saint-Denis"
                custom_session = aiohttp.ClientSession()

                APIClient = STIBAPIClient(LOOP, custom_session, CLIENT_ID, CLIENT_SECRET)

                service = STIBService(APIClient)
                print(await service.get_passages(stop_name, lang_message='fr', lang_stop_name='fr'))
            except:
                result = "Integration test Failed!"

            self.assertEqual(result, "Integration test Succeded!")

        self.LOOP.run_until_complete(go(self.LOOP))


if __name__ == '__main__':
    unittest.main()

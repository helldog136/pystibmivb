import unittest
from pystibmivb import STIBAPIClient, ShapefileService
import aiohttp
import asyncio

CLIENT_ID = 'Wirff1HT1tTH7mLX1dMQAbOEHDoa' # Put your openapi client ID here
CLIENT_SECRET = 'tYKqSKbmjw3hKsoNtaaKKtXXP0sa' # Put your openapi client secret here

class TestIntegrationApiCalls(unittest.TestCase):
    def setUp(self):
        self.LOOP = asyncio.get_event_loop()


    def test_filtered_in_terminus(self):
        async def go(LOOP):
            custom_session = aiohttp.ClientSession()

            APIClient = STIBAPIClient(LOOP, custom_session, CLIENT_ID, CLIENT_SECRET)
            shapefileService = ShapefileService(APIClient)


            print(await APIClient.api_call_passingTimeByPoint_for_stop_ids((await shapefileService.get_stop_infos("Scherdemael")).get_stop_ids()))

        self.LOOP.run_until_complete(go(self.LOOP))


if __name__ == '__main__':
    unittest.main()

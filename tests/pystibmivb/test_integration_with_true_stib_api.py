import unittest
from pystibmivb import STIBAPIClient, STIBService
import aiohttp
import asyncio

CLIENT_ID = 'Wirff1HT1tTH7mLX1dMQAbOEHDoa' # Put your openapi client ID here
CLIENT_SECRET = 'tYKqSKbmjw3hKsoNtaaKKtXXP0sa' # Put your openapi client secret here

class TestIntegrationWithTrueStibApi(unittest.TestCase):
    def setUp(self):
        self.LOOP = asyncio.get_event_loop()


    def test_filtered_in_terminus(self):
        async def go(LOOP):
            stop_name = "Saint-Denis"
            custom_session = aiohttp.ClientSession()

            APIClient = STIBAPIClient(LOOP, custom_session, CLIENT_ID, CLIENT_SECRET)

            service = STIBService(APIClient)
            shapefileService = service._shapefile_service
            passages = await service.get_passages(stop_name, lang=('fr', 'fr'))

            # Check message
            print(passages)

        self.LOOP.run_until_complete(go(self.LOOP))


if __name__ == '__main__':
    unittest.main()

"""Example usage of pystibmivb."""
import asyncio

import aiohttp

from pystibmivb import STIBAPIClient, STIBStop
from pystibmivb import STIBService
from pystibmivb import ShapefileService

CLIENT_ID = 'Wirff1HT1tTH7mLX1dMQAbOEHDoa'  # Put your openapi client ID here
CLIENT_SECRET = 'tYKqSKbmjw3hKsoNtaaKKtXXP0sa'  # Put your openapi client secret here


async def go(LOOP):
    stop_name = "Scherdemael"
    lines_filter = [(46, "Glibert")]
    custom_session = aiohttp.ClientSession()
    APIClient = STIBAPIClient(LOOP, custom_session, CLIENT_ID, CLIENT_SECRET)
    service = STIBService(APIClient)

    stop = STIBStop(service, stop_name, lines_filter, 3)
    print(await stop.get_passages())

    shapefile_service = ShapefileService(APIClient)

    scherdemael = await shapefile_service.get_stop_infos(stop_name)
    print(scherdemael.get_lines())
    # doesn't really make sense to specify a filter but hey... you can
    print(scherdemael.get_lines(lines_filter))
    print(scherdemael.get_lines_with_destinations(lines_filter))

    await custom_session.close()


if __name__ == '__main__':
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(go(LOOP))

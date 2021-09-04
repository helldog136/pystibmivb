# pystibmivb [![GitHub version](https://badge.fury.io/gh/helldog136%2Fpystibmivb.svg)](https://badge.fury.io/gh/helldog136%2Fpystibmivb) [![Build Status](https://travis-ci.com/helldog136%2Fpystibmivb.svg?branch=master)](https://travis-ci.com/helldog136/pystibmivb) [![PyPI version](https://badge.fury.io/py/pystibmivb.svg)](https://badge.fury.io/py/pystibmivb) [![Buy me a beer!](https://img.shields.io/badge/%F0%9F%A5%83-Buy%20me%20a%20Beer-orange)](https://www.buymeacoffee.com/helldog136) 
A Python package to retrieve realtime data of passages at stops of STIB/MIVB, the public transport company of Brussels (Belgium)

Main purpose at the moment is to feed a sensor in Home-Assistant (see: https://github.com/Emilv2/home-assistant/tree/stib-mivb/homeassistant/components/stib_mivb )

**Important note**: a developer account needs to be created at https://opendata.stib-mivb.be/ to generate a subscription key for the api's.

## Install

```bash
pip install pystibmivb
```

### Example usage

```python
"""Example usage of pystibmivb."""
import asyncio

import aiohttp

from pystibmivb import STIBAPIClient, STIBStop
from pystibmivb import STIBService
from pystibmivb import ShapefileService

CLIENT_ID = ''  # Put your openapi client ID here
CLIENT_SECRET = ''  # Put your openapi client secret here


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


```

Old repository: https://github.com/helldog136/pystibmvib
Initial inspiration came from : https://github.com/bollewolle/pydelijn 


# pystibmivb [![GitHub version](https://badge.fury.io/gh/helldog136%2Fpystibmivb.svg)](https://badge.fury.io/gh/helldog136%2Fpystibmivb) [![Build Status](https://travis-ci.com/helldog136%2Fpystibmivb.svg?branch=master)](https://travis-ci.com/helldog136/pystibmivb) [![PyPI version](https://badge.fury.io/py/pystibmivb.svg)](https://badge.fury.io/py/pystibmivb) [![Buy me a beer!](https://img.shields.io/badge/%F0%9F%A5%83-Buy%20me%20a%20Beer-orange)](https://www.buymeacoffee.com/helldog136) 
A Python package to retrieve realtime data of passages at stops of STIB/MIVB, the public transport company of Brussels (Belgium)

Main purpose at the moment is to feed a sensor in Home-Assistant (see: https://github.com/Emilv2/home-assistant/tree/stib-mivb )

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

from pystibmivb import STIBAPIClient
from pystibmivb.service.STIBService import STIBService

CLIENT_ID = '' # Put your openapi client ID here
CLIENT_SECRET = '' # Put your openapi client secret here


async def go(LOOP):
    stop_name = "scherdemael"
    lines_filter = [(46, "Glibert")]
    # lines_filter = [(46, 1)] # you can also give dirction instead of terminus
    custom_session = aiohttp.ClientSession()

    APIClient = STIBAPIClient(LOOP, custom_session, CLIENT_ID, CLIENT_SECRET)

    service = STIBService(APIClient)
    print(await service.get_passages(stop_name, lines_filter))

    await custom_session.close()


if __name__ == '__main__':
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(go(LOOP))




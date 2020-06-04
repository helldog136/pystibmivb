"""Common attributes and functions."""
import datetime
import json

from pystibmivb import AbstractSTIBAPIClient
from pystibmivb.client.STIBAPIClient import PASSING_TIME_BY_POINT_SUFFIX
from pystibmivb.service.ShapefileService import ENDPOINT_SHAPEFILES, ENDPOINT_GTFS


class MockAPIClient(AbstractSTIBAPIClient):
    """A class for common functions."""

    async def _api_call_passingTimeByPoint_for_10_stop_ids(self, point_ids: list) -> dict:
        return await self.api_call(PASSING_TIME_BY_POINT_SUFFIX + "%2C".join(point_ids))

    async def api_call_passingTimeByPoint_for_stop_ids(self, point_ids: set) -> dict:
        res = {"points": []}
        subset_point_ids = []
        for i in range(1, len(point_ids)+1):
            subset_point_ids.append(point_ids.pop())
            if i % 10 == 0 or len(point_ids) == 0:
                subset_res = await self._api_call_passingTimeByPoint_for_10_stop_ids(subset_point_ids)
                res["points"].extend(subset_res["points"])
                subset_point_ids = []
        return res

    async def api_call_passingTimeByPoint_for_stop_id(self, point_id: str):
        if point_id == "3755":
            now = datetime.datetime.now()
            delta1 = datetime.timedelta(minutes=3, seconds=25)
            delta2 = datetime.timedelta(minutes=13, seconds=22)
            return json.loads('''{"points": [
                            {"passingTimes": [
                                {
                                 "destination": 
                                    {"fr": "WTC / GLIBERT", "nl": "WTC / GLIBERT"}, 
                                 "expectedArrivalTime": "''' + (now + delta1).strftime("%Y-%m-%dT%H:%M:%S") + '''+01:00", 
                                 "message": 
                                    {"fr": "foofr", "nl": "foonl"},
                                 "lineId": "46"
                                }, 
                                {
                                 "destination": 
                                    {"fr": "WTC / GLIBERT", "nl": "WTC / GLIBERT"}, 
                                 "expectedArrivalTime": "''' + (now + delta2).strftime("%Y-%m-%dT%H:%M:%S") + '''+01:00", 
                                 "lineId": "46"
                                }
                            ], 
                             "pointId": "3755"
                            }
                        ]
                    }''')
        if point_id == "8012":
            now = datetime.datetime.now()
            delta1 = datetime.timedelta(minutes=3, seconds=25)
            delta2 = datetime.timedelta(minutes=13, seconds=22)
            return json.loads('''{"points": [{"passingTimes": [], "pointId": "8012"}]}''')

    def __init__(self):
        with open("../resources/shapefiles.zip", 'rb') as sf:
            self.shapefilezipcontent = sf.read()
        with open("../resources/gtfs.zip", 'rb') as sf:
            self.gtfszipcontent = sf.read()

    async def api_call(self, endpoint_suffix: str, additional_headers=None):
        if endpoint_suffix == ENDPOINT_SHAPEFILES:
            return self.shapefilezipcontent
        elif endpoint_suffix == ENDPOINT_GTFS:
            return self.gtfszipcontent
        elif endpoint_suffix.startswith(PASSING_TIME_BY_POINT_SUFFIX):
            if endpoint_suffix.endswith("3755"):
                now = datetime.datetime.now()
                delta1 = datetime.timedelta(minutes=3, seconds=25)
                delta2 = datetime.timedelta(minutes=13, seconds=22)
                return json.loads('''{"points": [
                                {"passingTimes": [
                                    {
                                     "destination": 
                                        {"fr": "WTC / GLIBERT", "nl": "WTC / GLIBERT"}, 
                                     "expectedArrivalTime": "'''+(now+delta1).strftime("%Y-%m-%dT%H:%M:%S")+'''+01:00", 
                                     "message": 
                                        {"fr": "foofr", "nl": "foonl"},
                                     "lineId": "46"
                                    }, 
                                    {
                                     "destination": 
                                        {"fr": "WTC / GLIBERT", "nl": "WTC / GLIBERT"}, 
                                     "expectedArrivalTime": "'''+(now+delta2).strftime("%Y-%m-%dT%H:%M:%S")+'''+01:00", 
                                     "lineId": "46"
                                    }
                                ], 
                                 "pointId": "3755"
                                }
                            ]
                        }''')
            if endpoint_suffix.endswith("8012"):
                now = datetime.datetime.now()
                delta1 = datetime.timedelta(minutes=3, seconds=25)
                delta2 = datetime.timedelta(minutes=13, seconds=22)
                return json.loads('''{"points": [{"passingTimes": [], "pointId": "8012"}]}''')

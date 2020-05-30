"""Common attributes and functions."""
import datetime

from pystibmivb import AbstractSTIBAPIClient
from pystibmivb.service.STIBService import PASSING_TIME_BY_POINT_SUFFIX
from pystibmivb.service.ShapefileService import ENDPOINT_SHAPEFILES, ENDPOINT_GTFS


class MockAPIClient(AbstractSTIBAPIClient):
    """A class for common functions."""

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
                return '''{"points": [
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
                        }'''
            print(endpoint_suffix)
            if endpoint_suffix.endswith("8012"):
                now = datetime.datetime.now()
                delta1 = datetime.timedelta(minutes=3, seconds=25)
                delta2 = datetime.timedelta(minutes=13, seconds=22)
                return '''{"points": [{"passingTimes": [], "pointId": "8012"}]}'''

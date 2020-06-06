import logging
import datetime

from pystibmivb.client import AbstractSTIBAPIClient
from pystibmivb.domain.passages import Passage
from pystibmivb.service.ShapefileService import ShapefileService

LOGGER = logging.getLogger(__name__)

LANGS = {"fr", "nl"}


class InvalidLineFilterException(Exception):
    pass


class STIBService:
    def __init__(self, stib_api_client: AbstractSTIBAPIClient):
        self._shapefile_service = ShapefileService(stib_api_client)
        self.api_client = stib_api_client

    async def get_passages(self, stop_name: str, line_filters: list = None, max_passages: int = None, lang_stop_name: str = None, lang_message: str = None,
                           now: datetime.datetime = datetime.datetime.now()):
        stop_infos = await self._shapefile_service.get_stop_infos(stop_name)

        if lang_message is None or lang_message not in LANGS:
            lang_message = "fr"
        if lang_stop_name is None or lang_stop_name not in LANGS:
            lang_stop_name = "fr"


        atomic_stop_infos = stop_infos.get_atomic_stop_infos(line_filters)
        if len(atomic_stop_infos) < 1:
            LOGGER.error("Invalid line filter for stop " + str(stop_name) + " Known infos:" + str(
                stop_infos) + " Provided line filter:" + str(line_filters))
            raise InvalidLineFilterException()
        passages = []
        is_only_end_of_service = True
        raw_passages = await self.api_client.api_call_passingTimeByPoint_for_stop_ids(stop_infos.get_stop_ids(line_filters))
        for point in raw_passages["points"]:
            for json_passage in point["passingTimes"]:
                message = ""
                try:
                    message = json_passage["message"][lang_message]
                except KeyError:
                    pass
                try:
                    if message.upper() == "FIN DE SERVICE" or message.upper() == "EINDE DIENST":
                        next_passage = await self._shapefile_service.get_next_stop_passage(point["pointId"], now)
                        passages.append(Passage(stop_id=point["pointId"],
                                                lineId=json_passage["lineId"],
                                                destination="",
                                                expectedArrivalTime=next_passage.strftime("%Y-%m-%dT%H:%M:%S"),
                                                lineInfos=await self._shapefile_service.get_line_info(
                                                    json_passage["lineId"]),
                                                message=message,
                                                now=now))
                    else:
                        is_only_end_of_service = False
                        passages.append(Passage(stop_id=point["pointId"],
                                                lineId=json_passage["lineId"],
                                                destination=json_passage["destination"][lang_stop_name],
                                                expectedArrivalTime=json_passage.get("expectedArrivalTime", None),
                                                lineInfos=await self._shapefile_service.get_line_info(
                                                    json_passage["lineId"]),
                                                message=message,
                                                now=now))
                except KeyError as ke:
                    LOGGER.error(
                        "Error while parsing response from STIB. Raw response is: " + str(raw_passages))
                    raise ke
        if is_only_end_of_service or len(passages) == 0:
            raised_passages = []
            message = "Information from Schedule"
            if lang_message == 'fr':
                message = "Information venant du planning"
            elif lang_message == 'nl':
                message = "Informatie uit de planning"
            for atomic in atomic_stop_infos:
                next_passage = await self._shapefile_service.get_next_stop_passage(atomic.get_stop_id(), now)
                raised_passages.append(Passage(stop_id=atomic.get_stop_id(),
                                               lineId=atomic.get_line_nr(),
                                               destination=atomic.get_destination(),
                                               expectedArrivalTime=next_passage.strftime("%Y-%m-%dT%H:%M:%S"),
                                               lineInfos=await self._shapefile_service.get_line_info(
                                                   atomic.get_line_nr()),
                                               message=message,
                                               now=now))
            raise NoScheduleFromAPIException(sorted(raised_passages))

        passages = sorted(passages)
        if max_passages is not None:
            passages = passages[0:max_passages]
        return passages


class NoScheduleFromAPIException(Exception):
    def __init__(self, passages):
        """ This exception provides information about the next scheduled passage.
        The fact that an exception is raised allows to differentiate passages returned from API or assumed values from GTFS
        It could be used to specify the user that this info is assumed instead of "official from API" """
        self.passages = passages

    def get_next_passages(self):
        return self.passages

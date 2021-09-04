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

    def __init__(self, stib_api_client: AbstractSTIBAPIClient, lang: str = "fr"):
        self._shapefile_service = ShapefileService(stib_api_client)
        self.api_client = stib_api_client
        if lang not in LANGS:
            raise ValueError("Invalid lang :"+lang+" accpted values are:"+str(LANGS))
        self.lang = lang

    async def get_passages(self, stop_name: str, line_filter: list = None, max_passages: int = None,
                           now: datetime.datetime = datetime.datetime.now()):
        stop_infos = await self._shapefile_service.get_stop_infos(stop_name)

        atomic_stop_infos = stop_infos.get_atomic_stop_infos(line_filter)
        if len(atomic_stop_infos) < 1:
            LOGGER.error("Invalid line filter for stop " + str(stop_name) + " Known infos:" + str(
                stop_infos) + " Provided line filter:" + str(line_filter))
            raise InvalidLineFilterException()

        passages = await self.get_passages_for_stop_ids(stop_infos.get_stop_ids(line_filter), now)
        if len(passages) == 0:
            raised_passages = await self.get_next_passages_from_schedule(atomic_stop_infos, line_filter, self.lang, now)
            raise NoScheduleFromAPIException(sorted(raised_passages))

        lines = stop_infos.get_lines()
        filter(lambda p: p.get_line_nr() in lines, passages)

        if max_passages is not None and len(passages) > max_passages:
            passages = passages[0:max_passages]
        return passages

    async def get_next_passages_from_schedule(self, atomic_stop_infos: list, line_filter: list, lang_message: str = None,
                                              now: datetime.datetime = datetime.datetime.now()):
        if lang_message is None or lang_message not in LANGS:
            lang_message = "fr"

        passages_from_schedule = []
        message = "Information from Schedule"
        if lang_message == 'fr':
            message = "Information venant du planning"
        elif lang_message == 'nl':
            message = "Informatie uit de planning"
        for atomic in atomic_stop_infos:
            # FIXME we're not sure that the passage corresponds to the line_nr here (it definitely not)
            next_passage = await self._shapefile_service.get_next_stop_passage(atomic.get_stop_id(), line_filter, now)
            passages_from_schedule.append(Passage(stop_id=atomic.get_stop_id(),
                                                  lineId=atomic.get_line_nr(),
                                                  destination=atomic.get_destination(),
                                                  expectedArrivalTime=next_passage.strftime("%Y-%m-%dT%H:%M:%S"),
                                                  lineInfos=await self._shapefile_service.get_line_info(
                                                      atomic.get_line_nr()),
                                                  message=message,
                                                  now=now))
        return passages_from_schedule

    async def get_passages_for_stop_ids(self, stop_ids: list,
                                        now: datetime.datetime = datetime.datetime.now()):
        passages = []
        raw_passages = await self.api_client.api_call_passingTimeByPoint_for_stop_ids(stop_ids)
        for point in raw_passages["points"]:
            await self.handlePoint(point, now, passages)
            return sorted(passages)

    async def handlePoint(self, point, now, passages):
        for json_passage in point["passingTimes"]:
            await self.handlePassage(json_passage, now, point, passages)

    async def handlePassage(self, json_passage, now, point, passages):
        message = ""
        try:
            message = json_passage["message"][self.lang]
        except KeyError:
            pass
        try:
            if message.upper() == "FIN DE SERVICE" or message.upper() == "EINDE DIENST":
                next_passage = (await self._shapefile_service.get_next_stop_passage(point["pointId"], now)).strftime("%Y-%m-%dT%H:%M:%S")
                destination = ""
            else:
                next_passage = json_passage.get("expectedArrivalTime", None)
                destination = json_passage["destination"][self.lang]

            passages.append(Passage(stop_id=point["pointId"],
                                    lineId=json_passage["lineId"],
                                    destination=destination,
                                    expectedArrivalTime= next_passage,
                                    lineInfos=await self._shapefile_service.get_line_info(
                                        json_passage["lineId"]),
                                    message=message,
                                    now=now))
        except KeyError as ke:
            LOGGER.error(
                "Error while parsing response from STIB. Raw point: " + str(point), ke)
            raise ke


class STIBStop:
    def __init__(self, stib_service: STIBService, stop_name: str, monitored_lines: list = None,
                 max_passages: int = None):
        self.max_passages = max_passages
        self.monitored_lines = monitored_lines
        self.stop_name = stop_name
        self.stib_service = stib_service

    def get_passages(self):
        return self.stib_service.get_passages(self.stop_name, self.monitored_lines, self.max_passages, datetime.datetime.now())


class NoScheduleFromAPIException(Exception):
    def __init__(self, passages):
        """ This exception provides information about the next scheduled passage.
        The fact that an exception is raised allows to differentiate passages returned from API or assumed values from GTFS
        It could be used to specify the user that this info is assumed instead of "official from API" """
        self.passages = passages

    def get_next_passages(self):
        return self.passages

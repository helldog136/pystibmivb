import json
import logging
import datetime

from pystibmivb.client import AbstractSTIBAPIClient
from pystibmivb.domain.passages import Passage
from pystibmivb.service.ShapefileService import ShapefileService

LOGGER = logging.getLogger(__name__)

PASSING_TIME_BY_POINT_SUFFIX = "/OperationMonitoring/4.0/PassingTimeByPoint/"
LANG_STOP_NAME = 0
LANG_MESSAGE = 1


class InvalidLineFilterException(Exception):
    pass


class STIBService:
    def __init__(self, stib_api_client: AbstractSTIBAPIClient):
        self._shapefile_service = ShapefileService(stib_api_client)
        self.api_client = stib_api_client

    async def get_passages(self, stop_name, line_filters=None, max_passages=15, lang: tuple = None,
                           now=datetime.datetime.now()):
        stop_infos = await self._shapefile_service.get_stop_infos(stop_name)

        if lang is None or lang == '':
            lang = ('fr', 'en')

        atomic_stop_infos = stop_infos.get_lines()
        if line_filters is not None and len(line_filters) > 0:
            line_filter_dict = {}
            for line_nr, line_variant_or_dest in line_filters:
                line_filter_dict[line_nr] = line_filter_dict.get(line_nr, [])
                line_filter_dict[line_nr].append(
                    line_variant_or_dest.upper() if isinstance(line_variant_or_dest, str) else line_variant_or_dest)
            new_atomic_stop_infos = []
            for atomic_stop_info in atomic_stop_infos:
                if atomic_stop_info.get_line_nr() in line_filter_dict.keys():  # the line nr is included in line_filter
                    # now we check for direction
                    if atomic_stop_info.get_destination().upper() in line_filter_dict[atomic_stop_info.get_line_nr()]:
                        new_atomic_stop_infos.append(atomic_stop_info)
                    elif atomic_stop_info.get_variante() in line_filter_dict[atomic_stop_info.get_line_nr()]:
                        new_atomic_stop_infos.append(atomic_stop_info)
            atomic_stop_infos = new_atomic_stop_infos
        if len(atomic_stop_infos) < 1:
            LOGGER.error("Invalid line filter for stop " + str(stop_name) + " Known infos:" + str(
                stop_infos) + " Provided line filter:" + str(line_filters))
            raise InvalidLineFilterException()
        passages = []
        is_only_end_of_service = True
        for atomic in atomic_stop_infos:
            call_url_suffix = PASSING_TIME_BY_POINT_SUFFIX + atomic.get_stop_id()

            raw_str_passages = await self.api_client.api_call(call_url_suffix)
            raw_passages = json.loads(raw_str_passages)
            for point in raw_passages["points"]:
                for json_passage in point["passingTimes"]:
                    if len(passages) >= max_passages:
                        break
                    message = ""
                    try:
                        message = json_passage["message"][lang[LANG_MESSAGE]]
                    except KeyError:
                        pass
                    try:
                        if message.upper() == "FIN DE SERVICE" or message.upper() == "EINDE VAN SERVICE":
                            delta = datetime.timedelta(minutes=42, seconds=42)
                            passages.append(Passage(stop_id=point["pointId"],
                                                    lineId=json_passage["lineId"],
                                                    destination="",
                                                    expectedArrivalTime=(now + delta).strftime("%Y-%m-%dT%H:%M:%S"),
                                                    lineInfos=await self._shapefile_service.get_line_info(
                                                        json_passage["lineId"]),
                                                    message=message,
                                                    now=now))
                        else:
                            is_only_end_of_service = False
                            passages.append(Passage(stop_id=point["pointId"],
                                                    lineId=json_passage["lineId"],
                                                    destination=json_passage["destination"][lang[LANG_STOP_NAME]],
                                                    expectedArrivalTime=json_passage["expectedArrivalTime"],
                                                    lineInfos=await self._shapefile_service.get_line_info(
                                                        json_passage["lineId"]),
                                                    message=message,
                                                    now=now))
                    except KeyError as ke:
                        LOGGER.error(
                            "Error while parsing response from STIB. Raw response is: " + str(raw_str_passages))
                        raise ke
        if is_only_end_of_service or len(passages) == 0:
            raised_passages = []
            message = "Information from Schedule"
            if lang[LANG_MESSAGE] == 'fr':
                message = "Information venant du planning"
            elif lang[LANG_MESSAGE] == 'nl':
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
            raise NoScheduleFromAPIException(raised_passages)
        return passages


class NoScheduleFromAPIException(Exception):
    def __init__(self, passages):
        """ This exception provides information about the next scheduled passage.
        The fact that an exception is raised allows to differentiate passages returned from API or assumed values from GTFS
        It could be used to specify the user that this info is assumed instead of "official from API" """
        self.passages = passages

    def get_next_passages(self):
        return self.passages

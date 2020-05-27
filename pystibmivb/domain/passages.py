from datetime import *

from .line import LineInfo
from .util import get_time_delta


class Passage(dict):
    def __init__(self, stop_id: int, lineId: int, destination: str, expectedArrivalTime: str, lineInfos: LineInfo,
                 message: str = "", now: datetime = datetime.now()):
        dict.__init__(self)
        self["stop_id"] = stop_id
        self["line_id"] = lineId
        self["destination"] = destination
        self["expected_arrival_time"] = expectedArrivalTime
        self["line_color"] = lineInfos.get_line_color()
        self["line_text_color"] = lineInfos.get_line_text_color()
        self["line_type"] = lineInfos.get_line_type()
        self["message"] = message
        delta = get_time_delta(now, expectedArrivalTime)
        self["arriving_in"] = {"min": delta // 60, "sec": delta % 60}


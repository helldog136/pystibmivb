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
        self["line_color"] = lineInfos.get_line_color()
        self["line_text_color"] = lineInfos.get_line_text_color()
        self["line_type"] = lineInfos.get_line_type()
        self["message"] = message
        if expectedArrivalTime is not None:
            self["expected_arrival_time"] = expectedArrivalTime
            delta = get_time_delta(now, expectedArrivalTime)
            self["arriving_in"] = {"min": delta // 60, "sec": delta % 60}

    def __lt__(self, other):
        if type(other) != type(self):
            return super(self).__lt__(other)
        other_arriving_in = other.get("arriving_in", None)
        if other_arriving_in is not None:
            self_arriving_in = self.get("arriving_in", None)
            if self_arriving_in is not None:
                if self_arriving_in["min"] < other_arriving_in["min"]:
                    return True
                elif other_arriving_in["min"] < self_arriving_in["min"]:
                    return False
                else:  # == we compare seconds
                    if self_arriving_in["sec"] < other_arriving_in["sec"]:
                        return True
                    else:
                        return False
            else:
                return False
        else:
            return True

    def __eq__(self, other):
        if type(other) != type(self):
            return super(self).__eq__(other)
        other_arriving_in = other.get("arriving_in", None)
        if other_arriving_in is not None:
            self_arriving_in = self.get("arriving_in", None)
            if self_arriving_in is not None:
                return self_arriving_in["min"] == other_arriving_in["min"] \
                       and self_arriving_in["sec"] == other_arriving_in["sec"]
            else:
                return False
        else:
            return False

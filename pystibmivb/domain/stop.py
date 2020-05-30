class AtomicStop:
    def __init__(self, stop_id, line_nr, variante, terminus):
        self.stop_id = stop_id
        self.line_nr = line_nr
        self.variante = variante
        self.terminus = terminus

    def get_stop_id(self):
        return self.stop_id

    def get_line_nr(self):
        return self.line_nr

    def get_destination(self):
        return self.terminus

    def get_variante(self):
        return self.variante

    def __str__(self):
        return f"{self.stop_id} {self.line_nr} {self.variante} {self.terminus}"

    def __repr__(self):
        return super().__repr__() + self.__str__()


class StopInfo:
    def __init__(self, stop_name):
        self.stop_name = stop_name
        self.lines = []
        self.line_infos = {}
        self.locations = {}

    def add_stop(self, stop_id, line_nr, variante, terminus):
        self.lines.append(AtomicStop(stop_id, line_nr, variante, terminus))

    def add_line_info(self, line_info):
        self.line_infos[line_info.get_line_nr()] = line_info

    def get_line_info(self, line_nr):
        return self.line_infos[line_nr]

    def get_lines(self):
        return self.lines

    def get_stop_ids(self):
        return [ln.get_stop_id() for ln in self.lines]

    def __str__(self):
        return f"{self.stop_name}({self.get_location()}): {[str(k) for k in self.lines]}: {[str(v) for v in self.line_infos.values()]}"

    def set_locations(self, locs):
        self.locations = locs

    def get_locations(self):
        """ https://xkcd.com/2170/ """
        return self.locations

    def get_location(self):
        """ https://xkcd.com/2170/ """
        latitudes = [loc["lat"] for loc in self.locations.values()]
        longitudes = [loc["lon"] for loc in self.locations.values()]
        return {"lat": sum(latitudes)/len(latitudes), "lon": sum(longitudes)/len(longitudes)}

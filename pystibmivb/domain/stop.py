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

    def get_atomic_stop_infos(self, line_filters=None) -> list:
        res = []
        if line_filters is not None and len(line_filters) > 0:
            line_filter_dict = {}
            for line_nr, line_variant_or_dest in line_filters:
                line_filter_dict[line_nr] = line_filter_dict.get(line_nr, [])
                line_filter_dict[line_nr].append(
                    line_variant_or_dest.upper() if isinstance(line_variant_or_dest, str) else line_variant_or_dest)
            for atomic_stop_info in self.lines:
                if atomic_stop_info.get_line_nr() in line_filter_dict.keys():  # the line nr is included in line_filter
                    # now we check for direction
                    if atomic_stop_info.get_destination().upper() in line_filter_dict[atomic_stop_info.get_line_nr()]:
                        res.append(atomic_stop_info)
                    elif atomic_stop_info.get_variante() in line_filter_dict[atomic_stop_info.get_line_nr()]:
                        res.append(atomic_stop_info)
        else:
            res = self.lines
        return res

    def get_stop_ids(self, line_filter=None) -> list:
        res = []
        if line_filter is not None and len(line_filter) > 0:
            line_filter_dict = {}
            for line_nr, line_variant_or_dest in line_filter:
                line_filter_dict[line_nr] = line_filter_dict.get(line_nr, [])
                line_filter_dict[line_nr].append(
                    line_variant_or_dest.upper() if isinstance(line_variant_or_dest, str) else line_variant_or_dest)
            for atomic_stop_info in self.lines:
                if atomic_stop_info.get_line_nr() in line_filter_dict.keys():  # the line nr is included in line_filter
                    # now we check for direction
                    if atomic_stop_info.get_destination().upper() in line_filter_dict[atomic_stop_info.get_line_nr()]:
                        res.append(atomic_stop_info)
                    elif atomic_stop_info.get_variante() in line_filter_dict[atomic_stop_info.get_line_nr()]:
                        res.append(atomic_stop_info)
        else:
            res = self.lines
        return [ln.get_stop_id() for ln in res]

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

    def get_lines(self, lines_filter=None):
        return set([asi.get_line_nr() for asi in self.get_atomic_stop_infos(lines_filter)])

    def get_lines_with_destinations(self, lines_filter=None):
        return [(asi.get_line_nr(), asi.get_destination()) for asi in self.get_atomic_stop_infos(lines_filter)]

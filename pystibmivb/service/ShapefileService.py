import datetime
import logging
import os
import tempfile
import zipfile

import shapefile

from pystibmivb.client import AbstractSTIBAPIClient
from pystibmivb.domain.line import LineInfo
from pystibmivb.domain.stop import StopInfo

LOGGER = logging.getLogger(__name__)

ENDPOINT_SHAPEFILES = '/Files/2.0/Shapefiles'
ENDPOINT_GTFS = '/Files/2.0/Gtfs'

SEP = os.sep
SHAPEFILESFOLDERPATH = tempfile.gettempdir() + SEP + "stibmivbshapefiles"
SHAPEFILES_ZIP_FILENAME = "shapefiles.zip"
SHAPEFILES_ZIP_FILEPATH = SHAPEFILESFOLDERPATH + SEP + SHAPEFILES_ZIP_FILENAME
GTFS_ZIP_FILENAME = "gtfs.zip"
GTFS_ZIP_FILEPATH = SHAPEFILESFOLDERPATH + SEP + GTFS_ZIP_FILENAME
LINES_FILENAME = "ACTU_LINES"
LINES_FILEPATH = SHAPEFILESFOLDERPATH + SEP + LINES_FILENAME
LINES_GTFS_FILENAME = "routes.txt"
LINES_GTFS_FILEPATH = SHAPEFILESFOLDERPATH + SEP + LINES_GTFS_FILENAME
STOPS_FILENAME = "ACTU_STOPS"
STOPS_FILEPATH = SHAPEFILESFOLDERPATH + SEP + STOPS_FILENAME
STOPS_GTFS_FILENAME = "stops.txt"
STOPS_GTFS_FILEPATH = SHAPEFILESFOLDERPATH + SEP + STOPS_GTFS_FILENAME
STOPS_SCHEDULES_GTFS_FILENAME = "stop_times.txt"
STOPS_SCHEDULES_GTFS_FILEPATH = SHAPEFILESFOLDERPATH + SEP + STOPS_SCHEDULES_GTFS_FILENAME
TIMESTAMPFILENAME = "timestamp"
TIMESTAMPFILEPATH = SHAPEFILESFOLDERPATH + SEP + TIMESTAMPFILENAME
DELTA_MAX_TIMESTAMP = 1 * 60 * 60 * 24 * 7  # 1 week


def _recur_find_next_passage(date: datetime.datetime, target_time: str, array: list, start: int,
                             end: int) -> datetime.datetime:
    mid = (start + end) // 2
    if mid == start:
        if target_time < array[end]:
            h, m, s = array[end].split(':')
            return datetime.datetime(year=date.year, month=date.month, day=date.day + int(h)//24, hour=int(h)%24,
                                     minute=int(m), second=int(s))
        else:
            h, m, s = array[0].split(':')
            return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=int(h), minute=int(m),
                                     second=int(s)) + datetime.timedelta(days=1)
    if target_time < array[mid]:
        return _recur_find_next_passage(date, target_time, array, start, mid)
    else:  # array[mid] <= target_time
        return _recur_find_next_passage(date, target_time, array, mid, end)


class ShapefileService:
    def __init__(self, stib_api_client: AbstractSTIBAPIClient):
        self.api_client = stib_api_client
        self.lines_cache = {}
        self.stops_cache = {}
        self.stops_schedules_cache = {}

    async def get_line_text_color(self, line_nr):
        await self._refresh_files()
        with open(LINES_GTFS_FILEPATH, 'r') as lines_file:
            for info_line in lines_file:
                splitted_info_line = info_line.split(',')
                if splitted_info_line[1].strip() == str(line_nr):
                    return "#" + splitted_info_line[-1].strip()
        return "#E1337E"

    async def get_line_info(self, line_nr: int) -> LineInfo:
        await self._refresh_files()
        if line_nr not in self.lines_cache.keys():
            sf = shapefile.Reader(LINES_FILEPATH)
            for record in sf.records():
                record = record.as_dict()
                current_line_nr, line_type = record["LIGNE"][:-1], record["LIGNE"][-1:]
                if int(line_nr) == int(current_line_nr):
                    line_color = record["COLOR_HEX"]
                    line_text_color = await self.get_line_text_color(line_nr)
                    self.lines_cache[line_nr] = LineInfo(int(current_line_nr), line_type.upper(), line_color,
                                                         line_text_color)
                    break
        return self.lines_cache[line_nr]

    async def get_stop_schedule(self, stop_id: str):
        await self._refresh_files()
        if stop_id not in self.stops_schedules_cache.keys():
            LOGGER.info("Stop schedule for stop_id:" + stop_id + " not cached, fetching it in GTFS files...")
            res = []
            with open(STOPS_SCHEDULES_GTFS_FILEPATH, 'r') as gtfs_schedules:
                for schedule_part in gtfs_schedules:
                    schedule_part_splitted = schedule_part.strip().split(',')
                    if schedule_part_splitted[3].upper() == stop_id.upper():
                        res.append(schedule_part_splitted[2].strip())
            self.stops_schedules_cache[stop_id] = sorted(res)
            LOGGER.info("Stop schedule for stop_id:" + stop_id + " successfully cached!")
        return self.stops_schedules_cache[stop_id]

    async def get_next_stop_passage(self, stop_id: str, time: datetime.datetime) -> datetime.datetime:
        stop_schedule = await self.get_stop_schedule(stop_id)
        return _recur_find_next_passage(time, time.strftime("%H:%M:%S"), stop_schedule, 0, len(stop_schedule) - 1)

    async def get_stop_infos(self, stop_name: str) -> StopInfo:
        await self._refresh_files()
        if stop_name not in self.stops_cache.keys():
            sf = shapefile.Reader(STOPS_FILEPATH)
            res = StopInfo(stop_name)
            for record in sf.records():
                record = record.as_dict()
                if record["alpha_fr"].upper() == stop_name.upper() or record["alpha_nl"].upper() == stop_name.upper() \
                        or record["descr_fr"].upper() == stop_name.upper() or record[
                    "descr_nl"].upper() == stop_name.upper():
                    res.add_stop(record["stop_id"], record["numero_lig"], record["variante"], record["terminus"])
                    res.add_line_info(await self.get_line_info(record["numero_lig"]))
            res.set_locations(await self.get_stop_locations(res.get_stop_ids()))
            self.stops_cache[stop_name] = res
        return self.stops_cache[stop_name]

    async def _refresh_files(self):
        if self._must_update_files():
            import time
            LOGGER.info("Shapefiles validity outdated, updating them...")
            with open(TIMESTAMPFILEPATH, 'w') as f:
                f.write(str(time.time()))
            await self._refresh_shapefiles()
            await self._refresh_gtfs()

    async def _refresh_gtfs(self):
        zipped_data = await self.api_client.api_call(ENDPOINT_GTFS)
        if zipped_data is not None:
            # save data to disk
            zip_path = GTFS_ZIP_FILEPATH
            LOGGER.info("Saving new zip of gtfs to " + str(zip_path))
            with open(zip_path, 'wb') as output:
                output.write(zipped_data)
                output.close()

            # extract the data
            zfobj = zipfile.ZipFile(zip_path)
            for name in zfobj.namelist():
                uncompressed = zfobj.read(name)
                name = name.split('/')[-1]

                # save uncompressed data to disk
                output_filename = SHAPEFILESFOLDERPATH + SEP + name
                LOGGER.info("Saving extracted file to " + str(output_filename))
                with open(output_filename, 'wb') as output:
                    output.write(uncompressed)

            # TODO os.remove(zip_filename)

            LOGGER.info("Finished updating GTFS!")
            self.lines_cache = {}
            self.stops_schedules_cache = {}
        else:
            LOGGER.error("Unable to update GTFS...")

    async def _refresh_shapefiles(self):
        """ Get most recent file info if not in local cache (api for files can be called only once per minute.
        These file change only 2 or 3 times per year thus we will invalidate them after one week.
        To force update simply delete the timestamp file."""
        zipped_data = await self.api_client.api_call(ENDPOINT_SHAPEFILES)
        if zipped_data is not None:
            # save data to disk
            zip_path = SHAPEFILES_ZIP_FILEPATH
            LOGGER.info("Saving new zip of shapefiles to " + str(zip_path))
            with open(zip_path, 'wb') as output:
                output.write(zipped_data)
                output.close()

            # extract the data
            zfobj = zipfile.ZipFile(zip_path)
            for name in zfobj.namelist():
                uncompressed = zfobj.read(name)
                name = name.split('/')[-1]

                # save uncompressed data to disk
                output_filename = SHAPEFILESFOLDERPATH + SEP + name
                LOGGER.info("Saving extracted file to " + str(output_filename))
                with open(output_filename, 'wb') as output:
                    output.write(uncompressed)

            # TODO os.remove(zip_filename)
            LOGGER.info("Finished updating Shapefiles!")
            self.stops_cache = {}
        else:
            LOGGER.error("Unable to update Shapefiles...")

    def _must_update_files(self):
        import time
        must_update = False
        if not os.path.isdir(SHAPEFILESFOLDERPATH):
            LOGGER.info("Shapefile folder not existing, creating it...")
            must_update = True
            os.mkdir(SHAPEFILESFOLDERPATH)
        if not os.path.isfile(TIMESTAMPFILEPATH):
            LOGGER.info("Shapefile timestamp file not existing, creating it...")
            with open(TIMESTAMPFILEPATH, 'w') as f:
                f.write(str(time.time()))
            must_update = True
        with open(TIMESTAMPFILEPATH, 'r') as f:
            timestamp = int(f.read().split(".")[0])
            now = time.time()
            if now - timestamp > DELTA_MAX_TIMESTAMP:
                must_update = True
                LOGGER.info(
                    f"Delta since last update is {now - timestamp} which is greater than {DELTA_MAX_TIMESTAMP}. Invalidating files...")
        return must_update

    async def get_stop_locations(self, stop_ids: list):
        await self._refresh_files()
        res = {}
        for stop_id in stop_ids:
            res[stop_id] = await self.get_stop_location(stop_id)
        return res

    async def get_stop_location(self, stop_id: str):
        await self._refresh_files()
        with open(STOPS_GTFS_FILEPATH, 'r') as stops_file:
            for info_stop in stops_file:
                splitted_info_line = info_stop.split(',')
                if splitted_info_line[0].strip() == stop_id:
                    return {"lat": float(splitted_info_line[4]), "lon": float(splitted_info_line[5])}
        return {"lat": 50.847180, "lon": 4.361610}

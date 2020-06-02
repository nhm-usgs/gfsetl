"""Main module."""
from pathlib import Path
import requests
import xarray
from datetime import datetime, timedelta
import geopandas as gpd
from gfsetl.helpers import get_gfs_url
class GFSEtl:

    def __init__(self, period=None, prefix=None, inpath=None, outpath=None, weightsfile=None,
        gpkg=None):
        self._start_date = period[0]
        self._end_date = period[1]
        self._fileprefix = prefix
        self._iptpath = Path(inpath)
        self._optpath = Path(outpath)
        self._wghts_file = Path(weightsfile)
        self._gpkg = Path(gpkg)
        self._GFS_vars = {
                'ppt': 'Total_precipitation_surface_6_Hour_Accumulation',
                'tmax': 'Maximum_temperature_height_above_ground_6_Hour_Maximum',
                'tmin': 'Minimum_temperature_height_above_ground_6_Hour_Minimum'
        }
        self._GFS_vars_2 ={
                'rh': 'Relative_humidity_sigma',
                'wsu': 'u-component_of_wind_sigma',
                'wsv': 'v-component_of_wind_sigma'}

        if self._start_date > self._end_date:
            raise ValueError(
                "start date ({0}) must be before end date ({1})".format(
                    self.start_date, self.end_date
                )
            )
        if self._end_date > datetime.now():
            raise ValueError(
                "end date cannot be a future date ({0} > {1}".format(
                    self.end_date, datetime.date.today()
                )
            )
        self.gdf = None


    def initialize(self):
        # self.gdf = gpd.read_file(self._gpkg)
        t_delta = timedelta(days=1)
        for key, value in self._GFS_vars.items():
            ncfile = []
            while self._start_date <= self._end_date:
                self.write_extract_file_per_day(self._start_date, key=key, value=value, incfile=ncfile)
                self._start_date += t_delta


    def write_extract_file_per_day(self, date, key, value, incfile):
        for hour in [0, 6, 12, 18]:
            date_hr = date + timedelta(hours=hour)
            for forecast_p in [6]:
                date_fc = date_hr + timedelta(hours=forecast_p)
                url, params = get_gfs_url(date=date_hr, forecast_p=forecast_p, dsvar=value)
                file = requests.get(url, params=params)
                file.raise_for_status()
                fn = '{var}_gfsanl_4_{dt:%Y%m%d}_{dt:%H}00_00{fp}.grb2.nc'.format(dt=date_hr, fp=forecast_p, var=key)
                tfile = self._iptpath / fn
                incfile.append(tfile)
                with open(tfile, 'wb') as fh:
                    fh.write(file.content)
                fh.close()


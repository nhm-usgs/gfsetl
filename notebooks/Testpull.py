
from datetime import datetime, timedelta
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from metpy.units import units
from netCDF4 import num2date
import numpy as np
import scipy.ndimage as ndimage
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
import xarray as xr
from pathlib import Path
from requests.exceptions import HTTPError
from xarray.backends import NetCDF4DataStore

year = 2020
month = 1
day = 1
hour = 0

dt = datetime(year, month, day, hour)
dt2 = datetime(year, month, day+1, hour)

base_url = 'https://www.ncei.noaa.gov/thredds/catalog/model-gfs-g4-anl-files'

# Programmatically generate the URL to the day of data we want
cat = TDSCatalog(f'{base_url}{dt:%Y%m}/{dt:%Y%m%d}/catalog.xml')
print(cat.datasets, type(cat.datasets[0]))
ds = cat.datasets.filter_time_range(dt, dt2)
print(ds)
print(dt, dt2)
for file in ds:
    ncss = None
    query = None
    # print(file)
    try:
        ncss = file.subset()
        query = ncss.query().lonlat_box(north=54, south=20, east=-65, west=-126)
        query.variables('Precipitation_rate_surface_6_Hour_Average').add_lonlat().accept('netcdf')
        data = ncss.get_data(query)
        print(file, flush=True)
        data.close()
    except HTTPError as http_err:
        print(f'HTTP error occured: {file}', flush=True)


# %%



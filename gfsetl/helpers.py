import datetime as dt
from datetime import timedelta

def get_gfs_url(date, forecast_p, dsvar):
    assert (date.hour in [0, 6, 12, 18]), f'Hour in date must be in {[0, 6, 12, 18]}'
    assert (forecast_p in [3, 6]), f'forecast_p must be in {[3, 6]}'
    
    base_url = 'https://www.ncei.noaa.gov/thredds/ncss/model-gfs-g4-anl-files/'
    url = \
        '{}{dt:%Y%m}/{dt:%Y%m%d}/gfsanl_4_{dt:%Y%m%d}_{dt:%H}00_00{fp}.grb2' \
        .format(base_url, dt=date, fp=forecast_p)
    
    sformat = "%Y-%m-%dT%H:00:00Z"
    # Format of this thredds server is that only 1-day available in a subset
    date_fh = date + timedelta(hours=forecast_p)
    str_start = date_fh.strftime(sformat)

    payload = {
        'var': dsvar,
        'north': '54',
        'west': '-126',
        'east': '-65',
        'south': '20',
        'disableProjSubset': 'on',
        'horizStride': '1',
        'time_start': str_start,
        'time_end': str_start,
        'timeStride': '1'}

    return url, payload
import geopandas as gpd
import pandas as pd
import numpy as np
import glob
import zipfile
import os
import xarray as xr
import json
from shapely.geometry import Polygon
import csv
from pathlib import Path
import logging


logging.basicConfig(level=logging.INFO)

hruid = 'nhru_v11' # for GFv11_v2e
gfs_file = Path('HRU_MAP/gfsanl_4_20200506_0000_003.grb2.nc')
ds = xr.open_dataset(gfs_file)
print(ds, flush=True)

print(os.getcwd(), flush=True)
from pathlib import Path

logging.info('Reading geopackage')
gdf = gpd.read_file(Path('HRU_MAP/GFv1.1_nhrusim_Topology_LATLON.gpkg'))
print(gdf.head(), flush=True)
logging.info('finished reading geopackage')

# create some variables from the GFS netcdf file for use later
lathandle = ds['lat']
lonhandle = ds['lon']
timehandle = ds['time']
datahandle = ds['Maximum_temperature_height_above_ground_3_Hour_Maximum']
logging.debug(f'lat: {lathandle}, lon: {lonhandle}, time: {timehandle}')

temp = ds.Maximum_temperature_height_above_ground_3_Hour_Maximum.isel(time=0, height_above_ground=0)
# Probably a better way to accomplish this but had to subtract 360 from lon values
# to make consistent with HRU shapefile/gdb.
lon, lat = np.meshgrid(lonhandle-360.0, lathandle)
df = pd.DataFrame({'temperature': temp.values.flatten()})
res = 0.5/2.0
numcells = np.shape(lat)[0]*np.shape(lat)[1]
poly = []
index = np.zeros(numcells)
count = 0
for i in range(np.shape(lon)[0]):
    for j in range(np.shape(lon)[1]):
        lat_point_list = [lat[i,j]-res, lat[i,j]+res, lat[i,j]+res, lat[i,j]-res]
        lon_point_list = [lon[i,j]+res, lon[i,j]+res, lon[i,j]-res, lon[i,j]-res]
        poly.append(Polygon(zip(lon_point_list, lat_point_list)))
        index[count] = count
        count += 1
ncfcells = gpd.GeoDataFrame(df, index=index, geometry=poly, crs=gdf.crs)
print(ncfcells.head())

spatial_index = ncfcells.sindex

def precise_matches(spatial_index, cells, geom):
    possible_matches_index = list(spatial_index.intersection(geom.bounds))
    if not (len(possible_matches_index) == 0):
        possible_matches = cells.iloc[possible_matches_index]
        return possible_matches[possible_matches.intersects(geom)]
    else:
        return 0

def intersect_area(precise_matches, gdf_loc):
    res_intersection = gpd.overlay(gdf_loc, precise_matches, how='intersection')
    return res_intersection.area
    
tcount = 0
with open('tmp2_GFS_weights_hru_v1_1f.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for index, row in gdf.iterrows():
        count = 0
        hru_area = gdf.loc[gdf[hruid]==row[hruid]].geometry.area.sum()
        if tcount == 0:
            writer.writerow(['grid_ids', hruid, 'w'])
        pm  = precise_matches(spatial_index, ncfcells, row['geometry'])
        if not (len(pm) == 0):
            area = intersect_area(pm, gdf.loc[[index]]).values
            it = np.nditer(area, flags=['f_index'])
            for a in it:
                writer.writerow([np.int(pm.index[it.index]), np.int(row[hruid]), np.float(a/hru_area)])
        else:
            print('no intersection: ', index, np.int(row[hruid]), flush=True)
        tcount += 1
        if tcount % 1000 == 0:
            print(tcount, index, flush=True)
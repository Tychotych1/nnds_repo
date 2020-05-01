#%% Clear and close all
from IPython import get_ipython
get_ipython().magic('reset -f')

### Import libraries
from netCDF4 import Dataset
import pandas as pd
import datetime
import json
import wget
import os
import urllib 

### Set directory
os.chdir("C:/Users/svvdb/OneDrive/Documents/Github/nnds_datascience/Python/Earthquake_map")

### Check whether url with downloadable file exists
def url_is_alive(url):

    request = urllib.request.Request(url)
    request.get_method = lambda: 'HEAD'

    try:
        urllib.request.urlopen(request)
        return True
    except urllib.request.HTTPError:
        return False

### url with earthquake data
url = "ftp://data.knmi.nl/download/aardbevingen_catalogus/1/noversion/1911/05/30/SEISM_OPER_P___EQALL___L2.nc"

if url_is_alive(url):
    ### Delete old file
    if os.path.isfile('SEISM_OPER_P___EQALL___L2.nc'):
        os.remove("SEISM_OPER_P___EQALL___L2.nc")

    ### Download new file
    wget.download(url, "C:/Users/svvdb/OneDrive/Documents/Github/nnds_datascience/Python/Earthquake_map")
    
    ### Get variables from nc file
    nc = Dataset('SEISM_OPER_P___EQALL___L2.nc', 'r')

else:    
    nc = Dataset('SEISM_OPER_P___EQALL___L2.nc', 'r')

for i in nc.variables:
    print(i, nc.variables[i])

iso_dataset 	= nc.variables['iso_dataset'][:]
product 		= nc.variables['product'][:]
projection 		= nc.variables['projection'][:]
id 				= nc.variables['id'][:]
time 			= nc.variables['time'][:]
depth 			= nc.variables['depth'][:]
magnitude_type 	= nc.variables['magnitude_type'][:]
magnitude 		= nc.variables['magnitude'][:]
event_type 		= nc.variables['event_type'][:]
evaluation_mode = nc.variables['evaluation_mode'][:]
agency_id 		= nc.variables['agency_id'][:]
location 		= nc.variables['location'][:]
link 			= nc.variables['link'][:]
lat 			= nc.variables['lat'][:]
lon 			= nc.variables['lon'][:]

### Transform variables to a pandas dataframe
data = [id, lat, lon, location, time, magnitude, depth]
df = pd.DataFrame(data)
df = df.T
df = df.rename(columns = {0: 'ID',  
                          1: 'latitude', 
                          2: 'longitude', 
                          3: 'location', 
                          4: 'timestamp', 
                          5: 'magnitude', 
                          6: 'depth'})
    
df['latitude'] = df['latitude'].replace('.', ',')
df['longitude'] = df['longitude'].replace('.', ',')
df['magnitude'] = pd.to_numeric(df['magnitude'])
df['depth'] = pd.to_numeric(df['depth'])

### Transform timestamp from time since 1900 to epoch
df['timestamp'] = df['timestamp'] - 2208988800

for index,row in df.iterrows():
    
    epoch = df.at[index, 'timestamp']
    
    try:
        date_time = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
    
    except:
        date_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=(epoch))
        date_time = date_time - datetime.timedelta(microseconds=date_time.microsecond)
        
    df.at[index, 'timestamp'] = date_time

df['timestamp'] =  df['timestamp'].astype(str)

df_voor1990 = df[df['timestamp'] < "1990-01-01 00:00:00"]
df_na1990 = df[df['timestamp'] > "1990-01-01 00:00:00"]

df.to_csv('earthquake_data.csv')
df_voor1990.to_csv('earthquake_data_voor1990.csv')
df_na1990.to_csv('earthquake_data_na1990.csv')

### Dataframe to geojson
def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
    
    df_geojson = {'type':'FeatureCollection', 'features':[]}
    
    for _, row in df.iterrows():
        
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point','coordinates':[]}}
        feature['geometry']['coordinates'] = [row[lon],row[lat]]
        
        for prop in properties:
            
            feature['properties'][prop] = row[prop]
            
        df_geojson['features'].append(feature)
    return df_geojson

cols = ['ID', 'location', 'timestamp', 'magnitude', 'depth']
df_geojson = df_to_geojson(df, cols)
df_voor1990_geojson = df_to_geojson(df_voor1990, cols)
df_na1990_geojson = df_to_geojson(df_na1990, cols)

with open('earthquake_data_point.geojson', 'w') as json_file:
    json.dump(df_geojson, json_file)
with open('earthquake_data_voor1990_point.geojson', 'w') as json_file:
    json.dump(df_voor1990_geojson, json_file)
with open('earthquake_data_na1990_point.geojson', 'w') as json_file:
    json.dump(df_na1990_geojson, json_file)
    
### Geojson point data to polygon data
def geojson_point_to_polygon(df_geojson, size = 1):

    for i in range(0, len(df_geojson['features'] ), 1):
        
        df_geojson['features'][i]['geometry']['type'] = 'Polygon'
        
        long_diff = size * 0.0015060 #degree change for 100m distance in longitude direction
        lat_diff = size * 0.0008983 #degree change for 100m distance in latitude direction
        
        long = df_geojson['features'][i]['geometry']['coordinates'][0]
        lat = df_geojson['features'][i]['geometry']['coordinates'][1]
    
        polygon_hexagon = [[[round(long, 6), round(lat + lat_diff, 6)],
                            [round(long + long_diff, 6), round(lat + 0.5*lat_diff, 6)],
                            [round(long + long_diff, 6), round(lat - 0.5*lat_diff, 6)],
                            [round(long, 6), round(lat - lat_diff, 6)],
                            [round(long - long_diff, 6), round(lat - 0.5*lat_diff, 6)],
                            [round(long - long_diff, 6), round(lat + 0.5*lat_diff, 6)],
                            [round(long, 6), round(lat + lat_diff, 6)]]]
        
        df_geojson['features'][i]['geometry']['coordinates'] = polygon_hexagon
        
    return df_geojson
    
df_geojson_hexagon = geojson_point_to_polygon(df_geojson, 3)
df_voor1990_geojson_hexagon = geojson_point_to_polygon(df_voor1990_geojson, 3)
df_na1990_geojson_hexagon = geojson_point_to_polygon(df_na1990_geojson, 3)

with open('earthquake_data_polygon.geojson', 'w') as json_file:
    json.dump(df_geojson_hexagon, json_file)
with open('earthquake_voor1990_data_polygon.geojson', 'w') as json_file:
    json.dump(df_voor1990_geojson_hexagon, json_file)
with open('earthquake_na1990_data_polygon.geojson', 'w') as json_file:
    json.dump(df_na1990_geojson_hexagon, json_file)


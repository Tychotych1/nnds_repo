from netCDF4 import Dataset
import pandas as pd
import datetime

nc = Dataset('aardbevingen.nc', 'r')
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


data = [lat, lon, location, id, time, depth]
df = pd.DataFrame(data)
df = df.T

df[4] = df[4] - 2208988800
for index,row in df.iterrows():
	epoch = df.at[index, 4]
	date_time = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
	df.at[index, 4] = date_time

df.to_csv('test.csv')

# df.columns = ["latitude", "longitude", "magnitude"]
# print(df.T)
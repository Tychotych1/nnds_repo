import json

with open("convertcsv.geojson") as f:
    gj = json.load(f)


features = gj['features']  
feature_type = gj['features'][0]['geometry']['type']
feature_coor = gj['features'][0]['geometry']['coordinates']

for i in range(0, len(features), 1):
    
    gj['features'][i]['geometry']['type'] = 'Polygon'
    
    long_diff = 2.5 * 0.0015060 #degree change for 100m distance in longitude direction
    lat_diff = 2.5 * 0.0008983 #degree change for 100m distance in latitude direction
    
    long = gj['features'][i]['geometry']['coordinates'][0]
    lat = gj['features'][i]['geometry']['coordinates'][1]
    
    polygon_square = [[[round(long - long_diff, 3), round(lat - lat_diff, 3)],
                       [round(long + long_diff, 3), round(lat - lat_diff, 3)],
                       [round(long + long_diff, 3), round(lat + lat_diff, 3)],
                       [round(long - long_diff, 3), round(lat + lat_diff, 3)],
                       [round(long - long_diff, 3), round(lat - lat_diff, 3)]]]

    polygon_hexagon = [[[round(long, 6), round(lat + lat_diff, 6)],
                        [round(long + long_diff, 6), round(lat + 0.5*lat_diff, 6)],
                        [round(long + long_diff, 6), round(lat - 0.5*lat_diff, 6)],
                        [round(long, 6), round(lat - lat_diff, 6)],
                        [round(long - long_diff, 6), round(lat - 0.5*lat_diff, 6)],
                        [round(long - long_diff, 6), round(lat + 0.5*lat_diff, 6)],
                        [round(long, 6), round(lat + lat_diff, 6)]]]
    
    gj['features'][i]['geometry']['coordinates'] = polygon_hexagon

with open('earthquake_data_polygon_hexagon.geojson', 'w') as json_file:
    json.dump(gj, json_file)

import math

def latitude_grid(latitude, 
    latitude_start = 8.834616884187174, 
    latitude_end = 9.098837418615586,
    radius = 6378137,
    distance = 500):
    if not latitude_start <= latitude <= latitude_end:
        return -1    
    d = (distance/radius) * (180/math.pi)
    return math.floor((latitude - latitude_start)/d)

def longitude_grid(longitude, 
    latitude,
    longitude_start = 38.65314470981974, 
    longitude_end = 38.91274583251382,
    radius = 6378137,
    distance = 500):
    if not longitude_start <= longitude <= longitude_end:
        return -1    
    d = (distance / radius) * (180 / math.pi) / math.cos(math.pi*latitude/180)
    # print(d, longitude_start, longitude, longitude-longitude_start)
    return math.floor((longitude - longitude_start)/d)
def convert_to_grid(latitude, longitude):
    return latitude_grid(latitude), longitude_grid(longitude,latitude)
bottom_left_corner = [8.834616884187174, 38.659962967829706]
tup = convert_to_grid(bottom_left_corner[0], bottom_left_corner[1])
print(tup[0])
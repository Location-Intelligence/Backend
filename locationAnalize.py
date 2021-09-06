from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import pandas as pd
import googlemaps
import numpy as np
import json
import os
import time
from const import API_KEY
gmaps = googlemaps.Client(API_KEY)

# Cleans the data extracted from google maps by removing unnecessary features and splitting coordinates
def cleanData(option, data_list):
    # Inner Functions for dataframe cleaning
    def lat(row):
        if 'location' in row:
            return row['location']['lat']
        return None
    def lng(row):
        if 'location' in row:
            return row['location']['lng']
        return None

    df = pd.DataFrame(data_list)    
    if len(data_list)>0:
        cleaned_df = df[ df.columns & ['name', 'place_id', 'rating', 'geometry']]    
        print(cleaned_df.columns)
        cleaned_df['latitude'] = cleaned_df['geometry'].apply(lat)
        cleaned_df['longitude'] = cleaned_df['geometry'].apply(lng)
        cleaned_df = cleaned_df.drop(['geometry'],axis=1, errors='ignore')
        print('Before dropping duplicates, the size was,',len(cleaned_df))
        cleaned_df.sort_values("place_id", inplace=True)
        print(cleaned_df.columns)
        cleaned_df.drop_duplicates(subset=['place_id'], ignore_index=True, inplace=True)
        print('After dropping duplicates, the size was,',len(cleaned_df))
        return cleaned_df
    else:
        return df

#Extract nearby places from google maps based on a 1km radius and list of categories
def extractFeatures(options, latitude, longitude):
    dataframes = []
    for opt in options:
        data_list = []
        params = {
            'location':[latitude, longitude],
            'radius':1000,
            'type': opt
        }

        first_page = gmaps.places_nearby(**params)
        
        second_page = {'results':[]}
        third_page = {'results':[]}
        
        #Fetching the second page if there is any
        if 'next_page_token' in first_page:
            params['page_token'] = first_page['next_page_token']
            time.sleep(2)
            second_page = gmaps.places_nearby(**params)
        
        #Fetching the third or last page if there is any
        if 'next_page_token' in second_page:
            params['page_token'] = second_page['next_page_token']
            time.sleep(2)
            third_page = gmaps.places_nearby(**params)
        
        data_list.extend(first_page['results'])
        data_list.extend(second_page['results'])
        data_list.extend(third_page['results'])
        cleaned_data = cleanData(opt, data_list)
        if cleaned_data.shape[0]>0:
            dataframes.append((opt, cleaned_data))
    return dataframes

#Calculate Distance between two coordinates
def calculateDistance(lat1, lon1, lat2, lon2):
    from math import sin, cos, sqrt, atan2, radians
    # approximate radius of earth in km
    R = 6373.0
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

#Collect Nearest Supermarkets to the coordinate given
def nearestSupermarkets(lat, lon, dataframe, count):
    import heapq
    nearest = []
    if len(dataframe)==0: return nearest
    for i in dataframe.itertuples(index=True, name='Pandas'):
        heapq.heappush(nearest, (calculateDistance(lat, lon, i.latitude, i.longitude), {
            'name': i.name,
            'latitude': i.latitude,
            'longitude': i.longitude,
            'google_rating': i.rating
        }))
    return [i[1] for i in heapq.nsmallest(count, nearest)]

#Preprocess each extracted dataframe and return their counts alongside nearest supermarkets
def collectNearbyPlaces(current_features, latitude, longitude):
    dataframes = extractFeatures(current_features, latitude, longitude)
    nearby_places = {}
    supermarkets = []
    for key in current_features:
        nearby_places[key] = 0
    for key, df in dataframes:
        if key=='shopping_mall' or key=='supermarket':
            if len(supermarkets)==0:
                supermarkets = df
            else:
                supermarkets = supermarkets.append(df)
        if 'permanently_closed' in df.columns:
            df = df[df['permanently_closed']!=True]
        if key=='shopping_mall' or key=='supermarket':
            nearby_places['competitors'] += df.shape[0]
        else:
            nearby_places[key] = df.shape[0]
    if len(supermarkets)!=0:
        supermarkets.drop_duplicates(inplace = True, subset=['name', 'latitude', 'longitude'])
    nearest_supermarkets = nearestSupermarkets(latitude, longitude, supermarkets, 5)
    return nearby_places, nearest_supermarkets

# Import population File
def importPopulationFile(location = 'Population_per_subcity.json'):
    script_dir = os.path.dirname("__file__")
    subcity_population_json = os.path.join(script_dir, location )
    subcity_population = open(subcity_population_json,)
    subcity_population_data = json.load(subcity_population)
    return subcity_population_data

# Based on coordinate determine the poplation per gender 
def determineSubcityAndAddPopulation(latitude, longitude):
    subcity_population_data = importPopulationFile()

    for subcity in subcity_population_data:
        point = Point(latitude,longitude)
        polygon = Polygon([(i,j) for i, j in subcity_population_data[subcity]['coordinates']])
        if polygon.contains(point):
            total_males = total_females = 0
            for age in subcity_population_data[subcity]['population']:
              total_males += subcity_population_data[subcity]['population'][age]['Males']  
              total_females += subcity_population_data[subcity]['population'][age]['Females']  
            return [total_males, total_females]
    return [0,0]

# Main function to extract places and population count
def extractData(current_features, latitude, longitude):
    nearby_places, supermarkets = collectNearbyPlaces(current_features, latitude, longitude)
    males, females = determineSubcityAndAddPopulation(latitude, longitude)
    nearby_places['Males'] = males
    nearby_places['Females'] = females
    return nearby_places, supermarkets
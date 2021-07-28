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
def cleanData(data_list):
    # Inner Functions for dataframe cleaning
    def lat(row):
        if 'location' in row:
            return row['location']['lat']
        return None
    def lng(row):
        if 'location' in row:
            return row['location']['lng']
        return None
    def check(row, col):
        if col in row:
            return 1
        return 0

    df = pd.DataFrame(data_list)    
    if len(data_list)>0:
        cleaned_df = df.drop(['photos', 'icon', 'scope', 'permanently_closed', 'opening_hours', 'reference', 'plus_code', 'user_ratings_total', 'vicinity'], axis=1, errors='ignore')    
        cleaned_df['latitude'] = cleaned_df['geometry'].apply(lat)
        cleaned_df['longitude'] = cleaned_df['geometry'].apply(lng)
        cleaned_df = cleaned_df.drop(['geometry', 'types'],axis=1, errors='ignore')
        print('Before dropping duplicates, the size was,',len(cleaned_df))
        cleaned_df.sort_values("place_id", inplace=True)
        cleaned_df.drop_duplicates(inplace=True)
        print('After dropping duplicates, the size was,',len(cleaned_df))
        return cleaned_df
    else:
        return df
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
        cleaned_data = cleanData(data_list)
        if cleaned_data.shape[0]>0:
            dataframes.append((opt, cleaned_data))
    return dataframes
def collectNearbyPlaces(current_features, latitude, longitude):
    dataframes = extractFeatures(current_features, latitude, longitude)
    nearby_places = {}
    for key in current_features:
        nearby_places[key] = 0
    for key, df in dataframes:
        if 'permanently_closed' in df.columns:
            df = df[df['permanently_closed']!=True]
        nearby_places[key] = df.shape[0]
    return nearby_places
def importPopulationFile(location = 'Data/Population_per_subcity.json'):
    script_dir = os.path.dirname("__file__")
    subcity_population_json = os.path.join(script_dir, location )
    subcity_population = open(subcity_population_json,)
    subcity_population_data = json.load(subcity_population)
    return subcity_population_data
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
def extractData(current_features, latitude, longitude):
    nearby_places = collectNearbyPlaces(current_features, latitude, longitude)
    males, females = determineSubcityAndAddPopulation(latitude, longitude)
    nearby_places['Males'] = males
    nearby_places['Females'] = females
    return nearby_places
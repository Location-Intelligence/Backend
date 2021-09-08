# app.py

from os import fsync
from typing import Collection
from flask import Flask, request, Response, json

from model import Location
from objectid import PydanticObjectId
from flask_pymongo import PyMongo
from gridTranslation import convert_to_grid
from const import API_KEY,CURRENT_FEATURES,DB_URI,FEATURE_ORDER
from bson.json_util import ObjectId
import torch 
import googlemaps
from locationAnalize import extractData

from flask_cors import CORS
gmaps = googlemaps.Client(API_KEY)
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
model = torch.load('tempmodel.h5')

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['MONGO_URI'] =DB_URI


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)

app.json_encoder = MyEncoder
pymong = PyMongo(app,fsync=True)

CORS(app)

location_details:Collection = pymong.db.location_details



@app.route('/rate/',methods=['GET','POST'])
def rate():
    data = request.get_json()
    locations = data["locations"]
    results = []
    # print("locations: ",locations)
    for i,location in enumerate(locations):
        id_ = location['id']
        name = location['name']
        latitude = location["latitude"]
        longitude = location["longitude"]
        location_data = find_location_by_grid(latitude,longitude)
        # if location_data!=None:
        #     results.append(location_data)
        # else:
        result,supermarkets = extractData(CURRENT_FEATURES,latitude,longitude)
        result_float = []
        for i in FEATURE_ORDER:
            if i=='competitors': continue
            result_float.append(float(result[i]))
        test_values = torch.tensor([result_float])
        rate = torch.argmax(torch.softmax(model(test_values),1), axis = 1)
        result["id"] = id_
        result["name"] = name
        result["rating"] = min(5,rate.item())
        result['nearest'] = supermarkets
        result["latitude"] =latitude
        result["longitude"] = longitude
        tup = convert_to_grid(latitude,longitude)
        result["latitude_grid"] = tup[0]
        result["longitude_grid"] = tup[1]
        # add_new_location(result)
        results.append(result)
    print(type(results), results)
    return Response(json.dumps(results),  mimetype='application/json')
    # except Exception as ex:
    #     print(ex)
    #     return {'Error': 'An unexpected error occurred'}
def rate_prediction(datas):
        try:
            test_values = torch.tensor([[15.0,41.0,85.0,70.0,36.0,30.0,15.0,20.0,16.0,40.0,20.0,15000,15000]])
            result = torch.argmax(torch.softmax(model(test_values), 1), axis=1)
            return jsonify({'rating':(result.item())})
        except Exception as ex:
            print(ex)
            return {'Error': 'An unexpected error occurred'}


@app.route('/predict/', methods=['POST'])
def predict():
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    
    # You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
    if latitude and longitude:
        return rate_prediction(latitude)

    else:
        return jsonify({
            "ERROR": "no latitude or longitude"
        })

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"


def add_new_location(location):
    new_location = Location(**location)
    insert_result = location_details.insert_one(new_location.to_bson())
    new_location.id = PydanticObjectId(str(insert_result.inserted_id))
    return new_location.to_json()

def find_location_by_grid(latitude,longitude):
    tup = convert_to_grid(latitude, longitude)
    location = location_details.find_one({"latitude_grid":tup[0],"longitude_grid":tup[1]})
    return location
if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)

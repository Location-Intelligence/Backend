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
import pandas as pd
from flask_cors import CORS
from torch.nn.init import kaiming_uniform_
from torch.nn.init import xavier_uniform_
import numpy as np
gmaps = googlemaps.Client(API_KEY)
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['MONGO_URI'] =DB_URI


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, set):
            return list(obj)
        return super(MyEncoder, self).default(obj)

app.json_encoder = MyEncoder
pymong = PyMongo(app,fsync=True)

CORS(app)

location_details:Collection = pymong.db.location_details

mean = pd.read_csv('mean.csv',header = None, index_col = 0, squeeze = True)
std = pd.read_csv('std.csv',header = None, index_col = 0, squeeze = True)
class MLP(torch.nn.Module):
    # define model elements
    def __init__(self, n_inputs):
        super(MLP, self).__init__()
        # input to first hidden layer
        self.hidden1 = torch.nn.Linear(n_inputs, 16)
        kaiming_uniform_(self.hidden1.weight, nonlinearity='relu')
        self.act1 = torch.nn.ReLU()
        # second hidden layer
        self.hidden2 = torch.nn.Linear(16, 8)
        kaiming_uniform_(self.hidden2.weight, nonlinearity='relu')
        self.act2 = torch.nn.ReLU()
        # third hidden layer and output
        self.hidden3 = torch.nn.Linear(8, 6)
        xavier_uniform_(self.hidden3.weight)
        self.act3 = torch.nn.Softmax(dim=1)
 
    # forward propagate input
    def forward(self, X):
        # input to first hidden layer
        X = self.hidden1(X)
        X = self.act1(X)
        # second hidden layer
        X = self.hidden2(X)
        X = self.act2(X)
        # output layer
        X = self.hidden3(X)
        X = self.act3(X)
        return X
model = MLP(15)
model.load_state_dict(torch.load('classification.pth'))
model.eval()
# model = torch.load('classification_model.h5')
def get_predict(row, model):
    # convert row to data
    row = torch.Tensor([row])
    # make prediction
    yhat = model(row)
    # retrieve numpy array
    yhat = yhat.detach().numpy()
    return yhat

@app.route('/rate/',methods=['GET','POST'])
def rate():
    try:
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
            if location_data!=None:
                results.append(location_data)
            else:
                result,supermarkets = extractData(CURRENT_FEATURES,latitude,longitude)
                # print('result', result)
                # print('supermarkets: ',supermarkets)
                # print('len: ',len(supermarkets))
                result_float = []
                for i in FEATURE_ORDER:
                    if i == 'train_station' or i == 'bus_station':
                        continue
                    result_float.append(float(result[i]))
            
                test_values = torch.tensor(result_float)
                # test_values = torch.tensor([1,9,7,3,3,0,2,28,4,145225,163770,75491,225517,7987,20])
                test_values=(test_values-mean)/std
                rate = (5- np.argmax(get_predict(test_values, model)))
                # print('my rate: ',rate)
                # rate = torch.argmax(torch.softmax(model(test_values),1), axis = 1)
                result["id"] = id_
                result["name"] = name
                result["rating"] = min(5,rate)
                result['nearest'] = supermarkets
                result["latitude"] =latitude
                result["longitude"] = longitude
                tup = convert_to_grid(latitude,longitude)
                result["latitude_grid"] = tup[0]
                result["longitude_grid"] = tup[1]
                add_new_location(result)
                results.append(result)
                # print('my result: ',result)
        # print(type(results), results)
        return Response(json.dumps(results),  mimetype='application/json')
    except Exception as ex:
        return {'Error':{ex} }
@app.route('/prediction/',methods=['GET','POST'])
def rate_prediction():
        try:
            data = request.get_json()
            locations = data["locations"]
            results = []
            for i,location in enumerate(locations):
                

                latitude = location["latitude"]
                longitude = location["longitude"]
                result,supermarkets = extractData(CURRENT_FEATURES,latitude,longitude)
                result_float = []
                for j in FEATURE_ORDER:
                    if j=='competitors': 
                        result_float.append(float(len(supermarkets)))
                        continue
                    result_float.append(float(result[j]))
                test_values = torch.tensor(result_float)
                # test_values = torch.tensor([1,9,7,3,3,0,2,28,4,145225,163770,75491,225517,7987,20])
                test_values=(test_values-mean)/std
                rate = (5- np.argmax(get_predict(test_values, model)))
                # print('my rate: ',rate)
                results = {'rating':rate,'log':1.3}
            return Response(json.dumps(results),  mimetype='application/json')
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

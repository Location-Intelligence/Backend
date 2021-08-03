# app.py
from flask import Flask, request, jsonify
import torch
import torch 
import googlemaps
from const import API_KEY,CURRENT_FEATURES
from locationAnalize import extractData
from flask_cors import CORS
# gmaps = googlemaps.Client(API_KEY)
app = Flask(__name__)
CORS(app)

@app.route('/rate/',methods=['GET','POST'])
def rate():
    data = [{'Females': 0,
  'Males': 0,
  'atm': 0,
  'bank': 0,
  'bus_station': 0,
  'church': 0,
  'gas_station': 0,
  'hospital': 0,
  'id': 1,
  'mosque': 0,
  'name': 'beklo bet',
  'pharmacy': 0,
  'rating': 0,
  'restaurant': 0,
  'school': 0,
  'train_station': 0,
  "name":"beklo bet",
  "latitude":38.72868186230371,
  "longtiude":38.72868186230371},
 {'Females': 167299,
  'Males': 148984,
  'atm': 1,
  'bank': 17,
  'bus_station': 0,
  'church': 5,
  'gas_station': 3,
  'hospital': 4,
  'id': 2,
  'mosque': 1,
  'name': 'urael',
  'pharmacy': 5,
  'rating': 5,
  'restaurant': 60,
  'school': 31,
  'train_station': 0,
  "name":"urael",
    "latitude":8.992021586554754,
    "longtiude":38.72606647576475}]
    return jsonify(data)
    # data = request.get_json()
    # locations = data["locations"]
    # results = []
    # # print("locations: ",locations)
    # for location in locations:
    #     id = location['id']
    #     name = location['name']
    #     latitude = location["latitude"]
    #     longtiude = location["longtiude"]
    #     # print('predicting id: ',id)
    #     result = extractData(CURRENT_FEATURES,latitude,longtiude)
    #     result_float = []
    #     for item in list(result.values()):
    #         result_float.append(float(item))
    #     test_values = torch.tensor([result_float])
    #     rate = torch.argmax(torch.softmax((test_values),1), axis = 1)
    #     result["id"] = id
    #     result["name"] = name
    #     result["rating"] = min(5,rate.item())
    #     results.append(result)
    # return jsonify(results)

def rate_prediction(datas):
        try:
            l = torch.load('tempmodel.h5')
            test_values = torch.tensor([[15.0,41.0,85.0,70.0,36.0,30.0,15.0,20.0,16.0,40.0,20.0,15000,15000]])
            result = torch.argmax(torch.softmax((test_values), 1), axis=1)
            return jsonify({'the rating':(result.item())})
        except:
            return {'data': 'An Error Occurred during fetching Api'}


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

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
# app.py
from flask import Flask, request, jsonify
import const
import torch
import torch 
import googlemaps
from const import API_KEY,CURRENT_FEATURES
from locationAnalize import extractData
from flask_cors import CORS
gmaps = googlemaps.Client(API_KEY)
app = Flask(__name__)
CORS(app)

@app.route('/rate/',methods=['GET','POST'])
def rate():
    try:
        data = request.get_json()
        locations = data["locations"]
        results = []
        # print("locations: ",locations)
        for location in locations:
            id_ = location['id']
            name = location['name']
            latitude = location["latitude"]
            longtiude = location["longitude"]
            # print('predicting id: ',id)
            result, supermarkets = extractData(CURRENT_FEATURES,latitude,longtiude)
            result_float = []
            for i in const.FEATURE_ORDER:
                if i=='competitors': continue
                result_float.append(float(result[i]))
            test_values = torch.tensor([result_float])
            rate = torch.argmax(torch.softmax(model(test_values),1), axis = 1)
            result["id"] = id_
            result["name"] = name
            result["rating"] = min(5,rate.item())
            result['nearest'] = supermarkets
            results.append(result)
        return jsonify(results)
    except Exception as ex:
        print(ex)
        return {'Error': 'An unexpected error occurred'}

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

if __name__ == '__main__':
    global model
    model = torch.load('tempmodel.h5')
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)

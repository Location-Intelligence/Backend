# app.py
from flask import Flask, request, jsonify
import torch
import torch 
import googlemaps
from const import API_KEY,CURRENT_FEATURES
from locationAnalize import extractData

gmaps = googlemaps.Client(API_KEY)
app = Flask(__name__)

@app.route('/rate/',methods=['GET','POST'])
def rate():
    data = request.get_json()
    latitude = data["latitude"]
    longtiude = data["longtiude"]
    result = extractData(CURRENT_FEATURES,latitude,longtiude)
    result_float = []
    for item in list(result.values()):
        result_float.append(float(item))
    test_values = torch.tensor([result_float])
    rate = torch.argmax(
    torch.softmax((test_values),1), axis = 1)
    result["rating"] = rate.item()
    return result

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
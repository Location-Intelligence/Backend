from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import torch

app = Flask(__name__)
api = Api(app)
CORS(app)

class predict (Resource):
    def get(self):
        try:
            l = torch.load('tempmodel.h5')
            test_values = torch.tensor([[15.0,41.0,85.0,70.0,36.0,30.0,15.0,20.0,16.0,40.0,20.0,15000,15000]])
            result = torch.argmax(torch.softmax(l(test_values), 1), axis=1)
            return jsonify({'rating':(result.item())})
        except:
            return {'data': 'An Error Occurred during fetching Api'}

api.add_resource(predict, '/predict')

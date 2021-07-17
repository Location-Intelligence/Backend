from flask import Flask
import torch
app = Flask(__name__)

@app.route('/')
def index():
  return 'Server Works!'
  
@app.route('/predict')
def predict():
  l = torch.load('tempmodel.h5')
  test_values = torch.tensor([[15.0,41.0,85.0,70.0,36.0,30.0,15.0,20.0,16.0,40.0,20.0,15000,15000]])
  result = torch.argmax(torch.softmax(l(test_values), 1), axis=1)
  return {'rating':(result.item())}
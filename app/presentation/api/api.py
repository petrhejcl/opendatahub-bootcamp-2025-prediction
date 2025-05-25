from flask import Flask, jsonify, request
from app.domain import make_prediction
from app.utils import load_data

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "OpenDataHub Parking Predictor API"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    prediction = make_prediction(data)
    return jsonify({"prediction": prediction})

def start_app():
    app.run(debug=True)

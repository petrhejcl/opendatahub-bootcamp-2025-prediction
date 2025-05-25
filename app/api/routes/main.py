# app/api/main.py
from flask import Flask, jsonify
from .routes.parking_routes import create_parking_routes
from ..services.parking_service import ParkingService


def create_app():
    app = Flask(__name__)

    # Initialize services
    parking_service = ParkingService()

    # Register routes
    parking_routes = create_parking_routes(parking_service)
    app.register_blueprint(parking_routes, url_prefix='/api')

    @app.route("/")
    def home():
        return jsonify({"message": "OpenDataHub Parking Predictor API"})

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"})

    return app


def start_app():
    app = create_app()
    app.run(debug=True)
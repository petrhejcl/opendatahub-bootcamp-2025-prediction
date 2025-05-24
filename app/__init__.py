from flask import Flask
from .presentation.api.parking_controller import parking_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(parking_bp, url_prefix='/api/v1')
    return app
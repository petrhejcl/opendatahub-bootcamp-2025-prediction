from flask import Blueprint, jsonify, request
from app.services.parking_service import ParkingService
from datetime import datetime

parking_bp = Blueprint('parking', __name__)
parking_service = ParkingService()


@parking_bp.route('/parking/<station_code>')
def get_parking_status(station_code):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    data = parking_service.get_parking_status(
        station_code,
        datetime.fromisoformat(start_date),
        datetime.fromisoformat(end_date)
    )

    return jsonify([vars(item) for item in data])
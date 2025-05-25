# app/api/routes/parking_routes.py
from flask import Blueprint, jsonify, request
from datetime import datetime
from ...services.parking_service import ParkingService

parking_bp = Blueprint('parking', __name__)


def create_parking_routes(parking_service: ParkingService):
    @parking_bp.route('/parking/<station_code>')
    def get_parking_status(station_code):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400

        try:
            data = parking_service.get_parking_status(
                station_code,
                datetime.fromisoformat(start_date),
                datetime.fromisoformat(end_date)
            )

            return jsonify([{
                'timestamp': item.timestamp.isoformat(),
                'free_spaces': item.free_spaces,
                'occupied_spaces': item.occupied_spaces,
                'station_code': item.station_code,
                'station_name': item.station_name
            } for item in data])

        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    return parking_bp
# main.py
from infrastructure.di_container import DIContainer
from presentation.app import ParkingApp


def main():
    # Initialize dependency injection container
    di_container = DIContainer()

    # Create application service
    app_service = di_container.create_application_service()

    # Create and run Streamlit app
    app = ParkingApp(app_service)
    app.run()


if __name__ == "__main__":
    main()

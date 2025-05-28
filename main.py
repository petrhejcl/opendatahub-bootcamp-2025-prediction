# main.py - Entry point dell'applicazione
from infrastructure.di_container import DIContainer
from presentation.app import ParkingApp


def main():
    """Entry point dell'applicazione"""
    # Crea il container DI e il servizio applicativo
    container = DIContainer()
    app_service = container.create_application_service()

    # Inizializza e avvia l'app
    app = ParkingApp(app_service)
    app.run()


if __name__ == "__main__":
    main()
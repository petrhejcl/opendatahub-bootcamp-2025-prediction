import streamlit as st
import logging
from pathlib import Path

from config.settings import get_config, UI_CONFIG
from core.logging_config import setup_logging
from ui.normal_version import NormalVersionPage
from ui.simplified_version import SimplifiedVersionPage
from core.exceptions import ParkingAppError

# Setup logging
logger = setup_logging()

# Load configuration
config = get_config()


def main():
    """Main application entry point."""
    try:
        # Configure Streamlit page
        st.set_page_config(
            page_title=config["ui"]["page_title"],
            layout=config["ui"]["page_layout"],
            initial_sidebar_state="collapsed"
        )

        # Main title
        st.title("🅿️ " + config["ui"]["page_title"])

        # Version toggle
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                simplified_mode = st.toggle(
                    label="🔄 Simplified Interface",
                    value=True,
                    help="Toggle between simplified map interface and full-featured version"
                )

        st.divider()

        # Initialize and render appropriate page
        if simplified_mode:
            page = SimplifiedVersionPage()
            page.render()
        else:
            page = NormalVersionPage()
            page.render()

        # Footer
        st.divider()
        with st.expander("ℹ️ About This Application", expanded=False):
            st.markdown("""
            **Parking Prediction System** - Powered by Machine Learning

            This application uses historical parking data to predict future availability:

            - **Simplified Version**: Quick predictions with interactive map
            - **Full Version**: Complete data analysis, model training, and performance monitoring

            **Features:**
            - Real-time data fetching from OpenDataHub
            - Advanced feature engineering with time-based patterns
            - Random Forest machine learning model
            - Interactive visualizations and performance metrics
            - Multi-threaded data processing for improved performance

            **Technology Stack:**
            - Frontend: Streamlit
            - ML: Scikit-learn (Random Forest)
            - Visualization: Plotly
            - Data Processing: Pandas, NumPy
            - Architecture: SOLID principles with dependency injection
            """)

    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"Application error: {e}")
        st.error("Please refresh the page or contact support if the problem persists.")


if __name__ == "__main__":
    main()

# services/service_manager.py
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from config.settings import get_config
from data.api_client import APIClient
from data.data_fetcher import ParkingDataFetcher
from data.data_repository import ParkingDataRepository
from ml.feature_engineering import FeatureEngineer
from ml.model_repository import ModelRepository
from ml.training_service import TrainingService
from ml.prediction_service import PredictionService
from visualization.data_plots import DataPlotService
from visualization.performance_plots import PerformancePlotService
from core.exceptions import ConfigurationError

logger = logging.getLogger("parking_prediction")


class ServiceManager:
    """
    Central service manager implementing dependency injection.
    Follows the Dependency Inversion Principle from SOLID.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the service manager.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self._services = {}
        self._initialized = False

    def initialize(self) -> None:
        """Initialize all services with proper dependency injection."""
        try:
            logger.info("Initializing services...")

            # Core services (no dependencies)
            self._services['api_client'] = APIClient(self.config['api'])
            self._services['data_repository'] = ParkingDataRepository(self.config['data'])
            self._services['model_repository'] = ModelRepository(self.config['ml'])

            # Data services
            self._services['data_fetcher'] = ParkingDataFetcher(
                self._services['api_client']
            )

            # ML services
            self._services['feature_engineer'] = FeatureEngineer(
                self.config['ml'],
                self.config['thread']
            )

            self._services['training_service'] = TrainingService(
                self.config['ml'],
                self._services['model_repository']
            )

            self._services['prediction_service'] = PredictionService(
                self.config['ml'],
                self._services['model_repository']
            )

            # Visualization services
            self._services['data_plot_service'] = DataPlotService()
            self._services['performance_plot_service'] = PerformancePlotService()

            self._initialized = True
            logger.info("All services initialized successfully")

        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            raise ConfigurationError(f"Failed to initialize services: {e}")

    def get_service(self, service_name: str) -> Any:
        """
        Get a service instance.

        Args:
            service_name: Name of the service

        Returns:
            Service instance

        Raises:
            ConfigurationError: If service not found or not initialized
        """
        if not self._initialized:
            self.initialize()

        if service_name not in self._services:
            raise ConfigurationError(f"Service '{service_name}' not found")

        return self._services[service_name]

    def get_api_client(self) -> APIClient:
        """Get API client service."""
        return self.get_service('api_client')

    def get_data_fetcher(self) -> ParkingDataFetcher:
        """Get data fetcher service."""
        return self.get_service('data_fetcher')

    def get_data_repository(self) -> ParkingDataRepository:
        """Get data repository service."""
        return self.get_service('data_repository')

    def get_feature_engineer(self) -> FeatureEngineer:
        """Get feature engineering service."""
        return self.get_service('feature_engineer')

    def get_model_repository(self) -> ModelRepository:
        """Get model repository service."""
        return self.get_service('model_repository')

    def get_training_service(self) -> TrainingService:
        """Get training service."""
        return self.get_service('training_service')

    def get_prediction_service(self) -> PredictionService:
        """Get prediction service."""
        return self.get_service('prediction_service')

    def get_data_plot_service(self) -> DataPlotService:
        """Get data plotting service."""
        return self.get_service('data_plot_service')

    def get_performance_plot_service(self) -> PerformancePlotService:
        """Get performance plotting service."""
        return self.get_service('performance_plot_service')

    def health_check(self) -> Dict[str, bool]:
        """
        Perform health check on all services.

        Returns:
            Dictionary with service health status
        """
        if not self._initialized:
            return {"status": "not_initialized"}

        health_status = {}

        try:
            # Check API client
            health_status['api_client'] = True  # Basic check

            # Check data repository
            data_repo = self.get_data_repository()
            health_status['data_repository'] = True

            # Check model repository
            model_repo = self.get_model_repository()
            health_status['model_repository'] = model_repo.model_exists()

            # Check prediction service
            pred_service = self.get_prediction_service()
            health_status['prediction_service'] = pred_service.is_model_available()

            logger.info(f"Health check completed: {health_status}")
            return health_status

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}


# Global service manager instance
service_manager = ServiceManager()


def get_service_manager() -> ServiceManager:
    """
    Get the global service manager instance.

    Returns:
        ServiceManager instance
    """
    return service_manager
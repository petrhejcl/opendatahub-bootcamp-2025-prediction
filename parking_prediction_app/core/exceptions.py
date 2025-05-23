class ParkingAppError(Exception):
    """Base exception class for parking prediction application."""
    pass

class APIError(ParkingAppError):
    """Exception raised for errors in the API communication."""
    pass

class AuthenticationError(APIError):
    """Exception raised for authentication failures."""
    pass

class DataError(ParkingAppError):
    """Exception raised for data processing errors."""
    pass

class ModelError(ParkingAppError):
    """Exception raised for model-related errors."""
    pass

class ConfigurationError(ParkingAppError):
    """Exception raised for configuration issues."""
    pass
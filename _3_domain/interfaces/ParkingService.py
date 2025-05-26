from _3_domain.interfaces import ITokenProvider
from _3_domain.interfaces import IDataRepository
from _3_domain.interfaces import IModelPersistence
from _4_infrastructure.data_fetcher import ApiTokenProvider


class ParkingService:
    def __init__(self,
                 token_provider: ITokenProvider,
                 data_repository: IDataRepository,
                 model_persistence: IModelPersistence):
        self._token_provider = token_provider
        self._data_repository = data_repository
        self._model_persistence = model_persistence

def create_parking_service():
    token_provider = ApiTokenProvider()
    return ParkingService(token_provider)

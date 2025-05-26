from abc import ABC, abstractmethod

class ITokenProvider(ABC):
    @abstractmethod
    def get_token(self, client_id: str, client_secret: str) -> str:
        pass

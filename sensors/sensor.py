from abc import ABC, abstractmethod
 
class Sensor(ABC):
 
    @abstractmethod
    def capture_data(self):
        pass

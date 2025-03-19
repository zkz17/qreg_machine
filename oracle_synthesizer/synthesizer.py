from abc import ABC, abstractmethod

# Oracle Synthesizer abstract class
class Synthesizer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def synthesize(self, code):
        pass
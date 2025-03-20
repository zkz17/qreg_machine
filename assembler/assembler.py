from abc import ABC, abstractmethod

# QINS Assembler abstract class
class Assembler(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def assemble(self, inst):
        pass

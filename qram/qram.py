from abc import ABC, abstractmethod

# Quantem Random Access Memory abstract class
class QRAM(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def swap_load(self, target_reg, addr_reg):
        pass

    @abstractmethod
    def fetch(self, target_reg, addr_reg):
        pass
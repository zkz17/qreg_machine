from qram.bbqram import BucketBrigadeQRAM, Router
from config import *
from qiskit import QuantumCircuit, QuantumRegister

class RegisterManager(BucketBrigadeQRAM):
    def __init__(self):
        names = [SYSREG_NAME_PC, SYSREG_NAME_RO, SYSREG_NAME_SP] + USRREG_NAME

        self.depth = 1
        self.size = 2
        while self.size < len(names):
            self.depth += 1
            self.size <<= 1

        for i in range(len(names), self.size):
            names.append(f'unused_memcell_{i}')

        self.circ = QuantumCircuit()
        self.top = QuantumRegister(1, 'router_root')
        self.circ.add_register(self.top)
        self.circ.x(self.top[0])

        self.root = Router(self.circ)
        self.memcells = self.root.create_children(self.depth - 1, names=names)
from qram.qram import QRAM
from qiskit import QuantumRegister
from config import MEM_SIZE, WORD_LENGTH

# Memory Cell class
class MemCell:
    def __init__(self, circuit, pos=0, control=None):
        self.pos = pos
        self.control = control
        self.circ = circuit

        self.reg = QuantumRegister(WORD_LENGTH, f'mem_cell_{self.pos}')
        self.circ.add_register(self.reg)

    def connect_circuit(self, circuit):
        self.circ = circuit

    def insert_register(self, circuit):
        circuit.add_register(self.reg)

    def controlled_swap(self, target_reg):
        for i in range(WORD_LENGTH):
            self.circ.cswap(self.control, self.reg[i], target_reg[i])

    def controlled_fetch(self, target_reg):
        for i in range(WORD_LENGTH):
            self.circ.ccx(self.control, self.reg[i], target_reg[i])

# Quantum Router class
class Router:
    def __init__(self, circuit, id=1, pos=0, incoming=None):
        self.input = incoming
        self.id = id    # identifier
        self.pos = pos  # position in memory

        self.reg = QuantumRegister(3, f'router_{id}')
        self.control = self.reg[0]
        self.left = self.reg[1]
        self.right = self.reg[2]

        self.circ = circuit
        self.circ.add_register(self.reg)

        self.lc = self.rc = None

    def connect_circuit(self, circuit):
        self.circ = circuit
        self.lc.connect_circuit(circuit)
        self.rc.connect_circuit(circuit)

    def insert_register(self, circuit):
        circuit.add_register(self.reg)
        self.lc.insert_register(circuit)
        self.rc.insert_register(circuit)

    def connect_mem_cell(self):
        self.lc = MemCell(self.circ, pos=(self.pos<<1), control=self.left)
        self.rc = MemCell(self.circ, pos=(self.pos<<1)+1, control=self.right)
        return [self.lc, self.rc]

    def create_children(self, depth):
        if depth:
            self.lc = Router(self.circ, id=(self.id<<1), pos=(self.pos<<1), incoming=self.left)
            self.rc = Router(self.circ, id=(self.id<<1)+1, pos=(self.pos<<1)+1, incoming=self.right)
            llst = self.lc.create_children(depth - 1)
            rlst = self.rc.create_children(depth - 1)
            return llst + rlst
        else:
            return self.connect_mem_cell()

    def set_incoming(self, incoming):
        self.input = incoming

    def set_control(self):
        self.circ.swap(self.control, self.input)

    def apply_control_circuit(self):
        self.circ.cswap(self.control, self.input, self.rc.control)
        self.circ.x(self.control)
        self.circ.cswap(self.control, self.input, self.lc.control)
        self.circ.x(self.control)

    def apply_routing_circuit(self):
        self.circ.cswap(self.control, self.input, self.right)
        self.circ.x(self.control)
        self.circ.cswap(self.control, self.input, self.left)
        self.circ.x(self.control)

    def route(self, depth):
        if depth > 1:
            self.apply_routing_circuit()
            self.lc.route(depth - 1)
            self.rc.route(depth - 1)
        elif depth == 1:
            if isinstance(self.lc, Router):
                self.apply_control_circuit()
            else:
                self.apply_routing_circuit()
        else:
            self.set_control()

    def undo_control_circuit(self):
        self.circ.x(self.control)
        self.circ.cswap(self.control, self.input, self.lc.control)
        self.circ.x(self.control)
        self.circ.cswap(self.control, self.input, self.rc.control)

    def undo_routing_circuit(self):
        self.circ.x(self.control)
        self.circ.cswap(self.control, self.input, self.left)
        self.circ.x(self.control)
        self.circ.cswap(self.control, self.input, self.right)

    def unroute(self, depth):
        if depth > 1:
            self.lc.unroute(depth - 1)
            self.rc.unroute(depth - 1)
            self.undo_routing_circuit()
        elif depth == 1:
            if isinstance(self.lc, Router):
                self.undo_control_circuit()
            else:
                self.undo_routing_circuit()
        else:
            self.set_control()

# Bucket-Brigade QRAM class
class BucketBrigadeQRAM(QRAM):
    # Giovannetti, V., Lloyd, S., & Maccone, L. (2008). Quantum random access memory. Physical review letters, 100(16), 160501.
    def __init__(self, circuit):
        self.depth = 1
        self.size = 2
        while self.size < MEM_SIZE:
            self.depth += 1
            self.size <<= 1

        self.circ = circuit
        self.top = QuantumRegister(1, 'router_root')
        self.circ.add_register(self.top)
        self.circ.x(self.top[0])

        self.root = Router(self.circ)
        self.memcells = self.root.create_children(self.depth - 1)

    def connect_circuit(self, circuit):
        self.insert_register(circuit)
        self.circ = circuit
        self.root.connect_circuit(circuit)

    def insert_register(self, circuit):
        if not circuit.has_register(self.top):
            circuit.add_register(self.top)
            self.root.insert_register(circuit)

    def load(self, target_reg, addr_reg):
        self.load_address(addr_reg)
        self.retrieve_data_swap(target_reg)
        self.unload_address(addr_reg)
    
    def fetch(self, target_reg, addr_reg):
        self.load_address(addr_reg)
        self.retrieve_data_fetch(target_reg)
        self.unload_address(addr_reg)

    def load_address(self, addr_reg):
        for i in range(self.depth):
            self.root.set_incoming(addr_reg[i - self.depth])
            self.root.route(i)

        self.root.set_incoming(self.top[0])
        self.root.route(self.depth)

    def unload_address(self, addr_reg):
        self.root.set_incoming(self.top[0])
        self.root.unroute(self.depth)

        for i in reversed(range(self.depth)):
            self.root.set_incoming(addr_reg[i - self.depth])
            self.root.unroute(i)

    def retrieve_data_swap(self, target_reg):
        for cell in self.memcells:
            cell.controlled_swap(target_reg)

    def retrieve_data_fetch(self, target_reg):
        for cell in self.memcells:
            cell.controlled_fetch(target_reg)
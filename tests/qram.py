from qiskit import QuantumCircuit, QuantumRegister
from config import print_config, set_config

def test_bbqram():
    set_config('MEM_SIZE', 8)
    set_config('WORD_LENGTH', 2)

    from qram.bbqram import BucketBrigadeQRAM
    addr = QuantumRegister(5, 'addr')
    tgt1 = QuantumRegister(2, 'tgt1')
    tgt2 = QuantumRegister(2, 'tgt2')

    circ = QuantumCircuit(addr, tgt1, tgt2)
    circ.x(addr[2])
    circ.x(addr[4])

    mem = BucketBrigadeQRAM(circ)
    mem.load(tgt1, addr)
    
    with open('circuit.txt', 'w', encoding='utf-8') as f:
        f.write(circ.draw(output='text').single_string())


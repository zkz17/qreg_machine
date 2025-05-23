from qiskit import QuantumCircuit, QuantumRegister

def test_all():
    test_rev_add()
    test_rev_increment()
    test_rev_decrement()

def test_rev_add():
    from utils.rev_circuit import rev_add

    qreg1 = QuantumRegister(3, 'qreg1')
    qreg2 = QuantumRegister(3, 'qreg2')
    qreg3 = QuantumRegister(3, 'qreg3')

    circ = QuantumCircuit(qreg1, qreg2, qreg3)
    rev_add(circ, qreg1, qreg2)
    rev_add(circ, qreg3, qreg2)
    
    with open('test_rev_add.txt', 'w', encoding='utf-8') as f:
        f.write(circ.draw(output='text').single_string())

def test_rev_increment():
    from utils.rev_circuit import rev_increment

    qreg1 = QuantumRegister(3, 'qreg1')
    qreg2 = QuantumRegister(4, 'qreg2')

    circ = QuantumCircuit(qreg1, qreg2)
    rev_increment(circ, qreg1)
    rev_increment(circ, qreg2)
    
    with open('test_rev_increment.txt', 'w', encoding='utf-8') as f:
        f.write(circ.draw(output='text').single_string())

def test_rev_decrement():
    from utils.rev_circuit import rev_decrement

    qreg1 = QuantumRegister(3, 'qreg1')
    qreg2 = QuantumRegister(4, 'qreg2')

    circ = QuantumCircuit(qreg1, qreg2)
    rev_decrement(circ, qreg1)
    rev_decrement(circ, qreg2)
    
    with open('test_rev_decrement.txt', 'w', encoding='utf-8') as f:
        f.write(circ.draw(output='text').single_string())
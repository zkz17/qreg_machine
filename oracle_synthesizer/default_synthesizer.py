from oracle_synthesizer.synthesizer import Synthesizer
from qiskit import QuantumCircuit, QuantumRegister
from bitarray import util

# Default Oracle Synthesizer
class DefaultSynthesizer(Synthesizer):
    def __init__(self):
        self.pc_numqubit = 10
        self.ins_numqubit = 20

    # Apply a cascade of multi-controlled Toffoli gates. 
    def synthesize(self, codelist):
        pc = QuantumRegister(self.pc_numqubit, name='pc')
        ins = QuantumRegister(self.ins_numqubit, name='ins')
        circuit = QuantumCircuit(pc, ins)

        line = 0
        for code in codelist.codelist:
            ctrl_str = util.int2ba(line, length=self.pc_numqubit).to01()
            x_circuit = self.get_x_circuit(code, ins)
            controlled_x_circuit = x_circuit.control(self.pc_numqubit, ctrl_state=ctrl_str)
            circuit.compose(controlled_x_circuit, qubits=pc[:]+ins[:], inplace=True)

            line += 1
            #if line >= 10: break

        return circuit
    
    def get_x_circuit(self, code, ins):
        x_circuit = QuantumCircuit(ins)
        for i in range(self.ins_numqubit):
            if code.code[i]: x_circuit.x(ins[i])
        return x_circuit
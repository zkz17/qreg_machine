from qiskit import QuantumCircuit, QuantumRegister
from config import *
from utils.rev_circuit import rev_add, rev_increment, rev_decrement

# Quantum Register Machine class
class QRegMachine:
    def __init__(self):
        self.pc   = QuantumRegister(WORD_LENGTH           , SYSREG_NAME_PC  )
        self.ins  = QuantumRegister(COMPRESSED_CODE_LENGTH, SYSREG_NAME_INS )
        self.br   = QuantumRegister(WORD_LENGTH           , SYSREG_NAME_BR  )
        self.ro   = QuantumRegister(WORD_LENGTH           , SYSREG_NAME_RO  )
        self.qifw = QuantumRegister(WORD_LENGTH           , SYSREG_NAME_QIFW)
        self.qifv = QuantumRegister(WORD_LENGTH           , SYSREG_NAME_QIFV)
        self.wait = QuantumRegister(1                     , SYSREG_NAME_WAIT)
        self.sp   = QuantumRegister(WORD_LENGTH           , SYSREG_NAME_SP  )

        self.circ = QuantumCircuit()

        self.mem = self.mem_init()
        self.mem_regs = self.circ.qregs.copy()
        #print([qubit for qreg in self.mem_regs for qubit in qreg])

        self.circ.add_register(self.pc)
        self.circ.add_register(self.ins)
        self.circ.add_register(self.br)
        self.circ.add_register(self.ro)
        self.circ.add_register(self.qifw)
        self.circ.add_register(self.qifv)
        self.circ.add_register(self.sp)

        self.udec = self.circ.copy(name='Udec')
        self.uexe = self.circ.copy(name='Uexe')

        self.circ.add_register(self.wait)

        self.ufet = None
        self.ucyc = self.circ.copy(name='Ucyc')

        # qubit mapping for circuit composition
        self.mem_qubits = [qubit for qreg in self.mem_regs for qubit in qreg]
        self.udec_qubits = self.mem_qubits + self.pc[:] + self.ins[:] + self.br[:] + self.ro[:] + self.qifw[:] + self.qifv[:] + self.sp[:]

    def execute(self, instlist):
        # Partial Evaluation.
        qif_table, execution_time = self.partial_evaluate(instlist)

        # Preprocess.
        codelist = self.assemble(instlist)
        #codelist.print()

        self.synthesize_ufet(codelist)
        self.synthesize_udec()
        self.synthesize_uexe()
        self.synthesize_ucyc()

        # Execution.
        for t in range(execution_time):
            self.apply_ucyc()
            break

        # Output.
        with open('circuit.txt', 'w', encoding='utf-8') as f:
            f.write(self.circ.draw(output='text').single_string())
        
    def assemble(self, instlist, compress=True):
        assembler = None
        if compress:
            from assembler.compressed_assembler import CompressedAssembler
            assembler = CompressedAssembler()
        else:
            from assembler.generic_assembler import GenericAssembler
            assembler = GenericAssembler()

        codelist = assembler.assemble(instlist)

        return codelist
    
    def apply_ufet(self, circuit):
        assert(circuit.has_register(self.pc))
        assert(circuit.has_register(self.ins))

        circuit.compose(self.ufet, qubits=self.pc[:]+self.ins[:], inplace=True, wrap=True)

    def apply_ucyc(self):
        self.circ.compose(self.ucyc, qubits=self.wait[:] + self.udec_qubits, inplace=True, wrap=True)

    def apply_udec(self, circuit):
        assert(circuit.has_register(self.pc))
        assert(circuit.has_register(self.ins))
        assert(circuit.has_register(self.br))
        assert(circuit.has_register(self.ro))
        assert(circuit.has_register(self.qifw))
        assert(circuit.has_register(self.qifv))
        assert(circuit.has_register(self.sp))
        for qreg in self.mem_regs:
            assert(circuit.has_register(qreg))

        circuit.compose(self.udec, qubits=self.udec_qubits, inplace=True, wrap=True)

    def synthesize_ufet(self, codelist):
        from oracle_synthesizer.default_synthesizer import DefaultSynthesizer

        synthesizer = DefaultSynthesizer()
        self.ufet = synthesizer.synthesize(codelist)

    def synthesize_ucyc(self):
        self.ucyc.clear()
        
        # 1. set wait flag
        self.ucyc.x(self.qifw)
        self.ucyc.mcx(self.qifw, self.wait)
        self.ucyc.x(self.qifw)
        self.ucyc.x(self.wait)

        # 2. execute or wait
        controlled_uexe = self.uexe.control(1, ctrl_state='0', annotated=True)

        decr = QuantumCircuit(self.qifw, name='decrement')
        rev_decrement(decr, self.qifw)
        controlled_decr = decr.control(1, ctrl_state='1')

        self.ucyc.compose(controlled_uexe, qubits=self.wait[:] + self.udec_qubits, inplace=True)
        self.ucyc.compose(controlled_decr, qubits=self.wait[:] + self.qifw[:], inplace=True)

        # 3. clear wait flag
        # TODO

        with open('ucyc.txt', 'w', encoding='utf-8') as f:
            f.write(self.ucyc.draw(output='text').single_string())

    def synthesize_uexe(self):
        self.uexe.clear()
        self.apply_ufet(self.uexe)
        self.apply_udec(self.uexe)
        self.apply_ufet(self.uexe)

        rev_add(self.uexe, self.pc, self.br)

        incr = QuantumCircuit(self.pc, name='increment')
        rev_increment(incr, self.pc)
        controlled_incr = incr.control(WORD_LENGTH, ctrl_state='0'*WORD_LENGTH)
        self.uexe.compose(controlled_incr, qubits=self.br[:]+self.pc[:], inplace=True)

        with open('uexe.txt', 'w', encoding='utf-8') as f:
            f.write(self.uexe.draw(output='text').single_string())

    def synthesize_udec(self):
        self.udec.clear()
        # TODO
    
    def partial_evaluate(self, instlist):
        from utils.qif_flow import QifFlow
        qif_table = QifFlow()

        for t in range(PRACTICAL_RUNNING_TIME):
            qif_table.execute(instlist)
            if qif_table.terminated(): return qif_table, t + 1

        raise Exception(r'Execution time out!!!')

    def mem_init(self):
        from qram.bbqram import BucketBrigadeQRAM
        return BucketBrigadeQRAM(self.circ)
    
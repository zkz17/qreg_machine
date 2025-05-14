from qiskit import QuantumCircuit, QuantumRegister
from config import *

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
        self.circ.add_register(self.pc)
        self.circ.add_register(self.ins)
        self.circ.add_register(self.br)
        self.circ.add_register(self.ro)
        self.circ.add_register(self.qifw)
        self.circ.add_register(self.qifv)
        self.circ.add_register(self.wait)
        self.circ.add_register(self.sp)

        self.ufet = None

    def execute(self, instlist):
        # Partial Evaluation. 
        qif_table, execution_time = self.partial_evaluate(instlist)

        # Preprocess. 
        mem = self.mem_init()

        codelist = self.assemble(instlist)
        codelist.print()

        self.synthesize_ufet(codelist)
        #with open('circuit.txt', 'w', encoding='utf-8') as f:
        #    f.write(ufet.draw(output='text').single_string())

        # Execution. 
        for t in range(execution_time):
            # 1. set wait flag
            self.set_wait_flag()

            # 2. execute or wait
            ## TODO

            # 3. clear wait flag
            self.clear_wait_flag()

            break
        print(self.circ)
        
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
    
    def apply_ufet(self):
        self.circ.compose(self.ufet, qubits=self.pc[:]+self.ins[:], inplace=True)

    def synthesize_ufet(self, codelist):
        from oracle_synthesizer.default_synthesizer import DefaultSynthesizer

        synthesizer = DefaultSynthesizer()
        self.ufet = synthesizer.synthesize(codelist)
    
    def partial_evaluate(self, instlist):
        from utils.qif_flow import QifFlow
        qif_table = QifFlow()

        for t in range(PRACTICAL_RUNNING_TIME):
            qif_table.execute(instlist)
            if qif_table.terminated(): return qif_table, t + 1

        raise Exception(r'Execution time out!!!')

    def mem_init(self):
        from qram.bbqram import BucketBrigadeQRAM
        mem = BucketBrigadeQRAM(self.circ)
        return mem
    
    def execute_or_wait(self):
        pass
    
    def clear_wait_flag(self):
        self.set_wait_flag()
    
    def set_wait_flag(self):
        self.circ.x(self.qifw)
        self.circ.mcx(self.qifw, self.wait)
        self.circ.x(self.qifw)
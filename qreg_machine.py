from config import PRACTICAL_RUNNING_TIME

# Quantum Register Machine class
class QRegMachine:
    def __init__(self):
        pass

    def execute(self, instlist):
        qif_table, execution_time = self.partial_evaluate(instlist)

        codelist = self.assemble(instlist)
        codelist.print()

        oracle = self.synthesize(codelist)
        #with open('circuit.txt', 'w', encoding='utf-8') as f:
        #    f.write(oracle.draw(output='text').single_string())

        ## TODO
        
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

    def synthesize(self, codelist):
        from oracle_synthesizer.default_synthesizer import DefaultSynthesizer

        synthesizer = DefaultSynthesizer()
        return synthesizer.synthesize(codelist)
    
    def partial_evaluate(self, instlist):
        from utils.qif_flow import QifFlow
        qif_table = QifFlow()

        for t in range(PRACTICAL_RUNNING_TIME):
            qif_table.execute(instlist)
            if qif_table.terminated(): return qif_table, t + 1

        raise Exception(r'Execution time out!!!')
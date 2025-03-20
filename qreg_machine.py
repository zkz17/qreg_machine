# Quantum Register Machine class
class QRegMachine:
    def __init__(self):
        pass

    def execute(self, text):
        self.partial_evaluation(text)

        codelist = self.assemble(text)
        codelist.print()

        oracle = self.synthesize(codelist)
        #with open('circuit.txt', 'w', encoding='utf-8') as f:
        #    f.write(oracle.draw(output='text').single_string())
        ## TODO
        
    def assemble(self, text, compress=True):
        assembler = None
        if compress:
            from assembler.compressed_assembler import CompressedAssembler
            assembler = CompressedAssembler()
        else:
            from assembler.generic_assembler import GenericAssembler
            assembler = GenericAssembler()

        codelist = assembler.assemble(text)

        return codelist

    def synthesize(self, codelist):
        from oracle_synthesizer.default_synthesizer import DefaultSynthesizer

        synthesizer = DefaultSynthesizer()
        return synthesizer.synthesize(codelist)
    
    def partial_evaluation(self, text):
        pass
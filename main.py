import sys

help_info = \
'''
Usage: python main.py <option> <arg>
'''

def assemble(text, compress=True):
    assembler = None
    if compress:
        from assembler.assembler import CompressedAssembler
        assembler = CompressedAssembler()
    else:
        from assembler.assembler import GenericAssembler
        assembler = GenericAssembler()

    codelist = assembler.assemble(text)

    return codelist

def synthesize(codelist):
    from oracle_synthesizer.default_synthesizer import DefaultSynthesizer

    synthesizer = DefaultSynthesizer()
    return synthesizer.synthesize(codelist)

def execute(text):
    codelist = assemble(text)
    codelist.print()

    oracle = synthesize(codelist)
    #with open('circuit.txt', 'w', encoding='utf-8') as f:
    #    f.write(oracle.draw(output='text').single_string())
    ## TODO

def main():
    args = sys.argv

    if len(args) == 1:
        print("Quantum Register Machine Version 0.1.0")
    elif len(args) >= 2:
        option = args[1]
        if option == "help":
            print(help_info)
        elif option == "compile":
            if len(args) == 2:
                raise Exception(r'Input file path missing. ')
            
            input_path = args[2]
            if not input_path.endswith('.rqcpp'):
                raise Exception(r'Unexpected input file format! Expected: *.rqcpp, Received: ' + input_path)
            
            if len(args) >= 4:
                output_path = args[3]
                if not output_path.endswith('.qins'):
                    raise Exception(r'Unexpected output file format! Expected: *.qins, Received: ' + output_path)
            else:
                output_path = input_path[:-6] + '.qins'

            f = open(input_path, mode='r')
            text = f.read()
            f.close()

            import os
            submodule_path = os.path.join(os.path.dirname(__file__), 'rqcpp_compiler')
            if submodule_path not in sys.path:
                sys.path.append(submodule_path)

            from rqcpp_compiler.rqcpp import compile
            code = compile(text, False)
            code.print()
            code.write(output_path)
        elif option == "execute":
            if len(args) == 2:
                raise Exception(r'Input file path missing. ')
            
            input_path = args[2]
            if not input_path.endswith('.qins'):
                raise Exception(r'Unexpected input file format! Expected: *.rqcpp, Received: ' + input_path)
            
            f = open(input_path, mode='r')
            text = f.readlines()
            f.close()

            ## TODO
            execute(text)

if __name__ == "__main__":
    main()
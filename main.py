import sys

help_info = \
'''
Usage: python main.py <option> <arg>
'''

def decode(text, compress=True):
    decoder = None
    if compress:
        from decoder.decoder import CompressedDecoder
        decoder = CompressedDecoder()
    else:
        from decoder.decoder import GenericDecoder
        decoder = GenericDecoder()

    code = decoder.decode(text)

    return code

def execute(text):
    code = decode(text)
    code.print()

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
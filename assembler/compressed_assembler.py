from assembler.assembler import Assembler
from utils.machine_code import MachineCode, MachineCodeList
import re

# Compressed Assembler class
class CompressedAssembler(Assembler):
    optype = {
        'i': ['ld', 'xori', 'addi', 'subi', 'bra', 'bez', 'bnz'],
        'r': ['ldr', 'fetr', 'swap', 'add', 'sub', 'neg', 'swbr', 'qif', 'fiq', 'start', 'finish'],
        'uni': ['uni'],
        'unib': ['unib'],
        'ari': ['ari'],
        'arib': ['arib']
    }
    opcode_i = { 'ld': 0, 'xori': 1, 'addi': 2, 'subi': 3, 'bra': 4, 'bez': 5, 'bnz': 6 }
    opcode_r = { 'ldr': 0, 'fetr': 1, 'swap': 2, 'add': 3, 'sub': 4, 'neg': 5, 'swbr': 6, 'qif': 7,
                 'fiq': 8, 'start': 9, 'finish': 10 }
    gate_1 = { 'H': 0, 'T': 1, 'Tdg': 2, 'S': 3, 'Sdg': 4, 'X': 5, 'Y': 6, 'Z': 7, 
               'Rx': 8, 'Ry': 9, 'Rz': 10, 'GPhase': 11 }
    gate_2 = { 'CX': 11, 'CY': 12, 'CZ': 13, 'Swap': 14 }
    op_1 = { 'sin': 15, 'cos': 16, 'tan': 17, 'asin': 18, 'acos': 19, 'atan': 20, 'sqrt': 21, 'not': 22,
             'log2': 23 }
    op_2 = { '+': 0, '-': 1, '*': 2, '/': 3, 'and': 4, 'or': 5, '==': 6, '!=': 7,
             '>': 8, '>=': 9, '<': 10, '<=': 11, '<<': 12, '>>': 13, '^': 14, '%': 15,
             'max': 16, 'min': 17 }
    reg2int = { 'pc': 0, 'ro': 1, 'sp':2, 'r1': 3, 'r2': 44, 'r3': 5, 'r4': 6, 'r5': 7, 
                'inst': 8, 'br': 9, 'qifw': 10, 'qifv': 11, 'wait': 12, 'r6': 13, 'r7': 14, 'r8': 15 }

    def __init__(self):
        pass

    def assemble(self, instlist):
        codelist = MachineCodeList()
        for op, args in instlist:
            for type, oplist in CompressedAssembler.optype.items():
                if op in oplist:
                    method_name = f'assemble_optype_{type}'
                    method = getattr(self, method_name, self.assemble_optype_default)
                    codelist.append(method(op, args))
        return codelist

    def assemble_optype_i(self, op, args):
        code = MachineCode()
        
        code.set_opcode(0)
        code.set_opcode_i(CompressedAssembler.opcode_i[op])
        if op == 'bra': 
            code.set_imm(int(args[0]))
        else: 
            code.set_reg(CompressedAssembler.reg2int[args[0]])
            code.set_imm(int(args[1]))

        return code

    def assemble_optype_r(self, op, args):
        code = MachineCode()

        code.set_opcode(2)
        code.set_opcode_r(CompressedAssembler.opcode_r[op])
        if op in ['start', 'finish', 'qif', 'fiq']:
            pass
        elif op in ['swbr', 'neg']:
            code.set_reg1(CompressedAssembler.reg2int[args[0]])
        else:
            code.set_reg1(CompressedAssembler.reg2int[args[0]])
            code.set_reg2(CompressedAssembler.reg2int[args[1]])

        return code

    def assemble_optype_uni(self, op, args):
        code = MachineCode()

        code.set_opcode(1)
        code.set_gate_1(CompressedAssembler.gate_1[args[0]])
        if op in ['Rx', 'Ry', 'Rz', "GPhase"]:
            code.set_imm(int(args[1]))

        return code

    def assemble_optype_unib(self, op, args):
        code = MachineCode()

        code.set_opcode(2)
        code.set_gate_2(CompressedAssembler.gate_2[args[0]])
        code.set_reg1(CompressedAssembler.reg2int[args[1]])
        code.set_reg2(CompressedAssembler.reg2int[args[2]])

        return code

    def assemble_optype_ari(self, op, args):
        code = MachineCode()

        code.set_opcode(2)
        code.set_op_1(CompressedAssembler.op_1[args[0]])
        code.set_reg1(CompressedAssembler.reg2int[args[1]])
        code.set_reg2(CompressedAssembler.reg2int[args[2]])

        return code

    def assemble_optype_arib(self, op, args):
        code = MachineCode()

        code.set_opcode(3)
        code.set_op_2(CompressedAssembler.op_2[args[0]])
        code.set_reg1(CompressedAssembler.reg2int[args[1]])
        code.set_reg2(CompressedAssembler.reg2int[args[2]])
        code.set_reg3(CompressedAssembler.reg2int[args[3]])
        
        return code

    def assemble_optype_default(self, op, args):
        raise Exception(f'Unrecognized instruction type {op}')
from bitarray import bitarray, util

# Machine Code class
class MachineCode:
    def __init__(self, code_length=20):
        self.code = bitarray(code_length)
        self.imm_length = code_length - 9

    def set_opcode(self, opcode):
        self.code[:2] = util.int2ba(opcode, length=2)

    def set_opcode_i(self, opcode_i):
        self.code[2:6] = util.int2ba(opcode_i, length=4)

    def set_opcode_r(self, opcode_r):
        self.code[2:7] = util.int2ba(opcode_r, length=5)

    def set_gate_1(self, gate):
        self.code[2:6] = util.int2ba(gate, length=4)

    def set_gate_2(self, gate):
        self.code[2:7] = util.int2ba(gate, length=5)

    def set_op_1(self, op):
        self.code[2:7] = util.int2ba(op, length=5)

    def set_op_2(self, op):
        self.code[2:7] = util.int2ba(op, length=5)

    def set_reg(self, reg):
        self.code[6:10] = util.int2ba(reg, length=4)

    def set_reg1(self, reg):
        self.code[7:11] = util.int2ba(reg, length=4)

    def set_reg2(self, reg):
        self.code[11:15] = util.int2ba(reg, length=4)

    def set_reg3(self, reg):
        self.code[15:19] = util.int2ba(reg, length=4)

    def set_imm(self, imm):
        if imm < 0: imm += (1 << self.imm_length)
        self.code[10:] = util.int2ba(imm, length=self.imm_length)

    def print(self):
        print(self.code.to01())

# Machine Code List class
class MachineCodeList:
    def __init__(self, code_length=19):
        self.code_length = code_length
        self.codelist = []

    def append(self, code):
        self.codelist.append(code)

    def print(self):
        for code in self.codelist:
            code.print()
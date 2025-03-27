from bitarray import bitarray, util
from config import *

# Machine Code class
class MachineCode:
    def __init__(self, code_length=COMPRESSED_CODE_LENGTH):
        self.code = bitarray(code_length)

    def set_opcode(self, opcode):
        self.code[OPCODE_START_COMPRESSED : OPCODE_END_COMPRESSED] = util.int2ba(opcode, length=OPCODE_LENGTH_COMPRESSED)

    def set_opcode_i(self, opcode_i):
        self.code[OPCODEI_START_COMPRESSED : OPCODEI_END_COMPRESSED] = util.int2ba(opcode_i, length=OPCODEI_LENGTH_COMPRESSED)

    def set_opcode_r(self, opcode_r):
        self.code[OPCODER_START_COMPRESSED : OPCODER_END_COMPRESSED] = util.int2ba(opcode_r, length=OPCODER_LENGTH_COMPRESSED)

    def set_gate_1(self, gate):
        self.code[GATE1_START_COMPRESSED : GATE1_END_COMPRESSED] = util.int2ba(gate, length=GATE1_LENGTH_COMPRESSED)

    def set_gate_2(self, gate):
        self.code[GATE2_START_COMPRESSED : GATE2_END_COMPRESSED] = util.int2ba(gate, length=GATE2_LENGTH_COMPRESSED)

    def set_op_1(self, op):
        self.code[OP1_START_COMPRESSED : OP1_END_COMPRESSED] = util.int2ba(op, length=OP1_LENGTH_COMPRESSED)

    def set_op_2(self, op):
        self.code[OP2_START_COMPRESSED : OP2_END_COMPRESSED] = util.int2ba(op, length=OP2_LENGTH_COMPRESSED)

    def set_reg(self, reg):
        self.code[REG_START_COMPRESSED : REG_END_COMPRESSED] = util.int2ba(reg, length=REGSEC_LENGTH)

    def set_reg1(self, reg):
        self.code[REG1_START_COMPRESSED : REG1_END_COMPRESSED] = util.int2ba(reg, length=REGSEC_LENGTH)

    def set_reg2(self, reg):
        self.code[REG2_START_COMPRESSED:REG2_END_COMPRESSED] = util.int2ba(reg, length=REGSEC_LENGTH)

    def set_reg3(self, reg):
        self.code[REG3_START_COMPRESSED:REG3_END_COMPRESSED] = util.int2ba(reg, length=REGSEC_LENGTH)

    def set_imm(self, imm):
        if imm < 0: imm += (1 << IMMSEC_LENGTH_COMPRESSED)
        self.code[IMM_START_COMPRESSED:IMM_END_COMPRESSED] = util.int2ba(imm, length=IMMSEC_LENGTH_COMPRESSED)

    def print(self):
        print(self.code.to01())

# Machine Code List class
class MachineCodeList:
    def __init__(self, code_length=COMPRESSED_CODE_LENGTH):
        self.code_length = code_length
        self.codelist = []

    def append(self, code):
        self.codelist.append(code)

    def print(self):
        for code in self.codelist:
            code.print()
# qreg = qreg + 1
def rev_increment(circ, qreg):
    for i in range(1, len(qreg)):
        circ.mcx(qreg[i:len(qreg)], qreg[i-1])
    circ.x(qreg[-1])

# qreg = qreg - 1
def rev_decrement(circ, qreg):
    circ.x(qreg[-1])
    for i in reversed(range(1, len(qreg))):
        circ.mcx(qreg[i:len(qreg)], qreg[i-1])

# qreg1 = qreg1 + qreg2
def rev_add(circ, qreg1, qreg2):
    assert(len(qreg1) == len(qreg2))
    for i in range(len(qreg1)):
        if i: circ.ccx(qreg1[-i-1], qreg2[-i-1], qreg1[-i])
        circ.cx(qreg2[-i-1], qreg1[-i-1])
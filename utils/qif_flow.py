# Qif Table Node class
class QifFlow:
    # Quantum Register Simulator class
    class QRegSimulator:
        def __init__(self, regs=None):
            if not regs:
                self.pc   = 0
                self.br   = 0
                self.ro   = 0
                self.sp   = 1000
                self.r1   = 0
                self.r2   = 0
                self.r3   = 0
                self.r4   = 0
                self.r5   = 0
                self.r6   = 0
                self.r7   = 0
                self.r8   = 0
                self.stack= []
                self.mem  = {}
            else:
                self.setall(regs)

        def setall(self, regs):
            self.pc   = regs.pc
            self.br   = regs.br
            self.ro   = regs.ro
            self.sp   = regs.sp
            self.r1   = regs.r1
            self.r2   = regs.r2
            self.r3   = regs.r3
            self.r4   = regs.r4
            self.r5   = regs.r5
            self.r6   = regs.r6
            self.r7   = regs.r7
            self.r8   = regs.r8
            self.stack= []
            self.mem  = {}
            for item in regs.stack:
                self.stack.append(item)
            for addr, value in regs.mem.items():
                self.mem[addr] = value

        def get(self, regname):
            return getattr(self, regname)
        
        def set(self, regname, value):
            setattr(self, regname, value)

        def mem_get(self, addr):
            if addr in self.mem: return self.mem[addr]
            else:
                self.mem[addr] = 0
                return 0
            
        def mem_set(self, addr, val):
            self.mem[addr] = val

        def print(self):
            print(self.__dict__)

    def __init__(self, id=0, regs=None, pred=None, fc_parent=None, lc_parent=None):
        self.empty = True
        self.finished = False
        self.wait_counter = 0
        
        self.id = id # 1 for fc1, 2 for fc2, 3 for next
        self.regs = self.QRegSimulator(regs)

        self.next = None
        self.pred = pred

        self.first_child1 = None
        self.first_child2 = None
        self.fc_parent = fc_parent

        self.last_child1 = None
        self.last_child2 = None
        self.lc_parent = lc_parent

    def execute(self, instlist):
        if self.next: self.next.execute(instlist)
        elif self.finished: self.wait_counter += 1
        elif self.empty: self.simulate(instlist[self.regs.pc])
        else:
            self.last_child1.execute(instlist)
            self.last_child2.execute(instlist)

            if self.last_child1.terminated() and self.last_child2.terminated(): self.merge()

    def terminated(self):
        if not self.next: return self.finished
        return self.next.terminated()
    
    def create_next(self):
        self.finished = True
        self.next = QifFlow(id=(self.id<<2)+3, regs=self.regs, pred=self, lc_parent=self.lc_parent)

        id = self.id
        while id & 1 and id & 2:
            id >>= 2
        if id & 1:   # self == self.lc_parent.last_child1
            self.lc_parent.last_child1 = self.next
        elif id & 2: # self == self.lc_parent.last_child2
            self.lc_parent.last_child2 = self.next
        self.lc_parent = None

    def fork(self):
        self.empty = False
        self.first_child1 = self.last_child1 = QifFlow(id=(self.id<<2)+1, regs=self.regs, fc_parent=self, lc_parent=self)
        self.first_child2 = self.last_child2 = QifFlow(id=(self.id<<2)+2, regs=self.regs, fc_parent=self, lc_parent=self)

    def merge(self):
        self.create_next()
        self.next.regs.set('pc', self.first_child1.regs.get('pc'))

    def branch(self):
        if not self.empty:
            self.first_child1.branch()
            self.first_child2.branch()
        elif self.regs.br:
            self.regs.pc += self.regs.br
        else:
            self.regs.pc += 1

    def simulate(self, inst):
        op, args = inst
        
        method_name = f'simulate_{op}'
        method = getattr(self, method_name, self.simulate_default)
        method(args)

        self.branch()

        #print(f'thread {self.id}: ', op, args)
        #self.regs.print()

    def simulate_default(self, args):
        pass

    def simulate_finish(self, args):
        self.finished = True
    
    def simulate_qif(self, args):
        self.fork()
        self.first_child1.regs.set(args[0], 0)
        self.first_child1.regs.set(args[0], 1)

    def simulate_fiq(self, args):
        self.finished = True

    def simulate_bra(self, args):
        self.regs.br += int(args[0])

    def simulate_bnz(self, args):
        if self.regs.get(args[0]): self.regs.br += int(args[1])

    def simulate_bez(self, args):
        if not self.regs.get(args[0]): self.regs.br += int(args[1])

    def simulate_swbr(self, args):
        br_val = self.regs.br
        reg_val = self.regs.get(args[0])
        self.regs.set('br', reg_val)
        self.regs.set(args[0], br_val)

    def simulate_xori(self, args):
        reg_val = self.regs.get(args[0])
        self.regs.set(args[0], reg_val ^ int(args[1]))

    def simulate_addi(self, args):
        reg_val = self.regs.get(args[0])
        self.regs.set(args[0], reg_val + int(args[1]))

    def simulate_subi(self, args):
        reg_val = self.regs.get(args[0])
        self.regs.set(args[0], reg_val - int(args[1]))

    def simulate_ld(self, args):
        reg_val, mem_addr = self.regs.get(args[0]), int(args[1])
        mem_val = self.regs.mem_get(mem_addr)
        self.regs.set(args[0], mem_val)
        self.regs.mem_set(mem_addr, reg_val)

    def simulate_ldr(self, args):
        reg_val, mem_addr = self.regs.get(args[0]), self.regs.get(args[1])
        mem_val = self.regs.mem_get(mem_addr)
        self.regs.set(args[0], mem_val)
        self.regs.mem_set(mem_addr, reg_val)

    def simulate_fetr(self, args):
        reg_val, mem_addr = self.regs.get(args[0]), self.regs.get(args[1])
        mem_val = self.regs.mem_get(mem_addr)
        self.regs.set(args[0], reg_val ^ mem_val)

    def simulate_swap(self, args):
        reg_val1, reg_val2 = self.regs.get(args[0]), self.regs.get(args[1])
        self.regs.set(args[0], reg_val2)
        self.regs.set(args[1], reg_val1)

    def simulate_add(self, args):
        reg_val1, reg_val2 = self.regs.get(args[0]), self.regs.get(args[1])
        self.regs.set(args[0], reg_val1 + reg_val2)

    def simulate_sub(self, args):
        reg_val1, reg_val2 = self.regs.get(args[0]), self.regs.get(args[1])
        self.regs.set(args[0], reg_val1 - reg_val2)

    def simulate_neg(self, args):
        reg_val = self.regs.get(args[0])
        self.regs.set(args[0], -reg_val)

    def simulate_ari(self, args):
        op, regs = args[0], args[1:]

    def simulate_arib(self, args):
        op, regs = args[0], args[1:]
        reg_val1, reg_val2 = self.regs.get(regs[1]), self.regs.get(regs[2])

        op_result = 0
        if op == '==':
            op_result = int(reg_val1 == reg_val2)
        elif op == '!=':
            op_result = int(reg_val1 != reg_val2)
        elif op == '<':
            op_result = int(reg_val1 < reg_val2)
        elif op == '<=':
            op_result = int(reg_val1 <= reg_val2)
        elif op == '>':
            op_result = int(reg_val1 > reg_val2)
        elif op == '>=':
            op_result = int(reg_val1 >= reg_val2)
        elif op == '+':
            op_result = reg_val1 + reg_val2
        elif op == '-':
            op_result = reg_val1 - reg_val2
        elif op == '*':
            op_result = reg_val1 * reg_val2
        elif op == '/':
            op_result = reg_val1 / reg_val2

        self.regs.set(regs[0], op_result)

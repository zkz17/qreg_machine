# Qif Table Node class
class QifFlow:
    # Quantum Register Simulator class
    class QRegSimulator:
        def __init__(self, regs=None):
            if not regs:
                self.pc   = 0
                self.br   = 1
                self.ro   = 0
                self.qifw = 0
                self.qifv = 0
                self.sp   = 0
                self.wait = 0
            else:
                self.set(regs)

        def set(self, regs):
            self.pc   = regs.pc
            self.br   = regs.br
            self.ro   = regs.ro
            self.qifw = regs.qifw
            self.qifv = regs.qifv
            self.sp   = regs.sp
            self.wait = regs.wait

    def __init__(self, regs=None, fc_parent=None, lc_parent=None):
        self.empty = True
        self.finished = False
        self.regs = self.QRegSimulator(regs)
        self.wait_counter = 0
        self.t = 0

        self.next = None
        self.pred = None

        self.first_child1 = None
        self.first_child2 = None
        self.fc_parent = fc_parent

        self.last_child1 = None
        self.last_child2 = None
        self.lc_parent = lc_parent

    def execute(self, instlist):
        if self.next: self.next.execute(instlist)
        elif self.empty: self.simulate(instlist[self.regs.pc])
        else:
            self.last_child1.execute(instlist)
            self.last_child1.execute(instlist)

    def terminated(self):
        if not self.next: return self.finished
        return self.next.terminated()

    def fork(self):
        self.empty = False
        self.first_child1 = self.last_child1 = QifFlow(regs=self.regs, fc_parent=self, lc_parent=self)
        self.first_child2 = self.last_child2 = QifFlow(regs=self.regs, fc_parent=self, lc_parent=self)

    def simulate(self, inst):
        op, args = inst
        print(op, args)
        method_name = f'simluate_{op}'
        method = getattr(self, method_name, self.simulate_default)
        method(args)

    def simluate_default(self, args):
        pass
    
    def simluate_qif(self, args):
        pass

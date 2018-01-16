class LineBuffer:
    def __init__(self):
        self.active = None
        self.lines = []
        self.height = 10
        self.offset = 0
        self.max_length = 0


    def add_line(self, line, color):
        self.lines.append((line,color))
        if not self.active:
            self.active = self.lines[0]

    def increase(self, cnt=1):
        if len(self.lines) == 0:
            return
        if self.active != self.lines[-1]:
            idx = self.lines.index(self.active)
            self.active = self.lines[idx+1]
            if (idx+1) > (self.offset+self.height-1):
                self.offset += 1


    def decrease(self, cnt=1):
        if len(self.lines) == 0:
            return
        if self.active != self.lines[0]:
            idx = self.lines.index(self.active)
            self.active = self.lines[idx-1]
            if (idx-1) < self.offset:
                self.offset -= 1

    def get_lines(self):
        if self.active == None and len(self.lines) > 0:
            self.active = self.lines[0]
        ret = []
        for i in range(0,self.height):
            idx = i+self.offset
            if idx < len(self.lines):
                active = False
                if self.lines[idx] == self.active:
                    active = True
                l = self.lines[idx][0]
                if len(l) < self.max_length:
                    l += (self.max_length-len(l)) * " "
                ret.append((l, active, self.lines[idx][1]))
            else:
                ret.append((' '*self.max_length,False, 0))
        return ret


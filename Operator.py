import time, itertools


def getAutomata(lines):
    it = iter(lines)
    automata = dict()
    automata['Sigma'] = next(it).split('=')[1].split()
    automata['Q'] = next(it).split('=')[1].split()
    automata['start'] = next(it).split('=')[1].strip()
    automata['F'] = next(it).split('=')[1].split()
    automata['delta'] = list()
    for line in it:
        if not line:
            break
        s, c, t = line.split()
        automata['delta'].append([s, c, t])

    return automata


def parseFile(fname):
    fin = []
    fout = []
    with open(fname + '.in') as f:
        lines = [line.rstrip('\n') for line in f]


    ind = [i for i, x in enumerate(lines) if x == ""] # find the empty lines
    auto = lines[:ind[0]] # get the automata
    strings = lines[ind[0]+1:] # get the strings
    # print(auto)
    # print(strings)

    with open(fname + '.out') as f:
        lines = [line.rstrip('\n') for line in f]

    # print(len(strings), len(lines))
    # print(lines)
    # print(ind)
    return auto, strings, lines


def remove_unreachable(automata):
    states = set(automata['Q'])
    states.remove(automata['start'])
    states = states.difference(automata['F'])
    states = states.difference(set([d[2] for d in automata['delta']]))
    # states = states.difference(set([d[2] for d in automata['delta']]))

    automata['delta'] = [d for d in automata['delta'] if d[0] not in states and d[2] not in states]
    automata['Q'] = [d for d in automata['Q'] if d not in states]
    if len(states) > 0:
        # print('Removed unreachable states:', states)
        remove_unreachable(automata)
    return

def rename_automata(automata):
    # Rename states
    d = {}
    for i in range(0, len(automata['Q'])):
        d[automata['Q'][i]] = i
        automata['Q'][i] = i

    # Rename start state
    automata['start'] = d[automata['start']]

    # Rename final states
    for i in range(0, len(automata['F'])):
        automata['F'][i] = d[automata['F'][i]]

    # Rename transitions
    for i in range(0, len(automata['delta'])):
        automata['delta'][i][0] = d[automata['delta'][i][0]]
        automata['delta'][i][2] = d[automata['delta'][i][2]]

    return

class Operator:
    def __init__(self):
        self.vbv_mem = {}
        self.mbv_mem = {}
        self.mbm_mem = {}

        self.mbm_s = {}
        self.pf = {}
        self.pb = {}
        self.n = 0
        return

    # def vbv_step(self, a, b):
    #     if a in self.vbv_mem:
    #         if b in self.vbv_mem:
    #             return self.vbv_mem[(a, b)]
    #         else:
    #             for i, j in zip(a, b):
    #                 if i & j:
    #                     self.vbv_mem[(a, b)] = 1
    #                     self.vbv_mem[(b, a)] = 1
    #                     self.vbv_mem[a] = 1
    #                     self.vbv_mem[b] = 1
    #                     return 1
    #             self.vbv_mem[a] = 1
    #             self.vbv_mem[b] = 1
    #             self.vbv_mem[(a, b)] = 0
    #             self.vbv_mem[(b, a)] = 0
    #             return 0
    #     else:
    #         for i, j in zip(a, b):
    #             if i & j:
    #                 self.vbv_mem[(a, b)] = 1
    #                 self.vbv_mem[(b, a)] = 1
    #                 self.vbv_mem[a] = 1
    #                 self.vbv_mem[b] = 1
    #                 return 1
    #         self.vbv_mem[a] = 1
    #         self.vbv_mem[b] = 1
    #         self.vbv_mem[(a, b)] = 0
    #         self.vbv_mem[(b, a)] = 0
    #         return 0

    def vbv_step(self, a, b):
        key = (a, b)
        if key in self.vbv_mem:
            return self.vbv_mem[key]
        else:
            if not any(a) or not any(b):
                self.vbv_mem[key] = 0
                return 0
            else:
                for i, j in zip(a, b):
                    if i & j:
                        self.vbv_mem[key] = 1
                        return 1
                self.vbv_mem[key] = 0
                return 0

    def mti(self, a):
        return set([(ix, iy) for ix, row in enumerate(a) for iy, i in enumerate(row) if i == 1])

    # def itm(self, a):

    def vti(self, a):
        return set([i for i, x in enumerate(a) if x == 1])

    def itm(self, a):
        r = [[0 for j in range(self.n)] for i in range(self.n)]
        for i in a:
            r[i[0]][i[1]] = 1
        return r


    # def mtd(self, a):
    #     d = dict()
    #     return dict([(ix, iy) for ix, row in enumerate(a) for iy, i in enumerate(row) if i == 0])

    # def itv(self, a):
    def mbv_d(self, a, b):
        nset = set()
        [nset.add(a[ind]) for ind in b if ind in a]
        return nset


    def mbv_sparse(self, a, b):
        # print(a, b)
        nset = set()
        [nset.add(row[0]) for row in a if row[1] in b]
        return nset

    # def mbv_sparse2(self, a, b):
    #     return set([row[0] for row in a if row[1] in b])


    def mbv(self, A, b):
        # return self.mbv_mem.setdefault((tuple(tuple(a) for a in X), tuple(b)), [self.vbv_step(X_row, b) for X_row in X])
        ta = tuple(tuple(a) for a in A)
        tb = tuple(b)
        key = (ta, tb)
        if key not in self.mbv_mem:
            self.mbv_mem[key] = [self.vbv_step(row, tb) for row in ta]
        # print(self.mbv_mem[key])
        # print('returning:', self.mbv_mem[key])
        return self.mbv_mem[key]

    # def mbm_d(self, A, B):
    #     ndict = dict()
    #     for k, v in A.items():
    #         if v in B:
    #             ndict[k] = v
    #     [nset.add(a) for a in A for b in B ]
    #     return

    # def mbm_sparse(self, X, Y):
    #     nset = set()
    #     [nset.add((row[0], col[1])) for row in X for col in Y if row[1] == col[0]]
    #     return nset

    def mbm_sparse(self, X, Y):
        # matX = self.itm(X)
        # start = time.time()
        tX = tuple(sorted(list(X)))
        if (X | Y) == X:
            tY = tX
        else:
            tY = tuple(sorted(list(Y)))
        key = (tX, tY)

        if key not in self.mbm_s:
            if tX not in self.pb:
                xPointer = dict()
                for row in X:
                    if row[1] not in xPointer:
                        xPointer[row[1]] = set()
                    xPointer[row[1]].add(row[0])
                self.pb[tX] = xPointer

            if tY not in self.pf:
                yPointer = dict()
                for row in Y:
                    if row[0] not in yPointer:
                        yPointer[row[0]] = set()
                    yPointer[row[0]].add(row[1])
                self.pf[tY] = yPointer

            K = set(self.pb[tX].keys()) & set(self.pf[tY].keys())

            x = set()
            [[x.add((i, j)) for i in self.pb[tX][k] for j in self.pf[tY][k]] for k in K]
            self.mbm_s[key] = x

        # diff = time.time() - start
        # if len(X) > 3000:
            # print(X)
            # print(Y)
            # print(len(X), diff)
        # start = time.time()
        # m1 = self.itm(X)
        # m2 = self.itm(Y)
        # m3 = self.mbm(m1, m2)
        # r = self.mti(m3)
        # diff2 = time.time() - start
        # if r != x:
        #     print('error')
            # print('sparse is faster')
        return self.mbm_s[key]

    # Comparison implementation
    # def mbm_sparse(self, X, Y):
    #     comps = [r[0] for r in Y]
    #     return  set([(row[0], col[1]) for row in X for col in Y if row[1] == col[0]])

    # Dictionary implementation

    def mbm(self, X, Y):
        # return self.mbm_mem.setdefault((tuple(tuple(a) for a in X), tuple(tuple(a) for a in Y)), [[self.vbv_step(X_row, Y_col) for Y_col in zip(*Y)] for X_row in X])
        tupX = tuple(tuple(a) for a in X)
        tupY = tuple(tuple(a) for a in Y)
        key = (tupX, tupY)
        if key not in self.mbm_mem:
            # print(self.mti(tupX))
            # print(self.mti(tupY))
            self.mbm_mem[key] = [[self.vbv_step(X_row, Y_col) for Y_col in zip(*tupY)] for X_row in tupX]
            # comp1 = self.mti(self.mbm_mem[key])
            # # print(comp1)
            # import time
            # start = time.time()
            # for i in range(0, 5):
            #     comp2 = self.mbm_sparse(self.mti(tupX), self.mti(tupY))
            # end = time.time()
            # diff = end - start
            # print('1', end - start)
            # start = time.time()
            # for i in range(0, 5):
            #     comp2 = self.mbm_sparse2(self.mti(tupX), self.mti(tupY))
            # end = time.time()
            # diff2 = end - start
            # print('2', end - start)
            # global full
            #
            # if diff > diff2:
            #     full += 1
            # elif diff < diff2:
            #     full -= 1
            # print(full)
            # if comp1 != comp2:
            #     print("asd")

        return self.mbm_mem[key]

# full = 0
from Operator import *
import math

def getTransitionMatrix(symbols, states, delta):
    deltaMatrix = {}
    for sym in symbols:
        deltaMatrix[sym] = [[0 for j in range(len(states))] for i in range(len(states))]

    # for d in automata['delta']:
    #     deltaMatrix[d[1]][int(d[0])][int(d[2])] = 1
    for d in delta:
        # print(d[0], d[1], d[2])
        # print(states.index(d[2]), states.index(d[0]), d)
        # pre = deltaMatrix[d[1]][states.index(d[2])][states.index(d[0])]
        deltaMatrix[d[1]][states.index(d[2])][states.index(d[0])] = 1
        # print(pre, deltaMatrix[d[1]][states.index(d[2])][states.index(d[0])])
        # print(d)

    transitions = {}
    for d in deltaMatrix:
        transitions[d] = {}
        transitions[d][1] = mti(deltaMatrix[d])

    # print(transitions)
    return transitions

def mti(a):
    return set([(ix,iy) for ix, row in enumerate(a) for iy, i in enumerate(row) if i == 1])


def splitPowers(num):
    powers = []
    while num != 0:
        powers.append(num & -num)
        num = num & (num - 1)
    return powers

class NFA:
    def __init__(self, automata):
        # Preprocess
        automata['delta'] = [list(d) for d in automata['delta']]
        remove_unreachable(automata)
        rename_automata(automata)
        self.automata = automata

        # Initialise NFA
        self.states = tuple(automata['Q'])
        self.symbols = tuple(automata['Sigma'])
        self.start = set([automata['start']])
        self.final = set(automata['F']) if type(automata['F']) == list else set(list(automata['F']))

        self.sTransitions = getTransitionMatrix(self.symbols, self.states, automata['delta'])

        self.Operator = Operator()
        self.Operator.n = len(self.states)

    # # Vectorise states
    # def s2v(self, s):
    #     return [1 if i in s else 0 for i in self.states]
    #
    # # Devectoreise states
    # def v2s(self, v):
    #     return set([state for i, state in enumerate(self.states) if v[i] == 1])

    # def setState(self, s):
    #     self.s = self.s2v(s)
    #
    # # Starts NFA
    # def start_nfa(self):
    #     self.setState(self.start)
    #
    # def get_state(self):
    #     return self.v2s(self.s)

    def setState(self, s):
        if type(s) is not set():
            self.s = set(s)
        else:
            self.s = s

    def start_nfa(self):
        self.setState(self.start)

    def get_state(self):
        return self.s

    def pstate(self):
        print(self.get_state())

    def step(self, char):
        # print(char)
        # print(self.sTransitions[char][1])
        self.s = self.Operator.mbv_sparse(self.sTransitions[char][1], self.s)
        # print(char, self.s)

    # def step(self, char):
    #     self.s = self.Operator.mbv_sparse(self.sTransitions[char][1], self.s)
    #
    # def steps(self, chars):
    #     for c in chars:
    #         self.step(c)

    def printST(self):
        for p in self.sTransitions:
            print(p, end=": ")
            for k in self.sTransitions[p]:
                print(k, end=" ")
        print(" ")
        return


    # def printTransitions(self):
    #     for p in self.transitions:
    #         print(p, end=": ")
    #         for k in self.transitions[p]:
    #             print(k, end=" ")
    #     print(" ")
    #     return
    #
    # def getMappings(self):
    #     for i in self.states:
    #         print(i, end=" ")
    #         for j in self.symbols:
    #             self.setState(i)
    #             # print(i, j)
    #             self.step(j)
    #             print(self.get_state(), end=" ")
    #         print(" ")

    def createPowers(self, upToPowerN, sym):
        for i in range(1, upToPowerN + 1):
            ind1 = 2 ** i
            ind2 = 2 ** (i - 1)
            if sym not in self.sTransitions:
                self.sTransitions[sym] = {}
            if ind1 not in self.sTransitions[sym]:
                self.sTransitions[sym][ind1] = self.Operator.mbm_sparse(self.sTransitions[sym][ind2], self.sTransitions[sym][ind2])

                # We can expand some strings
                if ind1 <= 10:
                    nstr = sym * ind1
                    if len(nstr) <= 10:
                        if nstr not in self.sTransitions:
                            self.sTransitions[nstr] = {}
                        if 1 not in self.sTransitions[nstr]:
                            self.sTransitions[nstr][1] = self.sTransitions[sym][ind1]
        return


    def addPowers(self, l, sym):
        tot = 0
        for p in l:
            tot += p
            if tot not in self.sTransitions[sym]:
                self.sTransitions[sym][tot] = self.Operator.mbm_sparse(self.sTransitions[sym][p], self.sTransitions[sym][tot - p])
                # We expand some strings
                if tot <= 10:
                    nstr = sym * tot
                    if len(nstr) <= 10:
                        if nstr not in self.sTransitions:
                            self.sTransitions[nstr] = {}
                        if 1 not in self.sTransitions[nstr]:
                            self.sTransitions[nstr][1] = self.sTransitions[sym][tot]

        return

    def dealWithPowers(self, sym, n):
        sumOfN = splitPowers(n)
        power = int(math.log(max(sumOfN), 2))
        self.createPowers(power, sym)
        self.addPowers(sumOfN, sym)
        return

    def stringConstructor(self):
        for i, c in enumerate(self.csym):
            cString = self.csym[:i + 1]
            if cString not in self.sTransitions:
                self.sTransitions[cString] = {}
                # print(mti(self.transitions[cString[:-1]][1]))
                # print(mti(self.transitions[cString[c]][1]))
                self.sTransitions[cString][1] = self.Operator.mbm_sparse(self.sTransitions[cString[:-1]][1], self.sTransitions[c][1])
                # print(mti(self.transitions[cString][1]))
        return

    def symbolManager(self):
        slist = []
        for s in self.csym:
            if len(slist) == 0:
                slist.append([s, 1])
            else:
                if s == slist[-1][0]:
                    slist[-1][1] += 1
                else:
                    slist.append([s, 1])

        for p in slist:
            if p[1] != 1:
                # print(p)
                self.dealWithPowers(p[0], p[1])


        l = slist
        while len(l) > 1:
            # print(l)
            for i in range(0, len(l) - 1):
                if i % 2 == 0:
                    s1 = l[i][0]
                    s2 = l[i + 1][0]
                    v1 = l[i][1]
                    v2 = l[i + 1][1]
                    ns = s1 * v1 + s2 * v2
                    nv = 1
                    if ns not in self.sTransitions:
                        self.sTransitions[ns] = {}
                    if nv not in self.sTransitions[ns]:
                        # m1 = mti(self.transitions[s1][v1])
                        # m2 = mti(self.transitions[s2][v2])

                        self.sTransitions[ns][nv] = self.Operator.mbm_sparse(self.sTransitions[s1][v1], self.sTransitions[s2][v2])
                        # comp = mti(self.transitions[ns][nv])
                        # print(comp)
                        # m3 = self.Operator.mbm_sparse(m1, m2)
                        # if set(comp) != set(m3):
                        #     print(comp)
                        #     print(m3)
                    l[i][0] = ns
                    l[i][1] = nv

            for i in reversed(range(0, len(l))):
                if i % 2 == 1:
                    l.pop(i)

        return

    def stepsMat(self, pair):
        self.csym = pair[0][::-1]
        self.n = int(pair[1])

        self.symbolManager()
        # self.stringConstructor()
        self.dealWithPowers(self.csym, self.n)


        self.s = self.Operator.mbv_sparse(self.sTransitions[self.csym][self.n], self.s)


    def get_result(self):
        return self.s & self.final

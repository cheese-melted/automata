from nfaSparseMatrix import *
import pparser

def decide(automata, rows):
    nfa = NFA(automata)
    for row in rows:
        nfa.start_nfa()

        for s in row:
            nfa.stepsMat(s)

        if nfa.get_result():
            print('True')
        else:
            print('False')
    return


if __name__ == '__main__':
    # read an automata via stdin. See parser.py for details on the returned object
    automata = pparser.parse_fa()
    # read a list of implicit strings via stdin. See parser.py for details on the returned object.
    rows = pparser.parse_strings()
    decide(automata, rows)

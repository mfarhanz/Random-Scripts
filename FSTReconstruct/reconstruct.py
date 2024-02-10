#########################################################
##  CS 4750 (Fall 2023), Assignment #2                 ##
##   Script File Name: reconstruct.py                  ##
##       Student Name: Mohammed Farhan                 ##
##         Login Name: mfarhan                         ##
##              MUN #: 201852902                       ##
#########################################################

import sys

def readFST(filename):
    fst, ptr = {}, 1
    with open(filename) as file:
        lines = [list(line.strip().split(" ")) for line in file]
    fst['num_states'] = lines[0][0]
    fst['symbols'] = lines[0][1]
    fst['states'] = {}
    for i in range(1, len(lines)):
        if lines[i][0].isdigit():
            fst['states'][lines[i][0]] = {'type': lines[i][1], 'transitions': []}
            ptr = 1
        else:
            fst['states'][lines[i-ptr][0]]['transitions'].append(tuple(x for x in lines[i]))
            ptr += 1
    return fst

def composeFST(F1, F2):
    F , ctr = {'num_states': None, 'symbols': F1['symbols'], 'states': {}}, 0
    for p in F1['states']:
        for q in F2['states']:
            F['states'][(p,q)] = {'type': 'F' if F1['states'][p]['type'] == 'F' and F2['states'][q]['type'] == 'F'
                                            else 'N',
                                  'transitions': []}
    for p in F1['states']:
        for q in F2['states']:
            for x in F1['states'][p]['transitions']:
                for y in F2['states'][q]['transitions']:
                    if x[1] == y[0]:
                        F['states'][(p, q)]['transitions'].append((x[0], y[1], (x[2], y[2])))
                    if x[1] == '-' and y[0] != '-':
                        break
                    if x[1] != '-' and y[0] == '-':
                        break
                if x[1] == '-' and y[0] != '-':
                    break
                if x[1] != '-' and y[0] == '-':
                    break
            if x[1] == '-' and y[0] != '-':
                F['states'][(p, q)]['transitions'].append((x[0], '-', (x[2], q)))
            if x[1] != '-' and y[0] == '-':
                F['states'][(p, q)]['transitions'].append(('-', y[1], (p, y[2])))
                break
    for s in F['states']:
        ctr += 1
    F['num_states'] = ctr
    return F

def reconstructUpper(l, u='', q=None, F=None):
    if l == '':
        if F['states'][q]['type'] == 'F':
            return [u]
        else:
            return
    else:
        ret = []
        if q is None:
            q = list(F['states'])[0]
        for s in F['states']:
            for t in F['states'][s]['transitions']:
                if l == t[0] + l[1:]:
                    ret += reconstructUpper(l[1:], u+t[1], t[2], F)
        return set(ret)

def reconstructLower(u, l='', q=None, F=None):
    if u == '':
        if F['states'][q]['type'] == 'F':
            return [l]
        else:
            return
    else:
        ret = []
        if q is None:
            q = list(F['states'])[0]
        for s in F['states']:
            for t in F['states'][s]['transitions']:
                if u == t[1] + u[1:]:
                    ret += reconstructUpper(u[1:], l+t[0], t[2], F)
        return set(ret)

if len(sys.argv) < 4:
    print("usage: python reconstruct.py surface/lexical wlf/wsf F1 F2 ... Fn")
    sys.exit(1)
with open(sys.argv[2]) as file:
    forms = [form.rstrip() for form in file]
fst_list, ctr = [], 0
for i in range(3, len(sys.argv)):
    fst_list.append(readFST(sys.argv[i]))
fst = fst_list[0]
for i in range(1, len(fst_list)):
    fst = composeFST(fst, fst_list[i])
for s in fst['states']:
    for t in fst['states'][s]['transitions']:
        ctr += 1
if sys.argv[1] == 'surface' and sys.argv[2][-3:] == 'lex':
    print("Composed FST has %s states and %s transitions" % (fst['num_states'], ctr))
    for lex in forms:
        print("Lexical form: ", lex)
        print("Reconstructed surface forms: ")
        try:
            srf_forms = reconstructUpper(lex, F=fst)
        except TypeError:
            print("------------------------")
            continue
        for srf in srf_forms:
            print(srf)
        print("------------------------")
elif sys.argv[1] == 'lexical' and sys.argv[2][-3:] == 'srf':
    print("Composed FST has %s states and %s transitions" % (fst['num_states'], ctr))
    for srf in forms:
        print("Surface form: ", srf)
        print("Reconstructed lexical forms: ")
        try:
            lex_forms = reconstructLower(srf, F=fst)
        except TypeError:
            print("------------------------")
            continue
        for lex in lex_forms:
            print(lex)
        print("------------------------")
else:
    print("usage: python reconstruct.py surface/lexical wlf/wsf F1 F2 ... Fn")
    sys.exit(1)

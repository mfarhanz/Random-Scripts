import sys

def print_table(tbl, rev=False):
    if rev: tbl = tbl[::-1]
    for row in tbl:  # pretty printing table
        for col in row:
            if len(col): spaces = int(28/len(col) ** 1/3)
            else: spaces = int(40 ** 1/3)
            print(" " * int(spaces/2), col, end=" " * spaces)
        print()

def create_ruleset(rules):
    ruleset = {}
    for rule in rules:
        if rule[0] not in ruleset:
            ruleset[rule[0]] = []
        if len(rule) == 3:
            ruleset[rule[0]].append((rule[2],))
        elif len(rule) == 4:
            ruleset[rule[0]].append((rule[2], rule[3]))
    return ruleset

def check_single_rules(nonterm, ruleset):
    ret = []
    for key, rules in ruleset.items():
        if (nonterm,) in rules:
            temp = check_single_rules(key, ruleset)
            if isinstance(temp,list):
                for nt in temp:
                    ret.append(nt)
        else:
            if nonterm not in ret:
                ret.append(nonterm)
    return ret

def init_tables(uttr, ruleset):
    n = len(uttr)
    bp_table = [[[] for i in range(n)] for j in range(n)]  # back-pointer rule table
    ss_table = [[[] for i in range(n)] for j in range(n)]  # substring table
    for i, (x1, x2) in enumerate(zip(ss_table, bp_table)):  # base case and init
        ss_table[0][i].append(uttr[i])
        for nt in check_single_rules(f'"{uttr[i]}"',ruleset):
            if nt != f'"{uttr[i]}"':
                bp_table[0][i].append(nt)
        if i > 0:
            for j1, y1 in enumerate(x1[0:n - i]):                               # fill substring table
                for y1x in uttr[j1:j1 + i + 1]:
                    y1.append(y1x)
            sys.stdout.flush()
    for i1, x1 in enumerate(bp_table):                                          # fill back-pointer rule table
        if i1 > 0:
            for j1, (y1, y2) in enumerate(zip(x1[0:n - i1], ss_table[i1][0:n - i1])):
                substrs, subrule_pair = [], []
                for z1 in range(len(y2)):
                    if y2[z1 + 1:]: substrs.append([y2[:z1 + 1], y2[z1 + 1:]])
                for substr in substrs:
                    subrule1, subrule2 = None, None
                    for i2, x2 in enumerate(ss_table):
                        for j2, x2y in enumerate(x2):
                            if x2y == substr[0]: subrule1 = bp_table[i2][j2]
                            if x2y == substr[1] : subrule2 = bp_table[i2][j2]
                    for nt1 in subrule1:
                        for nt2 in subrule2:
                            subrule_pair.append((nt1,nt2))
                for subrule in subrule_pair:
                    for key, rules in ruleset.items():
                        for rule in rules:
                            if subrule == rule:
                                for nt in check_single_rules(key, ruleset):
                                    if nt not in y1: y1.append(nt)
    for row in bp_table[:-1]:           # removing redundant start states
        for set in row:
            if set:
                for nt in set:
                    if 'S' in set: set.remove('S')
    return ss_table[::-1], bp_table[::-1]

def generate_parse(tables, ruleset, parent='S'):
    ref, table = tables[0], tables[1]
    ret, alt = [parent], []
    if len(table) == 1:
        word = f'"{sum([x[0] for x in ref], [])[0]}"'
        if len(table[0][0]) == 1: return [parent, word]
        elif len(table[0][0]) > 1:
            for nt in table[0][0]:
                for key, rules in ruleset.items():
                    if key == nt and (word,) in rules and nt == parent:
                        return [parent, word]
                    elif key == nt and (word,) in rules and nt != parent:
                        return ret + [[nt, word]]
    temp, left, right = None, None, None
    i_main, j_main, set = 0, 0, table[0][0]
    subtable_left, subtable_right, ref_left, ref_right = None, None, None, None
    if set:
        for nt in set:
            for nt2 in set:
                for key, rules in ruleset.items():
                    if key == nt and nt2 in [x[0] for x in rules]:
                        temp = nt2
                        if temp not in alt: alt.append(temp)
        for i2 in range(i_main + 1, len(table)):
            if table[i2][j_main]:
                for nt2 in table[i2][j_main]:
                    for key, rules in ruleset.items():
                        if key == parent and nt2 in [x[0] for x in rules] and nt2 != temp:
                            ret.append([nt2])
                            if i_main >= j_main:
                                subtable_left = [x[j_main:len(table) - i2 + j_main] for x in table][i2:]
                                ref_left = [x[j_main:len(ref) - i2 + j_main] for x in ref][i2:]
                            else:
                                subtable_left = [x[j_main:] for x in table][i2:len(table) - j_main + i2]
                                ref_left = [x[j_main:] for x in ref][i2:len(ref) - j_main + i2]
                        elif key == temp and nt2 in [x[0] for x in rules]:
                            if alt and type(alt[-1]) is not list:
                                alt.append([nt2])
                                if i_main >= j_main:
                                    subtable_left = [x[j_main:len(table) - i2 + j_main] for x in table][i2:]
                                    ref_left = [x[j_main:len(ref) - i2 + j_main] for x in ref][i2:]
                                else:
                                    subtable_left = [x[j_main:] for x in table][i2:len(table) - j_main + i2]
                                    ref_left = [x[j_main:] for x in ref][i2:len(ref) - j_main + i2]
                    if type(ret[-1]) is list:
                        break
                    elif alt and type(alt[-1]) is list:
                        break
            if type(ret[-1]) is list:
                break
            elif alt and type(alt[-1]) is list:
                break
        diagonal = []
        for k, r in enumerate(table):
            if r[k] not in [x2[1] for x2 in diagonal]:
                if len(r[k]) > 1:
                    for x in r[k]:
                        if [x] not in [x2[1] for x2 in diagonal]:
                            diagonal.append((k, [x]))
                else:
                    diagonal.append((k, r[k]))
        right_list = [(x[0], x[1][0]) for x in diagonal if x[1]]
        for index, nt in right_list:
            if nt != temp:
                for key, rules in ruleset.items():
                    if key == parent and nt in [x[1] for x in rules if len(x) > 1]:
                        if type(ret[-1]) is list and len(ret) < 3:
                            if (ret[1][0], nt) in rules:
                                ret.append([nt])
                                left = ret[1][0]
                                right = ret[2][0]
                                i_main, j_main = index, index
                                if i_main >= j_main:
                                    subtable_right = [x[j_main:len(table) - i_main + j_main] for x in table][i_main:]
                                    ref_right = [x[j_main:len(ref) - i_main + j_main] for x in ref][i_main:]
                                else:
                                    subtable_right = [x[j_main:] for x in table][i_main:len(table) - j_main + i_main]
                                    ref_right = [x[j_main:] for x in ref][i_main:len(ref) - j_main + i_main]
                    if key == temp and nt in [x[1] for x in rules if len(x) > 1]:
                        if type(alt[-1]) is list and len(alt) < 3:
                            if len(ret) == 3: break
                            if (alt[1][0], nt) in rules:
                                alt.append([nt])
                                left = alt[1][0]
                                right = alt[2][0]
                                ret = [ret[0], alt]
                                i_main, j_main = index, index
                                if i_main >= j_main:
                                    subtable_right = [x[j_main:len(table) - i_main + j_main] for x in table][i_main:]
                                    ref_right = [x[j_main:len(ref) - i_main + j_main] for x in ref][i_main:]
                                else:
                                    subtable_right = [x[j_main:] for x in table][i_main:len(table) - j_main + i_main]
                                    ref_right = [x[j_main:] for x in ref][i_main:len(ref) - j_main + i_main]
                                break
                if len(alt) == 3 or len(ret) == 3:
                    if len(ret) == 3:
                        ret[1] += generate_parse((ref_left, subtable_left), ruleset, left)[1:]
                        ret[2] += generate_parse((ref_right, subtable_right), ruleset, right)[1:]
                        return ret
                    elif len(alt) == 3 and len(ret) == 2:
                        ret[-1][1] += generate_parse((ref_left, subtable_left), ruleset, left)[1:]
                        ret[-1][2] += generate_parse((ref_right, subtable_right), ruleset, right)[1:]
                        return ret

if len(sys.argv) < 3:
    print("usage: python CKYdet.py ecfg_file utt_file")
    sys.exit(1)
elif sys.argv[1][-4:] == 'ecfg' and sys.argv[2][-3:] == 'utt':
    try:
        with open(sys.argv[2]) as file:
            uttrs = [uttr.strip().split(' ') for uttr in file]
        with open(sys.argv[1]) as file:
            rules = [rule.strip().split(' ') for rule in file]
        for i, uttr in enumerate(uttrs):
            print('Utterance #' + str(i + 1))
            # print_table(tables[1])
            # print()
            # print_table(tables[0])
            # print()
            try:
                ruleset = create_ruleset(rules)
                tables = init_tables(uttr, ruleset)
                parse = generate_parse(tables, ruleset)
                if parse is None:
                    print('No valid parse')
                else:
                    print('Parse #1:', end='\t')
                    for c in ''.join(str(parse).split(',')):
                        if c == '\'':
                            continue
                        print(c, end='')
                    print()
            except TypeError:
                print('Parsing failed')
            print()
    except FileNotFoundError:
        print("error: file not found")
elif sys.argv[1][-4:] != 'ecfg' or sys.argv[2][-3:] != 'utt':
    print("error: grammar files end with .ecfg, utterance files end with .utt")


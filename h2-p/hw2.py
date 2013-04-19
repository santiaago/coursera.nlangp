import json
import time
from functools import update_wrapper
#from math import log

rarewords = {}
trainwords = {}
nonterm_counts = {}
bin_counts = {}
un_counts = {}

def decorator(d):
    "Make function d a decorator: d wraps a function fn."
    def _d(fn):
        return update_wrapper(d(fn), fn)
    update_wrapper(_d, d)
    return _d

@decorator
def memo(f):
    """Decorator that caches the return value for each call to f(args).
    Then when called again with same args, we can just look it up."""
    cache = {}
    def _f(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = f(*args)
            return result
        except TypeError:
            # some element of args can't be a dict key
            return f(args)
    return _f

def get_rarewords(inputfile):
    wc = {}
    infile = open(inputfile,'r')
    for line in infile:
        tree = json.loads(line)
        word_count(tree,wc)
    return filter_by_count(wc),wc

def replace_infrequent_words(inputfile,inputfile_srw):
    
    wc = {}
    infile = open(inputfile,'r')
    for line in infile:
        tree = json.loads(line)
        word_count(tree,wc)

    wc = filter_by_count(wc)

    infile = open(inputfile,'r')
    outfile = open(inputfile_srw,'w')
    for line in infile:
        tree = json.loads(line)
        new_tree = word_replace(tree,wc)
        new_tree = convert(new_tree)
        outfile.write(str(new_tree).replace("'","\"")+'\n')

def word_count(tree,wc):
    if len(tree) == 2: # unary rule
        rule = tree[1]
        if type(rule) == list:
            word_update(wc,rule[1])
        else:
            word_update(wc,rule)
    elif len(tree)== 3: # binary rule
        word_count(tree[1],wc)
        word_count(tree[2],wc)

def word_replace(tree,wc):
    if len(tree) == 2: # unary rule
        rule = tree[1]
        if type(rule) == list:
            if rule[1] in wc:
                tree[1][1] = "_RARE_"
        else:
            if rule in wc:
                tree[1] = "_RARE_"
    elif len(tree) == 3: # binary rule
        tree[1] = word_replace(tree[1],wc)
        tree[2] = word_replace(tree[2],wc)
    return tree

def word_update(wc,w):
    if w in wc:
        wc[w] += 1
    else:
        wc[w] = 1
def filter_by_count(wc):
    filter_wc = {}
    for w in wc:
        if wc[w] < 5:
            filter_wc[w] = wc[w]
    return filter_wc
def print_dict(d):
    for k in d:
        if d[k] != 0:
            print '%s: %s'%(k,d[k])
def print_dict_ex(d,i,j):
    for k in d:
        if d[k] != 0:
            a,b,c = k
            if a == i and b == j:
                print '%s: %s'%(k,d[k])

def convert(input):
    '''from so: 
    http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-unicode-ones-from-json-in-python'''
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
@memo
def q_br(br):
    X = br[0]
    return float(bin_counts[br])/(float(nonterm_counts[X])*1.0)
@memo
def q_ur(ur):
    X = ur[0]
    return float(un_counts[ur])/(float(nonterm_counts[X])*1.0)

def counts_dic(countfilename):
    counts = {}
    counts_br = {}
    counts_ur = {}
    countfile = open(countfilename,'r')
    for line in countfile:
        split = line.split()
        if 'NONTERMINAL' in line: 
            counts[split[2]] = split[0]
        elif 'BINARYRULE' in line:
            counts_br[tuple(split[2:])] = split[0]
        elif 'UNARYRULE' in line:
            counts_ur[tuple(split[2:])] = split[0]
    return counts,counts_br,counts_ur

def cky(sentence):
    # initialization
    x = sentence.split()
    pi = {}
    n = len(x)
    for i in range(1,n+1):
        word = x[i-1]
        for X in nonterm_counts:
            q = 0#float('-inf')
            key = (i,i,X)
            
            if (word in rarewords) or (word not in trainwords):
                r = (X,'_RARE_')
                if r in bin_counts:
                    q = q_br(r)
                elif r in un_counts:
                    q = q_ur(r)
            elif ((X,word) in un_counts) or ((X,word) in bin_counts):
                r = (X,word)
                if r in bin_counts:
                    q = q_br(r)
                elif r in un_counts:
                    q = q_ur(r)
            pi[key] = q
    # init back pointers        
    bp = {}
    for l in range(1,n):
        for i in range(1,n-l+1):
            j = i + l
            for X in nonterm_counts:
                values = []
                arg_values = {}
                range_set = []
                if i == j-1:
                    range_set.append(i)
                else:
                    range_set = range(i,j)
                for s in range_set:
                    bin_rules = get_binrules(X)
                    un_rules = get_unrules(X)
                    for r in bin_rules:
                        Y = r[1]
                        Z = r[2]
                        if ((i,s,Y) in pi ) and ((s+1,j,Z) in pi):
                            v = q_br(r)*pi[(i,s,Y)]*pi[(s+1,j,Z)]
                            #v = q_br(r) + pi[(i,s,Y)] + pi[(s+1,j,Z)]
                            values.append(v)
                            arg_values[(s,r)] = v 
                if len(values) > 0:
                    max_val = max(values)
                    arg_max = max(arg_values,key = arg_values.get)
                    pi[(i,j,X)] = max_val
                    bp[(i,j,X)] = arg_max
            #print_dict_ex(pi,i,j)
    return pi,bp

def getMax(values):
    m = float('-inf')
    for v in values:
        if v >= m:
            m = v
    return m
def getArgMax(values):
    arg = None
    m = 0
    for v in values:
        if values[v]>=m:
            arg = v
    return arg

def bt(bp,i,j,symbol,x):
    '''
    bp: dict of back pointers
    i,j indexes
    symbol: eg: SBAR
    x: sentence
    '''
    result = []
    try:
        node = bp[(i,j,symbol)]
        s = node[0]
        r1,r2,r3 = node[1]
        left = bt(bp,i,s,r2,x)
        right = bt(bp,s+1,j,r3,x)
        result.append(r1)
        result.append(left)
        result.append(right)
    except:
        # terminal
        result.append(symbol)
        result.append(x[i-1])
    return result
@memo
def get_binrules(X):
    rules = {}
    for k in bin_counts:
        if k[0] == X:
            rules[k] = bin_counts[k]
    return rules
@memo
def get_unrules(X):
    rules = {}
    for k in un_counts:
        if k[0] == X:
            rules[k] = un_counts[k]
    return rules

def part1():
    #replace_infrequent_words('tree.example','tree.example.out')
    #replace_infrequent_words('parse_dev.key','parse_dev_srw.key')
    replace_infrequent_words('parse_train.dat','parse_train_srw.dat')

def part2():
    #infile = open('parse_dev.dat','r')
    infile = open('parse_test.dat','r')
    #outfile = open('parse_dev.out','w')
    outfile = open('parse_test.p2.out','w')
    global rarewords
    global trainwords
    rarewords,trainwords = get_rarewords('parse_train.dat')#'parse_dev.key')
    global nonterm_counts
    global bin_counts
    global un_counts
    nonterm_counts,bin_counts,un_counts = counts_dic('parse_train.counts.out')
    # this gets up your score but agains the rules I believe ^^
    #a,b,u = counts_dic('cfg.counts')
    #un_counts.update(u)
    count = 0
    for line in infile:
        pi,bp = cky(line)
        res = None
        res = bt(bp,1,len(line.split()),'SBARQ',line.split())
        outfile.write(str(res).replace("'","\"")+'\n')
        count = count + 1
        print count
    print 'finnish!'

def test_part2():
    lines = []
    
    lines.append('What are geckos ?')
    lines.append('Where is Inoco based ?')
    lines.append('Name the first private citizen to fly in space .')
    lines.append('How many miles is it from London , England to Plymouth , England ?')

    results = []
    results.append('''['SBARQ', ['WHNP+PRON', 'What'], ['SBARQ', ['SQ', ['VERB', 'are'], ['NP+NOUN', 'geckos']], ['.', '?']]]''')
    results.append('''['SBARQ', ['WHADVP+ADV', 'Where'], ['SBARQ', ['SQ', ['VERB', 'is'], ['NP', ['NOUN', 'Inoco'], ['NOUN', 'based']]], ['.', '?']]]''')
    results.append('''['SBARQ', ['SQ', ['VERB', 'Name'], ['SQ', ['NP', ['DET', 'the'], ['NP', ['ADJ', 'first'], ['NOUN', 'private']]], ['VP', ['VERB', 'citizen'], ['S+VP', ['PRT', 'to'], ['VP', ['VERB', 'fly'], ['PP', ['ADP', 'in'], ['NP+NOUN', 'space']]]]]]], ['.', '.']]''')
    results.append('''['SBARQ', ['WHNP', ['WHADJP', ['ADV', 'How'], ['ADJ', 'many']], ['NOUN', 'miles']], ['SBARQ', ['SQ', ['VERB', 'is'], ['SQ', ['NP+PRON', 'it'], ['VP', ['PP', ['ADP', 'from'], ['NP', ['NOUN', 'London'], ['NP', ['.', ','], ['NP+NOUN', 'England']]]], ['PP', ['PRT', 'to'], ['NP', ['NOUN', 'Plymouth'], ['NP', ['.', ','], ['NP+NOUN', 'England']]]]]]], ['.', '?']]]''')
    infile = open('parse_dev.dat','r')
    global rarewords
    global trainwords
    rarewords,trainwords = get_rarewords('parse_train.dat')
    global nonterm_counts
    global bin_counts
    global un_counts
    nonterm_counts,bin_counts,un_counts = counts_dic('parse_train.counts.out')
    for i in range(len(lines)):
        line = lines[i]
        print line
        pi,bp = cky(line)
        res = bt(bp,1,len(line.split()),'SBARQ',line.split())
        #print res
        assert(str(res) == results[i])
        print '--------------------------------------------------'
    print 'done!'
def test_backtrack():
    t0 = time.time()
    global nonterm_counts
    global bin_counts
    global un_counts
    nonterm_counts,bin_counts,un_counts = counts_dic('parse_train.counts.out')
    
    line = 'What are geckos ?'
    line1 = 'How many miles is it from London , England to Plymouth , England ?'
    line2 = 'Where is Inoco based ?'
    line2 = 'Name the first private citizen to fly in space .'
    pi,bp = cky(line1)
    print bt(bp,1,len(line1.split()),'SBARQ',line1.split())
    t1 = time.time()
    print t1-t0
    return 0

def test_json():
    tree = json.loads(open('tree.example').readline())
    return tree[2][1][1][1]

def tests():
    assert(test_json() == 'is')
    global nonterm_counts
    global bin_counts
    global un_counts
    nonterm_counts,bin_counts,un_counts = counts_dic('parse_train.counts.out')
    print_dict(bin_counts)
    for k in bin_counts:
        print k
        print k[0]
        print list(k)
        break
    print 'test binary rules'
    t1 = tuple('VP NP VP+S+VP'.split())
    assert(q_br(t1,nonterm_counts,bin_counts) == 1/803.0)
    t2 = tuple('VP VERB VP'.split())
    assert(q_br(t2,nonterm_counts,bin_counts) == 103/803.0)
    print 'test unary rules'
    t3 = tuple('NUM one'.split())
    assert(q_ur(t3,nonterm_counts,un_counts) == 5/103.0)
    t4 = tuple('NOUN France'.split())
    assert(q_ur(t4,nonterm_counts,un_counts) == 1/3852.0)
    t5 = tuple('VP VERB .'.split())
    print q_br(t5,nonterm_counts,bin_counts)
    print 'all tests passed'

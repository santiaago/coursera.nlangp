import json

def get_rarewords(inputfile):
    wc = {}
    infile = open(inputfile,'r')
    for line in infile:
        tree = json.loads(line)
        word_count(tree,wc)

    print 'word counts:'
    print len(wc)

    print 'filter'
    return filter_by_count(wc)

def replace_infrequent_words(inputfile,inputfile_srw):
    
    wc = {}
    infile = open(inputfile,'r')
    for line in infile:
        tree = json.loads(line)
        word_count(tree,wc)

    print 'word counts:'
    print len(wc)

    print 'filter'
    wc = filter_by_count(wc)

    print 'filtered word counts:'
    print len(wc)

    print 'write output'
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
    #print tree
    if len(tree) == 2: # unary rule
        rule = tree[1]
        if type(rule) == list:
            if rule[1] in wc:
                tree[1][1] = "_RARE_"
        else:
            if rule in wc:
                tree[1] = "_RARE_"
            pass
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

def q_br(br,counts, counts_br):
    #print 'binary rule'
    #split = br.split()
    X = br[0]
    #print X
    #print int(counts_br[br])
    #print int(counts[X])
    #print int(counts_br[br])/(int(counts[X])*1.0)
    #print '--'
    return int(counts_br[br])/(int(counts[X])*1.0)

def q_ur(ur,counts,counts_ur):
    #print 'unary rule'
    X = ur[0]
    #print X
    #print counts_ur[ur]
    #print counts[X]
    #print int(counts_ur[ur])/(int(counts[X])*1.0)
    #print '--'
    return int(counts_ur[ur])/(int(counts[X])*1.0)

def counts_dic(countfilename):
    counts = {}
    counts_br = {}
    counts_ur = {}
    countfile = open(countfilename,'r')
    for line in countfile:
        split = line.split()
        print split
        if 'NONTERMINAL' in line: 
            counts[split[2]] = split[0]
        elif 'BINARYRULE' in line:
            counts_br[tuple(split[2:])] = split[0]
        elif 'UNARYRULE' in line:
            counts_ur[tuple(split[2:])] = split[0]
    return counts,counts_br,counts_ur

def cky(sentence,nonterm_counts,bin_counts,un_counts):
    # rare words:
    rarewords = {}
    rarewords = get_rarewords('parse_dev.key')
    # initialization

    x = sentence.split()
    pi = {}
    n = len(x)
    for i in range(1,n+1):
        for X in nonterm_counts:
            key = (i,i,X)
            r = (X,x[i-1])
            q = 0
            if r in bin_counts:
                q = q_br(r,nonterm_counts,bin_counts)
            elif r in un_counts:
                q = q_ur(r,nonterm_counts,un_counts)
            else: # rare
                if x[i-1] in rarewords:
                    r = (X, '_RARE_')
                    if r in bin_counts:
                        q = q_br(r,nonterm_counts,bin_counts)
                    elif r in un_counts:
                        q = q_ur(r,nonterm_counts,un_counts)
            pi[key] = q
    print_dict(pi)
    # init back pointers        
    bp = {}
    for l in range(1,n):#n-1):
        print '\tcurrent l: %s'%l
        print '\tstart i'
        for i in range(1,n-l+1):#n-l):
            j = i + l
            print '\t\tcurrent i: %s'%i
            print '\t\tcurrent j: %s'%j
            print '------------------- Debug output for words %s to %s ---------------'%(i,j)
            print '%s to %s'%(x[i-1],x[j-1])
            #raw_input()
            print '\t\tstart X'
            for X in nonterm_counts:
                print '\t\t\tcurrent X: %s'%X
                #raw_input()
                values = []
                arg_values = {}
                print '\t\t\tstart s'
                range_set = []
                if i == j-1:
                    range_set.append(i)
                else:
                    range_set = range(i,j)#-1)
                print '\t\t\trange: %s'%range_set
                for s in range_set:#range(i,j-1):
                    print '\t\t\t\tcurrent s: %s'%s
                    print '--------------------- (%s %s) / (%s %s)--------------'%(i,s,s+1,j)
                    #raw_input()
                    bin_rules = get_binrules(X,bin_counts)
                    un_rules = get_unrules(X,un_counts)
                    #if X == '.':
                    #    print bin_rules
                    #    print un_rules
                    print '\t\t\t\tstart r'
                    for r in bin_rules:
                        print '\t\t\t\t\tbinary current rule: %s'%str(r)
                        Y = r[1]
                        Z = r[2]
                        print '\t\t\t\t\tcurrent Y: %s'%Y
                        print '\t\t\t\t\tcurrent Z: %s'%Z
                        print '\t\t\t\t\tr: %s, i: %s, s: %s, j: %s'%(r,i,s,j)
                        #print pi
                        if ((i,s,Y) in pi ) and ((s+1,j,Z) in pi):
                            v = q_br(r,nonterm_counts,bin_counts)*pi[(i,s,Y)]*pi[(s+1,j,Z)]
                            values.append(v)
                            #arg_values[str([s,r])] = v 
                            arg_values[(s,r)] = v 
                            print '\t\t\t\tq(%s) : %s'%(str(r),q_br(r,nonterm_counts,bin_counts))
                            print '\t\t\t\tpi(%s, %s, %s) : %s'%(i,s,Y,pi[(i,s,Y)])
                            print '\t\t\t\tpi(%s, %s, %s) : %s'%(s+1,j,Z,pi[(s+1,j,Z)])
                            print '\t\t\t\t\tvalue: %s'%v
                            print '\t\t\t\t\targ: %s'%str([s,r])
                    #for r in un_rules:
                    #    print '\t\t\t\t\tunary current rule: %s'%str(r)
                    #    Y = r[1]
                    #    print '\t\t\t\t\tcurrent Y: %s'%Y
                    #    print '\t\t\t\t\tr: %s, i: %s, s: %s, j: %s'%(r,i,s,j)
                    #    if (i,s,Y) in pi:
                    #        v = q_ur(r,nonterm_counts,un_counts)*pi[(i,s,Y)]
                    #        values.append(v)
                    #        arg_values[str([s,r])] = v 
                    #        print '\t\t\t\tpi(%s, %s, %s) : %s'%(i,s,Y,pi[(i,s,Y)])
                    #        print '\t\t\t\t\tvalue: %s'%v
                    #        print '\t\t\t\t\targ: %s'%str([s,r])
                    print '\t\t\t\tend r'
                print '\t\t\tend s'
                if len(values) > 0:
                    max_val = max(values)
                    arg_max = max(arg_values,key = arg_values.get)
                    print '\t\t\tmax val: %s'%max_val
                    print '\t\t\targ max: %s'%str(arg_max)
                    pi[(i,j,X)] = max_val
                    bp[(i,j,X)] = arg_max
                    print '\t\t\tofficial pi(%s, %s, %s) = %s'%(i,j,X,max_val)
                    print '\t\t\tofficial bp(%s, %s, %s) = %s'%(i,j,X,arg_max)
            print '\t\tend X'
            print 'current pi'
            #raw_input()
            print_dict_ex(pi,i,j)
            #raw_input()
    print '\tend l'
    print print_dict(pi)
    print '----------------------------'
    print print_dict(bp)
    return pi,bp#pi[(1,n,'SBARQ')], bp[(1,n,'SBARQ')]

def bt(bp,i,j,symbol,x):
    '''
    bp: dict of back pointers
    i,j indexes
    symbol: eg: SBAR
    x: sentence
    '''
    print 'bt: %s, %s, %s'%(i,j,symbol)
    result = []
    try:
        print 'begin'
        node = bp[(i,j,symbol)]
        print 'ok'
        print node
        s = node[0]
        print s
        r1,r2,r3 = node[1]
        print node[1]
        print 'split: %s'%s
        print '1: %s 2: %s 3: %s'%(r1,r2,r3)
        print 'left'
        left = bt(bp,i,s,r2,x)
        print 'end left'
        print 'right'
        right = bt(bp,s+1,j,r3,x)
        print 'end right'
        result.append(r1)
        result.append(left)
        result.append(right)
    except:
        # terminal
        print 'except %s %s'%(symbol,i)
        result.append(symbol)
        result.append(x[i-1])

    return result
    

def get_binrules(X,bin_counts):
    rules = {}
    for k in bin_counts:
        if k[0] == X:
            rules[k] = bin_counts[k]
    return rules
def get_unrules(X,un_counts):
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
    nonterm_counts,bin_counts,un_counts = counts_dic('parse_train.counts.out')
    #line = 'What are geckos ?'
    #line = 'Who called ?'
    #line = 'How many miles is it from London , England to Plymouth , England ?'
    #res,res1 = cky(line,nonterm_counts,bin_counts,un_counts)
    #return res, res1
    infile = open('parse_dev.dat','r')
    outfile = open('parse_dev.out','w')
    for line in infile:
        pi,bp = cky(line,nonterm_counts,bin_counts,un_counts)
        res = bt(bp,1,len(line.split()),'SBARQ',line.split())
        outfile.write(str(res).replace("'","\"")+'\n')
    #    print 'result'
    #    print res
    #    break
def back():
    nonterm_counts,bin_counts,un_counts = counts_dic('parse_train.counts.out')
    line = 'What are geckos ?'
    line1 = 'How many miles is it from London , England to Plymouth , England ?'
    line2 = 'Where is Inoco based ?'
    line2 = 'Name the first private citizen to fly in space .'
    #line = 'Who called ?'
    pi,bp = cky(line1,nonterm_counts,bin_counts,un_counts)
    return bt(bp,1,len(line1.split()),'SBARQ',line1.split())

def test_json():
    tree = json.loads(open('tree.example').readline())
    return tree[2][1][1][1]

def tests():
    assert(test_json() == 'is')
    c,b,u = counts_dic('parse_train.counts.out')
    print_dict(b)
    for k in b:
        print k
        print k[0]
        print list(k)
        break
    print 'test binary rules'
    t1 = tuple('VP NP VP+S+VP'.split())
    assert(q_br(t1,c,b) == 1/803.0)
    t2 = tuple('VP VERB VP'.split())
    assert(q_br(t2,c,b) == 103/803.0)
    print 'test unary rules'
    t3 = tuple('NUM one'.split())
    assert(q_ur(t3,c,u) == 5/103.0)
    t4 = tuple('NOUN France'.split())
    assert(q_ur(t4,c,u) == 1/3852.0)
    t5 = tuple('VP VERB .'.split())
    print q_br(t5,c,b)
    #q((VP,VERB,.))=1.245330e-03, pi(2,2,VERB)=5.959983e-03, pi(3,3,.)=8.341535e-01
    print 'all tests passed'
    # look for:
    # pi(2,3,VP)=6.191209e-06
    #pi(2,3,NP)=2.065880e-06

    #(2, 3, 'VP'): 0.00169587833441
    #official pi(2, 3, VP) = 0.00169587833441
    #official bp(2, 3, VP) = [2, ('VP', 'ADVP+ADV', 'VP+VERB')]
    
    #pi(2, 3, VP) comes from
    #q(('VP', 'ADVP+ADV', 'VP+VERB')) : 0.00498132004981
    #pi(2, 2, ADVP+ADV) : 0.815789473684
    #pi(3, 3, VP+VERB) : 0.417322834646

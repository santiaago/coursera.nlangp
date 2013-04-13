import json

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
def print_wc(wc):
    for w in wc:
        print '%s: %s'%(w,wc[w])

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

def part1():
    #replace_infrequent_words('tree.example','tree.example.out')
    #replace_infrequent_words('parse_dev.key','parse_dev_srw.key')
    replace_infrequent_words('parse_train.dat','parse_train_srw.dat')

def part2():
    pass

def test_json():
    tree = json.loads(open('tree.example').readline())
    return tree[2][1][1][1]

def tests():
    assert(test_json() == 'is')
    print 'all tests passed'

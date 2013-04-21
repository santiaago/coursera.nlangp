import codecs

def model1(filename_f, filename_e,S = 5):
    print '--------------------'
    print 'starting IBM Model 1'
    print
    print 'number of iterations is %s'%(S)
    print
    print 'training corpus f: %s'%(filename_f)
    print 'training corpus e: %s'%(filename_e)
    
    f = codecs.open(filename_f, "r", "utf-8").readlines()
    e = codecs.open(filename_e, "r", "utf-8").readlines()
    
    n = sum(1 for line in f)
    
    print 'number of lines f: %s'%(n)
    
    print 'f(%s) : %s'%(0,f[0])
    print 'e(%s) : %s'%(0,e[0])
    # initialize t(f|e) parameters
    # t(f|e) = c(e,f)/c(e)
    # start with the count:
    words = {}
    words['NULL'] = {}
    sentences = {}
    print '------------------------------'
    print 'building dictionary with words ...'
    for i in range(0,n):
        f_line = f[i]
        e_line = e[i]
        for en_word in e_line.split():
            if en_word not in words:
                words[en_word] = {}
            for es_word in set(f_line.split()):
                if es_word not in words[en_word]:
                    words[en_word][es_word] = 1
                if es_word not in words['NULL']:
                    words['NULL'][es_word] = 1
    print '------------------------------'
    print 'building dictionary with counts...'
    count = {}
    for w in words.keys():
        count[w] = len(words[w])
    print_counts(count)
    print_dict(words)
    # initializing t
    print '------------------------------'
    print 'building initial t parameters ...'
    t = {}
    for w_en in words.keys():
        for w_f in words[w_en]:
            if w_f not in t:
                t[w_f] = {}
            t[w_f][w_en] = 1/float(count[w_en])
    print_t(t)
    

    '''for s in range(1,S+1):
        #set counts to 0
        for k in range(1,n+1):
            # mk lenght of foreign sentence
            mk = f[k-1]
            for i in range(1,mk+1):
                # lk is the length of the english sentence
                lk = e[k-1]
                for j in range(0,lk+1):
                    # delta
                    #counts
                    pass
        # set t(f|e) = c(e,f)/c(e)'''
def print_dict(d):
    'print dictionary'
    print '------------------------------'
    print 'print dictionary'
    for k in d:
        print 'd(%s): %s'%(k,d[k])
    
def print_counts(count):
    'print count dictionary'
    print '------------------------------'
    print 'count dictionary'
    for c in count:
        print 'c(%s): %s'%(c,count[c])
def print_t(t):
    'print t dictionary'
    print '------------------------------'
    print 't dictionary'
    for es in t.keys():
        for en in t[es]:
            print '\tt(%s | %s): %s'%(es,en,t[es][en])
def part1():
    #model1('corpus.es','corpus.en', 5)
    model1('example.es','example.en', 2)
    pass
def part2():
    pass
def part3():
    pass
def tests():
    pass

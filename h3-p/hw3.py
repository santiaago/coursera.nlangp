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
    
    c = {}
    delta = {}
    for s in range(1,S+1):
        print
        print 'iteration #%s'%s
        #set counts to 0
        c = {}
        for k in range(1,n+1):
            # mk lenght of foreign sentence
            mk = len(f[k-1].split())
            print f[k-1]
            print mk
            sentence_f = f[k-1].split()
            for i in range(1,mk+1):
                # lk is the length of the english sentence
                lk = len(e[k-1].split())
                sentence_e = ['NULL']+e[k-1].split()
                print e[k-1]
                print lk
                for j in range(0,lk+1):
                    # delta
                    fik = sentence_f[i-1]
                    print sentence_e
                    print j
                    ejk = sentence_e[j]
                    sumt = 0
                    for m in range(lk+1):
                        emk = sentence_e[m]
                        sumt += t[fik][emk]
                    delta[(k,i,j)] = t[fik][ejk]/sumt
                    if (ejk,fik) not in c:
                        c[(ejk,fik)] = 0
                    c[(ejk,fik)] += delta[(k,i,j)]
                    if (ejk,) not in c:
                        c[(ejk,)] = 0
                    c[(ejk,)] += delta[(k,i,j)]
                    if j not in c:
                        c[(j,)]= {}
                        c[(j,)][(i,lk,mk)] = 0 
                    else:
                        if (i,lk,mk) not in c[j]:
                            c[(j,)][(i,lk,mk)] = 0 
                    c[(j,)][(i,lk,mk)] += delta[(k,i,j)]
                    if (i,lk,mk) not in c:
                        c[(i,lk,mk)] = 0
                    c[(i,lk,mk)] += delta[(k,i,j)]
        # set t(f|e) = c(e,f)/c(e)
        for w_en in words.keys():
            for w_f in words[w_en]:
                t[w_f][w_en] = c[(w_en,w_f)]/float(c[(w_en,)])
        print_t(t)
        print_c(c)
        raw_input()
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
def print_c(c):
    'print c dictionary'
    print '------------------------------'
    print 'c dictionary'
    for k in c.keys():
        print '\tc(%s): %s'%(k,c[k])
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

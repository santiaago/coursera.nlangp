import codecs
import sys
from collections import defaultdict

VERBOSE = False
DUMPALLITERATIONS = False
def model1(filename_f, filename_e,S = 5):
    print 'model1'
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

    # initialize t(f|e) parameters
    # t(f|e) = c(e,f)/c(e)
    # start with the count:
    words = defaultdict()
    words['NULL'] = defaultdict(int)

    print '------------------------------'
    print 'building dictionary with words ...'
    
    for i in range(0,n):
        f_line = f[i]
        e_line = e[i]
        for en_word in e_line.split():
            if en_word not in words:
                words[en_word] = defaultdict(int)
            for es_word in set(f_line.split()):
                if es_word not in words[en_word]:
                    words[en_word][es_word] = 1
                if es_word not in words['NULL']:
                    words['NULL'][es_word] = 1
    if False:
        print '------------------------------'
        print 'building dictionary with counts...'
    
    count = defaultdict(int)
    for w in words.keys():
        count[w] = len(words[w])

    if VERBOSE:
        print_counts(count)
        print_dict(words)

    # initializing t
    print '------------------------------'
    print 'building initial t parameters ...'
    t = defaultdict()
    for w_en in words.keys():
        for w_f in words[w_en]:
            if w_f not in t:
                t[w_f] = defaultdict(float)
            t[w_f][w_en] = 1/float(count[w_en])
    if VERBOSE:
        print_t(t)
    
    c = defaultdict()
    for s in range(1,S+1):
        print
        print 'iteration #%s'%s
        #set counts to 0
        c = defaultdict()
        for k in range(1,n+1):
            sys.stdout.write("\rWorking with line %s of %s" % (k,n+1) )
            sys.stdout.flush()
            # mk lenght of foreign sentence
            mk = len(f[k-1].split())
            sentence_f = f[k-1].split()
            for i in range(1,mk+1):
                # lk is the length of the english sentence
                lk = len(e[k-1].split())
                sentence_e = ['NULL']+e[k-1].split()
                for j in range(0,lk+1):

                    fik = sentence_f[i-1]
                    ejk = sentence_e[j]
                    sumt = 0
                    for m in range(lk+1):
                        emk = sentence_e[m]
                        sumt += t[fik][emk]
                    delta = t[fik][ejk]/sumt
                    if (ejk,fik) not in c:
                        c[(ejk,fik)] = 0
                    c[(ejk,fik)] += delta
                    if (ejk,) not in c:
                        c[(ejk,)] = 0
                    c[(ejk,)] += delta
                    if j not in c:
                        c[(j,)]= defaultdict(float)
                        c[(j,)][(i,lk,mk)] = 0 
                    else:
                        if (i,lk,mk) not in c[j]:
                            c[(j,)][(i,lk,mk)] = 0 
                    c[(j,)][(i,lk,mk)] += delta
                    if (i,lk,mk) not in c:
                        c[(i,lk,mk)] = 0
                    c[(i,lk,mk)] += delta
        # set t(f|e) = c(e,f)/c(e)
        for w_en in words.keys():
            for w_f in words[w_en]:
                t[w_f][w_en] = c[(w_en,w_f)]/float(c[(w_en,)])
        if DUMPALLITERATIONS:
            print '\ndumping iteration %s'%(s)
            name = 'corpus.t_iteration%s.out'%(s)
            dump_t(name,t)
        if VERBOSE:
            print_t(t)
            print_c(c)
    return t

def model2(filename_f, filename_e,t,S = 5):
    print 'model2'
    print '--------------------'
    print 'starting IBM Model 2'
    print
    print 'number of iterations is %s'%(S)
    print
    print 'training corpus f: %s'%(filename_f)
    print 'training corpus e: %s'%(filename_e)
    
    f = codecs.open(filename_f, "r", "utf-8").readlines()
    e = codecs.open(filename_e, "r", "utf-8").readlines()
    
    n = sum(1 for line in f)
    
    print 'number of lines f: %s'%(n)
    
    # initialize q
    q = defaultdict()
    for k in range(1,n+1):
        # mk lenght of foreign sentence
        mk = len(f[k-1].split())
        for i in range(1,mk+1):
            # lk is the length of the english sentence
            lk = len(e[k-1].split())
            for j in range(0,lk+1):
                if j not in q:
                    q[j] = defaultdict(float)
                q[j][(i,lk,mk)] = 1/float(lk+1)

    c = defaultdict()
    for s in range(1,S+1):
        print
        print 'iteration #%s'%s
        #set counts to 0
        c = defaultdict()
        for k in range(1,n+1):
            sys.stdout.write("\rWorking with line %s of %s" % (k,n+1) )
            sys.stdout.flush()
            # mk lenght of foreign sentence
            mk = len(f[k-1].split())
            sentence_f = f[k-1].split()
            for i in range(1,mk+1):
                # lk is the length of the english sentence
                lk = len(e[k-1].split())
                sentence_e = ['NULL']+e[k-1].split()
                for j in range(0,lk+1):

                    fik = sentence_f[i-1]
                    ejk = sentence_e[j]
                    # delta
                    sumqt = 0
                    for m in range(lk+1):
                        emk = sentence_e[m]
                        sumqt += t[fik][emk]*q[m][(i,lk,mk)]

                    delta = (t[fik][ejk]*q[j][(i,lk,mk)])/sumqt

                    # cs
                    if (ejk,fik) not in c:
                        c[(ejk,fik)] = 0
                    c[(ejk,fik)] += delta

                    if (ejk,) not in c:
                        c[(ejk,)] = 0
                    c[(ejk,)] += delta

                    if j not in c:
                        c[(j,)]= defaultdict(float)
                        c[(j,)][(i,lk,mk)] = 0 
                    else:
                        if (i,lk,mk) not in c[j]:
                            c[(j,)][(i,lk,mk)] = 0 
                            
                    c[(j,)][(i,lk,mk)] += delta
                    if (i,lk,mk) not in c:
                        c[(i,lk,mk)] = 0
                    c[(i,lk,mk)] += delta
        # set t(f|e) = c(e,f)/c(e)
        for w_f in t:
            for w_e in t[w_f]:
                t[w_f][w_e] = c[(w_e, w_f)]/ float(c[(w_e,)])
        # set q(j|i,l,m) = c(j|i,l,m)/c(i,l,m)
        for kk in range(1,n+1):
            mkk = len(f[kk-1].split())
            for ii in range(1,mkk+1):
                # lk is the length of the english sentence
                lkk = len(e[kk-1].split())
                for jj in range(0,lkk+1):
                    q[jj][(ii,lkk,mkk)] = 1/float(lkk+1)
                
        if VERBOSE:
            print_t(t)
            print_c(c)
    return t


def alignments(t,filename_f,filename_e):
    print 'alignments'
    f = codecs.open(filename_f, "r", "utf-8").readlines()
    e = codecs.open(filename_e, "r", "utf-8").readlines()

    n = sum(1 for line in f)
    
    align = []
    for i in range(0,n):
        f_line = f[i].split()
        e_line = e[i].split()
        current_align = []
        for f_word in f_line:
            arg_values = defaultdict(float)#{}
            for e_word in e_line:
                arg_values[(f_word,e_word)] = t[f_word][e_word]
            max_f,max_e = max(arg_values,key = arg_values.get)
            current_align.append((e_line.index(max_e)+1,f_line.index(max_f)+1))
        align.append(current_align)

    if False:
        print_alignments(align)
    return align

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
def print_alignments(a):
    for i in a:
        s = ''
        for j in i:
            s += ' '+str(j)
        print s
def dump_t(filename,t):
    print 'dumping'
    out = codecs.open(filename, "w", "utf-8")
    for f in t.keys():
        for e in t[f]:
            s = '%s %s %s\n'%(f,e,t[f][e])
            out.write(s)
def read_t(filename):
    print 'reading file %s to get t'%(filename)
    t = defaultdict()
    f = codecs.open(filename, "r", "utf-8").readlines()
    for line in f:
        split = line.split()
        foreign = split[0]
        english = split[1]
        p = float(split[2])
        if foreign not in t:
            t[foreign] = defaultdict(float)
        t[foreign][english] = p
    return t

def dump_align(filename,alignment):
    print '\nalignments'
    out = codecs.open(filename, "w", "utf-8")
    for index in range(len(alignment)):
        line = alignment[index]
        for pair in line:
            e,f = pair
            s = '%s %s %s\n'%(index+1,e,f)
            out.write(s)

def test_part1():
    t = model1('example.es','example.en', 5)
    print
    dump_t('example.t.out',t)
    alignments(t,'example.es','example.en')
def part1():
    #t = model1('corpus.es','corpus.en', 5)

    #dump_t('corpus.t5.p1.out',t)
    #t = read_t('corpus.t.1.p1.out')
    t = read_t('corpus.t_iteration2.out')
    #a = alignments(t,'dev.es','dev.en')
    a = alignments(t,'test.es','test.en')
    dump_align('alignment_test.p1.out',a)
    #dump_align('alignment_dev_4.p1.out',a)

def part2():
    #t = read_t('corpus.t_iteration2.out')
    #t = model2('corpus.es','corpus.en',t,5)
    #dump_t('corpus.t5.p2.out',t)
    t = read_t('corpus.t5.p2.out')
    #a = alignments(t,'dev.es','dev.en')
    #dump_align('alignment_dev.p2.out',a)

    a = alignments(t,'test.es','test.en')
    dump_align('alignment_test.p2.out',a)
def part3():
    pass
def tests():
    pass

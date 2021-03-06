from math import log

def compute_emission_params(countfile,x,y):
    V = False
    if V:
        print 'compute emission params'
        print 'count file: %s'%(countfile)
        print 'word x: %s'%(x)
        print 'tag y %s'%(y)

    county = 0
    count_y_to_x = 0
    f = open(countfile,'r')
    found = 0
    for line in f:
        split = line.split()
        count = int(split[0])
        token = str(split[1])
        if token == '1-GRAM':
            tag = str(split[2])
            if y == tag:
                county = count
                found += 1
        elif token == 'WORDTAG':
            tag = str(split[2])
            word = str(split[3])
            if tag == y and word == x:
                count_y_to_x = count
                found += 1
        if found == 2:
            break

    if county >0:
        e = float(count_y_to_x)/float(county)
    else:
        print 'count y is zero'
        e = 0
    if V:
        print 'Count(y -> x)'
        print 'Count(%s -> %s) : %s'%(y,x,count_y_to_x)
        print 
        print 'Count(y)'
        print 'Count(%s) : %s'%(y,county)
        print 
        print 'e(x|y)'
        print 'e(%s|%s) : %s'%(x,y,e)
    return e

def dic_of_compute_emission_params(countfile,rare_words):

    dic_count_wordtags = {}
    dic_count_1gram = {}

    county = 0
    count_y_to_x = 0

    f = open(countfile,'r')
    found = 0
    for line in f:
        split = line.split()
        count = int(split[0])
        token = str(split[1])
        if token == '1-GRAM':
            tag = str(split[2])
            dic_count_1gram[tag] = count
        elif token == 'WORDTAG':
            tag = str(split[2])
            word = str(split[3])
            dic_count_wordtags[(word,tag)] = count
    # build dictionary of emission e(x | y)
    dic_emission = {}
    for key in dic_count_wordtags:
        word, tag = key
        count_tag_to_word = dic_count_wordtags[key]
        count_tag = dic_count_1gram[tag]
        if(count_tag >0):
            dic_emission[(word,tag)] = float(count_tag_to_word)/float(count_tag)
        else:
            dic_emision[(word,tag)] = 0
    # modify dictionary of emission to take into account _RARE_ words
    for key in dic_count_wordtags:
        word, tag = key
        count_tag_to_word = dic_count_wordtags[key]
        count_tag = dic_count_1gram[tag]
        if(count_tag >0):
            if word in rare_words:
                tagclass = getClass(word)
                count_tag_to_rare = dic_emission[(tagclass,tag)]
                dic_emission[(word,tag)] = float(count_tag_to_rare)/float(count_tag)

    return dic_emission

def getClass(word):
    if isNumeric(word):
        return '_NUMERIC_'
    if isAllCapitals(word):
        return '_ALLCAPITALS_'
    if isLastCapital(word):
        return '_LASTCAPITAL_'
    else:
        return '_RARE_'

def InClass(tag):
    return tag in ['_NUMERIC_','_ALLCAPITALS_','_LASTCAPITAL_','_RARE_']

def dic_of_compute_q_params(countfile):
    'q(yi|yi-2,yi-1)= c(yi-2,yi-1,yi)/c(yi-2,yi-1)'

    dic_2_gram = {}
    dic_3_gram = {}
    f = open(countfile,'r')
    for line in f:
        split = line.split()
        count = int(split[0])
        token = str(split[1])
        if token == '1-GRAM':
            pass
        elif token == '2-GRAM':
            yn_1 = str(split[2])
            yn = str(split[3])
            dic_2_gram[(yn_1,yn)] = count
        elif token == '3-GRAM':
            yn_2 = str(split[2])
            yn_1 = str(split[3])
            yn = str(split[4])
            dic_3_gram[(yn_2,yn_1,yn)] = count

    return dic_2_gram, dic_3_gram
            
def compute_q_params(dic_2_gram,dic_3_gram,yi_2,yi_1,yi,verbose=False):
    if verbose:
        print 'computing q params for:'
        print 'q(yi|yi-2,yi-1)'
        print 'q(%s|%s,%s)'%(yi,yi_2,yi_1)
    
    c1 = dic_3_gram[(yi_2,yi_1,yi)]
    c2 = dic_2_gram[(yi_2,yi_1)]
    q = float(c1)/float(c2)
    if q == 0:
        q =float('-inf')
    else:
        q = log(q)
    return q

def rare_words_from_count_file(filepath):
    'from a count file returns a list of words that are _RARE_'
    datafile = open(filepath, 'r')
    data = []
    rare_words = []
    all_words = []
    dic_words = {}
    for line in datafile:
        #print line
        split = line.split()
        count = int(split[0])
        token = str(split[1])
        if token == 'WORDTAG':
            tag = str(split[2])
            word = str(split[3])
            if word not in dic_words:
                dic_words[word] = [count]
            else:
                dic_words[word].append(count)
    for word in dic_words:
        all_words.append(word)
        if sum(dic_words[word])<5:
            rare_words.append(word)
    return all_words,rare_words

def isNumeric(word):
    import re
    match = re.search(r'\d',word)
    if match:
        return True
    return False

def isAllCapitals(word):
    import re
    match = re.search(r'^[A-Z]+$',word)
    if match:
        return True
    return False

def isLastCapital(word):
    import re
    match = re.search(r'[A-Z]$',word)
    if match and not isAllCapitals(word):
        return True
    return False

def replace_infrequent_words_in_input_file(inputfile,rare_words,inputfile_sans_rare_words):
    'from input file and list of rare words, create inputfile_sans_rare_words'
    
    infile = open(inputfile,'r')
    outfile = open(inputfile_sans_rare_words,'w')
    for line in infile:
        if line != '\n':
            split = line.split()
            word = split[0]
            tag = split[1]
            if word in rare_words:
                word = '_RARE_'
                outfile.write(word+' '+tag+'\n')
            else:
                outfile.write(line)                
        else:
            outfile.write(line)

def replace_infrequent_words_in_input_file_ex(inputfile,rare_words,inputfile_sans_rare_words):
    'from input file and list of rare words, create inputfile_sans_rare_words'
    
    infile = open(inputfile,'r')
    outfile = open(inputfile_sans_rare_words,'w')
    for line in infile:
        if line != '\n':
            split = line.split()
            word = split[0]
            tag = split[1]
            if word in rare_words:
                if isNumeric(word):
                    word = '_NUMERIC_'
                elif isAllCapitals(word):
                    word = '_ALLCAPITALS_'
                elif isLastCapital(word):
                    word = '_LASTCAPITAL_'
                else:
                    word = '_RARE_'
                outfile.write(word+' '+tag+'\n')
            else:
                outfile.write(line)                
        else:
            outfile.write(line)
                
def replace_infrequent_words():

    filepath = 'gene.counts'
    print '::> count file:'
    print '::> file path: %s'%(filepath)
    w , rare_words = rare_words_from_count_file(filepath)
    
    # create file from input file and change tags to _RARE_ for infrequent words
    inputfile = 'gene.train'
    inputfile_sans_rare_words = 'gene.train.with.rare'
    print '::> input file:'
    print '::> file path: %s'%(inputfile)
    replace_infrequent_words_in_input_file(inputfile,rare_words,inputfile_sans_rare_words)

def replace_infrequent_words_ex():
    filepath = 'gene.counts'
    print '::> count file:'
    print '::> file path: %s'%(filepath)
    w, rare_words = rare_words_from_count_file(filepath)
    
    # create file from input file and change tags to _RARE_ for infrequent words
    inputfile = 'gene.train'
    inputfile_sans_rare_words = 'gene.train.with.rare.ex'
    print '::> input file:'
    print '::> file path: %s'%(inputfile)
    replace_infrequent_words_in_input_file_ex(inputfile,rare_words,inputfile_sans_rare_words)


def get_tags_from_count_file(countfile):
    'build a set of tags from count file'
    count_f = open(countfile,'r')
    set_tags =set()
    for line in count_f:
        split = line.split()
        count = int(split[0])
        token = str(split[1])
        if token == '1-GRAM':
            tag = str(split[2])
            set_tags.add(tag)
    return set_tags

def simple_gene_tagger(countfile,genedevfile,outfile):

    genedev_f = open(genedevfile,'r')
    out_f = open(outfile,'w')
    set_tags =set()
    set_tags = get_tags_from_count_file(countfile)
    print set_tags
    tags = list(set_tags)
    print 'looking for rare words'
    all_words, rare_words = rare_words_from_count_file('gene.counts')
    print 'lengh of rare words %s'%(len(rare_words))
    print 'start compute emission params'
    dic_e = dic_of_compute_emission_params(countfile,rare_words)
    print 'writing dictionary of emission of file dic_e'
    f_e = open(countfile+'_dic_e','w')
    for e in dic_e:
        w,t = e
        f_e.write(w+' '+t+' : '+str(dic_e[e])+'\n')
    f_e.close()
    print 'finnish compute emission params'
    print 'length of dictionary of emissions: %s'%(str(len(dic_e)))
    counter = 0
    for word in genedev_f:
        if word != '\n':
            tagger = {}
            word = word.strip()
            for t in tags:
                if (word,t) in dic_e:
                    e = dic_e[(word,t)]
                else:
                    if word in all_words:
                        if word in rare_words:
                            e = dic_e[('_RARE_',t)]
                        else:
                            e = 0
                    else:
                        e = dic_e[('_RARE_',t)]
                if (word,t) in tagger:
                    tagger[(word,t)]= max(tagger[(word,t)],e)
                else:
                    tagger[(word,t)] = e
            key = max(tagger,key=tagger.get)
            w,t = key
            out_f.write(w+' '+t+'\n')
        else:
            out_f.write(word)
        counter += 1
        if counter%10000 == 0:
            print 'simple_gene_tagger running: %s'%(counter)

def viterbi_dev():
    countfile = 'gene.counts.with.rare'
    genedevfile = 'gene.dev'
    outfile = 'gene_dev.p2.out'
    viterbi(countfile,genedevfile,outfile)

def viterbi_test():
    countfile = 'gene.counts.with.rare'
    genetestfile = 'gene.test'
    outfile = 'gene_test.p2.out'
    viterbi(countfile,genetestfile,outfile)

def viterbi_ex_dev():
    countfile = 'gene.counts.with.rare.ex'
    genedevfile = 'gene.dev'
    outfile = 'gene_dev.p3.out'
    viterbi(countfile,genedevfile,outfile)

def viterbi_ex_test():
    countfile = 'gene.counts.with.rare.ex'
    genedevfile = 'gene.test'
    outfile = 'gene_test.p3.out'
    viterbi(countfile,genedevfile,outfile)

def viterbi(countfile,genefile,outfile):

    print '--------------------------------------------------'
    print 'start viterbi algorithm'
    print 'getting emission params'
    all_words, rare_words = rare_words_from_count_file('gene.counts')
    dic_e = dic_of_compute_emission_params(countfile,rare_words)
    print 'getting q params'
    dic_2_gram,dic_3_gram = dic_of_compute_q_params('gene.counts')
    print 'build K, the set of possible tags'
    Kk = list(get_tags_from_count_file(countfile))
    K = {}
    print 'initialization of pi'
    pi = {}
    pi[(0,'*','*')] = log(1)#1
    print 'initilization of back pointers'
    bp = {}
    print 'opening files'
    gene_f = open(genefile,'r')
    out_f = open(outfile,'w')
    sentence = []
    for word in gene_f:
        if word != '\n':
            sentence.append(word)
        else:
            n = len(sentence)
            # * fill K vector
            for i in range(-1,n+1):
                if i <1:
                    K[i] = ['*']
                else:
                    K[i]= Kk
            # * algorithm
            for k in range(1,n+1): 
                for u in K[k-1]:
                    for v in K[k]:
                        values = []
                        arg_values = {}
                        for w in K[k-2]:
                            q = compute_q_params(dic_2_gram,dic_3_gram,w,u,v,False)
                            xk = sentence[k-1].strip()
                            e = emission(xk,v,dic_e,all_words,rare_words,False)
                            values.append(pi[(k-1,w,u)]+q+e)
                            arg_values[w] = pi[(k-1,w,u)]+q+e
                            #values.append(pi[(k-1,w,u)]*q*e)
                            #arg_values[w] = pi[(k-1,w,u)]*q*e
                        max_val = max(values)
                        arg_max = max(arg_values,key=arg_values.get)
                        bp[(k,u,v)] = arg_max
                        pi[(k,u,v)] = max_val
            # * set yn-1 and yn
            arg_values = {}
            for u in K[n-1]:
                for v in K[n]:
                    q = compute_q_params(dic_2_gram,dic_3_gram,u,v,'STOP')
                    arg_values[(u,v)] = pi[(n,u,v)]+q
                    #arg_values[(u,v)] = pi[(n,u,v)]*q
            yn_1,yn = max(arg_values,key=arg_values.get)
            # * set other yk tags
            dic_y = {}
            dic_y[n-1] = yn_1
            dic_y[n] = yn
            for k in range(n-2,0,-1):
                yk1 = dic_y[k+1]
                yk2 = dic_y[k+2]
                dic_y[k] = bp[(k+2,yk1,yk2)]
            # * use yk tags to write in out file
            for k in range(n):
                s = sentence[k].strip() + ' ' + dic_y[k+1] + '\n'
                out_f.write(s)
            sentence = []
            out_f.write('\n')

def emission(word,t,dic_e,all_words,rare_words,verbose=False):
    e = -1
    if (word,t) in dic_e:
        e = dic_e[(word,t)]
    else:
        if word in all_words:
            if word in rare_words:
                tagclass = getClass(word)
                e = dic_e[(tagclass,t)]
            else:
                e = 0
        else:
            tagclass = getClass(word)
            e = dic_e[(tagclass,t)]
    if verbose:
        print 'emission of %s : %s = %s'%(word,t,str(e))
    if e == 0:
        e = float('-inf')
    else:
        e = log(e)
    return e
            
def gene_dev():
    countfile = 'gene.counts.with.rare'
    genedevfile = 'gene.dev'
    outfile = 'gene_dev.p1.out'
    simple_gene_tagger(countfile,genedevfile,outfile)
    print 'end of gene_dev'

def gene_test():
    countfile = 'gene.counts.with.rare'
    genetestfile = 'gene.test'
    outfile = 'gene_test.p1.out'
    simple_gene_tagger(countfile,genetestfile,outfile)
    print 'end of gene_test'

def tests():
    print 'tests'
    print 'part1'
    w,rare = rare_words_from_count_file('gene.counts')
    assert('molecular' not in rare)
    assert('ill' in w)
    assert('colestipol' in rare)
    assert('leukocytosis' in rare)
    assert('prominent' not in rare)
    assert('This' not in rare)
    assert(',"' not in rare)
    
    assert(compute_emission_params('gene.counts.with.rare','achieved','O')>0)
    assert(compute_emission_params('gene.counts.with.rare','achieved','O')<5.6e-05)
    assert(compute_emission_params('gene.counts.with.rare','achieved','O')>5.5e-05)
    assert(compute_emission_params('gene.counts.with.rare','achieved','error')==0)
    print 'tests of part 1 passed!'

    print 'part2'
    v = False
    dic_2_gram,dic_3_gram = dic_of_compute_q_params('gene.counts')
    assert(compute_q_params(dic_2_gram,dic_3_gram,'*','I-GENE','STOP',v)==log(1./749.))
    assert(compute_q_params(dic_2_gram,dic_3_gram,'*','*','O',v)==log(0.9457089011307626))
    assert(compute_q_params(dic_2_gram,dic_3_gram,'I-GENE','I-GENE','O',v)==log(9622/24435.))
    print 'tests of part 2 passed!'

    print 'part3'
    assert(isNumeric('world')==False)
    assert(isNumeric('w0rld')==True)
    assert(isNumeric('w03234rld')==True)
    assert(isNumeric('world123')==True)
    assert(isNumeric('e&dfgkjhfgworld')==False)

    assert(isAllCapitals('SANTIAGO')==True)
    assert(isAllCapitals('sANTIAGO')==False)
    assert(isAllCapitals('SaNTIAGO')==False)
    assert(isAllCapitals('SAnTIAGO')==False)

    assert(isLastCapital('SAnTIAGO')==True)
    assert(isLastCapital('SANTIAGo')==False)
    assert(isLastCapital('SANTIAGO')==False)
    assert(isLastCapital('SAnTIAGo')==False)


    print 'all tests passed!'
    

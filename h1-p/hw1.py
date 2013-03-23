
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
                count_tag_to_rare = dic_emission[('_RARE_',tag)]
                dic_emission[(word,tag)] = float(count_tag_to_rare)/float(count_tag)

    return dic_emission

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
                
def replace_infrequent_words():

    filepath = 'gene.counts'
    print '::> count file:'
    print '::> file path: %s'%(filepath)
    rare_words = rare_words_from_count_file(filepath)
    
    # create file from input file and change tags to _RARE_ for infrequent words
    inputfile = 'gene.train'
    inputfile_sans_rare_words = 'gene.train.with.rare'
    print '::> input file:'
    print '::> file path: %s'%(inputfile)
    replace_infrequent_words_in_input_file(inputfile,rare_words,inputfile_sans_rare_words)

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
def gene_dev():
    countfile = 'gene.counts.with.rare'
    genedevfile = 'gene.dev'
    outfile = 'gene_dev.p1.out'
    simple_gene_tagger(countfile,genedevfile,outfile)
    print 'end of gene_dev'

def gene_test():
    countfile = 'gene.counts.with.rare'
    genedevfile = 'gene.test'
    outfile = 'gene_test.p1.out'
    simple_gene_tagger(countfile,genedevfile,outfile)
    print 'end of gene_test'

def tests():
    print 'tests'
    w,rare = rare_words_from_count_file('gene.counts')
    print 'molecular' in rare
    assert('colestipol' in rare)
    assert('leukocytosis' in rare)
    assert('prominent' not in rare)
    assert('This' not in rare)
    assert(',"' not in rare)
    
    #replace_infrequent_words_in_input_file('gene.train',rare,'gene.train.with.rare')
    assert(compute_emission_params('gene.counts.with.rare','achieved','O')>0)
    assert(compute_emission_params('gene.counts.with.rare','achieved','O')<6.7e-05)
    assert(compute_emission_params('gene.counts.with.rare','achieved','O')>6.6e-05)
    assert(compute_emission_params('gene.counts.with.rare','achieved','error')==0)
    print 'all tests passed!'
    


def compute_emission_params(countfile,x,y):
    
    print 'compute emission params'
    print 'count file: %s'%(countfile)
    print 'word x: %s'%(x)
    print 'tag y %s'%(y)
    county = -1
    count_y_to_x = -1
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
    print 'Count(y -> x)'
    print 'Count(%s -> %s) : %s'%(y,x,count_y_to_x)
    print 
    print 'Count(y)'
    print 'Count(%s) : %s'%(y,county)
    print 
    print 'e(x|y)'
    
    print 'e(%s|%s) : %s'%(x,y,e)
    return e

def rare_words_from_count_file(filepath):
    'from a count file returns a list of words that are _RARE_'
    datafile = open(filepath, 'r')
    data = []
    rare_words = []
    for line in datafile:
        #print line
        split = line.split()
        count = int(split[0])
        token = str(split[1])
        if token == 'WORDTAG':
            tag = str(split[2])
            word = str(split[3])
            if count < 5:
                rare_words.append(word)
    return rare_words

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
                tag = '_RARE_'
                outfile.write(word+' '+tag+'\n')
            else:
                outfile.write(line)                
        else:
            outfile.write(line)
                
def replace_infrequent_words():
    # get rare words from file count
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

def tagger():
    countfile = 'gene.train.with.rare'
    genedevfile = 'gene.dev'
    outfile = 'gene-dev.p1.out'

def tests():
    rare = rare_words_from_count_file('gene.counts')
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
    

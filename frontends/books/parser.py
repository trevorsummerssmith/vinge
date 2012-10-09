import sys
from vinge.stop_words import STOP_WORDS
from vinge.vertex import LogLineVertex
from sets import Set
from datetime import datetime

def clean_up_word(w):
    return w.strip(' .,;:()[]{}!@#$%^&*-_+=|\\/`~"!?\'0123456789') 

def split_on_terminal_punc(string):
    sentences = [ string ]
    sentences = sum((s.split('.') for s in sentences), [])
    sentences = sum((s.split('!') for s in sentences), [])
    sentences = sum((s.split('?') for s in sentences), [])
    return sentences

def split_sentence_into_words(s):
    words = s.split()
    words = [ clean_up_word(w) for w in words ]
    return words

def find_proper_nouns(sentences, word_freqs):
    proper_freqs = {}
    improper_freqs = {}
    proper_nouns = []
    
    for s in sentences:
        for idx, word in enumerate(split_sentence_into_words(s)):
            lword = word.lower()
            uword = word.upper()
            proper = not ((word == uword) or (word == lword) or (idx == 0) or (lword in STOP_WORDS))
            improper = ((word == uword) or (word == lword) or (lword in STOP_WORDS))

            if proper:
#                print 'PROPER', word
                if word in proper_freqs:
                    proper_freqs[word] += 1
                else:
                    proper_freqs[word] = 1

            if improper:
                if word in improper_freqs:
                    improper_freqs[word] += 1
                else:
                    improper_freqs[word] = 1

    for w in proper_freqs:
        prop_freq = proper_freqs[w] 
        tot_freq = prop_freq  + improper_freqs.get(w, 0)

        if prop_freq > 0.5 * tot_freq:
            proper_nouns.append(w)
#            print '%d/%d PROPER: %s' % (proper_freqs[w], tot_freq, w)


    return Set(proper_nouns)

def parse_file_into_sentences(f):
    curpar = ''
    all_sentences = []
    word_freqs = {}
    
    for line in f:
        line = line.rstrip()
        words = line.split()
        words = [ clean_up_word(w) for w in words]

        for idx, word in enumerate(words):
            word = word.lower()

            if word in STOP_WORDS:
                continue

            if word in word_freqs:
                word_freqs[word] += 1
            else:
                word_freqs[word] = 1            


        if line == '':
            sentences = split_on_terminal_punc(curpar)
            all_sentences.extend(sentences)
            print 'nsentences', len(all_sentences)
            curpar = ''
        else:
            curpar = curpar + ' ' + line

    return all_sentences, word_freqs


def parse_log(f):
    log_lines = []
    tag_map = {}
    id_map = {}

    sentences, word_freqs = parse_file_into_sentences(f)
    proper_nouns = find_proper_nouns(sentences, word_freqs)

    for sentence_number, sentence in enumerate(sentences):
        vertex = LogLineVertex(sentence, sentence, sentence_number, '', 
                               datetime(1,1,1,1,1,1,sentence_number))
        log_lines.append(vertex)

        for word in split_sentence_into_words(sentence):
            if word in STOP_WORDS:
                continue

            if word in proper_nouns:
                this_map = id_map
            else:
                this_map = tag_map

            this_set = this_map.get(word, set())
            this_set.add(vertex)
            this_map[word] = this_set


    return (log_lines, tag_map, id_map)


f = open('data/sherlock.txt', 'r')
parse_log(f)
          

import sys, re
from vinge.stop_words import STOP_WORDS
from vinge.vertex import LogLineVertex
from tokens import TokenType
from backend import BackEnd
from sets import Set
from datetime import datetime

def clean_up_word(w):
    w = w.strip(' \.,;:()[]{}!@#$%^&*\-_+=|\\/`~"!?\'0123456789')
    w = w.replace('-','')
    w = w.replace('.','')
    return w

def _split_on_terminal_punc(string):
    sentences = [ string ]
    sentences = sum((s.split('.') for s in sentences), [])
    sentences = sum((s.split('!') for s in sentences), [])
    sentences = sum((s.split('?') for s in sentences), [])
    return sentences

def _split_sentence_into_words(s):
    words = s.split()
    words = [ clean_up_word(w) for w in words ]
    return words

class BooksBackEnd(BackEnd):
    def __init__(self, idfile):
        self.line_number = 0
        self.line_vertices = []
        self.tag_map = {}
        self.id_map = {}
        self.proper_nouns = set(line.rstrip() for line in open(idfile,'r'))

    def parse_line_into_vertex_and_msg(self, line):
        dt = datetime(1,1,1,1,1,1,self.line_number)
        return LogLineVertex(line, line, self.line_number, 'foo', dt), line
                               
    def parse_file_into_line_generator(self, fname):
        line = ''
        f = open(fname, 'r')

        for new_line in f:
            line = line + ' ' + new_line
            punc = ['.', '!', '?']
            split_failed = True

            while line != '' and split_failed:
                line = line.rstrip()

                # print 'LINE', line

                for p in punc:
                    before, period, after = line.partition(p)
                    if period != '':
                        # print 'BEFORE', before
                        # print 'PERIOD', period
                        # print 'AFTER', after

                        yield ''.join([before, period])
                        split_failed = False
                        cur_words = ''
                        line = after
                        break

                if split_failed:
                    cur_words = cur_words + ' ' + line
                    break

        f.close()

    def tokenize_msg(self, msg):
        words = msg.split()
        for word in words:
            clean_word = clean_up_word(word)
            clean_word = clean_word.lower()
            if clean_word == '':
                continue
            elif clean_word in STOP_WORDS:
                yield (word, TokenType.STOP_WORD)
            elif clean_word.title() in self.proper_nouns:
                yield (word, TokenType.ID)
            elif re.match('[\s=,]+', clean_word) is not None:
                yield (word, TokenType.SPLITTER)
            else:
                yield (word, TokenType.TAG)



        

# def find_proper_nouns(sentences, word_freqs):
#     proper_freqs = {}
#     improper_freqs = {}
#     proper_nouns = []
    
#     for s in sentences:
#         for idx, word in enumerate(split_sentence_into_words(s)):
#             lword = word.lower()
#             uword = word.upper()
#             proper = not ((word == uword) or (word == lword) or (idx == 0) or (lword in STOP_WORDS))
#             improper = ((word == uword) or (word == lword) or (lword in STOP_WORDS))

#             if proper:
# #                print 'PROPER', word
#                 if word in proper_freqs:
#                     proper_freqs[word] += 1
#                 else:
#                     proper_freqs[word] = 1

#             if improper:
#                 if word in improper_freqs:
#                     improper_freqs[word] += 1
#                 else:
#                     improper_freqs[word] = 1

#     for w in proper_freqs:
#         prop_freq = proper_freqs[w] 
#         tot_freq = prop_freq  + improper_freqs.get(w, 0)

#         if prop_freq > 0.5 * tot_freq:
#             proper_nouns.append(w)
# #            print '%d/%d PROPER: %s' % (proper_freqs[w], tot_freq, w)


#     return Set(proper_nouns)


          

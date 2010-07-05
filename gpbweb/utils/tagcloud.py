# coding: utf-8
# esto es muy, muy naive

import re
import es_stopwords
import unicodedata

def strip_accents(s):
   return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

CLEANER = re.compile(r'[^a-zA-Z0-9\r\n ]', re.IGNORECASE)
STOPWORDS = re.compile(r'\b([a-z]|\d+|%s)\b' % '|'.join([strip_accents(u) for u in es_stopwords.STOPWORDS]), re.IGNORECASE)

def _clean_document(document):
    document = strip_accents(document)
    document = CLEANER.sub('', document.lower()) # sacar todo lo que no alphanum o espacio
    document = STOPWORDS.sub('', document)
    return document

def make_tagcloud(documents, count=20):
    blob = ' '.join([_clean_document(d) for d in documents])
    tc = {}
    for w in blob.split(None):
        if tc.get(w): tc[w] += 1
        else: tc[w] = 1

    return list(sorted(tc.items(), key=lambda i: i[1], reverse=True))[:count]

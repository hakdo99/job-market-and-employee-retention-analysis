#*************************************
# Created by: Rovenna Chu (ytc17@sfu.ca)
# Purpose: this is for skill extraction from consolidated parquet files containing all job posts to list of skills for each post and job title
# This py file contains all functions for data processing (pre- and post-) and tokenization methods
# usage: from job_skill_extraction_data_processing import *
#*************************************

# Pre-processing Job Posts
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer
import contractions
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Prerequisite
#pip install -U pip setuptools wheel
#pip install -U spacy
#python -m spacy download en_core_web_lg

import spacy
from spacy import displacy
from collections import Counter
from spacy.matcher import Matcher
from spacy.util import filter_spans
from spacy.tokens import Span
import en_core_web_lg
nlp = en_core_web_lg.load()


import pandas as pd
import numpy as np

def data_preparation_preprocessing(df):
    # Data Pre-processing: most processing / transformation part has already done in web scrapping
    df['description'] = df['description'].apply(lambda x: contractions.fix(str(x)))
    import regex as re
    df['description'] = df['description'].str.lower()
    df['description'] = df['description'].apply(lambda x: re.sub(r'[^-\w\d\s\n\.\!\?\;\,\']+', '', x))
    #df['description'] = df['description'].apply(lambda x: re.sub(r'[\.\!\?\;\']+', '.', x))
    df['description'] = df['description'].apply(lambda x: re.sub(r'\n+', '.', x))
    # amp to & and "andor" to "and or"
    df['description'] = df['description'].str.replace(r'\bandor\b', ' and or ')
    df['description'] = df['description'].str.replace(r'\bamp\b', ' and ')
    #df['sentence'] = df['description'].str.split("\n")

    return df
    
def data_preparation_postprocessing(df):

    df['text'] = df.text.str.strip().str.strip(".").str.strip().str.strip(",").str.strip().str.strip("-").str.strip()
    df['text'] = df.text.str.strip().str.strip(".").str.strip().str.strip(",").str.strip().str.strip("-").str.strip()

    df['text'] = df['text'].apply(lambda s: s.replace("a ", '', 1) if s.startswith("a ") else s)
    df['text'] = df['text'].apply(lambda s: s.replace("an ", '', 1) if s.startswith("an ") else s)
    df['text'] = df['text'].apply(lambda s: s.replace("this ", '', 1) if s.startswith("this ") else s)
    df['text'] = df['text'].apply(lambda s: s.replace("the ", '', 1) if s.startswith("the ") else s)
    df['text'] = df['text'].apply(lambda s: s[0:len(s)-2] if s.endswith(" a") else s)
    df['text'] = df['text'].apply(lambda s: s[0:len(s)-3] if s.endswith(" an") else s)
    import string
    df['text'] = df['text'].apply(lambda s: ''.join(filter(lambda x: x in string.printable, s)))
    df['text'] = df['text'].apply(lambda s: s.replace(".", ' '))

    df['text'] = df['text'].apply(lambda s: s.replace("a ", '', 1) if s.startswith("a ") else s)
    df['text'] = df['text'].apply(lambda s: s.replace("an ", '', 1) if s.startswith("an ") else s)
    df['text'] = df['text'].apply(lambda s: s.replace("this ", '', 1) if s.startswith("this ") else s)
    df['text'] = df['text'].apply(lambda s: s.replace("the ", '', 1) if s.startswith("the ") else s)
    df['text'] = df['text'].apply(lambda s: s[0:len(s)-2] if s.endswith(" a") else s)
    df['text'] = df['text'].apply(lambda s: s[0:len(s)-3] if s.endswith(" an") else s)
    df['text'] = df['text'].apply(lambda s: ''.join(filter(lambda x: x in string.printable, s)))
    df['text'] = df['text'].apply(lambda s: s.replace(".", ' '))

    # Added by Kukpyo (Andrew) Han to remove empty texts
    df = df[df['text']!=""]

    return df
    
# Extraction of Identified POS Patterns


experience_qualifiers = ['previous', 'prior', 'following', 'recent', 'the above', 'past',
                         
                         'proven', 'demonstrable', 'demonstrated', 'relevant', 'significant', 'practical',
                         'essential', 'equivalent', 'desirable', 'required', 'considerable', 'similar',
                         'working', 'specific', 'qualified', 'direct', 'hands on', 'handson', 
                         
                         'strong', 'solid', 'good', 'substantial', 'excellent', 'the right', 'valuable', 'invaluable',
                         
                         'some', 'any', 'none', 'much', 'extensive', 'no', 'more',
                         'your', 'their',
                         'years', 'months',
                         'uk',
                        ]

stopwords = ['a', 'an', '*', '**', '•', 'this', 'the', ':', 'Skills']

experience_qualifier_pattern = rf'\b(?:{"|".join(experience_qualifiers)})\b'

EXP_TERMS = ['experience', 'experienced', 'expertise', 'expert', 'familiar', 'familiarity', 'ability', 'able', 'required', 'is required', 'knowledge', 'understanding']

# extract noun phrase to the left of the keywords using SpaCy's noun_chunks
def extract_noun_phrase(doc, label_list=None):
    label_list = ['experience'] if label_list is None else label_list
    for item in label_list:    
        label = item
        for np in doc.noun_chunks:
            if np[-1].lower_ == label.lower():
                if len(np) > 1:
                    yield label.upper(), np[0].i, np[-1].i
# extract by looking to the right for a preposition (e.g. in/with) and then looking for its object and extracting the whole left subtree
def extract_adp(doc, label_list=None):
    label_list = ['experience'] if label_list is None else label_list
    for item in label_list:
        label = item
        for tok in doc:
            if tok.lower_ == label.lower():
                for child in tok.rights:
                    if child.dep_ == 'prep':
                        for obj in child.children:
                            if obj.dep_ == 'pobj':
                                yield label.upper(), obj.left_edge.i, obj.i+1
# extract by looking for a phrase like "Experience in/with/using" and then the noun phrase
def extract_adp_2(doc, label_list=None):
    label_list = ['experience'] if label_list is None else label_list
    for item in label_list:
        label = item
        for np in doc.noun_chunks:
            start_tok = np[0].i
            if start_tok >= 2 and doc[start_tok - 2].lower_ == label.lower() and doc[start_tok - 1].pos_ == 'ADP':
                yield label.upper(), start_tok, start_tok + len(np)
def get_conjugations(tok):
    new = [tok]
    while new:
        tok = new.pop()
        yield tok
        for child in tok.children:
            if child.dep_ == 'conj':
                new.append(child)
def get_left_span(tok, label='', include=True):
    offset = 1 if include else 0
    idx = tok.i
    while idx > tok.left_edge.i:
        if tok.doc[idx - 1].pos_ in ('NOUN', 'PROPN', 'ADJ', 'X', 'VERB'):
            idx -= 1
        else:
            break
    return label, idx, tok.i+offset
# expanding conjugations
def extract_adp_conj(doc, label_list=['experience']):
    for item in label_list:
        label = item
        for tok in doc:
            if tok.lower_ in EXP_TERMS:
                for child in tok.rights:
                    if child.dep_ == 'prep':
                        for obj in child.children:
                            if obj.dep_ == 'pobj':
                                for conj in get_conjugations(obj):
                                    yield get_left_span(conj, label.upper())
# extract verb followed by an adposition followed by the Noun, e.g Experience dealing with business clients
def extract_verb_maybeadj_noun(doc, label_list=None):
    label_list = ['experience'] if label_list is None else label_list
    for item in label_list:
        label = item
        for tok in doc:
            if tok.lower_ in EXP_TERMS:
                for child in tok.rights:
                    if child.dep_ == 'acl':
                        for gc in child.children:
                            if gc.dep_ == 'prep':
                                for ggc in gc.children:
                                    if ggc.dep_ == 'pobj':
                                        for c in get_conjugations(ggc):
                                            yield get_left_span(c, label.upper())
                            elif gc.dep_ == 'dobj':
                                for c in get_conjugations(gc):
                                    yield get_left_span(c, label.upper())

def extract_df(df, *extractors, n_max=None, **kwargs):
    if n_max is None:
        n_max = len(df)
    ent_df = pd.DataFrame(list(get_extractions(df.description[:n_max], *extractors, **kwargs)),
                          columns=['text', 'docidx', 'start', 'end', 'label', 'sent_start', 'sent_end'])
    return ent_df.merge(df, how='left', left_on='docidx', right_index=True)

def get_extractions(examples, *extractors, **kwargs):
    # Could use context instead of enumerate
    for idx, doc in enumerate(nlp.pipe(examples, batch_size=100, disable=['ner'])):
        for ent in filter_spans([Span(doc, start, end, label) for extractor in extractors for label, start, end in extractor(doc, **kwargs)]):
            sent = ent.root.sent
            yield ent.text, idx, ent.start, ent.end, ent.label_, sent.start, sent.end

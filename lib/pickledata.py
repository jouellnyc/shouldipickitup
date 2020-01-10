#!/usr/bin/env python3

import pickle


datafile = "../data/sf.pickle"

def save(mongodoc, file=datafile):
    with open(file,'wb') as fh:
        pickle.dump(mongodoc,fh)

def loadit(file=datafile):
    try:
        with open(file,'rb') as fh:
            mongodoc = pickle.load(fh)
    except IOError as e:
        raise
    except Exception as e:
        raise ValueError('Bad pickle data')
    else:
        return mongodoc

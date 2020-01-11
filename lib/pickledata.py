#!/usr/bin/env python3


""" pickledata.py - return locally stored data

- This script module pulls up failsafe data to show a user if Mongo is down.

-This script requires the pickle module.

-This file is meant to be imported as a module.
 (mainly by crawler.py on the cmd line)

- It contains the following functions:
    *save   - write pickle data to file
    *loadit - read pickle data to file
"""

import pickle


datafile = "../data/sf.pickle"

def save(mongodoc, file=datafile):
    """
    Write pickle data to file

    Parameters
    ----------
    mongodoc
        MongoDB specific doc
    file:
        str - name of local file

    Returns
    -------
    Nothing if successful
    Errors pass to caller
    """
    with open(file,'wb') as fh:
        pickle.dump(mongodoc,fh)

def loadit(file=datafile):
    """
    Read pickle data from  file

    Parameters
    ----------
    file:
        str - name of local file

    Returns
    -------
    mongodoc
        MongoDB specific doc
    """
    try:
        with open(file,'rb') as fh:
            mongodoc = pickle.load(fh)
    except IOError as e:
        raise
    except Exception as e:
        raise ValueError('Bad pickle data')
    else:
        return mongodoc

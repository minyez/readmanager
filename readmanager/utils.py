#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Utilities used in the main program readmana

TODO
----
1. Open the note and pdf book from applications
2. Create/Modify book item
'''

from __future__ import print_function, absolute_import
import os
import sys
import json
from readmanager.presenter import presenter
from readmanager.manager import manager

def __init_default_config(pathConfig):
    '''
    Initialize default config.json and create the database directory, if not exist
    The initialization involve setting the JSON and note databases, which will be
    set interactively. Default can be used.
    '''
    # default database path
    dirShare = "~/.local/share/readmana"
    dbJSONDe = os.path.expanduser(os.path.join(dirShare, "JSON"))
    dbNoteDe = os.path.expanduser(os.path.join(dirShare, "note"))
     
    try:
        os.makedirs(os.path.dirname(pathConfig))
    except FileExistsError:
        pass
    finally:
        # convert to absolute path
        # direct enter to use default
        dbJSON = input("JSON database (enter for default: %s)\n--> " % dbJSONDe)
        if dbJSON != '':
            dbJSON = os.path.expanduser(dbJSON.split()[0])
        else:
            dbJSON = dbJSONDe
        dbNote = input("note database (enter for default: %s)\n--> " % dbNoteDe)
        if dbJSON != '':
            dbNote = os.path.expanduser(dbNote.split()[0])
        else:
            dbNote = dbNoteDe
    # check JSON and note databases
    try:
        os.makedirs(dbJSON)
        print("JSON database created: %s" % dbJSON)
    except FileExistsError:
        print("JSON database exist: %s" % dbJSON)
     
    try:
        os.makedirs(dbNote)
        print("Note database created: %s" % dbNote)
    except FileExistsError:
        print("Note database exist: %s" % dbNote)
     
    # dump to config file
    with open(pathConfig, 'w') as hFileOut:
        json.dump({"dbJSON":dbJSON, "dbNote":dbNote}, hFileOut, indent=2)
    print("Default config file initialized: %s" % pathConfig)

# ==============================================================================
def get_config():
    '''
    get the config file for manager, which should be a json file
    The environment variable `READMANA_CONFIG` will be used, if defined and exists.
    Otherwise, pathConfigDe will be used.

    Returns
    -------
    str : the path of config file
    '''
    pathConfigDe = os.path.expanduser("~/.config/readmana/config.json")
    fUseConfigDe = True

    try:
        pathConfig = os.path.expanduser(os.environ["READMANA_CONFIG"])
        fUseConfigDe = False
        print("Use READMANA_CONFIG: %s" % pathConfig)
    except KeyError:
        print("Environment variable READMANA_CONFIG undefined. Use default.")
        # use default config file
        pathConfig = pathConfigDe
     
    if not os.path.isfile(pathConfig):
        if fUseConfigDe:
            print("The default config.json is not found. Initializing...")
            __init_default_config(pathConfig)
        else:
            raise FileNotFoundError("Custom READMANA_CONFIG file is not found.")

    return pathConfig

# ===========================================================
# TODO open utilities
def open_book(bm, iBI):
    '''
    Parameters
    ----------
    bm : manager instance
    iBI : int
    '''
    assert isinstance(bm, manager)
    book = bm[iBI]

# ===========================================================
# TODO Manager utilities
def modify(bm):
    '''
    Modify an book item
    '''
    assert isinstance(bm, manager)
    # input n, tag, newValue
    n, tag, newValue = input("Type (#, tag, newValue)")
    iBI = n - 1
    bm.change_tag_book(iBI, tag, newValue)

def create_new(bm):
    '''
    create a new book item
    '''
    assert isinstance(bm, manager)

# ===========================================================
# TODO Presenter utilities
def show_item(pre):
    '''
    Show the a book item
    '''
    assert isinstance(pre, presenter)

def print_pre(pre):
    '''
    Show presenter
    '''
    assert isinstance(pre, presenter)
    pre.show()

# ===========================================================
# TODO Manager & Presenter utilities
def find_item(bm, pre):
    '''
    Find a particular item
    '''
    assert isinstance(bm, manager)
    assert isinstance(pre, presenter)
    # ask key tag to find
    # ask find criterion

# ===========================================================
# TODO Exit utilities
def save_exit(bm):
    '''
    Save all jsons and exit

    TODO
    ----
    Update logs
    '''
    assert isinstance(bm, manager)
    bm.update_json_all()
    sys.exit(0)

def exit_wo_save():
    '''
    Exit without saving anything
    '''
    sys.exit(-1)

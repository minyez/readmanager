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
import subprocess as sp
from readmanager.presenter import presenter
from readmanager.manager import manager
from readmanager.bookitem import book_item

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

def flush_screen():
    '''
    flush the screen
    '''
    os.system('clear')

# ===========================================================
# TODO open utilities for linux and windows
def open_book(bm, iBI):
    '''
    Open the book and note with the default opener in subprocess
    and ask for page and log update
    Note: currently support macOS only

    Parameters
    ----------
    bm : manager instance
    iBI : int
        the index of the book item in bm
    '''
    assert isinstance(bm, manager)
    assert iBI in range(len(bm))
    book = bm.books[iBI]
    stateNote, stateFile = bm.get_note_source_state(iBI)
    pathNote, pathFile = bm.get_note_path(iBI), bm.books[iBI].get_source()
    extNote = book.get_tag("noteType").lower()
    extFile = book.get_source_ext()

    openSystem = {"darwin": __open_book_darwin, }
    platform = sys.platform.lower()

    print("--  Try to open note from: %s" % pathNote)
    print("--  Try to open file from: %s" % pathFile)
    if platform in openSystem:
        openSystem[platform](bm, (stateNote, stateFile), (pathNote, pathFile), (extNote, extFile))
    else:
        print("--  Open utility for %s is not supported. Please open manually") 
    __fUpdate = input("--  Update page? (y/N)").strip().lower()
    if __fUpdate in ["y", "yes"]:
        while True:
            __pageNew = input("    %d --> (max %d)" % (book.pageCurrent, book.pageTotal))
            try:
                __pageNew = int(__pageNew.split()[0])
                break
            except ValueError:
                pass
            except IndexError:
                pass
        book.update_current_page(__pageNew)
        book.update_last_read()
        book.update_log()
        book.update_json()
        print("--  Log, JSON updated :)")
    else:
        print("--  Maybe next time :)")

def __open_book_darwin(bm, states, paths, exts):
    '''
    Open the book and note with the default opener in subprocess for macOS

    Parameters
    ----------
    bm : manager instance
    states : 2-member tuple of bool or None
        states of note and source file
    paths: 2-member tuple of str
        paths of note and source file
    exts : 2-member tuple of str
        extensions of note and source file
    '''

    stateNote, stateFile = states
    pathNote, pathFile = paths
    extNote, extFile = exts

    openerNote = ["open", pathNote]
    openerFile = ["open", pathFile]
    if extFile == '':
        # opener with Textedit for file without extension
        openerFile.append("-e")
    if extNote in bm.opener:
        if bm.opener[extNote] is not None:
            openerNote.extend(["-a", bm.opener[extNote]])
    if extFile in bm.opener:
        if bm.opener[extFile] is not None:
            openerFile.extend(["-a", bm.opener[extFile]])

    # start opening by calling subprocess
    if stateNote:
        noteProc = sp.Popen(openerNote)
    if stateFile:
        fileProc = sp.Popen(openerFile)

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

# TODO create_new
def create_new(bm):
    '''
    create a new book item
    '''
    assert isinstance(bm, manager)
    return
   
    while True:
        newJSONName = input("Enter filename of new item (wo .json): ").strip()
        if newJSONName.lower().endswith(".json"):
            newJSONName = newJSONName[:-5]
        newJSONPath = os.path.join(bm.dbJSON, newJSONName) + ".json"
        # check duplicate
        if os.path.isfile(newJSONPath):
            print("Found json with the same name in database. Retry.")
        else:
            break
    newBookItem = book_item(newJSONPath, create_new=True)
    # update tags
    __author = input("Author: ").strip()
    __title = input("Title: ").strip()
    __pageTotal = input("Total #pages: ").strip()
    # noteType create new
    # timeLastMod
    # dateAdded
    # datePlan
    # update log
    bm.add_new_book(newBookItem)

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
def save_exit(bm):
    '''
    Save all jsons and exit
    '''
    assert isinstance(bm, manager)
    bm.update_json_all()
    sys.exit(0)

def exit_wo_save():
    '''
    Exit without saving anything
    '''
    sys.exit(-1)

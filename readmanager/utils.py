#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Utilities used in the main program readmana
'''

from __future__ import print_function, absolute_import
import os
import sys
import re
import json
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
        os.makedirs(os.path.join(dbJSON, "archive"))
        print("JSON and archive database created: %s" % dbJSON)
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
    if sys.platform.lower() == "windows":
        os.system('cls')
    else:
        os.system('clear')

def ask_for_sure(tipStr, verbose=True):
    '''
    Ask the user for ensuring some action, namely "tipStr (y/N) "

    Parameters
    ----------
    tipStr : str
        the string of tip that is shown to the use
    verbose : bool
        flag for asking. Function will always return True if verbose is set False

    Returns
    -------
    bool : 
        When verbose, True if get "y" or "yes", False otherwise
        When not verbose, always True
    '''
    if verbose:
        flag = input("%s (y/N) " % tipStr).strip().lower()
        if flag in ["y", "yes"]:
            return True
        return False
    return True

# ===========================================================
def modify(bm):
    '''
    Modify an book item
    '''
    assert isinstance(bm, manager)
    while True:
        n = input("--  Which book to modify (#, 0 to return): ")
        try:
            n = int(n)
            if n == 0:
                break
        except ValueError:
            print("    Invalid input. Break out.")
            break
        iBI = n - 1

        __dictOption = { \
                "nd": __modify_note_dir, \
                "nt": __modify_note_type, \
                "pd": __modify_plan_date, \
                "tp": __modify_total_page, \
                "sp": __modify_source_path, \
                "a": __modify_author, \
                "t": __modify_title, \
                "at": __add_tag, \
                "dt": __delete_tag, \
                #"r": __add_remark, \
                }
        __book = bm[iBI]
        __helpStr = ''
        for key in sorted(__dictOption.keys()):
            __helpStr += "    %2s : %s\n" % (key, get_func_doc(__dictOption[key]))

        __selection = input(__helpStr + "--  select: ").strip()
        try: 
            __dictOption[__selection](__book)
        except KeyError:
            print("    Invalid input. Break out.")
            break

# ===========================================================
# key modify utilities
def __modify_note_dir(BI):
    '''
    modify the Note Directory of book

    Paramters
    ---------
    BI : book_item instance
    '''
    jsonName = os.path.basename(BI.filepath)[:-5]
    noteDirStr = input("    Note directory (enter for %s): " % jsonName).strip()
    if noteDirStr == '':
        __noteDirStr = "-/" + jsonName
    else:
        __noteDirStr = noteDirStr
    BI.update_note_dir(__noteDirStr)

def __modify_note_type(BI):
    '''
    modify the Note Type

    Paramters
    ---------
    BI : book_item instance
    '''
    __noteType = input("    Note type (%s):" % ", ".join(BI.noteSupportType)).strip()
    BI.update_note_type(__noteType)

def __modify_plan_date(BI):
    '''
    modify the plan date of book reading

    Paramters
    ---------
    BI : book_item instance
    '''
    __datePlan = input("    Plan date (yyyy-mm-dd, enter to skip): ").strip()
    if __datePlan != "":
        BI.update_date("plan", __datePlan)

def __modify_total_page(BI):
    '''
    modify the number of Total Pages of the book

    Paramters
    ---------
    BI : book_item instance
    '''
    while True:
        __pageTotal = input("    Total #pages: ").strip()
        try:
            BI.update_page("total", int(__pageTotal))
            break
        except ValueError:
            print("    Bad input. Retry.")

def __modify_source_path(BI):
    '''
    modify the Path of the local Source file of book

    Paramters
    ---------
    BI : book_item instance
    '''
    __sourcePath = input("    Local book file path (Enter if no e-source): ").strip()
    BI.update_source_path(__sourcePath)

def __modify_author(BI):
    '''
    modify the Author

    Paramters
    ---------
    BI : book_item instance
    '''
    __author = input("    Author: ").strip()
    BI.update_author(__author)

def __modify_title(BI):
    '''
    modify the Title

    Paramters
    ---------
    BI : book_item instance
    '''
    __title = input("    Title: ").strip()
    BI.update_title(__title)

def __add_tag(BI):
    '''
    Add new Tags 

    Paramters
    ---------
    BI : book_item instance
    '''
    __listTag = []
    __strTag = input("    new tags (separate by comma): ")
    for tag in re.split(r'[,\n]', __strTag):
        if tag.strip():
            __listTag.append(tag.strip())
    BI.update_tag(__listTag, fAdd=True)

def __delete_tag(BI):
    '''
    Delete Tags

    Paramters
    ---------
    BI : book_item instance
    '''
    __tagsCurrent = BI.get_tag()
    print("    Tags now: '%s'" % "', '".join(__tagsCurrent))
    __listTag = input("    tags to delete (separate by space): ").split()
    BI.update_tag(__listTag, fAdd=False)
# ===========================================================

def add_remark(bm):
    '''
    add quick Remark for today

    Paramters
    ---------
    bm : manager instance
    '''
    n = input("--  Which book to remark (#, 0 to return): ")
    try:
        n = int(n)
        if n == 0:
            return
    except ValueError:
        print("    Invalid input. Break out.")
        return
    iBI = n - 1
    __book = bm.books[iBI]
    __remark = input("    New remark (be short, otherwise write it in note): \n    > ").strip()
    __book.update_remark(__remark)

def get_func_doc(func):
    '''
    get the main doc line of a function

    Parameters
    ----------
    modFunc : function object

    Returns
    -------
    str : the main doc line of func.
        "N/A" if doc string is not set
    '''
    try:
        docSplit = func.__doc__.split("\n")
    except AttributeError:
        return "N/A"
    docSplit = [s.strip() for s in docSplit]
    if docSplit[0] == '':
        return docSplit[1]
    return docSplit[0]

# ===========================================================
def create_new(bm):
    '''
    Create a new book item

    Paramters
    ---------
    bm : manager instance
    '''
    assert isinstance(bm, manager)
  
    newJSONPath = __generate_new_json_path(bm)
    newBI = book_item(newJSONPath, create_new=True)
    # update tags
    __modify_author(newBI)
    __modify_title(newBI)
    __modify_total_page(newBI)
    __modify_note_dir(newBI)
    __modify_note_type(newBI)
    __modify_source_path(newBI)
    __add_tag(newBI)
    newBI.update_last_time("mod")
    newBI.update_date("added")
    __modify_plan_date(newBI)
    newBI.update_log()
    bm.add_new_book(newBI)
    # Ask for saving
    __fSave = ask_for_sure("--  Save to json?")
    if __fSave:
        newBI.update_json()
        print("--  Saved new json at %s " % newBI.filepath)
        __fNewNote = __create_new_note(bm, -1, False)
        if __fNewNote:
            print("--  Create new note at %s " % bm.get_note_path(-1))

def __create_new_note(bm, iBI, verbose=True):
    '''
    Creating new note for a book item

    Paramters
    ---------
    bm : manager instance
    iBI : int
        the index of book item for note creation
    verbose : bool
    '''
    noteState = bm.get_note_source_state(iBI)[0]
    if noteState is None:
        if verbose:
            print("    Need to first specify the note directory and type.")
        return False

    notePath = bm.get_note_path(iBI)
    if noteState:
        if verbose:
            print("    Note exists: %s" % notePath)
            return False
    else:
        if verbose:
            print("    Note not found: %s" % notePath)
            return False
        flag = ask_for_sure("    Create an empty new?", verbose=verbose)
        if flag:
            try:
                os.makedirs(os.path.dirname(notePath))
            except FileExistsError:
                pass
            with open(notePath, 'w') as hFileOut:
                pass
            return True
    return False

def __generate_new_json_path(bm):
    '''
    Generate path for a new json file with name from input. Check duplicate

    Paramters
    ---------
    bm : manager instance
    '''
    while True:
        newJSONName = input("--  Enter filename of new item (wo .json): ").strip()
        if newJSONName.lower().endswith(".json"):
            newJSONName = newJSONName[:-5]
        newJSONPath = os.path.join(bm.dbJSON, newJSONName) + ".json"
        # check duplicate
        if os.path.isfile(newJSONPath):
            print("    Found json with the same name in database. Retry.")
        else:
            break
    return newJSONPath

# ===========================================================
# TODO show_item_details
def show_item_details(pre):
    '''
    Show the details of a book item (TODO)
    '''
    assert isinstance(pre, presenter)

def print_pre(pre):
    '''
    print the Presenter
    '''
    assert isinstance(pre, presenter)
    pre.rebuild()
    pre.show()

# TODO show_tags
def show_tags(pre):
    '''
    show all existing Tags of the books (TODO)

    Paramters
    ---------
    pre : presenter instance
    '''
    assert isinstance(pre, presenter)

# ===========================================================
def find_item(pre):
    '''
    Find a particular item by title, author or tag
    '''
    assert isinstance(pre, presenter)
    # ask find criterion
    __filterTitle = input("--  Title filter? (Enter to skip) ").split()
    __filterAuthor = input("--  Author filter? (Enter to skip) ").split()
    __filterTag = input("--  Tag filter? (Enter to skip) ").split()
    __fAnd = ask_for_sure("--  'AND' search?")
    pre.rebuild()
    pre.show(__filterTitle, __filterAuthor, __filterTag, __fAnd)

def sort_items(bm, pre):
    '''
    Sort book items
    '''
    assert isinstance(bm, manager)
    assert isinstance(pre, presenter)

    __key = input("--  Sort by? [(T)itle, (A)uthor, last(M)od, last(R)ead] ").strip()
    __keyTitle = ["t", "T", "title", ]
    __keyAuthor = ["a", "A", "author", ]
    __keyLastMod = ["m", "M", "lastmod", ]
    __keyLastRead = ["r", "R", "lastread", ]

    if __key in __keyTitle:
        bm.sort_books_by("title")
    if __key in __keyAuthor:
        bm.sort_books_by("author")
    if __key in __keyLastMod:
        bm.sort_books_by("mod")
    if __key in __keyLastRead:
        bm.sort_books_by("read")

    pre.rebuild()
    pre.show()

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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Routines used to open the book and note files
'''

from __future__ import print_function, absolute_import
import sys
import subprocess as sp
from readmanager.manager import manager
from readmanager.utils import ask_for_sure

# ===========================================================
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
    extNote = book.get_key("noteType").lower()
    extFile = book.get_source_ext()

    openSystem = { \
            "darwin": __open_book_darwin, \
    #        "windows": __open_book_windows, \
    #        "linux": __open_book_linux, \
            }
    platform = sys.platform

    print("--  Try to open note from: %s" % pathNote)
    print("--  Try to open file from: %s" % pathFile)
    if platform.lower() in openSystem:
        openSystem[platform.lower()](bm, \
                                     (stateNote, stateFile), \
                                     (pathNote, pathFile), \
                                     (extNote, extFile))
    else:
        print("--  Open utility for %s is not supported. Please open manually." % platform) 
     
    __fUpdate = ask_for_sure("--  Update page?")
    if __fUpdate:
        while True:
            __pageNew = input("    %d --> (max %d) " % (book.pageCurrent, book.pageTotal))
            try:
                __pageNew = int(__pageNew.split()[0])
                if __pageNew > book.pageTotal or __pageNew < 0:
                    continue
                break
            except ValueError:
                pass
            except IndexError:
                pass
        book.update_page("current", __pageNew)
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

# TODO Windows open utility
def __open_book_windows(bm, states, paths, exts):
    '''
    Open the book and note with the default opener in subprocess for Windows
    
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

    openerNote = ["", pathNote]
    openerFile = ["", pathFile]

    if extFile == '':
        # opener with Textedit for file without extension
        openerFile.append("-e")
    if extNote in bm.opener:
        if bm.opener[extNote] is not None:
            openerNote.extend(["", bm.opener[extNote]])
    if extFile in bm.opener:
        if bm.opener[extFile] is not None:
            openerFile.extend(["", bm.opener[extFile]])

    # start opening by calling subprocess
    if stateNote:
        noteProc = sp.Popen(openerNote)
    if stateFile:
        fileProc = sp.Popen(openerFile)

# TODO Linux open utility
def __open_book_linux(bm, states, paths, exts):
    '''
    Open the book and note with the default opener in subprocess for Linux

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

    openerNote = ["", pathNote]
    openerFile = ["", pathFile]

    if extFile == '':
        # opener with Textedit for file without extension
        openerFile.append("")
    if extNote in bm.opener:
        if bm.opener[extNote] is not None:
            openerNote.extend(["", bm.opener[extNote]])
    if extFile in bm.opener:
        if bm.opener[extFile] is not None:
            openerFile.extend(["", bm.opener[extFile]])

    # start opening by calling subprocess
    if stateNote:
        noteProc = sp.Popen(openerNote)
    if stateFile:
        fileProc = sp.Popen(openerFile)


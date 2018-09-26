# -*- coding: utf-8 -*-
'''
the presenter class is defined to show the reading and note progress of books
'''

from __future__ import print_function, absolute_import
import os
from readmanager.manager import manager

class presenter:
    '''
    presenter class
    '''
    __lenIndex = 3
    __lenTitle = 64
    __lenAuthor = 48
    __lenProgBar = 102
    __lenProg = 3
    __lenPageTot = 5
    __lenNoteMark = 1
    __lenSourceMark = 1
    
    __colorHead = '\033[30;47m'
    __colorItem = '\033[0m'
    
    __formatItem = "%s%-*s %-*.*s %-*.*s %*s %-*s %-*s %-*s %*s%s"
    __head = __formatItem % (\
            __colorHead, \
            __lenIndex, "#", \
            __lenAuthor, __lenAuthor, "Author", \
            __lenTitle, __lenTitle, "Title", \
            __lenPageTot, "Pages", \
            __lenNoteMark, "N", \
            __lenSourceMark, "S", \
            __lenProgBar, "Progress", \
            __lenProg, "%", \
            '\033[0m', \
            )

    def __init__(self, bookmanager):
        '''
        Initialize
        '''
        assert isinstance(bookmanager, manager)
        self.__manager = bookmanager
        self.__build()

    def __build(self):
        '''
        Build the items to show
        '''
        self.__nBooks = len(self.__manager)
        self.__titles = self.__manager.get_tags("title")
        self.__authors = self.__manager.get_tags("author")
        self.__progress = self.__manager.get_progress()
        self.__pages = self.__manager.get_tags("pageTotal")
        self.__localSources = self.__manager.get_tags("bookLocalSource")

    def rebuild(self):
        '''
        Rebuild the items to show, when the manager has been refreshed
        '''
        self.__build()

    def show(self):
        '''
        Show the presenter
        '''
        print("=" * (len(self.__head) - len(self.__colorHead) - len('\033[0m')))
        print(self.__head)
        for i in range(self.__nBooks):
            self.print_item_status(i)
        print("=" * (len(self.__head) - len(self.__colorHead) - len('\033[0m')))

    def print_item_status(self, iBI):
        '''
        Print the status, i.e. index, author, title, note & source status, progress bar and progress

        Parameters
        ----------
        iBI : int
            the index of item in self.__manager.books
        '''
        print(self.__formatItem % (
            self.__colorItem, \
            self.__lenIndex, iBI + 1, \
            self.__lenAuthor, self.__lenAuthor, self.__authors[iBI], \
            self.__lenTitle, self.__lenTitle, self.__titles[iBI], \
            self.__lenPageTot, self.__pages[iBI], \
            self.__lenNoteMark, get_file_state(self.__manager.get_note_path(iBI)), \
            self.__lenSourceMark, get_file_state(self.__localSources[iBI]), \
            self.__lenProgBar, get_prog_barstr(self.__progress[iBI], self.__lenProgBar), \
            self.__lenProg, self.__progress[iBI][0], \
            '\033[0m', \
            ))

def get_file_state(notePath):
    '''
    Parameters
    ----------
    notePath : str
        the path of note directory

    Returns
    -------
    str : notation for note, ✗ for None, ◆ if the path exists and ? otherwise 
    '''
    if notePath is None:
        return "✗"
    if os.path.isfile(notePath):
        return "◆"
    return "?"

def get_prog_barstr(prog, totalBarLen):
    '''
    get progress bar string

    Parameters
    ----------
    progPercent : list of 2 int
        a percentage of current and plan progress
    totalBarLen : int

    Returns
    -------
    str : progress bar for one book item
    '''
    assert totalBarLen > 2
    assert len(prog) == 2
    assert 0 <= prog[0] <= 100
    assert 0 <= prog[1] <= 100
    colorEnd = '\033[0m'
    colorPlan = '\033[93m'
    colorCurrent = '\033[92m'

    nCurrent = int(prog[0] / 100.0 * (totalBarLen - 2))
    nPlan = int(prog[1] / 100.0 * (totalBarLen - 2))

    # overdue
    if nPlan > 100:
        nPlan = 100
        colorPlan = '\033[31m'

    colorSmall = colorCurrent
    nSmall = nCurrent
    colorBig = colorPlan
    nBig = nPlan

    if nCurrent > nPlan:
        colorSmall, colorBig = colorBig, colorSmall
        nSmall, nBig = nBig, nSmall

    return "|%s%-*s%s%-*s%s%-*s|" % ( \
            colorSmall, nSmall, "=" * nSmall, \
            colorBig, nBig - nSmall, "-" * (nBig - nSmall), \
            colorEnd, \
            totalBarLen - 2 - nBig, "." * (totalBarLen - 2 - nBig) \
            )

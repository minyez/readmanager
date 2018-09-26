# -*- coding: utf-8 -*-
'''
the presenter class is defined to show the reading and note progress of books
'''

from __future__ import print_function, absolute_import
#import os
from readmanager.manager import manager
try:
    import curses
except ImportError:
    pass

class presenter:
    '''
    presenter class
    '''
    # TODO get terminal widths and allocate proportionally for title, author and ProgBar
    __lenIndex = 3
    __lenTitle = 64
    __lenAuthor = 48
    __lenProgBar = 102
    __lenProg = 3
    __lenPageTot = 5
    __lenNoteMark = 1
    __lenSourceMark = 1
  
    __use256 = False
    # use curses to check if 256 term
    try:
        curses.setupterm()
        if curses.tigetnum("colors") == 256:
            __use256 = True
    # pass if failed to load curses
    except NameError:
        pass

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
        self.__progress = self.__manager.get_progress_all()
        self.__pages = self.__manager.get_tags("pageTotal")

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
        noteState, sourceState = self.__manager.get_note_source_state(iBI)
        print(self.__formatItem % (
            self.__colorItem, \
            self.__lenIndex, iBI + 1, \
            self.__lenAuthor, self.__lenAuthor, self.__authors[iBI], \
            self.__lenTitle, self.__lenTitle, self.__titles[iBI], \
            self.__lenPageTot, self.__pages[iBI], \
            self.__lenNoteMark, get_file_state_marker(noteState), \
            self.__lenSourceMark, get_file_state_marker(sourceState), \
            self.__lenProgBar, \
            get_prog_barstr(self.__progress[iBI], self.__lenProgBar, self.__use256), \
            self.__lenProg, self.__progress[iBI][0], \
            '\033[0m', \
            ))

def get_file_state_marker(fileState):
    '''
    Parameters
    ----------
    fileState : str
        the path of note directory

    Returns
    -------
    str : ✗ for None, ◆ for True and ? otherwise 
    '''
    if fileState is None:
        return "✗"
    if fileState is True:
        return "◆"
    return "?"

def get_prog_barstr(prog, totalBarLen, use256=False):
    '''
    get progress bar string

    Parameters
    ----------
    progPercent : list of 2 int
        a percentage of current and plan progress
    totalBarLen : int
    use256 : bool
        flag to use 256 color

    Returns
    -------
    str : progress bar for one book item
    '''
    assert totalBarLen > 2
    assert len(prog) == 2
    assert 0 <= prog[0] <= 100
    assert 0 <= prog[1] <= 100
    colorEnd = '\033[0m'
    colorPlan = '\033[34m'
    
    # generate color gradient by __color_grad
    colorCurrent = __color_grad(prog[0], use256)
    nCurrent = int(prog[0] / 100.0 * (totalBarLen - 2))
    nPlan = int(prog[1] / 100.0 * (totalBarLen - 2))

    # overdue reset
    if nPlan > 100:
        nPlan = 100

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

def __color_grad(prog, use256):
    '''
    Generate color for the current progress.
    If non-256 terminal is used, the light green color (\033[92m) will be used for all prog
    If a 256 terminal is used, the color for prog will be generated from a manually set gradient.
    Check https://en.wikipedia.org/wiki/ANSI_escape_code#Colors

    Paramters
    ---------
    prog : int
        the percentage of current progress
    use256 : bool
        the flag to use 256-color terminal

    Returns
    -------
    str : ANSI escape code
    '''
    colorDAC8 = '\033[92m' 
    ANSISeq = '\033[38;5;%dm'
    colorGrad256 = [202, 214, 172, 178, 142, 100, 106, 70, 34, 28, 2]
    iColor = int(float(prog) / 100.0 * (len(colorGrad256) - 1))
    color256 = ANSISeq % colorGrad256[iColor]
    if not use256:
        return colorDAC8
    return color256


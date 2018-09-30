# -*- coding: utf-8 -*-
'''
the presenter class is defined to show the reading and note progress of books
'''

from __future__ import print_function, absolute_import
import sys
import subprocess as sp
from readmanager.manager import manager
#from readmanager.bookitem import book_item
try:
    import curses
except ImportError:
    pass

class presenter:
    '''
    presenter class
    '''
    __lenIndex = 4
    __lenPageTot = 5
    __lenNoteMark = 2
    __lenSourceMark = 2
    __lenProg = 4
    # get terminal widths, allocate proportionally for title, author and ProgBar
    if sys.platform.lower() in ["linux", "darwin"]:
        __rows, __cols = sp.check_output(['stty', 'size']).split()
        __colsAvail = int(__cols) - \
                __lenIndex - __lenPageTot - __lenNoteMark - __lenSourceMark -__lenProg
        __lenTitle = int(__colsAvail * 0.33)
        __lenAuthor = int(__colsAvail * 0.2)
        __lenProgBar = __colsAvail - __lenTitle - __lenAuthor
    else:
        __lenTitle = 72
        __lenAuthor = 40
        __lenProgBar = 102
  
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
    __colorEnd = '\033[0m'
   
    # Format (number for arguments required
    # colorStart  index author title pageTotal noteState sourceState progBar prog colorEnd
    # 1           2     3      3     2         2         2           2       2    1
    __formatItem = "%s%-*s%-*.*s%-*.*s%-*s%-*s%-*s%-*s%*s%s"
    __head = __formatItem % (\
            __colorHead, \
            __lenIndex, "#", \
            __lenAuthor, __lenAuthor, "Author", \
            __lenTitle, __lenTitle, "Title", \
            __lenPageTot, "Page", \
            __lenNoteMark, "N", \
            __lenSourceMark, "S", \
            __lenProgBar, "Progress", \
            __lenProg, "%", \
            __colorEnd, \
            )
    __lenHead = len(__head) - len(__colorHead) - len(__colorEnd)

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
        self.__titles = self.__manager.get_keys("title")
        self.__authors = self.__manager.get_keys("author")
        self.__progress = self.__manager.get_progress_all()
        self.__pages = self.__manager.get_keys("pageTotal")

    def rebuild(self):
        '''
        Rebuild the items to show, when the manager has been refreshed
        '''
        self.__build()

    def show(self, filterAuthor='', filterTitle='', filterTag='', fAnd=True):
        '''
        Show the presenter
        '''
        # check whether the manager has added new book items
        # and rebuild the presenter
        if self.__nBooks != len(self.__manager):
            self.__build()
        
        print("=" * self.__lenHead)
        print(self.__head)
        for iBI in range(self.__nBooks):
            flag = self.__manager[iBI].filter(filterAuthor, filterTitle, filterTag, fAnd)
            if flag:
                self.print_item_status(iBI)
        print("=" * self.__lenHead)

    def print_item_status(self, iBI):
        '''
        Print the status of a book item

        Parameters
        ----------
        iBI : int
            the index of item in self.__manager.books
        '''
        __nSpaceSep = 4
        noteState, sourceState = self.__manager.get_note_source_state(iBI)
        print(self.__formatItem % (
            self.__colorItem, \
            self.__lenIndex, iBI + 1, \
            self.__lenAuthor, self.__lenAuthor - __nSpaceSep, self.__authors[iBI], \
            self.__lenTitle, self.__lenTitle - __nSpaceSep, self.__titles[iBI], \
            self.__lenPageTot, self.__pages[iBI], \
            self.__lenNoteMark, get_file_state_marker(noteState), \
            self.__lenSourceMark, get_file_state_marker(sourceState), \
            self.__lenProgBar, \
            get_prog_barstr(self.__progress[iBI], self.__lenProgBar, self.__use256), \
            self.__lenProg, self.__progress[iBI][0], \
            self.__colorEnd, \
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
    __markerToRead = ' '
    
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

    return "|%s%-*s%s%-*s%s%-.*s|" % ( \
            colorSmall, nSmall, "=" * nSmall, \
            colorBig, nBig - nSmall, "-" * (nBig - nSmall), \
            colorEnd, \
            totalBarLen - 2 - nBig, __markerToRead * (totalBarLen - 2 - nBig) \
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


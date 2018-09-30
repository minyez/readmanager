# -*- coding: utf-8 -*-
'''
The book_item class is defined. Each book item will be a book_item instance
'''

from __future__ import print_function, absolute_import
import json
import os
import time
from shutil import copy2
import datetime as dt

# datePlan default is set to a huge value 
# so that the default plan progress will be 0
tagsMust = { \
            "title": None, "author": None, \
            "pageTotal": 1, "pageCurrent": 0, \
            "noteType": None, "noteLocation": None, \
            "bookLocalSource": None, \
            "timeLastRead": None, "timeLastMod": None, \
            "dateAdded": "1900-01-01", \
            "datePlan": "9999-12-31", \
            "log": {}, \
            }
tagsOptl = ("press", "edition", "year", "titleShort", "isbn", "url")

# book_item
class book_item():
    '''
    class for book item.
    attributes:
        private:
            __fMod : bool
                the flag to mark if the information contained in __tagDict
                is different from those of the initial load of JSON file
            __tagsMust : dict
                the keys are tags that the JSON file MUST include, even 
                though they can be null. the value are the default value
                for initialization.
            __tagsOptl : dict
                similar to __tagsMust, but the tags are optional to help 
                to clarify the book item
            __tagDict : dict
                the dictionary that includes all the tags and their value 
                of the book item
            __formatTime : str
                the format of time that timeLastRead and timeLastMod adapt
        public:
            title : str
                the title of the book
            pageTotal : str
                the total number of pages
            pageCurrent : str
                current page of reading
    '''

    __tagsMust = tagsMust
    __tagsOptl = tagsOptl
    __formatTime = "%Y-%m-%d %X"
    noteSupportType = ["md", "tex", "txt", "docx"]

    # private methods
    def __init__(self, jsonfile, create_new=False):
        self.__readjson(jsonfile, create_new)
        self.__fMod = False
        self.__check_tagsMust()
        self.__update_public_attr()

    def __readjson(self, jsonfile, create_new):
        '''
        Read and decode the JSON file

        Parameters
        ----------
        jsonfile : str
            the file name of JSON input

        create_new : bool
            flag to create a new #empty json file by __dump_json
            #if set true, the original JSON will be overwritten
        '''
        assert os.path.splitext(jsonfile)[1] == '.json'
        if create_new:
            # deal with duplicate outside
            assert not os.path.isfile(jsonfile)
            self.__tagDict = {}
            #self.__dump_json(jsonfile, overwrite=True)
        else:
            with open(jsonfile, 'r') as hFileIn:
                self.__tagDict = json.load(hFileIn)
        # absolute path is used
        self.filepath = os.path.abspath(jsonfile)

    def __update_public_attr(self):
        '''
        Update the public attributes from __tagDict
        '''
        self.title = self.__tagDict["title"]
        self.pageTotal = self.__tagDict["pageTotal"]
        self.pageCurrent = self.__tagDict["pageCurrent"]
        self.noteLocation = self.__tagDict["noteLocation"]

    def __check_tagsMust(self):
        '''
        Check if all member in tagsMust exist in __tagDict dictionatry
        if tag does not exist, add k-v pair {tag: None} to __tagDict
        '''
        # record the original __tagDict
        tagDictOrig = self.__tagDict.copy()
        # check members in tagsMust
        for tag in self.__tagsMust:
            self.__tagDict.setdefault(tag, self.__tagsMust[tag])
        if self.__tagDict != tagDictOrig:
            self.__fMod = True

    def __dump_json(self, jsonout, overwrite=False):
        '''
        Dump the tags to a JSON file
        If the JSON file exists and overwrite is False, back up it with _bak suffix

        Parameters
        ----------
        jsonout : str
            the file name of output JSON
        overwrite : bool
            flag to overwrite file if jsonout exists

        '''
        if os.path.isfile(jsonout) and not overwrite:
            copy2(jsonout, jsonout.strip()+'_bak')
        with open(jsonout, 'w') as hFileOut:
            json.dump(self.__tagDict, hFileOut, indent=2)

    def __calculate_progress(self):
        '''
        Calculate the reading progress (in percentage) 
        and the progress as planed

        Returns
        -------
        int, int : reading and plan progress (in percentage)

        '''
        assert self.pageTotal != 0
        progCurrent = float(self.pageCurrent) / float(self.pageTotal) * 100.0
        progCurrent = int(progCurrent)
        assert 0 <= progCurrent <= 100
        progPlan = 0
        try:
            dateAdded = dt.date.fromisoformat(self.__tagDict["dateAdded"])
            datePlan = dt.date.fromisoformat(self.__tagDict["datePlan"])
            today = dt.date.today()
            assert datePlan - dateAdded > dt.timedelta()
            assert today - dateAdded >= dt.timedelta()
            progPlan = (today - dateAdded) / (datePlan - dateAdded) * 100
            progPlan = int(progPlan)
        except AssertionError:
            print("in %s:" % self.filepath)
            raise ValueError("datePlan is earlier than dateAdded, or dateAdded later than today")
        except ValueError:
            print("in %s:" % self.filepath)
            raise ValueError("check whether the date tags are in iso format, i.e. YYYY-MM-DD")

        return progCurrent, progPlan

    def __change_tag(self, tag, newValue):
        '''
        Change a non-log tag.
        The tag should exist in the __tagDict,
        otherwise __add_tag method should be used instead
        
        Parameters
        ----------
        tag : str
        value : int, str, list, dict
        '''
        assert tag != "log"
        assert self.__check_tag_exist(tag)
        oldValue = self.__tagDict[tag]
        self.__tagDict.update({tag: newValue})
        if newValue != oldValue:
            self.__fMod = True
            self.__update_public_attr()
            self.update_last_mod()

    def __add_tag(self, tag, value):
        '''
        Add new tag to book_item
        
        Parameters
        ----------
        tag : str
            the tag to add
        value : int, str, list, dict
            the value of the new tag
        '''
        assert not self.__check_tag_exist(tag)
        self.__tagDict.update({tag: value})
        self.__fMod = True
        self.update_last_mod()

    def __check_tag_exist(self, tag):
        '''
        check if a tag already exists in the __tagDict
        
        Parameters
        ----------
        tag : str
        
        Returns
        -------
        bool : True if the tag exists, False otherwise
        '''
        if tag in self.__tagDict:
            return True
        return False

    # public methods
    def get_tag(self, tag):
        '''
        Get the value of a particular tag
        
        Parameters
        ----------
        tag : str
            the tag name to extract
        
        Returns
        -------
        int or str or list or dict : the value of the tag if it exists, otherwise None
        '''
        return self.__tagDict.get(tag, None)

    def update_author(self, newAuthor):
        '''
        Update book author with newAuthor

        Parameters
        ----------
        newAuthor : str
        '''
        self.__change_tag("author", newAuthor)

    def update_title(self, newTitle):
        '''
        Update book title with newTitle

        Parameters
        ----------
        newTitle : str
        '''
        self.__change_tag("title", newTitle)
    
    def get_title(self, short=False):
        '''
        Return the title or short title of the book.
        
        Parameters
        ----------
        short : bool
            if true, the short title will be returned, if available.
        
        Returns
        -------
        str : title or short title of book
        '''
        if short and "titleShort" in self.__tagDict.keys():
            return self.__tagDict["titleShort"]
        return self.__tagDict["title"]

    def get_progress(self):
        '''
        Return the reading progress of the book in a percentage

        Returns
        -------
        int, int : current and plan progress of the book
        '''
        progCurrent, progPlan = self.__calculate_progress()
        return progCurrent, progPlan

    def get_source(self):
        '''
        Return the path of source file of the book
        '''
        return self.__tagDict["bookLocalSource"]

    def get_source_ext(self):
        '''
        Return the extension name (lowercase) of the source file of the book
        '''
        try:
            pathName, pathExt = os.path.splitext(self.__tagDict["bookLocalSource"])
        except TypeError:
            return None
        if len(pathExt) > 0:
            pathExt = pathExt[1:]
        return pathExt.lower()

    def update_last_read(self):
        '''
        Update timeLastRead with current time
        '''
        self.__change_tag("timeLastRead", time.strftime(self.__formatTime))

    def update_last_mod(self):
        '''
        Update timeLastRead with current time
        '''
        self.__change_tag("timeLastMod", time.strftime(self.__formatTime))

    def update_page(self, pageType, pageNew):
        '''
        Update page of type specified by pageType with pageNew
        
        Parameters
        ----------
        pageType : str
            the type of page, either "current" or "total"
        pageNew : int
            the new value of page to set
        '''
        __pageType = pageType.lower()
        if __pageType == "current":
            assert 0 <= pageNew <= self.pageTotal
            self.__change_tag("pageCurrent", pageNew)
        elif __pageType == "total":
            assert isinstance(pageNew, int)
            self.__change_tag("pageTotal", pageNew)

    def update_source_path(self, sourcePath):
        '''
        Update the path of loca book source
        
        Parameters
        ----------
        sourcePath : str
            the path of the loca book source file
        '''
        if sourcePath != "":
            self.__change_tag("bookLocalSource", os.path.expanduser(os.path.expandvars(sourcePath)))

    def update_note_dir(self, noteDir):
        '''
        Update the directory of book note directory
        
        Parameters
        ----------
        noteDir : str
            the path of the book directory
        '''
        self.__change_tag("noteLocation", os.path.expanduser(os.path.expandvars(noteDir)))

    def update_note_type(self, noteType):
        '''
        Update the file type of note
        
        Parameters
        ----------
        noteType : str
            the type of the note
        '''
        __noteType = noteType.lower()
        if __noteType in self.noteSupportType:
            self.__change_tag("noteType", __noteType)

    def update_date(self, dateType, dateStr=None):
        '''
        update the date tag specified by dateType with dateStr
     
        Parameters
        ----------
        dateType : str, "added" or "plan"
            the tag of date to change
        dateStr : str
            the isoformat date string
        '''
        __dictDateType = {"added": "dateAdded", "plan": "datePlan"}
        __dateType = dateType.lower()
        # use today as default date
        __dateStr = str(dt.date.today())
        if dateStr:
            __dateStr = dateStr
            # dateStr is needed when dateType is "plan"
        try:
            __date = dt.date.fromisoformat(__dateStr)
            self.__change_tag(__dictDateType[__dateType], __dateStr)
        except ValueError:
            if __dateType == "plan":
                pass
            else:
                raise ValueError("isoformat yyyy-mm-dd should be entered")
        except KeyError:
            raise KeyError("unsupported dateType: only '%s'" % "', '".join(__dictDateType.keys()))

    def update_log(self):
        '''
        Update the log dictionary with {"yyyy-mm-dd": self.pageCurrent} 
        the date stamp in iso format is generated by datetime.date.today()
        '''
        self.__tagDict["log"].update({str(dt.date.today()): self.pageCurrent})
        # hard to tell if the log is really updated. Let's say it is
        self.__fMod = True

    #def write_json(self, jsonout):
    #    '''
    #    write the book item as a json file
    #    
    #    Parameters
    #    ----------
    #    jsonout : str
    #        the file name of JSON output
    #    '''
    #    self.__dump_json(jsonout)

    def update_json(self, overwrite=False):
        '''
        Update the json file with current __tagDict
        only when the __tagDict has been modified
        
        Parameters
        ----------
        overwrite : bool
            flag to overwrite the originial JSON file
        '''
        if self.__fMod:
            self.__dump_json(self.filepath, overwrite)
            self.__fMod = False


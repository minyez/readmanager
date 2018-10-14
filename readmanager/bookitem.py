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
keysMust = { \
            "title": None, "author": None, \
            "pageTotal": 1, "pageCurrent": 0, \
            "noteType": None, "noteLocation": None, \
            "bookLocalSource": None, \
            "timeLastRead": None, "timeLastMod": None, \
            "dateAdded": "1900-01-01", \
            "datePlan": "9999-12-31", \
            "log": {}, \
            "remark": {}, \
            "tag": [], \
            }
keysOptl = ("press", "edition", "year", "titleShort", "isbn", "url")

# book_item
class book_item():
    '''
    class for book item.
    attributes:
        private:
            __fMod : bool
                the flag to mark if the information contained in __jsonDict
                is different from those of the initial load of JSON file
            __keysMust : dict
                the keys in dictionary are the keys that the JSON file 
                MUST include, even though they can be null. the values are 
                the default value for initialization.
            __keysOptl : dict
                similar to __keysMust, but the keys are optional for book
                JSON to help to clarify the book item
            __jsonDict : dict
                the dictionary that includes all the keys and their value 
                of the book item
            __formatTime : str
                the format of time that timeLastRead and timeLastMod adapt.
        public:
            title : str
                the title of the book
            pageTotal : str
                the total number of pages
            pageCurrent : str
                current page of reading
    '''

    __keysMust = keysMust
    __keysOptl = keysOptl
    __formatTime = "%Y-%m-%d %X"
    noteSupportType = ["md", "tex", "txt", "docx"]

    # private methods
    def __init__(self, jsonfile, create_new=False):
        self.__readjson(jsonfile, create_new)
        self.__fMod = False
        self.__check_keysMust()
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
            if set true, the original JSON will be overwritten
        '''
        assert os.path.splitext(jsonfile)[1] == '.json'
        if create_new:
            # deal with duplicate outside
            assert not os.path.isfile(jsonfile)
            self.__jsonDict = {}
            #self.__dump_json(jsonfile, overwrite=True)
        else:
            with open(jsonfile, 'r') as hFileIn:
                self.__jsonDict = json.load(hFileIn)
        # absolute path is used
        self.filepath = os.path.abspath(jsonfile)

    def __update_public_attr(self):
        '''
        Update the public attributes from __jsonDict
        '''
        self.title = self.__jsonDict["title"]
        self.pageTotal = self.__jsonDict["pageTotal"]
        self.pageCurrent = self.__jsonDict["pageCurrent"]
        self.noteLocation = self.__jsonDict["noteLocation"]

    def __check_keysMust(self):
        '''
        Check if all member in keysMust exist in __jsonDict dictionatry
        if tag does not exist, add k-v pair {tag: None} to __jsonDict
        '''
        # record the original __jsonDict
        tagDictOrig = self.__jsonDict.copy()
        # check members in keysMust
        for tag in self.__keysMust:
            self.__jsonDict.setdefault(tag, self.__keysMust[tag])
        if self.__jsonDict != tagDictOrig:
            self.__fMod = True

    def __dump_json(self, jsonout, overwrite=False):
        '''
        Dump the __jsonDict to a JSON file
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
            json.dump(self.__jsonDict, hFileOut, indent=2)

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
            dateAdded = dt.date.fromisoformat(self.__jsonDict["dateAdded"])
            datePlan = dt.date.fromisoformat(self.__jsonDict["datePlan"])
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
            raise ValueError("check whether the date keys are in iso format, i.e. YYYY-MM-DD")

        return progCurrent, progPlan

    def __change_key(self, key, newValue):
        '''
        Change a non-log/tag/remark key.
        The key should exist in the __jsonDict,
        otherwise __add_key method should be used instead
        
        Parameters
        ----------
        key : str
        value : int, str, list, dict
        '''
        assert key != "log"
        assert key != "tag"
        assert key != "remark"
        assert self.__check_key_exist(key)
        oldValue = self.__jsonDict[key]
        self.__jsonDict.update({key: newValue})
        if newValue != oldValue:
            self.__fMod = True
            self.__update_public_attr()
            self.update_last_time("mod")

    def __add_key(self, key, value):
        '''
        Add new key to book_item
        
        Parameters
        ----------
        key : str
            the key to add
        value : int, str, list, dict
            the value of the new key
        '''
        assert not self.__check_key_exist(key)
        self.__jsonDict.update({key: value})
        self.__fMod = True
        self.update_last_time("mod")

    def __check_key_exist(self, key):
        '''
        check if a key already exists in the __jsonDict
        
        Parameters
        ----------
        key : str
        
        Returns
        -------
        bool : True if the key exists, False otherwise
        '''
        if key in self.__jsonDict:
            return True
        return False

    # public methods
    def get_key(self, key):
        '''
        Get the value of a particular key
        
        Parameters
        ----------
        key : str
            the key to extract
        
        Returns
        -------
        int or str or list or dict : the value of the key if it exists, otherwise None
        '''
        return self.__jsonDict.get(key, None)

    def get_tag(self):
        '''
        get the tag of book item
        '''
        return self.__jsonDict["tag"]

    def filter(self, filterTitle='', filterAuthor='', filterTag='', fAnd=True):
        '''
        Filter the book item itself by title, author or tags

        Parameters
        ----------
        filterTitle : str, list or tuple
        filterAuthor : str, list or tuple
        filterTag : str, list or tuple
        fAnd : bool
            True for 'and' filter, False for 'or' filter

        Returns 
        -------
        bool : 
        '''
        flag = fAnd

        __filters = [ \
                filterTitle, \
                filterAuthor, \
                filterTag, \
                ]
        __patternToFilter = [ \
                self.get_title(), \
                self.get_author(), \
                self.get_tag(), \
                ]

        for __filter, __pattern in zip(__filters, __patternToFilter):
            # make all lower case
            if isinstance(__pattern, (list, tuple)):
                __patternLower = [p.lower() for p in __pattern]
            else:
                __patternLower = __pattern.lower()
            if __filter:
                if isinstance(__filter, (list, tuple)):
                    for item in __filter:
                        f = item.lower() in __patternLower
                        if f != fAnd:
                            return not flag
                else:
                    f = __filter.lower() in __patternLower
                    if f != fAnd:
                        return not flag
        return flag

    def get_author(self):
        '''
        Get the author of book

        Returns
        -------
        str : author name
        '''
        return self.__jsonDict["author"]

    def update_author(self, newAuthor):
        '''
        Update book author with newAuthor

        Parameters
        ----------
        newAuthor : str
        '''
        self.__change_key("author", newAuthor)

    def update_title(self, newTitle):
        '''
        Update book title with newTitle

        Parameters
        ----------
        newTitle : str
        '''
        self.__change_key("title", newTitle)
    
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
        if short and "titleShort" in self.__jsonDict.keys():
            return self.__jsonDict["titleShort"]
        return self.__jsonDict["title"]

    def get_progress(self):
        '''
        Return the reading progress of the book in a percentage

        Returns
        -------
        int, int : current and plan progress of the book
        '''
        progCurrent, progPlan = self.__calculate_progress()
        return progCurrent, progPlan

    def get_source(self, ext=False):
        '''
        Return the path of source file of the book

        Parameters
        ----------
        ext : bool
            Use True to return the extension name of the source file, False for full path
        '''
        if ext:
            try:
                pathName, pathExt = os.path.splitext(self.__jsonDict["bookLocalSource"])
            except TypeError:
                return None
            if len(pathExt) > 0:
                pathExt = pathExt[1:]
            return pathExt.lower()
        return self.__jsonDict["bookLocalSource"]

    def update_last_time(self, timeType):
        '''
        update the key of last time of read or modification with current time
        
        Parameters
        ----------
        timeType : str
            "read" for "timeLastRead", "mod" for "timeLastMod"
        '''
        try:
            __timeType = timeType.strip().lower()
            if __timeType == "read":
                __key = "timeLastRead"
            elif __timeType.startswith("mod"):
                __key = "timeLastMod"
            self.__change_key(__key, time.strftime(self.__formatTime))
        except AttributeError:
            pass

    def get_last_time(self, timeType):
        '''
        Get the time of last read or modification, specified by timeType

        Parameters
        ----------
        timeType : str, "read" or "mod"
            choose which time to return, "read" for last read and "mod" for last modification
     
        Returns
        -------
        datetime : the datetime instance corresponding to the time last read/mod.
            if the time is null in json, 1990-01-01 will be returned
        '''

        __timeType = timeType.strip().lower()
        if __timeType == "read":
            __key = "timeLastRead"
        elif __timeType.startswith("mod"):
            __key = "timeLastMod"
        else:
            raise ValueError("timeType should be either \"read\" or \"mod\".")
       
        if self.__jsonDict[__key] in [None, ""]:
            return dt.datetime(1900, 1, 1, 0, 0, 0)
        return dt.datetime.strptime(self.__jsonDict[__key], self.__formatTime)


    #def get_last_read(self):
    #    '''
    #    Get the time of last read
    # 
    #    Returns
    #    -------
    #    datetime : the datetime instance corresponding to the time last read.
    #    '''
    #    return dt.datetime.strptime(self.__jsonDict["timeLastRead"], self.__formatTime)

    #def get_mod_time(self):
    #    '''
    #    Get the time of last modification

    #    Returns
    #    -------
    #    `datetime` instance representing the time of last modification
    #    if "timeLastMod" is null, return datime(1900, 1, 1, 0, 0, 0)
    #    '''
    #    if self.__jsonDict["timeLastMod"] in [None, ""]:
    #        return dt.datetime(1900, 1, 1, 0, 0, 0)
    #    return dt.datetime.strptime(self.__jsonDict["timeLastMod"], self.__formatTime)

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
            self.__change_key("pageCurrent", pageNew)
        elif __pageType == "total":
            assert isinstance(pageNew, int)
            self.__change_key("pageTotal", pageNew)

    def update_source_path(self, sourcePath):
        '''
        Update the path of loca book source
        
        Parameters
        ----------
        sourcePath : str
            the path of the loca book source file
        '''
        if sourcePath != "":
            self.__change_key("bookLocalSource", os.path.expanduser(os.path.expandvars(sourcePath)))

    def update_note_dir(self, noteDir):
        '''
        Update the directory of book note directory
        
        Parameters
        ----------
        noteDir : str
            the path of the book directory
        '''
        self.__change_key("noteLocation", os.path.expanduser(os.path.expandvars(noteDir)))

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
            self.__change_key("noteType", __noteType)

    def update_date(self, dateType, dateStr=None):
        '''
        update the date key specified by dateType with dateStr
     
        Parameters
        ----------
        dateType : str, "added" or "plan"
            the key of date to change
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
            self.__change_key(__dictDateType[__dateType], __dateStr)
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
        self.__jsonDict["log"].update({str(dt.date.today()): self.pageCurrent})
        # hard to tell if the log is really updated. Let's say it is
        self.__fMod = True

    def update_tag(self, listTag, fAdd=True):
        '''
        Parameters
        ----------
        listTags : list or tuple
            list/tuple containing tag strings to add. string should be in lowercase
        fAdd : bool
            True to add tags, False to remove tags
        '''
        __bookTag = [tag.lower() for tag in self.__jsonDict["tag"]]
        for tag in listTag:
            if tag:
                if fAdd and tag not in __bookTag:
                    self.__jsonDict["tag"].append(tag)
                    self.__fMod = True
                elif not fAdd and tag in __bookTag:
                    i = self.__jsonDict["tag"].index(tag)
                    del self.__jsonDict["tag"][i]
                    self.__fMod = True

    def update_json(self, overwrite=False):
        '''
        Update the json file with current __jsonDict
        only when the __jsonDict has been modified
        
        Parameters
        ----------
        overwrite : bool
            flag to overwrite the originial JSON file
        '''
        if self.__fMod:
            self.update_last_time("mod")
            self.__fMod = False
            self.__dump_json(self.filepath, overwrite)

    def update_remark(self, strRemark):
        '''
        Add remark

        Parameters
        ----------
        strRemark : str
            the remark string
        '''
        # if an empty remark string is typed, skip update
        if strRemark == '':
            return

        strToday = str(dt.date.today())
        remarkToday = self.__jsonDict['remark'].get(strToday, False)
        if remarkToday:
            remarkToday.append(strRemark)
        else:
            self.__jsonDict["remark"].update({strToday:[strRemark]})
        self.__fMod = True


# -*- coding: utf-8 -*-
'''
the manager class is defined to manage the book item instances and notes
'''

from __future__ import print_function, absolute_import
import json
import os
from fnmatch import fnmatch
from readmanager.bookitem import book_item

class manager():
    '''
    manager class
    attributes:
        private:
        public:
    methods:
        private:
        public:
    TODOs:
        initialize config.json
    '''

    # default note opener 
    __openerDe = { \
            "tex": None, \
            "md": None, \
            "txt": None, \
            "pdf": None, \
            "docx": None, \
            "doc": None, \
            }
    __paraConfigMust = ("dbJSON", "dbNote")

    # try to get custom config file path from READMANA_CONFIG environment variable

    def __init__(self, pathConfig, modeNonInter=False):
        '''
        Initialize the book manager instance from the JSON file pathConfig
        
        Parameters
        ----------
        pathConfig : str
            the path of config json
        modeNonInter : bool
            flag for non-interactive mode, used for unittest of ui
        '''
        assert not os.path.isdir(pathConfig)
        if os.path.isfile(pathConfig):
            self.pathConfig = pathConfig
        else:
            raise FileNotFoundError("Specified config file is not found.")
        #if os.path.abspath(pathConfig) == self.__pathConfigDe:
        #    self.__fUseConfigDe = True
        self.books = []
        self.booksArchive = []
        assert isinstance(modeNonInter, bool)
        self.modeNonIner = modeNonInter
        #self.__check_config()
        self.__load_config()
        self.__load_book_items()

    def __getitem__(self, i):
        return self.books[i]

    def __len__(self):
        return len(self.books)

    def __load_config(self):
        '''
        Load existing config file
        Namely, define dbJSON, dbNote and opener attributes
        '''
        with open(self.pathConfig, 'r') as hFileIn:
            self.__dictConfig = json.load(hFileIn)
        # check config file consistency
        for key in self.__paraConfigMust:
            if key not in self.__dictConfig:
                raise ValueError("Broken config.json: key \"%s\" not found" % key)
        # JSON and note are in the same directory as configuration json. For travis test
        if self.__dictConfig["dbJSON"] in ["-", "-/"]:
            self.dbJSON = os.path.abspath(self.pathConfig + "/../JSON")
        else:
            self.dbJSON = os.path.expanduser(os.path.expandvars(self.__dictConfig["dbJSON"]))
        assert os.path.isdir(self.dbJSON)

        # Archive database under dbJSON
        self.dbArchive = os.path.join(self.dbJSON, "archive")
        try:
            assert os.path.isdir(self.dbArchive)
        except AssertionError:
            os.makedirs(self.dbArchive)

        if self.__dictConfig["dbNote"] in ["-", "-/"]:
            self.dbNote = os.path.abspath(self.pathConfig + "/../note")
        else:
            self.dbNote = os.path.expanduser(os.path.expandvars(self.__dictConfig["dbNote"]))
        assert os.path.isdir(self.dbNote)

        self.opener = self.__openerDe
        if "opener" in self.__dictConfig:
            self.opener = self.__dictConfig["opener"]
        assert isinstance(self.opener, dict)

    def __load_book_items(self, reLoad=False):
        '''
        load all json files in dbJSON directory as a list of book_item instances to self.books list
        Note that this method will first clean the self.books list.
        '''
        if not reLoad:
            print("Manager getting all book items...", end=" ")
        else:
            print("Manager reloading...", end=" ")
        
        # clear books
        self.books = []
        self.booksArchive = []
        for ifile in os.listdir(self.dbJSON):
            if fnmatch(ifile.lower(), "*.json"):
                self.books.append(book_item(os.path.join(self.dbJSON, ifile)))
        for ifile in os.listdir(self.dbArchive):
            if fnmatch(ifile.lower(), "*.json"):
                self.booksArchive.append(book_item(os.path.join(self.dbArchive, ifile)))
        if not reLoad:
            print("Done. %d items read." % len(self.books))
        else:
            print("Reloaded. %d items read." % len(self.books))
        self.sort_books_by_mod_time()

    def sort_books_by_mod_time(self):
        '''
        Sort book_item instances by descending datetime
        '''
        self.books = sorted(self.books, key=lambda x: x.get_last_time("mod"), reverse=True)

    def sort_books_by_author(self):
        '''
        Sort book_item instances by ascending author name, with simple string comparing
        '''
        self.books = sorted(self.books, key=lambda x: x.get_author())

    def sort_books_by_title(self):
        '''
        Sort book_item instances by ascending author name, with simple string comparing
        '''
        self.books = sorted(self.books, key=lambda x: x.get_title(short=False))

    def add_new_book(self, bi):
        '''
        Append new book_item instance 
        '''
        assert isinstance(bi, book_item)
        self.books.append(bi)

    def update_json_all(self):
        '''
        Update all book_item JSONs with update_json method
        '''
        for bi in self.books:
            bi.update_json()
        for bi in self.booksArchive:
            bi.update_json()

    def refresh(self):
        '''
        Refresh the manager
        Namely, update all book_item JSONs, then reload them
        '''
        self.update_json_all()
        self.__load_book_items(reLoad=True)

    def get_keys(self, key):
        '''
        Get the values of a particular key from all books by get_key book_item method.
        See book_item class for more information
        Note that "log" and "remark" cannot be extracted by get_keys. (TODO)
     
        Parameters
        ----------
        key : str
            the name of the key
     
        Returns
        -------
        list : values of the key from all book_item.
            if key == "tag", the list consists all unique (case-insensitive) tags
            None if the key does not exist for the book_item
        '''
        assert not key in ["log", "remark"]
        if key == "tag":
            __tags = []
            for bi in self.books:
                __tagi = bi.get_key("tag")
                for i in __tagi:
                    if not i.lower() in __tags:
                        __tags.append(i)
            return __tags
                    
        return [bi.get_key(key) for bi in self.books]

    def get_progress_all(self):
        '''
        get progress of all books
        '''
        return [bi.get_progress() for bi in self.books]

    def get_note_path(self, iBI):
        '''
        Parameters
        ----------
        iBI : int
            index of book item. Negative value allowed.
        
        Returns
        -------
        None : if the book item does not have note
        otherwise str : the path of note
        '''
        assert iBI < len(self.books)
        noteLoc = self.books[iBI].get_key("noteLocation")
        noteType = self.books[iBI].get_key("noteType")
     
        if noteLoc is None or noteType is None:
            return None
     
        notePrefix = os.path.basename(noteLoc)
        notePath = os.path.join(os.path.expanduser(noteLoc), notePrefix)
        notePath = notePath + "." + noteType
        if notePath.startswith("-/"):
            notePath = os.path.join(self.dbNote, notePath[2:])
        return notePath

    def get_first_match(self, key, pattern):
        '''
        Get the first match of pattern in the key domain of book item
        '''
        pass

    def get_note_source_state(self, iBI):
        '''
        Parameters
        ----------
        iBI : int
            index of book item
        
        Returns
        -------
        None/False/True, None/False/True : note state, source state
            None if path not set, True for file found, otherwise False
        '''
       
        # note, source file
        state = [None, None]
        path = [self.get_note_path(iBI), self.books[iBI].get_source()]
     
        for i in range(2):
            if path[i] is None:
                continue
            state[i] = os.path.isfile(path[i])
        
        return tuple(state)

# TODO archive/unarchive books
    def archive(self, iBI, op):
        '''
        Archive/Unarchive

        Parameters
        ----------
        iBI : int or a list of int
            index or list of indices of book item
        op : str, "arch" or "unarch"
        
        '''
        pass

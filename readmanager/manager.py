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

    def __init__(self, pathConfig):
        '''
        Initialize the book manager instance from the JSON file pathConfig
        
        Parameters
        ----------
        pathConfig : str
            the path of config json
        '''
        assert not os.path.isdir(pathConfig)
        if os.path.isfile(pathConfig):
            self.pathConfig = pathConfig
        else:
            raise FileNotFoundError("Specified config file is not found.")
        #if os.path.abspath(pathConfig) == self.__pathConfigDe:
        #    self.__fUseConfigDe = True
        self.books = []
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
        load all json files in dbJSON directory as a list of book_item instances
        '''
        if not reLoad:
            print("Manager getting all book items... ", end="")
        else:
            print("Manager reloading... ", end="")
        
        # clear books
        self.books = []
        for ifile in os.listdir(self.dbJSON):
            if fnmatch(ifile.lower(), "*.json"):
                self.books.append(book_item(os.path.join(self.dbJSON, ifile)))
        if not reLoad:
            print("Done. %d items read." % len(self.books))
        else:
            print("Reloaded. %d items read." % len(self.books))

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

    def refresh(self):
        '''
        Refresh the manager
        Namely, update all book_item JSONs, then reload them
        '''
        self.update_json_all()
        self.__load_book_items(reLoad=True)

    def get_tags(self, tag):
        '''
        Get the values of a particular tag from all book_item by get_tag method
        See book_item class for more information
     
        Parameters
        ----------
        tag : str
            the name of the tag
     
        Returns
        -------
        list : values of the tag from all book_item.
            has the same length as self.books. 
            None if the tag does not exist for the book_item
        '''
        return [bi.get_tag(tag) for bi in self.books]

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
        noteLoc = self.books[iBI].get_tag("noteLocation")
        noteType = self.books[iBI].get_tag("noteType")
     
        if noteLoc is None or noteType is None:
            return None
     
        notePrefix = os.path.basename(noteLoc)
        notePath = os.path.join(os.path.expanduser(noteLoc), notePrefix)
        notePath = notePath + "." + noteType
        if notePath.startswith("-/"):
            notePath = os.path.join(self.dbNote, notePath[2:])
        return notePath

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


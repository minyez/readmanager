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
    __noteOpenDe = {"tex": "texstudio", "md": "Typora", "txt": "nvim"}
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
        load existing config file
        '''
        with open(self.pathConfig, 'r') as hFileIn:
            self.__dictConfig = json.load(hFileIn)
        # check config file consistency
        for key in self.__paraConfigMust:
            if key not in self.__dictConfig:
                raise ValueError("Broken config.json: key \"%s\" not found" % key)
        self.dbJSON = self.__dictConfig["dbJSON"]
        self.dbNote = self.__dictConfig["dbNote"]
        assert os.path.isdir(self.dbJSON)
        assert os.path.isdir(self.dbNote)

    def __load_book_items(self, reLoad=False):
        '''
        load all json files in dbJSON directory as a list of book_item instances
        '''
        if not reLoad:
            print("Manager getting all book items... ", end="")
        else:
            print("Manager reloading... ", end="")
            
        for ifile in os.listdir(self.dbJSON):
            if fnmatch(ifile.lower(), "*.json"):
                self.books.append(book_item(os.path.join(self.dbJSON, ifile)))
        if not reLoad:
            print("Done. %d items read." % len(self.books))
        else:
            print("Reloaded. %d items read." % len(self.books))

    def update_json_all(self):
        '''
        Update all book_item JSONs with update_json method
        '''
        for bi in self.books:
            bi.update_json()

    def change_book_tag(self, iBI, tag, newValue):
        '''
        change tag of the book_item with index i by newValue
        
        Parameters
        ----------
        iBI : int
            the index of book_item in self.books
        tag : str
            the name to tag to change
        newValue : int or str
            the new value to adopt in tag
        '''
        assert iBI in range(len(self.books))
        self.books[iBI].change_tag(tag, newValue)

    def refresh(self):
        '''
        Refresh the manager
        Namely, update all book_item JSONs, then reload them
        '''
        self.update_json_all()
        self.__load_book_items(reLoad=True)

    def get_tags(self, tag):
        '''
        get the values of a particular tag from all book_item

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

    def get_progress(self):
        '''
        get progress of all books
        '''
        return [bi.return_progress() for bi in self.books]

    def get_note_path(self, iBI):
        '''
        Parameters
        ----------
        iBI : int
            index of book item
        
        Returns
        -------
        None : if the book item does not have note
        otherwise str : the path of note
        '''
        assert iBI in range(len(self.books))
        noteLoc = self.books[iBI].get_tag("noteLocation")
        noteType = self.books[iBI].get_tag("noteType")

        if noteLoc is None or noteType is None:
            return None

        notePrefix = os.path.basename(noteLoc)
        notePath = os.path.join(noteLoc, notePrefix)
        notePath = notePath + "." + noteType
        if notePath.startswith("-/"):
            notePath = os.path.join(self.dbNote, notePath[2:])
        return notePath




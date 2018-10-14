#!/usr/bin/env python3
'''
Main executable classes of readmanager.
'''

from __future__ import print_function, absolute_import
import sys
from readmanager import utils, opener
from readmanager.manager import manager
from readmanager.presenter import presenter

class __executable:
    '''
    metaclass for public methods of ui and batch mode
    '''

    helpStrRead = ''
    helpStr0SQ = ''
    helpStrMana = ''
    helpStrPre = ''
    helpStrManaPre = ''
    helpStrExit = ''
    helpStrPrompt = ''
    helpStr = ''

    dictOptionsMana = {}
    dictOptionsPre = {}
    dictOptionsManaPre = {}

    def set_help_str(self):
        '''
        define help string for UI
        '''
        self.helpStrRead = 'Menu:\n    #: open No.# book and note (if available);\n'
        self.helpStr0SQ = ''
        self.helpStrMana = ''
        self.helpStrPre = ''
        self.helpStrManaPre = ''
        self.helpStrExit = '    other letters or <0: quit without save;\n'
        self.helpStrPrompt = '--> '

    def set_utils_options(self):
        '''
        Method to define option dictionary utilities 
        '''
        self.dictOptionsMana = { \
           "s": utils.save_exit, \
           "m": utils.modify, \
           "c": utils.create_new, \
           }
        self.dictOptionsPre = { \
           "p": utils.print_pre, \
           "i": utils.show_item_details, \
           "f": utils.find_item, \
           "t": utils.show_tags, \
           }
        self.dictOptionsManaPre = { \
           "S": utils.sort_items, \
           }

class readmanager_ui(__executable):
    '''
    readmanager user interface class
    '''

    def __init__(self, modeCheck=False, modeRead=False):
     
        assert isinstance(modeCheck, bool)
        assert isinstance(modeRead, bool)
        self.modeCheck = modeCheck
        self.modeRead = modeRead
     
        # get config file path
        configFile = utils.get_config()
        # initialize manager instance
        self.__bm = manager(configFile, modeBatch=False)
        # flush screen and show all items once.
        if not modeCheck:
            utils.flush_screen()
        self.__pre = presenter(self.__bm)
        
        # initialize presenter instance
        self.__pre.show()
        # if check-mode is triggered, exit safely
        # ===================================================================
        if self.modeCheck:
            sys.exit(0)
        self.set_utils_options()
        self.set_help_str()
        self.__update_helpStr()
        self.loop()

    def __update_helpStr(self):

        if self.modeRead:
            self.helpStr0SQ = '%5s: %s\n' % \
                    ("0", self.dictOptionsMana["s"].__doc__.split("\n")[1].strip())
        else:
            for key in self.dictOptionsMana:
                __key = key
                if __key == "s":
                    __key = "0/s"
                self.helpStrMana += '%5s: %s\n' % \
                        (__key, utils.get_func_doc(self.dictOptionsMana[key]))
            for key in self.dictOptionsPre:
                self.helpStrPre += '%5s: %s\n' % \
                        (key, utils.get_func_doc(self.dictOptionsPre[key]))
            for key in self.dictOptionsManaPre:
                self.helpStrManaPre += '%5s: %s\n' % \
                        (key, utils.get_func_doc(self.dictOptionsManaPre[key]))
        
        self.helpStr = self.helpStrRead + self.helpStr0SQ + \
                self.helpStrMana + self.helpStrPre + self.helpStrManaPre + \
                self.helpStrExit + \
                self.helpStrPrompt
   
    def loop(self):
        '''
        start main UI loop
        '''
        fRetry = False
        while True:
            if fRetry:
                option = input(self.helpStrPrompt).strip()
            else:
                option = input(self.helpStr).strip()
                
            try:
                iBI = int(option) - 1
                fRetry = self.__read_book(iBI)
            except ValueError:
                fRetry = self.__run_option(option)

    def __read_book(self, iBI):
        '''
        Read the book and open the note by functions defined in opener
        
        Parameters
        ----------
        iBI : int

        Returns
        -------
        bool : True if an empty option is selected, False otherwise
            this is used to specify if it is a retry of option input
        '''
        if iBI in range(len(self.__bm)):
            fRetry = False
            opener.open_book(self.__bm, iBI)
        elif iBI >= len(self.__bm):
            print("Invalid book #. Retry. ", end="")
            fRetry = True
        elif iBI == -1:
            utils.save_exit(self.__bm)
        else:
            utils.exit_wo_save()
        return fRetry

    def __run_option(self, option):
        '''
        Run utility defined by the option dictionary, specified by argument 'option'

        Parameters
        ----------
        option : str
            the name for the utility, defined in the option dictionary

        Returns
        -------
        bool : True if an empty option is selected, False otherwise
            this is used to specify if it is a retry of option input
        '''
        if option == '':
            return True
        if option in ["exit", "q"]:
            sys.exit(0)
        if self.modeRead:
            utils.exit_wo_save()
        
        if option in self.dictOptionsMana:
            self.dictOptionsMana[option](self.__bm)
            #bookpre.rebuild()
        elif option in self.dictOptionsPre:
            self.dictOptionsPre[option](self.__pre)
        elif option in self.dictOptionsManaPre:
            self.dictOptionsManaPre[option](self.__bm, self.__pre)
        else:
            utils.exit_wo_save()
        return False

#TODO batch mode
class readmanager_batch(__executable):
    '''
    Readmanager batch mode class
    '''

    def __init__(self, command):
        '''
        command : str list
        '''
        self.set_utils_options()
        self.__analyze_command(command)

    def __analyze_command(self, command):
        '''
        Analyze the command input
        '''
        pass


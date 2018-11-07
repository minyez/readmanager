#!/usr/bin/env python3
'''
Main executable classes of readmanager.
'''

from __future__ import print_function, absolute_import
import sys
#from copy import deepcopy
from readmanager import utils, opener
from readmanager.manager import manager
from readmanager.presenter import presenter

class readmanager_ui():
    '''
    readmanager user interface class
    '''

    def __init__(self, modeRead=False, modeNonInter=False):
     
        assert isinstance(modeRead, bool)
        self.modeRead = modeRead
        self.helpStrRead = ''
        self.helpStr0SQ = ''
        self.helpStrMana = ''
        self.helpStrPre = ''
        self.helpStrManaPre = ''
        self.helpStrExit = ''
        self.helpStrPrompt = ''
        self.helpStr = ''

        self.dictOptionsMana = {}
        self.dictOptionsPre = {}
        self.dictOptionsManaPre = {}
     
        # flush screen and show all items once.
        if not modeNonInter:
            utils.flush_screen()
        # get config file path
        configFile = utils.get_config()
        # initialize manager instance
        self.__bm = manager(configFile, modeNonInter=modeNonInter)
        # initialize presenter instance
        self.__pre = presenter(self.__bm)
        
        # ===================================================================
        # initialize options and help string
        self.__set_utils_options_mana()
        self.__set_utils_options_pre()
        self.__set_utils_options_manapre()
        self.__set_ui_help_str()
        self.__update_helpStr()

    def __set_utils_options_mana(self):
        '''
        Method to define option dictionary of manager utilities 
        '''
        self.dictOptionsMana = { \
           "s": utils.save_exit, \
           "m": utils.modify, \
           "c": utils.create_new, \
           "r": utils.add_remark, \
           # "check archive"
           # "archive"
           # "unarchive"
           }

    def __set_utils_options_pre(self):
        '''
        Method to define option dictionary of presenter utilities 
        '''
        self.dictOptionsPre = { \
           "p": utils.print_pre, \
           "i": utils.show_item_details, \
           "f": utils.find_item, \
           "t": utils.show_tags, \
           }

    def __set_utils_options_manapre(self):
        '''
        Method to define option dictionary of utilities of manager+presenter
        '''
        self.dictOptionsManaPre = { \
           "S": utils.sort_items, \
           }

    def __set_ui_help_str(self):
        '''
        define help string for UI
        '''
        self.helpStrRead = 'Menu:\n    #: open No.# book and note (end with & to avoid note);\n'
        self.helpStr0SQ = ''
        self.helpStrMana = ''
        self.helpStrPre = ''
        self.helpStrManaPre = ''
        self.helpStrExit = '    other letters or <0: quit without save;\n'
        self.helpStrPrompt = '--> '

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
   
    def __read_book(self, iBI, fNoNote=False):
        '''
        Read the book and open the note by functions defined in opener
        
        Parameters
        ----------
        iBI : int
        fNoNote : bool
            flag for recording page without openning any book or note source

        Returns
        -------
        bool : True if an empty option is selected, False otherwise
            this is used to specify if it is a retry of option input
        '''
        if iBI in range(len(self.__bm)):
            fRetry = False
            opener.open_book(self.__bm, iBI, fNoNote)
        elif iBI >= len(self.__bm):
            print("Invalid book #. Retry. ", end="")
            fRetry = True
        elif iBI == -1:
            utils.save_exit(self.__bm)
        else:
            utils.exit_wo_save()
        return fRetry

    def show_pre(self):
        '''
        Show the presenter
        '''
        utils.print_pre(self.__pre)

    def run_option(self, option):
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

    def loop(self):
        '''
        start main UI loop
        '''
        fRetry = False
        while True:
            if fRetry:
                option = input(self.helpStrPrompt).strip()
            else:
                utils.flush_screen()
                self.show_pre()
                option = input(self.helpStr).strip()
                
            try:
                iBI = int(option) - 1
                fRetry = self.__read_book(iBI)
            except ValueError:
                if option.endswith("&"):
                    try:
                        iBI = int(option[:-1]) - 1
                        fRetry = self.__read_book(iBI, fNoNote=True)
                    except ValueError:
                        pass
                else:
                    fRetry = self.run_option(option)

#T O D O batch mode
#class readmanager_batch(__executable):
#    '''
#    Readmanager batch mode class. 
#    '''
#
#    def __init__(self, command):
#        '''
#        command : str list
#        '''
#        configFile = utils.get_config()
#        self.__bm = manager(configFile, modeBatch=True)
#        self.__command = command
#        self.set_utils_options_mana()
#        self.__analyze_command()
#
#    def __analyze_command(self):
#        '''
#        Analyze the command input
#        '''
#        
#        __command = deepcopy(self.__command)
#        __opt = __command[0]
#        del __command[0]
#        try:
#            iBI = int(__opt)
#        except ValueError:
#            if __opt == "FA":
#                pass

            


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
test module
'''

from __future__ import print_function, absolute_import
import os
import unittest as ut
import datetime as dt
from readmanager.bookitem import book_item
from readmanager.manager import manager

class test_bookitem(ut.TestCase):
    '''
    Unit test for book_item class
    '''

    def test_read_json(self):
        '''
        read from an existing json
        '''
        # raise FileNotFoundError if the file is not found
        self.assertRaises(FileNotFoundError, book_item, "data/JSON/book_notexist.json")
        self.assertTrue(book_item("data/JSON/book_1.json"))

    def test_create_json(self):
        '''
        test new JSON creation
        '''
        newbook = "newbook.json"
        book = book_item(newbook, create_new=True)
        # the modification flag must be true when creating new json
        self.assertTrue(book._book_item__fMod)
        book.update_json(True)
        self.assertTrue(not book._book_item__fMod)
        # remove the test json
        os.remove(newbook)

    def test_tag_manipulate(self):
        '''
        test book item manipulation
        '''
        # book_2 has 100 total pages and currently 0 page is read
        book = book_item("data/JSON/book_2.json")
        # AssertionError when a non-percentage progress is encountered
        self.assertRaises(AssertionError, book.update_current_page, book.pageTotal + 1)
        
        book.update_current_page(1)
        # public attributes should be updated if the tag value is changed indeed
        self.assertEqual(book.pageCurrent, 1)
        self.assertTrue(book._book_item__fMod)
        progCurrent, progPlan = book.get_progress()
        self.assertTrue(progCurrent, 1)
        # log cannot be modified by change_tag method
        #self.assertRaises(AssertionError, book.change_tag, "log", 1)
        # log
        book.update_log()
        self.assertTrue(book._book_item__tagDict["log"][str(dt.date.today())] == 1)


class test_manager(ut.TestCase):
    '''
    Unit test for manager class
    '''

    def test_from_custom_config(self):
        '''
        read from custom config file with dbJSON and dbNote specified
        '''
        # raise IOError if the specified config file is not found.
        self.assertRaises(FileNotFoundError, manager, 'data/config_notexist.json')

        mana = manager('data/config_test.json')
        # two JSONs in the JSON directory specified in data/config_test.json
        self.assertTrue(len(mana), 2)

        # use change_book_tag to change dateAdded tag of second book to today, test effectiveness
        todayStr = str(dt.date.today())
        mana[1].update_date_added(todayStr)
        self.assertTrue(mana[1]._book_item__tagDict["dateAdded"] == todayStr)

        # test progress calculation utility
        progress = mana.get_progress_all()
        self.assertTrue(progress, [(0, 0), (0, 0)])

    def test_from_environ(self):
        '''
        test from reading config file defined in the environment variable READ
        '''
        pass


if __name__ == "__main__":
    ut.main()

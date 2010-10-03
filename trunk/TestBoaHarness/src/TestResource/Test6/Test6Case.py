import unittest
import Test6Case
import TestCaseHelper
import os
from selenium import selenium
import SeleniumHelper


def injectParam(param,tepar) :
    Test6Case.param = param
    Test6Case.tepar = tepar

class TestSuite(unittest.TestCase):

    def setUp(self):
       self.selenium = selenium("localhost", 4444, "*firefox", "http://hotelnajavie.appspot.com/")
       self.selenium.start()
       self.seHelper = SeleniumHelper.SeleniumHelper(self.selenium)
       self.seHelper.setParam(self,Test6Case.param,Test6Case.tepar)

    def testCase1(self):
       self.selenium.open("")
       self.seHelper.runTest('test')


    def tearDown(self) :
        pass

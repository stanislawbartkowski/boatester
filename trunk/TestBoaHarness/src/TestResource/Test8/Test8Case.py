import os
import sys
import unittest

import Test8Case
import ODBCHelper

def setHe(he):
     Test8Case.helper = he

def injectParam(param,tepar) :
     Test8Case.param = param
     Test8Case.teparam = tepar
    
class TestSuite(unittest.TestCase):

    def setUp(self):
         self.param = Test8Case.param
         self.teparam = Test8Case.teparam
         self.odbcH = ODBCHelper.ODBCHelper(self, self.param, self.teparam)
        

    def testCase(self):
         self.odbcH.executeSection()
         for i in range(100) :
             self.odbcH.execute("INSERT INTO MESS VALUES(?)",  'MESS ' + str(i))
         self.odbcH.executeSection("check")
         self.odbcH.executeSection("test1")
        

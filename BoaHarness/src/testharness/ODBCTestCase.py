#
# Copyright [2013] the stanislaw.bartkowski@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Helper class for executing automatically single ODBC test
     Factory and TestCase
"""
__authors__ = [
    '"Stansislaw Bartkowski" <stanislawbartkowski@gmail.com>',
]

import os
import sys
import unittest

_ODBCTEST='odbcrun'
        
class ODBCTestCase(unittest.TestCase):
     """ Class for executing single odbc test  
     """
    
     def __init__(self, param, teparam) :
         """ Constructor
         Args: TestParam and OneTestParam
         """
         unittest.TestCase.__init__(self)
         self.param = param
         self.teparam = teparam
 
     def setUp(self):
         import ODBCHelper
         self.odbcH = ODBCHelper.ODBCHelper(self, self.param, self.teparam)

     def runTest(self):
         starttest = self.teparam.getPar(_ODBCTEST)
         if starttest.strip() == '' : self.odbcH.executeSection()
         else : self.odbcH.executeSection(starttest.strip())
         
     def tearDown(self) :
         # very important: close connection, autocommit off and transaction can be in progress
         self.odbcH.close()
        
class ODBCUnitTestFactory:
     """ Factory for default ODBC test case
        This test is recognizable by 'odbctest=1' property

      Attributes:
      Nothing
     """

     def constructTestCase(self, param, par):
         """ Recognizes and returns command test case

         Args:
          param : TestParam container
          par : OneTestParam container

         Returns:
          Command test case or None

         Raise:
          Exception if error
         """
         starttest = par.getPar(_ODBCTEST)
         if starttest == None: return None
         return [ODBCTestCase(param, par)]

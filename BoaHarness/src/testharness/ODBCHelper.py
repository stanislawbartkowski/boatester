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

"""  Helper for running ODBC/SQL related tests
"""

__authors__ = [
    '"Stansislaw Bartkowski" <stanislawbartkowski@gmail.com>',
]

import pyodbc
import logging
import TestCaseHelper
import TestBoa
import os
import re
import datetime

_CONNECTIONPARAM = 'odbcconnection'
_DBTYPE='dbtype'
_SQLFILE='sqlfile'
_BEGS = '['
_ENDS = ']'
_DEFAULTSECTION = '*'
_DEFAULTNAME='default'

_SQLCOMMANDSTART="sql:"
_COMMENT='--'
_COMMIT='commit'
_VERIFY='verify:'
_PRINT='print:'
_SQLCOMMANDSTARTEXCEPTION="sqlexception:"
_CALLTEST="calltest:"

_SPLITWORDINVER='(?<!\\\\) '
_SPLITVER='(?<!\\\\),'
_ESCAPESPACE='\\ '
_ESCAPECOMA='\\,'

_EQUAL='equal'
_EOF='eof'
_ISNULL='isnull'
_ISNOTNULL='isnotnull'

_DATEFORMAT='%Y-%m-%d'
_BEGA = '('
_ENDA = ')'

class SQLFileHelper() : 
     """ Class for keeping sqlfile (global and local)
     """ 
     def __init__(self, fName):
         """ Constructor
         
         Args: 
           fName  full path name of sql file
         """
         self.__fName = fName
         TestBoa.exist(fName)
         logging.debug("Starting reading file " + fName)
         f = open(fName, "r")
         self.lines = f.readlines()
         f.close()
         
     def getSection(self, secname):
         """ Get lines from sqlfile for for given section name
         
         Args:
           secname section name
           
         Returns:
           list of lines, empty lines are removed
           None : if section not found in  the sql file
         """
         sname = _BEGS + secname + _ENDS
         secline = None
         # secline != None if in the middle of the section
         for l in self.lines :
             if secline != None :
                 #inside section, check if the beginning of the next section
                 if l.find(_BEGS) == 0 : break
                 la = l.strip()
                 # do not add empty lines (possible at the end of line)
                 if la != '' :  secline.append(l.strip())
                 continue
             i = l.find(sname)
             if i == 0 :
                 # section found and lines gathering started
                 secline = []
         if secline != None :
             logging.debug(secname + " found in " + self.__fName)
         return secline
        
class CallSQL :
     """ Class for keeping data for sql statement execution
     """
    
     def __init__(self, he, sql, exceptionexpected, add): 
         """ Constructor
         Args:
           he reference to ODBCHelper
           sql sql statement
           exceptionexpected started with sqlexception:
           add addional parameter, example: sql(52000 John 28), can be None
         """
         self.__he = he
         self.__sql = sql
         self.__exceptionexpected = exceptionexpected
         self.__param = None
         self.__sqlerror = None
         first = True
         if add != None :
             # parse additional string
            split = re.split(_SPLITWORDINVER, add)
             # fields separated by spaces (recognize (escape space), this is why regular expression is used
            for l in split :
                 v = l.replace(_ESCAPESPACE, ' ').strip()
                 # replace escaped space with normal space
                 if first and exceptionexpected :
                     # first file is excpected sqlcode (if not empty)
                     if v != '' :
                         self.__sqlerror = v
                     first = False
                     continue
                 first = False
                 if self.__param == None : self.__param = []
                 # create list of marked parameters
                 self.__param.append(v)
                 
     def execute(self):
         """ Execute sql statement 
         """
         if self.__exceptionexpected :
                 # exceptions is expected, enclose in try except clause
                 try :
                     self.__he.execute(self.__sql, self.__param)
                 except pyodbc.Error, e :
                     sqlerror = e[0]
                     logging.debug(str(e))
                     # test if sql code as expected (if defined)
                     if self.__sqlerror != None :
                         logging.debug("Expected sqlcode " + self.__sqlerror)
                         self.__he.testcase.assertEquals(self.__sqlerror, sqlerror)
         else: self.__he.execute(self.__sql, self.__param)
         
     def append(self, s):
         """ Add content to the existing sql statement
         Args: 
           s next part of sql statement
         """
         self.__sql = self.__sql + " " + s

class ODBCHelper() :
     """ Main class for intepreting and execuing sql related test
     
     Attributes:
       self.dbtype dbtype parameter 
       self.testcase testunit.TestCase
       self.cnxn Connection object
       self.cursor Cursor object (set after self.execute)
     """
    
     def __init__(self,  testcase, param, teparam) :
         """ Constructor
         Args:
           testcase unittest.TestCase
           param TestParam
           teparam OneTestParam
         """
         self.param = param
         self.teparam = teparam
         self.testcase = testcase
         self.dbtype = param.getPar(_DBTYPE)
         self.sqlfile=param.getPar(_SQLFILE)
         if self.sqlfile == None :
             raise TestCaseHelper.TestException(_SQLFILE  + ' sql command file not defined')
         if self.dbtype != None :
             logging.debug(_DBTYPE + " = " + self.dbtype) 
         odbc = self.getPar(_CONNECTIONPARAM )
         if odbc == None :
             raise TestCaseHelper.TestException(_CONNECTIONPARAM  + ' ODBC connection string not defined')
          
         # connect immediately
         logging.info('ODBC connection: ' + odbc)
         self.cnxn = pyodbc.connect(odbc)
         logging.debug('Successfully connected.') 

         # read main and local sqlfile
         self.mainSQL = None
         self.teSQL = None
         resDir = self.param.getGlobResDir()
         mainfile = os.path.join(resDir, self.sqlfile)
         if os.path.exists(mainfile):
             self.mainSQL = SQLFileHelper(mainfile)
         id = self.teparam.getTestId()
         teDir = self.param.getTestDir(id)
         testfile = os.path.join(teDir, self.sqlfile)
         if os.path.exists(testfile):
             self.teSQL = SQLFileHelper(testfile)
    
     def close(self):
         """ Close connection
          Very important: it is running in not "autocommit on" mode
          If not closed and commit has not been released then even after
          test completed the connection is alive and transaction in progress and all locks are held
          Close rolls back all not commited transactions and releases locks
         """
         self.cnxn.close()
          
     def execute(self, s, param = None):
         """ Execute sql statement using connection and keep cursor returned
         Args:
           SQL statement to execute
           param if not None then list of values for parameter markers in the statement
         
         Returns:
           self.cursor Cursor object
         """
         logging.debug(s )        
         if param == None : self.cursor = self.cnxn.execute(s)
         else : self.cursor = self.cnxn.execute(s, param)
    
     def __getParam(self, s, te):
         """ Parameter getter
      
         Args:
          s parameter name
          te SQLFileHelper refrence to search for parameter
          
         Returns:
           Parameter value or None if not found 
         """
         if self.dbtype != None :
             # firstly qualify with database name
             key = self.dbtype + '.' + s
             val = te.getPar(key)
             if val != None : return val
             # if not then without database name
         return te.getPar(s)
    
     def getPar(self, s):
         """ Parameter getter, firstly look in local then in global
         Args:
           s parameter name
           
         Returns:
           Parameter value or None if not found
        
         """
         val = self.__getParam(s, self.teparam)
         # firstly in local OneTestParam
         if val != None : return val
         # if not found then reach out to global TestParam
         return self.__getParam(s, self.param)
                 
     def __runactsql(self):
         """ Execute statement cached in __actsql object
         """
         if self.__actsql != None :
             self.__actsql.execute()
         self.__actsql = None
     
     def __linetokenizer(self, s, listof) :
         """ Analize line having sql statement
         
         Args:
           s Line to analize
           listof Vector of tokens to recognize
           
         Returns:
           Tuple with 3 elements 0: index of action, 1 content and 2 additonal parameters selected from token name
         """
         add = None
         # search for ( and )
         be = s.find(_BEGA)
         en = s.find(_ENDA)
         if be != -1 and en != -1 and en > be :
             add = s[be+1:en]
             # add : string between (..)
             news = s[0:be] + s[en+1:]
             # news : string with ( ..) excluded
         for i in range(len(listof)) :
             to = listof[i]
             if to == None : continue
             inde = s.find(to)
             # firstly look for token ignoring ()
             if inde == -1 and add != None:
                 # if not found try to find token in string with (...) excluded
                 inde = news.find(to)
                 if inde == 0 :
                     # found : return addtional value
                     val = news[len(to):].strip()
                     return (i, val, add)
             if inde == 0 : 
                 # return without additional value
                 val = s[len(to):].strip()
                 return (i, val, None)
         # not recognized
         return (-1, None, None)
         
     def __getValues(self, row, col,  s) :
         """ Gets value from row read and coverts also string to type related to column type
         Args:
          row Row object
          col column name
          s string value (if not none)
          
         Returns:
           Tuple with two objects related to parameters
         """
         for i in range(len(row.cursor_description)) :
             # scan through columns
             coldescr = row.cursor_description[i]
             colN = coldescr[0]
             if colN.upper() == col.upper() :
                 # column found
                 val = None
                 rowval = row[i]
                 ty = coldescr[1]
                 if ty is datetime.datetime and rowval != None :
                     # unfortunately for NULL date column it pyodbc does not return None but meaningless data
                    if rowval.month > 12 or rowval.year > 20000 or rowval.day > 31: rowval = None
                 if s != None :
                     if ty is datetime.datetime :
                         # in case of date convert to datetime object
                         val = datetime.datetime.strptime(s, _DATEFORMAT)
                     else : val = coldescr[1](s)
                 return (rowval, val)
         raise TestCaseHelper.TestException(col + " not found in result set columns")
         
     def __verifyline(self, l):
         """ Validates row according to verify lines
         
         Args:
             l line with veryfying data 
         """
         row = self.cursor.fetchone()
         # fetch next row
         split = re.split(_SPLITVER, l)
         # only for comparators recognized now
         comparators=[_EQUAL, _EOF, _ISNULL, _ISNOTNULL]
         for v in split :
             logging.debug(v)
             vv = v.strip().replace(_ESCAPECOMA, ',')
             # split the veryfying string regarding escaped space (via regular expression)
             elemver = re.split(_SPLITWORDINVER, vv)
             if len(elemver) != 2 and len(elemver ) != 3 and len(elemver) != 1:
                 raise TestCaseHelper.TestException(l + " element: " + v + "  1, 2 or 3 elements expected")
             name = elemver[0].strip().lower()
             par1 = None
             par2 = None
             # recognize additonal parameters
             if len(elemver) >= 2 : par1 = elemver[1].replace(_ESCAPESPACE, ' ')
             if len(elemver) == 3 : par2 = elemver[2].replace(_ESCAPESPACE, ' ')
             # recognize comparator
             action = None
             for i in range(len(comparators)) :
                 co = comparators[i]
                 if co == name :
                     action = i
                     break
             if action == None :
                 error = name +" not recognized verifier. Expected:"
                 for a in comparators : error = error + " " + a
                 raise TestCaseHelper.TestException(error)
             # check number of parameters
             expected = 2
             if action == 1 : expected = 0
             if action == 2 or action == 3 or action == 6 : expected = 1
             if len(elemver) -1 != expected :
                 error = name + " number of arguments invalid, " + str(expected) + " expected, " + str(len(elemver) -1)  + " found"
                 raise TestCaseHelper.TestException(error)
             # now execute validation
             if action == 1 :
                 # if last row recognized properly
                 if row == None : continue
                 self.testcase.fail("End of result set expected")
             if row == None :            
                 self.testcase.fail("Unexpected end of result set, fetch next returned None")
             (val1, val2) = self.__getValues(row, par1, par2)
             if action == 0:
                 self.testcase.assertEqual(val1, val2)
             if action == 2:
                 self.testcase.assertIsNone(val1)
             if action == 3:
                 self.testcase.assertIsNotNone(val1)
                 
     def __createListOf(self) :
         listof = [_SQLCOMMANDSTART,_COMMENT, _COMMIT, _VERIFY, _PRINT, _SQLCOMMANDSTARTEXCEPTION, _CALLTEST]
         return listof   

     def __executeSectionLines(self, seclines):
         """ Executes test case described in list of lines
         
         Args:
           seclines : list of lines
         """ 
         self.__actsql = None
         # self.__sctsql caches current  sql statement
         listof = self.__createListOf()
         # if True then validation data
         verify = False
         
         for l in seclines :
             (op, content,  add) = self.__linetokenizer(l, listof)
             # mark the end of validation data
             if op == 0 or op == 2 or op == 5 or op == 6: verify = False
             if op == 0  or  op == 5: 
                 # sql statement with exception expected or not
                 self.__runactsql()
                 self.__actsql = CallSQL(self, content,(op == 5), add)
                 # statement is not executed now, only cached for later execution
                 # sql statement can be multilined
                 continue
             if op == 1 : continue
             if op == 2:
                 # commit
                 self.__runactsql()
                 logging.debug("commit")
                 self.cnxn.commit()
                 continue
             if op == 3 :
                 # verify,, next lines contains validation data
                 self.__runactsql()
                 # statement for validation executed immediately
                 self.execute(content)
                 verify = True
                 continue
             if op == 4 :
                 # print only, comand for debugging purpose only
                 self.__runactsql()
                 print content
                 continue
             if op == 6:
                 # run another section
                 self.__runactsql()
                 self.executeSection(content)
                 continue
             if not verify :    
                 # multilined sql statement, add next part
                 self.__actsql.append(l)
             else :
                 # validation line
                 self.__verifyline(l)  
         
         self.__runactsql()
         
     def executeSection(self, secname=_DEFAULTNAME):
         """ Execute testcase described in the section
         Args:
           secname section name, it is expected that the section exists
           if secname is equal to _DEFAULTSECTION (*) then 'default' is assumed
         """
         logging.debug("Looking for " + secname)
         seclines = None
         # recognize default
         if secname ==_DEFAULTSECTION :
             secname = _DEFAULTNAME
         # determine where to read test case (section)
         # firstly local look up then global
         if self.teSQL != None :
             seclines = self.teSQL.getSection(secname)
         if seclines == None :
             # if not found locally then look in glopbal sqlfile
             if self.mainSQL != None :
                 seclines = self.mainSQL.getSection(secname)
         if seclines == None :
             raise TestCaseHelper.TestException(secname + " cannot find")
         self.__executeSectionLines(seclines)
         
  

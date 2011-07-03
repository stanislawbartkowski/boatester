#
# Copyright [2010] the stanislaw.bartkowski@gmail.com
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

"""  Helper for running Selenium test
"""

__authors__ = [
    '"Stanislaw Bartkowski" <stanislawbartkowski@gmail.com>',
]

import logging
import TestCaseHelper
import TestBoa
import os
import os.path
import time

def _readC(fname, param, teparam):
   """ Produces ConfigP object for reading selenium files
    
    Args:
      fname : configuration file name (full path)
      param : TestParam container
      tepar : OneTestParam container

      
    Returns:
      ConfigP object created
      
    Raise:
      TestException if file does not exist
    """
   if fname == None : return None
   TestBoa.exist(fname)
   logging.debug("Read selenium config file from : " + fname)
   co = ConfigP(fname, param, teparam)
   return co

class ConfigP :

    """ Helper class for maintaining selenium configurationf iles
    """

    def __init__(self,fname, param, teparam):
        """ Constructor for ConfigP file

        Args:
          fname : configuration file name, full path
          param : TestParam container
          tepar : OneTestParam container
        """
        f = open(fname)
        list = f.readlines()
        f.close()
        self.lines = []
        for l in list :
            self.lines.append(TestCaseHelper.replaceLine(l, param, teparam))

    """ Returns sequence of selenium action to execute

    Args:
      secname : section name in configuraiton file to read

    Returns:
      Sequence of action elem (actionname, (list of params))

    """
    def getSec(self,secname):
        secname = '[' + secname + ']'
        res = None
        for l in self.lines :
            ll = l.strip()
            if ll == "" : continue
            if ll[0] == ';' : continue
            if ll[0] == '-' : continue
            if res == None :
                if ll == secname :
                    res = []
                continue
            if ll[0] == '[' : break
            a = ll.split(':',1)
            if len(a) > 1 :
               res.append((a[0].strip(),a[1].strip()))
            else :
               res.append((a[0].strip(),None))
        return res

    """ Getter for option name from [alias] section

    Args:
      key : key of option to return

    Returns:
      option value or None if option does not exist

    """
    def getOption(self,key):
        res = self.getSec('alias')
        if res == None : return None
        for a in res :
            ke = a[0]
            va = a[1]
            if ke == key : return va
        return None


class ConfigFileHelper :
    """ Helper for maintaing selenium configuration file

    """

    def __init__(self,mainfile,testfile, param, teparam):
        """ Constructor

        Args:
          mainfile : file path name of global selenium file (secondary)
          testfile : file  path name of test selenium file (primary)

        """
        self.param = param
        self.teparam = teparam        
        self.mainco = _readC(mainfile, self.param, self.teparam)
        self.testco = _readC(testfile, self.param, self.teparam)

        
    def __getAlias(self,key):
        """ Getter for alias value. Firsty primary file is searched,
            than secondary file

        Args:
          key : alias key

        Returns:
          alias value

        Raise:
           TestException if alias does not exist

        """
        o = key.strip()
        if self.testco != None :
           al = self.testco.getOption(o)
           if al != None : return al
        if self.mainco != None :
           al = self.mainco.getOption(o)
           if al != None : return al
        raise TestCaseHelper.TestException(key + " no alias with that name")

    def getSequence(self,name):
        """ Returns sequence of selenium actions

        Args:
          name : test name (section name)

        Returns:
          Sequence of action. Action if firstly search in primary file
          and (if not found) in secondary file

        Raise:
           TestException if name does not exist
        """
        keys = None
        if self.testco != None :
            keys = self.testco.getSec(name)
        if keys == None :
            if self.mainco != None :
               keys = self.mainco.getSec(name)
        if keys == None :
           raise TestCaseHelper.TestException(name + " no such section")
        res = []
        for k in keys :
            ke = k[0]
            va = k[1]
            pa = []
            if va != None:
                pa = va.split('|')
                for i in range(0,len(pa)) :
                  ss = pa[i]
                  if len(ss) != 0 :
                    ch = ss[0]
                    if ch == '#' :
                      re = ss[1:]
                      pa[i] = self.__getAlias(re)
            res.append((ke,pa))
        return res

class seleniumTypeContext :
    """  Base class for extending by action handler
    """

    def __init__(self) :
        """ Constructor - empty for the time being
        """
        pass

    def setParam(self,cparam,se,tcase,param,teparam) :
        """ Set context param. Called by test runner
        
         Args:
           cparam :  ConfigFileHelper refrence
           se : Selenium class
           tcase : unittest.TestCase class containing this test
           param : TestParam container
           tepar : OneTestParam container
        
        """
        if cparam != None :
            logging.debug(self.key + " " + str(cparam))
        else :
            logging.debug(self.key)
        self.cparam = cparam
        if cparam == None or len(cparam) < self.nof :
            # check default vales
            dlen = 0
            if self.defa != None : dlen = len(self.defa)
            if len(cparam) + dlen < self.nof :        
              raise TestCaseHelper.TestException(self.key + " requires " + str(self.nof) + " parameters! Actual number : " +  str(cparam))
            # default values  
            for pa in self.defa :
              self.cparam.append(pa)  
              
           
        self.se = se
        self.tcase = tcase
        self.param = param
        self.teparam = teparam
        
    def getParam(self):
        """ Getter for params
        
        Returns:
          Look setParam
        """
        return (self.ce, self.cparam, self.tcase, self.param, self.teparam)

    def setInfo(self,key,nof, defa=None) :
        """ Set additonal information for action handler
        
        Args:
          key : action name
          nof : number of parameters
          defa : list of default parameters (if actual less than nof)
        """
        self.key = key
        self.nof = nof
        self.defa = defa

def waitForElement(tcase,sel,ele,sec=5) :
    """ Waits for element on the screen
    
    Args:
       tcase : Unittest class
       sel : Selenium type
       ele : element to wait for
       sec : maximum number of second to wait for
       
     Raise:
       fails test case if time expires
       
    """
    for i in range(1,sec) :
        if sel.is_element_present(ele) : return
        time.sleep(1)
    tcase.fail(ele + " cannot find that element !")
        

class seleniumType(seleniumTypeContext) :
    """ Action class for 'type' action 
    First parameter - element selector
    Second parameter - string to be typed in
    """
    def do(self):
        self.se.type(self.cparam[0], self.cparam[1])
        
class seleniumKeyDown(seleniumTypeContext) :
    """ Action class for 'type' action 
    First parameter - element selector
    Second parameter - string to be typed in
    """
    def do(self):
        self.se.key_press(self.cparam[0], self.cparam[1])
        
class seleniumFocus(seleniumTypeContext) :
    """ Action class for 'click' action
    First parameter: element selector to be clicked
    """

    def do(self):
        id = self.cparam[0]
        self.se.focus(id)


class seleniumClick(seleniumTypeContext) :
    """ Action class for 'click' action
    First parameter: element selector to be clicked
    """

    def do(self):
        id = self.cparam[0]
        self.se.click(id)
        
class seleniumWait(seleniumTypeContext) :
    """ Action class for 'sleep' action
    First parameter: number of seconds to slepp
    """

    def do(self):
        nosec = int(self.cparam[0])
        time.sleep(nosec)
        
class seleniumDebug(seleniumTypeContext) :
    """ Empty class only for debug purpose
    Allows to set breakpoint
    """

    def do(self):
        pass
        
class seleniumWaitFor(seleniumTypeContext) :
    """ Action class for 'waitFor' action
    First parameter: element selector to be waited
    """

    def do(self):
        sec = int(self.cparam[1])
        waitForElement(self.tcase,self.se,self.cparam[0], sec)
        
class selectCombo(seleniumTypeContext) :
    """ Action class for 'selectCombo' action
    First parameter: element selector for 'select' tag
    Second parameter: Value to be selected
    """
    def do(self):
        locator = self.cparam[0]
        label = self.cparam[1]
        self.se.select(locator, 'value=' + label)
        
class seleniumMouseOver(seleniumTypeContext) :
    """ Action class for 'mouseOver' action
    First parameter: element selector for which 'mouseOver' action is performed
    """

    def do(self):
        self.se.mouse_over(self.cparam[0]);        
        
# sel.mouse_over(self.PASSWORD)

class seleniumIsPresent(seleniumTypeContext) :
    """ Action class for 'isPresent' action
    First parameter: element selector to be searched
    """

    def do(self):
        ele = self.cparam[0]
        ispresent= self.se.is_element_present(ele)
        self.tcase.assertTrue(ispresent, ele + " not present")

class seleniumVerEqual(seleniumTypeContext) :
    """ Action class for 'verEqual' verification action
    First parameter: element selector
    Second parameter: string to be verified 
    """

    def do(self):
        id = self.cparam[0]
        vermess = self.cparam[1]
        mess = self.se.get_value(id)
        self.tcase.assertEqual(vermess, mess)

class SeleniumHelper :
    """ Helper supporting selenium action
    """

    def __init__(self,se):
        """ Constructor
        
        Args:
          se - Selenium class
        """
        self.se = se
        self.a = {}
        self.registerAction('type',seleniumType(),2)
        self.registerAction('click',seleniumClick())
        self.registerAction('sleep',seleniumWait())
        self.registerAction('waitFor',seleniumWaitFor(),2,  [5])
        self.registerAction('debug',seleniumDebug(),0)
        self.registerAction('verEqual',seleniumVerEqual(),2)
        self.registerAction('isPresent',seleniumIsPresent())
        self.registerAction('mouseOver',seleniumMouseOver())
        self.registerAction('selectCombo',selectCombo(), 2)
        self.registerAction('keyDown',seleniumKeyDown(), 2)
        self.registerAction('focus',seleniumFocus(), 1)
        

    def registerAction(self,key,o,nofParam = 1, defa=None):
        """ Register custom action handler
        
        Args:
          key : action name
          o : action handler (extends SeleniumTypeContext)
          nofParam : number of parameters expected
        """
        logging.debug('Register action ' + key + ' num of params:' + str(nofParam))
        o.setInfo(key,nofParam, defa)
        self.a[key] = o
        

    def setParam(self,tcase,param,teparam):
        """ Sets param
        
        Args:
          tcase : unittest.TestCase
          param : TestParam container
          tepar : OneTestParam container
        """
        self.tcase = tcase
        self.param = param
        self.teparam = teparam
        
    def getParam(self):    
        """ Getter
        Returns:
          Look setParam
        """
        return (self.tcase, self.param, self.teparam)

    def runTest(self,name):
        """ Runs test 'name'
        
        Args:
          name : test name to be run
          
        Raise:
           Fails test in case of error
        """
        mainfile = None
        gName = self.param.getPar('selfile')
        if gName != None :
           resDir = self.param.getGlobResDir()
           mainfile = os.path.join(resDir, gName)
        testfile = None
        tefile = self.teparam.getPar('selfile')
        if tefile != None :
            id = self.teparam.getTestId()
            teDir = self.param.getTestDir(id)
            testfile = os.path.join(teDir, tefile)
        co = ConfigFileHelper(mainfile,testfile, self.param, self.teparam)
        seq = co.getSequence(name)
        for step in seq :
            key = step[0]
            param = step[1]
            action = self.a[key]
            action.setParam(param,self.se,self.tcase,self.param,self.teparam)
            action.do()

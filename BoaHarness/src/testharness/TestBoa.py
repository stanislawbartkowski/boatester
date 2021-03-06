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

"""Main Boa test harness package
"""

__authors__ = [
    '"Stanislaw Bartkowski" <stanislawbartkowski@gmail.com>',
]

import ConfigParser
import logging
import os
import os.path
import sys
import unittest


import TestCaseHelper
import ODBCTestCase
import NZPDATestCase

_TEST = "test"

_HOST='host'
_PORT='port'
_BROWSER='browser'
_HTTP='http'
_START='start'
_QUERY="httpquery"
_BINARY="browserbinary"

def _getDir(param, s):
    """ Get directory local to common resource.

    Args:
      param : TestParam container
      s : subdirectory

    Returns:
      Path name to local (in common resource) directory

    Raise:
      Nothing
    """
    dd = param.getResDir()
    di = os.path.join(dd, s)
    return di

def _readTests(param, testrun, testid):
    """ Read list of tests in test resource directory
        Resolves 'testrun' property

    Args:
      param : TestParam container
      testrun : all, one or from
      testid : number of test for one or from value

    Returns:
      List of tuples (testid, testno)

    Raises:
      Exception if error
      Also raises TestException if no any test was found
    """
    logging.debug("Read tests testrun=" + testrun + " testid=" + testid)
    dd = param.getResDir()
    if not os.path.isdir(dd):
        raise TestCaseHelper.TestException(dd + " : directory not found !")
    li = os.listdir(dd)
    list = []
    for d in li:
        logging.debug("Directory " + d)
        di = _getDir(param, d)
        if not os.path.isdir(di):
            logging.debug(di + " not directory, omit")
            continue;
        lower = d.lower()
        logging.debug(lower + " test if contains " + _TEST)
        if lower.find(_TEST) != 0:
            logging.debug("Does not contain, omit")
            continue;
            
        disabled = os.path.join(di, "disabled")    
        logging.debug("Check for disabled:" + disabled)
        if os.path.exists(disabled):
            logging.debug("Test disabled : ignore this test") 
            continue
        numb = lower[len(_TEST): 100]
        testno = int(numb)
        logging.debug("Testno=" + str(testno))

        dodaj = 0
        if testrun == "all":
            dodaj = 1
        elif testrun == "one":
            if int(testid) == testno:
                dodaj = 1
        elif testrun == "from":
            if testno >= int(testid):
                dodaj = 1

        if dodaj:
            logging.debug("Add test directory " + d + " with number " + str(testno))
            list.append((d, testno))


    if len(list) == 0:
        raise TestCaseHelper.TestException(dd + " : no test case found !")

    return list

def _getTestCase(factory, param, testId):
    """ Find test case handlerfor test

    Args:
      factory : TestCaseFactory intance
      param : TestParam container
      testId : test id

    Returns:
      unittest.TestCase valid for testId

    Raise:
      Exception if error
    """
    li = param.getTestDir(testId)
    desc = os.path.join(li, "test.properties")
    logging.debug("Check if exists file " + desc)
    if not os.path.isfile(desc):
        logging.debug("Does not exist, omit")
        return None
    cfte = _readListParam(desc, param.suiteparam)
    par = TestCaseHelper.OneTestParam(testId, cfte)
    for fa in factory.getListFactory():
        testcase = fa.constructTestCase(param, par)
        if testcase != None: return testcase

    return None

def _resReport(res):
    """ Report test result

    Args:
      res : unittest.TestResult object

    Returns:
      Nothing

    Raise:
      Nothing
    """
    no = res.testsRun
    print "========================="
    restest = 0
    infores = "TEST FAILED"
    if res.wasSuccessful():
        infores = "TEST PASSED"
        restest = 1
    print infores, " number of tests :", no
    li = res.errors
    for t in res.failures:
        li.append(t)
    if not restest:
        print "Number of tests failed :", len(li)
        print "LIST OF FAILED TESTS :"
        fullinfo = len(li) == 1
        for te in li:
            tes = te[0:2]
            ca = tes[0]
            descr = tes[1]
            if fullinfo : print descr
            print "    ", ca.teparam.getTestId()

def _readListParam(desc, suiteParam ):
    """ Read property file

    Args:
      desc : property file (path name)
      suiteParam : SuiteParam

    Returns:
      Dictionary key:value

    Raise:
      Exception if error
      TestException if property file does not exist
    """
    cf = ConfigParser.ConfigParser(suiteParam.createDict())
    logging.debug("Read property file " + desc)
    TestCaseHelper.exist(desc)
    cf.read(desc)
    list = cf.items("defaults")
    h = {}
    for (key, val) in list:
        h[key] = val
    return h

class PythonUnitTestFactory:
    """ Factory for python unit tests

    This test is recognizable by 'testcase' property

    Attributes:
      Nothing

    """

    def constructTestCase(self, param, par):
        """ Recognizes and returns python unit test

        Args:
          param : TestParam container
          par : OneTestParam container

        Returns:
          python unit test if it is
          None : otherwise

        Raise:
          Exception if error
        """
        if par.isTestCase():
            val = par.getPar('dirtestcase')
            if val == None :
               li = param.getTestDir(par.getTestId())
            else :
               li = val   
            prev = sys.path
            sys.path.append(li)
            lo = unittest.TestLoader()
            logging.debug('Read test case ' + par.getTestCase() + " from directory " + li)
            mod = __import__(par.getTestCase())
            mod.injectParam(param, par)
            ca = lo.loadTestsFromModule(mod)
            sys.path = prev
            return ca
        return None

class CommandTestCase(unittest.TestCase):
    """ Command (shell) test case

    Attributes:
      param : TestParam container
      teparam : OneTestParam container

    """

    def __init__(self, param, teparam):
        """ Constructor

          Args:
            param : TestParam container
            teparam: OneTestParam container

        """
        unittest.TestCase.__init__(self, 'runTest')
        self.param = param
        self.teparam = teparam

    def setUp(self):
        """ unititest SetUp
        """
        TestCaseHelper.prepareRunDir(self.param, self.teparam)

    def runTest(self):
        """ unittest runTest
        """
        TestCaseHelper.copyFile(self.param, self.teparam, self.teparam.getCommand())
        destd = self.param.getRunDir()
        runcommand = os.path.join(destd, self.teparam.getCommand())
        TestCaseHelper.prepareRunCommand(runcommand)
        res = TestCaseHelper.runBin(self.param, runcommand, runcommand)
        if res != 0:
            unittest.TestCase.fail(self, runcommand + " failed. Return code:" + str(res))


class CommandUnitTestFactory:
    """ Factory for CommandTestCase
        This test is recognizable by 'command' property

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
        command = par.getCommand()
        if command == None: return None
        return [CommandTestCase(param, par)]

class SeleniumTestCase(unittest.TestCase):

     def __init__(self, param, teparam):
         unittest.TestCase.__init__(self, 'runTest')
         self.param = param
         self.teparam = teparam

     def __getP(self, key, default=None) :
         return TestCaseHelper.getParam(self.param, self.teparam, key, default)
         
     def setUp(self):
         from selenium import selenium
         import SeleniumHelper
         host = self.__getP(_HOST)
         port = int(self.__getP(_PORT))
         browser = self.__getP(_BROWSER)
         http = self.__getP(_HTTP)
         self.selenium = selenium(host, port, browser, http)
         binary = self.__getP(_BINARY,"")
         browserOptions = None
         if binary != "":
            browserOptions=("executablePath=" + binary)
         self.selenium.start(browserOptions)
         self.seHelper = SeleniumHelper.SeleniumHelper(self.selenium)
         self.seHelper.setParam(self,self.param,self.teparam)
         self.ok = False

     def runTest(self):
         query=self.__getP(_QUERY, "")
         self.selenium.open(query)
         self.seHelper.runTest(self.__getP(_START,'start'))
         self.ok = True
    
     def tearDown(self) :
         if self.ok :
             self.selenium.close()
             self.selenium.stop()

class SeleniumTestFactory:

    def constructTestCase(self, param, tepar):
         selFile = tepar.getPar('selfile')
         if selFile == None : return None
         teca = SeleniumTestCase(param, tepar)
         return [teca]

class TestCaseFactory:

    """ Container for test case factories
        Two factories are predefined

    Attributes:
      factory : queue with all factory registered
    """

    def __init__(self):
        """ Contructor
            Defines two default factories
        """
        self.factory = []
        self.register(PythonUnitTestFactory())
        self.register(CommandUnitTestFactory())
        self.register(ODBCTestCase.ODBCUnitTestFactory())
        self.register(SeleniumTestFactory())
        self.register(NZPDATestCase.NZPDAFactory())


    def register(self, fa):
        """ Register next factory

        Args:
          fa : factory

        Returns:
          Nothing

        Raises:
          Nothing
        """
        self.factory.append(fa)

    def getTestCase(self, param, tepar):
        """ Return test case by looking up in the factories defined

        Args:
          param : TestParam container
          tepar: OneTestParam container

        Returns:
          test case if found
          None otherwise

        Raise:
          Nothing
        """
        for fa in self.factory:
            testcase = fa.constructTestCase(param, tepar)
            if testcase != None: return testcase
        return None

    def getListFactory(self):
        """ Returns factory list
        """
        return self.factory

class RunSuiteParam:
    """ Container for run test suite command

    Attributes:
      factory : TestCaseFactory
      customC : custom object
      testprop : file name for common test suite property file (can be None)
      globresdir : directory for common resources
      resdir : directory with test cases
      rundir : working directory for test running tests
    """


    def __init__(self, factory, customC, testprop, globresdir, resdir, rundir, customdic=None):
        """ Constructor

        Args:
          look above
        """
        self.factory = factory
        if factory == None :
            self.factory = TestCaseFactory()
        self.customC = customC
        self.testprop = testprop
        self.globresdir = globresdir
        self.resdir = resdir
        self.rundir = rundir
        self.customdic = customdic
        
    def createDict(self) :
         dict = {}
         for key in os.environ : dict[key] = os.environ[key]
         dict['globresdir'] = self.globresdir
         dict['resdir'] = self.resdir
         dict['rundir'] = self.rundir
         if self.customdic != None :
          for key in self.customdic:
             dict[key] = self.customdic[key]
         return dict


def runSuite(suiteparam, testrun, testid):
    """ Runs the whole test suite, main entry
    Args:
      suiteparam : RunSuiteParam container
      testrun: following values possible: one, all or from
      testid: test case to run (for 'one' or 'from')
    
    Returns:
      nothing
      
    Raises:
      Exception in case of any error
    """

    try:
        he = None
        if suiteparam.testprop != None:
            he = _readListParam(suiteparam.testprop,  suiteparam)
        param = TestCaseHelper.TestParam(he, suiteparam)

        list = _readTests(param, testrun, testid)
        list.sort()
        suite = unittest.TestSuite()

        for (testid, num) in list:
            logging.info("Run: " + testid + " " + str(num))
            te = _getTestCase(suiteparam.factory, param, testid)
            if te != None: suite.addTests(te)

        res = unittest.TestResult()
        suite.run(res)
        _resReport(res)

    except TestCaseHelper.TestException, e:
        e.draw()

def printhelp():
    print "Usage:"
    print "prog /res dir/ /run dir/ /spec/ /testid/"

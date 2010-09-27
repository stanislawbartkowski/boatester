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

_TEST = "test"

def exist(fname):
    """ Check if directory exists (as expected)
    
    Args:
      fname : directory, path name, to test
      
    Returns:
      Nothing
      
    Raise:
      TestException if directory not exist
    """

    if not os.path.exists(fname):
        raise TestCaseHelper.TestException(fname + " file does not exists")

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
            logging.debug("Add test diectory " + d + " with number " + str(testno))
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
    cfte = _readListParam(desc)
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
        print "LIST OF FAILED TESTS :"
        for te in li:
            tes = te[0:2]
            ca = tes[0]
            descr = tes[1]
            print descr
            print "    ", ca.id()

def _readListParam(desc):
    """ Read property file

    Args:
      desc : property file (path name)

    Returns:
      Dictionary key:value

    Raise:
      Exception if error
      TestException if property file does not exist
    """
    cf = ConfigParser.ConfigParser()
    logging.debug("Read property file " + desc)
    exist(desc)
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
            li = param.getTestDir(par.getTestId())
            prev = sys.path
            sys.path.append(li)
            lo = unittest.TestLoader()
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
        """ Return test case by looking up in factories defined

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


    def __init__(self, factory, customC, testprop, globresdir, resdir, rundir):
        """ Constructor

        Args:
          look above
        """
        self.factory = factory
        self.customC = customC
        self.testprop = testprop
        self.globresdir = globresdir
        self.resdir = resdir
        self.rundir = rundir


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
            he = _readListParam(suiteparam.testprop)
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

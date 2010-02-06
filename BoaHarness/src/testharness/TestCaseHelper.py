#!/usr/bin/python2.5
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

"""Some public helper functions and classes for Boa test harness
"""

__authors__ = [
    '"Stansislaw Bartkowski" <stanislawbartkowski@gmail.com>',
]

import filecmp
import logging
import os
import shutil
import tempfile
import time
import unittest

def _getKey(cf, key):
    if cf == None : return None
    ikey = osPrefix() + "." + key
    if cf.has_key(ikey): return cf[ikey]
    if cf.has_key(key): return cf[key]
    return None

def osPrefix():
    """Returns system prefix

  Args:
    No args

  Returns:
    linux/windows

  Raises:
    Nothing
    """
    name = os.name
    if name == "posix": return "linux"
    return "windows"

def isLinux():
    """Is host system linux

  Args:
    No args

  Returns:
    True: linux, False: windows

  Raises:
    Nothing
    """
    prefix = osPrefix()
    if prefix == "linux": return True
    return False

def prepareRunCommand(command):
    """Modify command (binary file) with 'executable' access
    
    Is valid for windows but do nothing
    On linux: chmod a+x,g+a,u+x command

  Args:
    File name

  Returns:
    Nothing

  Raises:
    Exception if error
    """
    if not isLinux(): return
    os.chmod(command, 0777)

def _getTmpName():
    """Returns temporary and uniq file name

  Args:
    Nothing

  Returns:
    File name

  Raises:
    Exception if error
    """
    f = tempfile.mkstemp()
    tmp = f[1]
    os.close(f[0])
    return tmp


def __waitforBin(bin):
    """Stops until process is not visible in ps command.

    Wait for command to exit

  Args:
    Command to watch

  Returns:
    Nothing

  Raises:
    Nothing
    """
    logging.debug("Wait for " + bin)
    while True:
        time.sleep(1)
        tmp = _getTmpName()
        logging.debug("Read ps output to temp " + tmp)
        os.system("ps -aef >" + tmp)
        f = open(tmp)
        li = f.readlines()
        f.close()
        os.unlink(tmp)
        found = 0
        for l in li:
            if l.find(bin) != -1:
                found = 1
                break
        if not found:
            break

def runBin(param, com, binarywaited):
    """Launch command and wait for exit


  Args:
    param: TestParam
    com: command to lauch
    binarywaited: binary string visible in ps command

  Returns:
    Exit code

  Raises:
    Exception if any error has occured
    """
    dir = os.getcwd()
    os.chdir(param.getRunDir())
    res = os.system(com)
    __waitforBin(binarywaited)
    os.chdir(dir)
    return res


class TestException(Exception):

    """General exception raised

      Attributes:
       s : error message

    """

    def __init__(self, s):
        """Constructor

        Args:
          s : error message
        """
        self.s = s

    def draw(self):
        """Prints error message

        Args: nothing

        Returns: nothing

        Raises: nothing

        """
        print self.s


class OneTestParam:

    """Container for test case parameters

     Attributes:
       testId : string, test identifier
       cf : dictionary, test properties, key : value
         predefined:
          'descr' - short test description
          'testcase' : if not None predefined python test case
          'copytestres' : if not Nodn test resource to copy
          'copycommonres' : if not None common resource to copy
          'command' : if not None predefined command test case
    """

    def __init__(self, testId, cf):
        """ Constructor

        Args:
          testId : test identifier
          cf : dictionary for test specific properties

        """
        self.testId = testId;
        self.cf = cf

    def getPar(self, key):
        """ Getter for test properties

        Args:
          key : key for property

        Returns:
          Value or None  if property not defined

        """
        return _getKey(self.cf, key)

    def getDescr(self):
        """ Getter for description property
        """
        return self.getPar('descr')

    def getTestId(self):
        """ Getter for test id property
        """
        return self.testId

    def isTestCase(self):
        """ Checker if test case is predefined python test case

        Returns:
           True: if predefined python test case
           False: otherwise

        """
        if self.cf.has_key('testcase'): return 1
        return 0

    def getTestCase(self):
        """ Getter for test case property

        Returns:
          Test case name or None if not defined

        """
        return self.getPar('testcase')

    def getCopyTestRes(self):
        """ Getter  for 'copytestres' property
        """

        return self.getPar('copytestres')

    def getCopyCommonRes(self):
        """ Getter for 'copycommonres' property
        """
        return self.getPar('copycommonres')

    def getCommand(self):
        """ Getter for 'command' property
        """
        return self.getPar('command')


class TestParam:

    """ Container for general test suite properties

    Attributes:
      suiteparam : container for test suite run parameters
      cf : dictionary with test suite properties
        can be None if not defined

    """

    def __init__(self, he, suiteparam):
        """ Constructor

        Args:
          he : dictionary with test suite properties (can be None)
          suiteparam : container with test suite run param

        """
        self.cf = he
        self.suiteparam = suiteparam

    def getResDir(self):
        """ Getter for 'resdir' parameter
            (directory where test cases and resources are placed)
        """
        return self.suiteparam.resdir

    def getGlobResDir(self):
        """ Getter for 'globresdir' parameter
            (directory where common resources are located)
        """
        return self.suiteparam.globresdir

    def getTestDir(self, s):
        """ Getter for directory where resource for one test case are located

        Args:
          s : test case identifier

        Returns:
          Path name, directory for test case

        """
        dd = self.suiteparam.resdir
        di = os.path.join(dd, s)
        return di
    
    def getRunDir(self):
        """ Getter for 'run dir' parameter
            (directory where test case is copied and launched)
        """
        return self.suiteparam.rundir

    def getPar(self, key):
        """ Getter for global test suite property

        Args:
          key : parameter key

        Returns:
          value or None if property not defined

        """
        return _getKey(self.cf, key)

    def getCustomC(self):
        """ Getter for 'customC' reference
        """
        return self.suiteparam.customC


def removeDir(te):
    """ Remove directory and all subdirectories.

    Args:
      te : directory name to be removed

    Returns:
      Nothing

    Raise:
      Exception if error

    """
    if not os.path.isdir(te): return
    shutil.rmtree(te)

def copyDir(sou, dest):
    """ Copy directory (with subdirectories)

    Args:
      sou : directory name to be copied from
      dest : directory to be copied to

    Returns:
      Nothing

    Raise:
      Exception if error
    """
    if not os.path.isdir(dest):
        shutil.copytree(sou, dest)
        return
    li = os.listdir(sou)
    for na in li:
        soul = os.path.join(sou, na)
        destl = os.path.join(dest, na)
        if os.path.isfile(soul):
            shutil.copyfile(soul, destl)
        else:
            copyDir(soul, destl)

def copyFile(param, teparam, file):
    """ Copy  file from test case directory to run directory

    Args:
      param : TestParam container
      teparam: OneTestParam container
      file : file name to be copied

    Returns:
      Nothing

    Raise:
      Exception if error

    """
    soud = param.getTestDir(teparam.getTestId())
    soufile = os.path.join(soud, file)
    destd = param.getRunDir()
    destfile = os.path.join(destd, file)
    shutil.copyfile(soufile, destfile)


def clearRunDir(param):
    """ Clean run directory, removes all files

    Args:
      param : TestParam container

    Returns:
      Nothing

    Raise:
      Exception if error

    """
    tt = param.getRunDir()
    logging.debug("Clear " + tt)
    removeDir(tt)
    if not os.path.isdir(tt):
        os.makedirs(tt)

def __copyRes(test, testId, dest):
    """ Copy resource (command or test case specific) to run directory

    Args:
      test : TestParam container
      testId : if None common resource, test case resource otherwise
      dest : resource description (<name sou> : <name dest>

    Returns:
      Nothing

    Raise:
      Exception if error

    """
    if dest == None: return
    sou = test.getResDir()
    if testId != None:
        sou = test.getResDir()
        sou = test.getTestDir(testId)
    else:
        sou = test.getGlobResDir()
    list = dest.split(":")
    if len(list) == 1:
        soud = list[0]
        destd = soud
    else:
        soud = list[0]
        destd = list[1]
    soudir = os.path.join(sou, soud)
    destdir = os.path.join(test.getRunDir(), destd)
    logging.debug(soudir + " ==> " + destdir)
    copyDir(soudir, destdir)


def prepareRunDir(param, teparam):
    """ Prepare run directory for testcase : cleans and copy resources


    Args:
      param : TestParam container
      teparam : OneTestParam container

    Returns:
      Nothing

    Raise:
      Exception if error

    """
    clearRunDir(param)
    __copyRes(param, None, teparam.getCopyCommonRes())
    __copyRes(param, teparam.getTestId(), teparam.getCopyTestRes())

def compareFiles(param, teparam, testdir, patt, destdir):
    """ Compare files in test case resource directory and test dir

    Args:
      param : TestParam container
      teparam: OneTestParam container
      testdir : subdirectory in test case resource with files to compare
      patt : file pattern for file to be compared
      destdir : subdirectory in run dir containing files to be compares

    Returns:
      True: all files are the same
      False: at least one file is different

    Raise:
      Exception if any error

    """
    t = param.getTestDir(teparam.getTestId())
    xdir = os.path.join(t, testdir)
    if not os.path.isdir(xdir): return 1
    li = os.listdir(xdir)
    tdir = param.getRunDir()
    res = 1
    for l in li:
        if l.find(patt) == -1: continue
        sou = os.path.join(xdir, l)
        dest = os.path.join(tdir, destdir)
        dest = os.path.join(dest, l)
        logging.info(sou + " <=> " + dest)
        if not os.path.isfile(dest):
            logging.info ("  " + dest + " - does not exist")
            res = 0
            continue
        eq = filecmp.cmp(sou, dest)
        if not eq:
            logging.info("  different")
            res = 0
    return res

class SampleTestCase(unittest.TestCase):
    """ Sample test case, do nothing

    Attributes:
      param : TestParam container
      teparam : OneTestParam container

    """

    def __init__(self, param, teparam):
        unittest.TestCase.__init__(self, 'runTest')
        self.param = param
        self.teparam = teparam

    def setUp(self):
        prepareRunDir(self.param, self.teparam)

    def runTest(self):
        print self.teparam.getDescr()

